"""C4.3 (offline): the agent loop through the real gateway with a scripted provider — tool call → submit, repair of
an invalid citation, fallback on provider error or exhausted repairs. Live behaviour is checked by C4.3's live run."""
import json
from datetime import datetime, timedelta, timezone

import pytest
from google.genai import errors, types

from conftest import DATASET, read_csv
from ghostaudit.agent import apply_submission, investigate, validate_submission
from ghostaudit.config import load_config
from ghostaudit.evidence import EvidenceStore, Observation
from ghostaudit.identity import IdentityIndex, email_hash
from ghostaudit.intent import Intent
from ghostaudit.llm.gateway import Gateway
from ghostaudit.llm.ledger import Ledger
from ghostaudit.ownership import Link, Ownership, WorkflowAssignment, _Req
from ghostaudit.planner import plan_case
from ghostaudit.policy import assess, load_rules
from ghostaudit.temporal import CaseView
from ghostaudit.tools import CaseTools

AUDIT = datetime(2026, 9, 15, tzinfo=timezone.utc)
CFG = load_config()
RULES = load_rules(read_csv(DATASET / "deletion_rules.csv"))
YES = Intent(True, "high", "test")
ROW = {"case_id": "case_t", "email": "a@x.com", "requested_at": "2026-09-10T00:00:00Z", "reported_status": "COMPLETE",
       "reported_at": "2026-09-12T00:00:00Z", "audit_at": "2026-09-15T00:00:00Z", "request_text": "Delete my account."}


def _obs(oid, resource, system, fields, kind="record", days=-2):
    t = AUDIT + timedelta(days=days)
    return Observation(obs_id=f"{oid}#1", source_id=oid, source_kind="json", kind=kind, captured_at=t, observed_at=t,
                       system_id=system, resource_id=resource, container=system, fields=fields, locator="1")


def _call(name, args):
    return types.Part(function_call=types.FunctionCall(name=name, args=args))


def _resp(*parts):
    return types.GenerateContentResponse(
        candidates=[types.Candidate(content=types.Content(role="model", parts=list(parts)), finish_reason="STOP")],
        usage_metadata=types.GenerateContentResponseUsageMetadata(prompt_token_count=1000, candidates_token_count=50))


class Script:
    def __init__(self, outs):
        self.outs, self.sent = list(outs), 0

    def send(self, *, model, contents, config):
        self.sent += 1
        o = self.outs.pop(0)
        if isinstance(o, Exception):
            raise o
        return o


@pytest.fixture
def case(tmp_path):
    store = EvidenceStore(resource_prefixes=["search", "account"])
    store.add(_obs("ev_search", "search_1", "search_service", {"email": "a@x.com"}))
    store.add(_obs("ev_acct", "account_1", "account_service", {"rows": "0"}, kind="lookup"))
    store.add(_obs("ev_other", "search_2", "search_service", {"email": "a@x.com", "index": "v3"}))
    ids = [{"user_id": "user_1", "name": "Ana", "email": "a@x.com", "phone": "+1 555 0100",
            "email_hash": email_hash("a@x.com"), "updated_at": ""}]
    subject = IdentityIndex(ids, []).resolve("a@x.com", AUDIT)
    own = Ownership("case_t", links={"search_1": Link("search_1", "search_service", "explicit", ("ev_search#1",))})
    q = _Req("case_t", subject, AUDIT - timedelta(days=5), AUDIT - timedelta(days=3), AUDIT, {})
    tools = CaseTools("case_t", CaseView(store, AUDIT), subject, own, WorkflowAssignment(store.observations, [q]),
                      RULES, store.resource_re)
    assessments = {r: assess(r, l.system_id, tools.view, RULES, subject) for r, l in own.links.items()}
    det = plan_case("case_t", AUDIT, YES, subject, own, assessments, {"ev_search": AUDIT - timedelta(days=2),
                                                                        "ev_other": AUDIT - timedelta(days=2)})
    times = {"ev_search": AUDIT - timedelta(days=2), "ev_other": AUDIT - timedelta(days=2),
             "ev_acct": AUDIT - timedelta(days=2)}
    return tools, det, times, tmp_path


def _run(case, script):
    tools, det, times, tmp = case
    gw = Gateway("t", CFG, Ledger(tmp / "l.jsonl", 4.5), cache_dir=tmp / "c", provider=Script(script),
                 sleep=lambda s: None)
    return investigate(ROW, tools, det, gw, "gemini-3.1-flash-lite", CFG, times, YES, AUDIT), gw


