"""C3.4: policy registry, copy-level state (A20) and compliance. Activity claims never set a state."""
import json
from collections import defaultdict
from datetime import datetime, timedelta, timezone

import pytest

from conftest import DATASET, read_csv
from ghostaudit.evidence import EvidenceStore, Observation
from ghostaudit.identity import IdentityIndex
from ghostaudit.policy import SYSTEM_CATEGORY, UNMAPPED, assess, load_rules
from ghostaudit.temporal import CaseView
from ghostaudit.timeutil import parse_ts

RULES = load_rules(read_csv(DATASET / "deletion_rules.csv"))
T = datetime(2026, 9, 1, tzinfo=timezone.utc)
AUDIT = T + timedelta(days=10)


def _rec(oid, days, system, resource, fields, topology=None, kind="record", result=None, wrapper=None, source=None):
    t = T + timedelta(days=days)
    return Observation(obs_id=f"{source or oid}#{oid}", source_id=source or oid, source_kind="json", kind=kind,
                       captured_at=t, observed_at=t, system_id=system, resource_id=resource, result=result,
                       container=system, topology=topology, fields=fields, wrapper=wrapper or {}, locator=oid)


def _activity(oid, days, system, resource, etype, result="SUCCESS"):
    t = T + timedelta(days=days)
    return Observation(obs_id=f"{oid}#row", source_id=oid, source_kind="csv", kind="activity", captured_at=t,
                       observed_at=t, system_id=system, resource_id=resource, record_type=etype, result=result,
                       container="system_activity",
                       fields={"source_system": "deletion_worker", "target_system": system, "reported_result": result},
                       locator="row")


def _assess(obs, resource, system):
    store = EvidenceStore(resource_prefixes=[resource.rsplit("_", 1)[0]])
    for o in obs:
        store.add(o)
    return assess(resource, system, CaseView(store, AUDIT), RULES)


def test_every_rule_category_is_reachable_from_the_registry():
    rows = read_csv(DATASET / "deletion_rules.csv")
    assert len(rows) >= 15
    mapped = {c for pair in SYSTEM_CATEGORY.values() for c in pair if c}
    assert {r["data_category"] for r in rows} <= mapped | set(UNMAPPED)
    assert not mapped & set(UNMAPPED)
    # an unmapped category stays unmapped only while no evidence file mentions it
    for cat in UNMAPPED:
        needle = cat.split("_")[0].lower().encode()
        assert not [p for p in (DATASET / "evidence").rglob("*") if p.is_file() and needle in p.read_bytes().lower()]


def test_tombstone_with_only_the_stable_reference_is_compliant():
    a = _assess([_rec("t1", 1, "identity_service", "tombstone_1",
                      {"subject_reference": "user_1", "name": None, "email": None, "phone": None, "email_hash": None})],
                "tombstone_1", "identity_service")
    assert a.verdict == "compliant" and a.ops[2] == "VERIFY_RECORD_REDACTED"


def test_tombstone_still_holding_the_email_hash_is_exposed():
    a = _assess([_rec("t1", 1, "identity_service", "tombstone_1",
                      {"subject_reference": "user_1", "name": None, "email": None, "email_hash": "ab" * 32})],
                "tombstone_1", "identity_service")
    assert a.verdict == "violation" and a.ops[0] == "REPORT_EXPOSED_PII" and a.proof.source_id == "t1"


def test_retained_security_record_is_verified_present():
    a = _assess([_rec("s1", 1, "security_service", "audit_record_1", {"subject_reference": "user_1"})],
                "audit_record_1", "security_service")
    assert a.verdict == "compliant" and a.ops == (None, None, "VERIFY_RECORD_PRESENT")


def test_an_identifier_only_in_the_wrapper_is_not_exposure():
    a = _assess([_rec("a1", 1, "analytics_platform", "analytics_1", {"email": None, "customer_reference": None},
                      wrapper={"lookup_key": "a@x.com", "subject_reference": "user_1",
                               "customer_email": "a@x.com"}), _activity("act1", 0, "analytics_platform", "analytics_1",
                                                                    "ANONYMIZE_RECORD")],
                "analytics_1", "analytics_platform")
    assert a.verdict == "compliant" and a.ops[2] == "VERIFY_RECORD_ANONYMIZED"


def test_a_success_claim_does_not_beat_a_present_record():
    # the claim is *later* than the observation, so only "claims never set state" keeps the record present
    a = _assess([_rec("s1", 2, "search_service", "search_1", {"email": "a@x.com"}),
                 _activity("act1", 4, "search_service", "search_1", "DELETE_RECORD", "SUCCESS")],
                "search_1", "search_service")
    assert a.verdict == "violation" and a.ops[0] == "REPORT_REMAINING_RECORD"


