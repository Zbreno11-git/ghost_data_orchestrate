"""C3.3: ownership tiers. Workflow links are candidates (A20): interleaved runs, a repeated person and a tie are
resolved only by deduction, never forced; link strength and supporting obs_ids survive."""
import json
from datetime import datetime, timedelta, timezone

import pytest

from conftest import DATASET, read_csv
from ghostaudit.evidence import Observation
from ghostaudit.identity import IdentityIndex, Subject, email_hash
from ghostaudit.ownership import OwnerIndex, WorkflowAssignment, _Req, build_requests, link_case
from ghostaudit.temporal import CaseView
from ghostaudit.timeutil import parse_ts

T = datetime(2026, 9, 1, 12, 0, tzinfo=timezone.utc)
FAR = datetime(2100, 1, 1, tzinfo=timezone.utc)


def _row(aid, minutes, resource, system="account_service", source="deletion_worker", etype="DELETE_RECORD"):
    t = T + timedelta(minutes=minutes)
    return Observation(obs_id=f"{aid}#row", source_id=aid, source_kind="csv", kind="activity", captured_at=t,
                       observed_at=t, system_id=system, resource_id=resource, record_type=etype, result="SUCCESS",
                       container="system_activity", fields={"source_system": source, "target_system": system},
                       locator="row")


def _req(case, user, start, report, explicit=None):
    s = Subject(user, f"{user}@x.com", "current", ())
    return _Req(case, s, T + timedelta(minutes=start), T + timedelta(minutes=report), FAR, explicit or {})


def test_interleaved_runs_are_assigned_by_deduction_not_proximity():
    # Two concurrent workflows: A's account row comes *after* B's, so "nearest to report" would swap them.
    rows = [_row("a1", 0, "account_B"), _row("a2", 10, "account_A"), _row("a3", 30, "search_A", "search_service")]
    a = _req("case_A", "user_a", -60, 50, explicit={"search_A": ["ev#1"]})
    b = _req("case_B", "user_b", -60, 50, explicit={"account_B": ["ev#2"]})
    wf = WorkflowAssignment(rows, [a, b])
    assert wf.assigned["case_B"][0].resource_id == "account_B" and wf.assigned["case_B"][1] == "explicit_account"
    assert wf.assigned["case_A"][0].resource_id == "account_A"      # the only row left after B's fixed pair
    assert wf.assigned["case_A"][1] in ("only_feasible_row", "corroborated_run", "forced_matching")


def test_a_repeated_person_does_not_inherit_the_earlier_requests_account():
    rows = [_row("old", 0, "account_old"), _row("new", 60 * 24 * 90, "account_new")]
    first = _req("case_first", "user_7", -60, 30, explicit={"account_old": ["ev#old"]})
    second = _req("case_second", "user_7", 60 * 24 * 90 - 60, 60 * 24 * 90 + 30, explicit={"account_old": ["ev#old"]})
    wf = WorkflowAssignment(rows, [first, second])
    assert wf.assigned["case_first"][0].resource_id == "account_old"
    assert wf.assigned["case_second"][0].resource_id == "account_new"
    owners = OwnerIndex(IdentityIndex([], []), FAR)
    from ghostaudit.evidence import EvidenceStore
    own = link_case(second, CaseView(EvidenceStore(), FAR), wf, owners)
    assert own.account.resource_id == "account_new" and "account_old" not in own.links
    assert "case_first" in own.excluded["account_old"]


@pytest.mark.parametrize("mode", ["strict", "scored"])
def test_a_tie_stays_ambiguous_and_is_never_forced(mode):
    rows = [_row("r1", 0, "account_1"), _row("r2", 20, "account_2")]
    a, b = _req("case_A", "user_a", -60, 10), _req("case_B", "user_b", -60, 10)   # same window, same report
    wf = WorkflowAssignment(rows, [a, b])
    assert wf.assigned == {} and set(wf.ambiguous) == {"case_A", "case_B"}
    from ghostaudit.evidence import EvidenceStore
    owners = OwnerIndex(IdentityIndex([], []), FAR)
    for q in (a, b):
        own = link_case(q, CaseView(EvidenceStore(), FAR), wf, owners, mode)
        if mode == "strict":
            assert own.account is None and own.ambiguities
        else:   # scored may rank a weak candidate, but it is never explicit and the case is weak
            assert own.account is None or (own.account.tier == "workflow" and own.weak)


def test_workflow_links_keep_their_tier_and_supporting_rows():
    rows = [_row("r1", 0, "account_9"), _row("r2", 15, "analytics_9", "analytics_platform")]
    q = _req("case_A", "user_a", -60, 30)
    wf = WorkflowAssignment(rows, [q])
    from ghostaudit.evidence import EvidenceStore
    own = link_case(q, CaseView(EvidenceStore(), FAR), wf, OwnerIndex(IdentityIndex([], []), FAR), "scored")
    assert own.account.tier == "workflow" and own.account.reasons == ("r1#row",)
    assert own.links["analytics_9"].tier == "workflow" and own.links["analytics_9"].reasons == ("r1#row", "r2#row")
    assert own.weak


# --- on the real data (evaluation side: compares with sample_output.csv, full 111 denominator) ---

@pytest.fixture(scope="module")
def linked(store):
    ids, audit = read_csv(DATASET / "user_identities.csv"), read_csv(DATASET / "user_audit_log.csv")
    idx = IdentityIndex(ids, audit)
    owners = OwnerIndex(idx, FAR)
    rows = read_csv(DATASET / "sample_deletion_requests.csv") + read_csv(DATASET / "deletion_requests.csv")
    reqs, _ = build_requests(rows, idx, store, store.resource_re, owners)
    wf = WorkflowAssignment(store.observations, reqs)
    byq = {q.case_id: q for q in reqs}
    samples = [r["case_id"] for r in read_csv(DATASET / "sample_deletion_requests.csv")]
    return {m: {c: link_case(byq[c], CaseView(store, byq[c].audit_at), wf, owners, m) for c in samples}
            for m in ("strict", "scored")}


def test_the_look_alike_record_is_never_the_subjects(linked, sample_requests):
    for mode in ("strict", "scored"):
        assert "search_8168" not in linked[mode]["case_28"].links   # holds smartinez6461.jr@gmail.com


def test_sample_ownership_regression_gates(linked, sample_gold):
    # Measured 2026-10-24 (strict): 78/111 gold resources linked, 2 extras (object_19, tombstone_17: the
    # subject's own, not listed in the answers). A drop or a new extra must be explained, not absorbed.
    gold = {c: {s["resource_id"] for s in steps} for c, (_, steps) in sample_gold.items()}
    assert sum(map(len, gold.values())) == 111
    strict = linked["strict"]
    found = sum(len(gold[c] & set(strict[c].links)) for c in gold)
    extra = sorted((c, r) for c in gold for r in set(strict[c].links) - gold[c])
    assert found >= 78, found
    assert extra == [("case_07", "object_19"), ("case_17", "tombstone_17")], extra
    assert all(l.reasons for own in strict.values() for l in own.links.values())