def test_tool_call_then_valid_submission_recompiles_the_plan(case):
    out, gw = _run(case, [
        _resp(_call("search_evidence", {"query": "a@x.com"})),
        _resp(_call("submit_audit", {"account": {"resource_id": None}, "notes": "found a second index entry",
                                     "add": [{"resource_id": "search_2", "evidence": ["ev_other#1"], "reason": "r"}]}))])
    assert out.status == "submitted" and out.model_calls == 2 and out.tool_calls == ["search_evidence"]
    assert {s["resource_id"] for s in out.plan.steps} == {"search_1", "search_2"}
    added = [d for d in out.plan.decisions if d["resource_id"] == "search_2"][0]
    assert added["tier"] == "explicit"            # its cited evidence carries the subject's email


def test_a_citation_no_tool_returned_is_rejected_and_repaired(case):
    out, _ = _run(case, [
        _resp(_call("submit_audit", {"account": {"resource_id": None}, "notes": "x",
                                     "add": [{"resource_id": "search_2", "evidence": ["ev_other#1"]}]})),
        _resp(_call("search_evidence", {"query": "search_2"})),
        _resp(_call("submit_audit", {"account": {"resource_id": None}, "notes": "x",
                                     "add": [{"resource_id": "search_2", "evidence": ["ev_other#1"]}]}))])
    assert out.status == "submitted" and "never returned by a tool" in out.errors[0]


def test_exhausted_repairs_fall_back_to_the_deterministic_plan_flagged(case):
    bad = _resp(_call("submit_audit", {"account": {"resource_id": "account_999"}, "notes": "x"}))
    tools, det, _, _ = case
    out, _ = _run(case, [bad, bad, bad])
    assert out.status == "fallback" and out.plan.support == "unresolved"
    assert out.plan.steps == det.steps


def test_a_provider_error_is_never_a_status(case):
    tools, det, _, _ = case
    out, _ = _run(case, [errors.ClientError(400, {"error": {"code": 400, "message": "bad", "status": "INVALID"}})])
    assert out.status == "fallback" and out.plan.status == det.status and out.plan.support == "unresolved"
    assert "ClientError" in out.errors[0]


# --- S5 C5.4: what the cited evidence establishes, not only that it was seen ---

def _world(extra_obs, audit_rows=(), worker_rows=()):
    """Tools over a small world: subject Ana (a@x.com, formerly ana.old@x.com), a known other user Bob."""
    store = EvidenceStore(resource_prefixes=["search", "account", "analytics"])
    for o in [_obs("ev_search", "search_1", "search_service", {"email": "a@x.com"})] + list(extra_obs) + list(worker_rows):
        store.add(o)
    ids = [{"user_id": "user_1", "name": "Ana", "email": "a@x.com", "phone": "", "email_hash": "", "updated_at": ""},
           {"user_id": "user_2", "name": "Bob", "email": "bob@x.com", "phone": "", "email_hash": "", "updated_at": ""}]
    idx = IdentityIndex(ids, list(audit_rows))
    from ghostaudit.ownership import OwnerIndex
    subject = idx.resolve("a@x.com", AUDIT)
    own = Ownership("case_t", links={"search_1": Link("search_1", "search_service", "explicit", ("ev_search#1",))})
    q = _Req("case_t", subject, AUDIT - timedelta(days=5), AUDIT - timedelta(days=3), AUDIT, {})
    tools = CaseTools("case_t", CaseView(store, AUDIT), subject, own, WorkflowAssignment(store.observations, [q]),
                      RULES, store.resource_re, owners=OwnerIndex(idx))
    tools.seen.update(o.obs_id for o in store.observations)      # as if every one was returned by a tool
    return tools


def _sub(**kw):
    return {"account": {"resource_id": None}, "notes": "n", **kw}


def test_an_exclusion_without_evidence_is_rejected():
    tools = _world([])
    errs = validate_submission(_sub(exclude=[{"resource_id": "search_1", "reason": "looks unrelated"}]), tools)
    assert any("exclude" in e and "evidence" in e for e in errs)


def test_an_exclusion_of_an_explicit_violation_needs_evidence_of_another_owner():
    tools = _world([])
    errs = validate_submission(_sub(exclude=[{"resource_id": "search_1", "reason": "x", "evidence": ["ev_search#1"]}]),
                               tools)
    assert any("another" in e for e in errs)            # the cited record is the subject's own


def test_another_persons_resource_cannot_be_added():
    tools = _world([_obs("ev_bob", "search_3", "search_service", {"email": "bob@x.com"})])
    errs = validate_submission(_sub(add=[{"resource_id": "search_3", "evidence": ["ev_bob#1"]}]), tools)
    assert errs