def test_a_newer_clean_primary_does_not_clear_an_older_dirty_replica():
    # A20 safeguard 2, the exact scenario: replica dirty on day 1, primary clean on day 5, no later replica evidence.
    a = _assess([_activity("act1", 0, "analytics_platform", "analytics_1", "ANONYMIZE_RECORD"),
                 _rec("rep", 1, "analytics_platform", "analytics_1", {"email": "a@x.com"}, topology="read_replica"),
                 _rec("pri", 5, "analytics_platform", "analytics_1", {"email": None, "customer_reference": None},
                      topology="primary")], "analytics_1", "analytics_platform")
    assert a.verdict == "violation" and a.proof.source_id == "rep"
    assert {c.copy[1]: c.state for c in a.copies} == {"read_replica": "PRESENT_EXPOSED", "primary": "ANONYMIZED"}


def test_later_evidence_of_the_same_replica_does_clear_it():
    a = _assess([_activity("act1", 0, "analytics_platform", "analytics_1", "ANONYMIZE_RECORD"),
                 _rec("rep1", 1, "analytics_platform", "analytics_1", {"email": "a@x.com"}, topology="read_replica"),
                 _rec("rep2", 6, "analytics_platform", "analytics_1", {"email": None}, topology="read_replica")],
                "analytics_1", "analytics_platform")
    assert a.verdict == "compliant"


def test_scope_absence_never_overrides_a_direct_observation_of_the_same_copy():
    later_scope = Observation(obs_id="bundle#snap0", source_id="bundle", source_kind="json", kind="scope",
                              captured_at=T + timedelta(days=3), observed_at=None, system_id="account_service",
                              resource_id=None, container="customer_profiles", fields={"record_count": 1}, locator="s")
    a = _assess([_rec("p1", 1, "account_service", "account_1", {"email": "a@x.com"}), later_scope],
                "account_1", "account_service")
    assert a.verdict == "violation"


def test_scope_absence_alone_proves_a_deleted_row_but_not_a_missing_retained_one():
    scope = Observation(obs_id="snap#t", source_id="snap", source_kind="sql", kind="scope", captured_at=T,
                        observed_at=None, system_id="account_service", resource_id=None, container="profiles",
                        fields={"row_count": 0}, locator="t")
    assert _assess([scope], "account_1", "account_service").verdict == "compliant"
    sec = Observation(obs_id="snap#s", source_id="snap", source_kind="sql", kind="scope", captured_at=T,
                      observed_at=None, system_id="security_service", resource_id=None, container="audit",
                      fields={"row_count": 0}, locator="s")
    assert _assess([sec], "audit_record_1", "security_service").verdict == "unknown"


def test_unknown_category_signals_never_default_silently():
    # content says attachment, but the workflow treated it as a redaction → unknown, not a guess
    doc = Observation(obs_id="pdf#p1", source_id="pdf", source_kind="pdf", kind="text", captured_at=T,
                      observed_at=None, system_id=None, resource_id=None, container="doc",
                      fields={"text": "Attachment upload history support_1"}, locator="p1")
    a = _assess([doc, _activity("act1", 0, "support_platform", "support_1", "REDACT_RECORD")],
                "support_1", "support_platform")
    assert a.verdict == "unknown" and a.category.name is None


# --- on the real data (evaluation side; full sample denominators) ---

def test_sample_policy_regression_gates(store, sample_gold, sample_requests):
    idx = IdentityIndex(read_csv(DATASET / "user_identities.csv"), read_csv(DATASET / "user_audit_log.csv"))
    tally = defaultdict(int)
    for cid, (status, steps) in sample_gold.items():
        q = sample_requests[cid]
        view = CaseView(store, parse_ts(q["audit_at"]))
        subject = idx.resolve(q["email"], view.audit_at)
        per = defaultdict(dict)
        for s in steps:
            per[(s["system_id"], s["resource_id"])][s["phase"]] = s
        for (system, rid), ph in per.items():
            a = assess(rid, system, view, RULES, subject)
            if "FINDING" in ph:
                ok = (a.verdict == "violation" and a.ops[0] == ph["FINDING"]["operation"]
                      and a.proof.source_id == ph["FINDING"]["evidence_id"])
                tally["finding", ok] += 1
            elif status == "COMPLETE":
                ok = (a.verdict == "compliant" and a.ops[2] == ph["VERIFICATION"]["operation"]
                      and a.proof.source_id == ph["VERIFICATION"]["evidence_id"])
                tally["complete", ok] += 1
    # Measured 2026-10-24: 41/41 findings and 34/34 COMPLETE verifications, verdict + op + citation.
    assert tally["finding", True] == 41 and tally["finding", False] == 0
    assert tally["complete", True] == 34 and tally["complete", False] == 0