def test_a_genuine_but_irrelevant_citation_does_not_ground_an_addition():
    # The observation exists, was returned by a tool and names the resource, but ties it to nobody.
    tools = _world([_obs("ev_orphan", "search_4", "search_service", {"index": "v1"})])
    errs = validate_submission(_sub(add=[{"resource_id": "search_4", "evidence": ["ev_orphan#1"]}]), tools)
    assert any("subject" in e for e in errs)


def test_an_account_chosen_by_timing_alone_is_rejected():
    from ghostaudit.evidence import Observation as O
    t = AUDIT - timedelta(days=3, minutes=30)
    row = O(obs_id="act_9#row", source_id="act_9", source_kind="csv", kind="activity", captured_at=t, observed_at=t,
            system_id="account_service", resource_id="account_9", record_type="DELETE_RECORD", result="SUCCESS",
            container="system_activity", fields={"source_system": "deletion_worker",
                                                 "target_system": "account_service"}, locator="row")
    tools = _world([], worker_rows=[row])
    assert "account_9" in {c["account"] for c in tools.workflow_candidates()["candidates"]}
    errs = validate_submission(_sub(account={"resource_id": "account_9", "evidence": ["act_9#row"]}), tools)
    assert any("account" in e and "subject" in e for e in errs)


def test_a_historical_email_link_is_explicit():
    audit = [{"audit_id": "au1", "user_id": "user_1", "field_name": "email", "old_value": "ana.old@x.com",
              "new_value": "a@x.com", "event_time": (AUDIT - timedelta(days=30)).isoformat()}]
    tools = _world([_obs("ev_old", "search_6", "search_service", {"email": "ana.old@x.com"})], audit_rows=audit)
    sub = _sub(add=[{"resource_id": "search_6", "evidence": ["ev_old#1"]}])
    assert validate_submission(sub, tools) == []
    assert apply_submission(sub, tools).links["search_6"].tier == "explicit"


def test_multi_observation_lineage_reaches_an_anonymized_record():
    # analytics_7 is anonymized (no PII); it names account_1, whose lookup was keyed by the subject's email.
    a = _obs("ev_an", "analytics_7", "analytics_platform", {"segment": "anonymized", "account_ref": "account_1"})
    b = _obs("ev_acct", "account_1", "account_service", {"rows": "0"}, kind="lookup")
    b = b.__class__(**{**b.__dict__, "wrapper": {"lookup_key": "a@x.com"}})
    tools = _world([a, b])
    sub = _sub(add=[{"resource_id": "analytics_7", "evidence": ["ev_an#1", "ev_acct#1"]}])
    assert validate_submission(sub, tools) == []
    assert apply_submission(sub, tools).links["analytics_7"].tier == "explicit"
    only_a = _sub(add=[{"resource_id": "analytics_7", "evidence": ["ev_an#1"]}])
    assert validate_submission(only_a, tools)                   # half the chain is not a link


def test_a_wrapper_only_identifier_supports_discovery():
    o = _obs("ev_w", "search_5", "search_service", {"index": "v2"})
    o = o.__class__(**{**o.__dict__, "wrapper": {"lookup_key": "a@x.com"}})
    tools = _world([o])
    sub = _sub(add=[{"resource_id": "search_5", "evidence": ["ev_w#1"]}])
    assert validate_submission(sub, tools) == []


def test_an_exclusion_backed_by_another_owner_is_accepted_and_applied():
    o = _obs("ev_dual", "search_1", "search_service", {"email": "a@x.com", "owner_email": "bob@x.com"})
    tools = _world([o])
    sub = _sub(exclude=[{"resource_id": "search_1", "reason": "Bob's", "evidence": ["ev_dual#1"]}])
    assert validate_submission(sub, tools) == []
    assert "search_1" not in apply_submission(sub, tools).links


def test_a_unit_naming_the_subject_and_another_person_links_nothing():
    tools = _world([_obs("ev_mix", "search_8", "search_service", {"email": "a@x.com", "cc": "bob@x.com"})])
    errs = validate_submission(_sub(add=[{"resource_id": "search_8", "evidence": ["ev_mix#1"]}]), tools)
    assert any("does not tie it" in e for e in errs)


def test_the_brief_never_shows_the_case_id(case):
    from ghostaudit.agent import brief
    tools, det, _, _ = case
    assert ROW["case_id"] not in json.dumps(brief(ROW, tools, det), default=str)
