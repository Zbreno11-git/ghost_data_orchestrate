"""C3.5: planner step-set rules and support levels, then the deterministic run end to end (A20: a valid row is
not a supported verdict, so support is asserted separately from validity)."""
import csv
import json
from datetime import datetime, timezone
from pathlib import Path

import pytest

from conftest import CODE, DATASET, read_csv
from ghostaudit.identity import Subject
from ghostaudit.intent import Intent
from ghostaudit.ownership import Link, Ownership
from ghostaudit.planner import plan_case
from ghostaudit.policy import Assessment, Category, CopyState
from ghostaudit.runner import run_deterministic
from evaluation.metrics import evaluate, load_output

AUDIT = datetime(2026, 9, 15, tzinfo=timezone.utc)
TIMES = {"ev_1": datetime(2026, 9, 1, tzinfo=timezone.utc)}
YES = Intent(True, "high", "test")
SUBJECT = Subject("user_1", "a@x.com", "current", ())


def _a(rid, system, verdict, treat, ops, cite="ev_1"):
    proof = CopyState((system, "primary"), "X", f"{cite}#1", cite, TIMES["ev_1"]) if verdict != "unknown" else None
    return Assessment(rid, system, Category("C", "test"), treat, verdict, (), proof, ops)


def _own(*links, account="account_1"):
    o = Ownership("case_t")
    for rid, tier in links:
        o.links[rid] = Link(rid, None, tier, ("ev_1#1",))
    o.account = o.links.get(account)
    return o


DEL = ("REPORT_REMAINING_RECORD", "DELETE_RECORD", "VERIFY_RECORD_ABSENT")
RET = (None, None, "VERIFY_RECORD_PRESENT")
ANON = ("REPORT_EXPOSED_PII", "ANONYMIZE_RECORD", "VERIFY_RECORD_ANONYMIZED")


def test_incomplete_lists_violations_account_and_retained_records_only():
    own = _own(("account_1", "explicit"), ("search_1", "explicit"), ("audit_record_1", "explicit"),
               ("analytics_1", "explicit"))
    p = plan_case("case_t", AUDIT, YES, SUBJECT, own, {
        "account_1": _a("account_1", "account_service", "compliant", "DELETE", DEL),
        "search_1": _a("search_1", "search_service", "violation", "DELETE", DEL),
        "audit_record_1": _a("audit_record_1", "security_service", "compliant", "RETAIN", RET),
        "analytics_1": _a("analytics_1", "analytics_platform", "compliant", "ANONYMIZE", ANON)}, TIMES)
    ops = [(s["operation"], s["resource_id"], s["evidence_id"]) for s in p.steps]
    assert p.status == "INCOMPLETE" and p.support == "resolved"
    assert ops == [("REPORT_REMAINING_RECORD", "search_1", "ev_1"), ("DELETE_RECORD", "search_1", ""),
                   ("VERIFY_RECORD_ABSENT", "account_1", ""), ("VERIFY_RECORD_ABSENT", "search_1", ""),
                   ("VERIFY_RECORD_PRESENT", "audit_record_1", "")]   # the compliant analytics record is not listed


def test_complete_cites_every_relevant_resource():
    own = _own(("account_1", "explicit"), ("analytics_1", "explicit"))
    p = plan_case("case_t", AUDIT, YES, SUBJECT, own, {
        "account_1": _a("account_1", "account_service", "compliant", "DELETE", DEL),
        "analytics_1": _a("analytics_1", "analytics_platform", "compliant", "ANONYMIZE", ANON)}, TIMES)
    assert p.status == "COMPLETE" and {s["evidence_id"] for s in p.steps} == {"ev_1"} and len(p.steps) == 2


def test_a_workflow_only_link_makes_the_case_weak_not_resolved():
    own = _own(("account_1", "workflow"))
    p = plan_case("case_t", AUDIT, YES, SUBJECT, own,
                  {"account_1": _a("account_1", "account_service", "compliant", "DELETE", DEL)}, TIMES)
    assert p.status == "COMPLETE" and p.support == "weak"


def test_unknown_state_or_missing_account_is_unresolved_even_when_the_row_validates():
    own = _own(("search_1", "explicit"), ("analytics_1", "explicit"), account=None)
    p = plan_case("case_t", AUDIT, YES, SUBJECT, own, {
        "search_1": _a("search_1", "search_service", "violation", "DELETE", DEL),
        "analytics_1": _a("analytics_1", "analytics_platform", "unknown", "ANONYMIZE", ANON)}, TIMES)
    assert p.status == "INCOMPLETE" and p.support == "unresolved"
    assert any("no account" in r for r in p.reasons) and any("analytics_1" in r for r in p.reasons)


def test_not_applicable_has_no_steps_and_unknown_intent_is_unresolved():
    na = plan_case("case_t", AUDIT, Intent(False, "high", "export only"), SUBJECT, None, {}, TIMES)
    assert (na.status, na.steps, na.support) == ("NOT_APPLICABLE", [], "resolved")
    own = _own(("account_1", "explicit"))
    unk = plan_case("case_t", AUDIT, Intent(None, "low", "?"), SUBJECT, own,
                    {"account_1": _a("account_1", "account_service", "compliant", "DELETE", DEL)}, TIMES)
    assert unk.support == "unresolved"


def test_a_row_that_fails_validation_is_unresolved():
    own = _own(("account_1", "explicit"))
    p = plan_case("case_t", AUDIT, YES, SUBJECT, own,
                  {"account_1": _a("account_1", "account_service", "compliant", "DELETE", DEL, cite="ev_404")}, TIMES)
    assert p.support == "unresolved" and any("UNKNOWN_EVIDENCE" in r for r in p.reasons)


# --- end to end (evaluation side: compares with sample_output.csv on the full official denominators) ---

@pytest.fixture(scope="module")
def sample_run(tmp_path_factory):
    out = tmp_path_factory.mktemp("run")
    summary = run_deterministic(DATASET, "samples", out, "strict")
    return out, summary


def test_deterministic_sample_run_validates_and_reports_support(sample_run):
    from ghostaudit.ingest.manifest import evidence_times
    from ghostaudit.validate import validate_file
    out, summary = sample_run
    requests = {r["case_id"]: r for r in read_csv(DATASET / "sample_deletion_requests.csv")}
    assert validate_file(out / "output.csv", requests, evidence_times(DATASET)) == []
    assert summary["rows"] == 32 and sum(summary["support"].values()) == 32
    assert (out / "unresolved.md").exists() and len(read_csv(out / "output.csv")) == 32


def test_deterministic_sample_baseline_regression_gate(sample_run):
    # Measured 2026-10-24 20:52 UTC (strict): status 32/32, step precision 161/162, recall 161/193, evidence on
    # matched 161/161. Denominators are the official ones (A20: the D10/D12/D13 gaps are not subtracted).
    out, _ = sample_run
    m = evaluate(load_output(out / "output.csv"), load_output(DATASET / "sample_output.csv"))
    assert m["step_recall"]["den"] == 193 and m["status_accuracy"]["den"] == 32
    assert m["status_accuracy"]["num"] == 32
    assert m["step_recall"]["num"] >= 161
    assert m["step_precision"]["den"] - m["step_precision"]["num"] <= 1
    assert m["evidence_accuracy_on_matched"]["value"] == 1.0


@pytest.mark.parametrize("case", sorted(p for p in (CODE / "evaluation" / "custom_cases").iterdir()
                                        if (p / "expected_output.csv").exists()), ids=lambda p: p.name)
def test_custom_cases_are_reproduced_exactly(case, tmp_path):
    run_deterministic(case / "dataset", "targets", tmp_path, "strict")
    m = evaluate(load_output(tmp_path / "output.csv"), load_output(case / "expected_output.csv"))
    assert m["whole_case_exact"]["value"] == 1.0


def test_agent_resume_never_reinvestigates_a_checkpointed_case(tmp_path):
    # C4.5 offline: a case with a checkpoint is loaded, not re-run; replay mode guarantees no provider is reachable.
    from ghostaudit.planner import Plan
    from ghostaudit.runner import _save_case, run
    plan = Plan("case_01", "COMPLETE", [{"step_no": 1, "phase": "VERIFICATION", "system_id": "account_service",
                                         "resource_id": "account_001", "operation": "VERIFY_RECORD_ABSENT",
                                         "state": "ABSENT", "evidence_id": "evidence_54"}], "weak", ["checkpointed"])
    from ghostaudit.config import load_config
    from ghostaudit.runner import case_fingerprint, run_fingerprint
    cfg = load_config()
    row = [r for r in read_csv(DATASET / "sample_deletion_requests.csv") if r["case_id"] == "case_01"][0]
    fp = case_fingerprint(run_fingerprint(DATASET, cfg, cfg["agent"]["model"]), row)
    _save_case(tmp_path, plan, {"agent": {"status": "submitted"}}, fp)
    summary = run(DATASET, "samples", tmp_path, engine="agent", gateway_mode="replay", cases={"case_01"},
                  run_id="resume-test")
    assert summary["agent"]["resumed"] == 1 and summary["agent"].get("model_calls", 0) == 0
    assert read_csv(tmp_path / "output.csv")[0]["steps_json"].count("account_001") == 1


def test_a_checkpoint_from_other_inputs_is_recomputed_not_reused(tmp_path):
    # S5 C5.5 (amendment 2): a pre-fix checkpoint must never survive a targeted rerun.
    from ghostaudit.planner import Plan
    from ghostaudit.runner import _save_case, run
    stale = Plan("case_01", "COMPLETE", [{"step_no": 1, "phase": "VERIFICATION", "system_id": "account_service",
                                          "resource_id": "account_stale", "operation": "VERIFY_RECORD_ABSENT",
                                          "state": "ABSENT", "evidence_id": "evidence_54"}], "resolved", ["old"])
    _save_case(tmp_path, stale, {"agent": {"status": "submitted"}}, "fingerprint-of-older-code")
    summary = run(DATASET, "samples", tmp_path, engine="agent", gateway_mode="replay", cases={"case_01"},
                  run_id="stale-test")
    assert summary["agent"].get("resumed", 0) == 0 and summary["agent"]["stale_checkpoints"] == 1
    assert "account_stale" not in (tmp_path / "output.csv").read_text()


def test_the_fingerprint_moves_with_every_input_and_only_with_them(tmp_path):
    import shutil
    from ghostaudit.config import load_config
    from ghostaudit.runner import case_fingerprint, run_fingerprint
    code = tmp_path / "code"
    for sub in ("ghostaudit", "prompts", "config"):
        shutil.copytree(CODE / sub, code / sub, ignore=shutil.ignore_patterns("__pycache__"))
    data = tmp_path / "dataset"
    data.mkdir()
    (data / "deletion_requests.csv").write_text("case_id,email\ncase_a,a@x.com\n")
    cfg = load_config()
    base = run_fingerprint(data, cfg, "m1", code)
    assert run_fingerprint(data, cfg, "m1", code) == base                       # stable
    for name in ("sample_" + "output.csv", "notes.txt"):                        # not read by predictions: ignored
        (data / name).write_text("anything")
    assert run_fingerprint(data, cfg, "m1", code) == base
    assert run_fingerprint(data, cfg, "m2", code) != base                       # model
    assert run_fingerprint(data, {**cfg, "agent": {**cfg["agent"], "max_tool_rounds": 9}}, "m1", code) != base
    (code / "prompts" / "investigator.md").write_text("changed")                 # prompt
    after_prompt = run_fingerprint(data, cfg, "m1", code)
    assert after_prompt != base
    (code / "ghostaudit" / "policy.py").write_text("# changed")                  # code
    after_code = run_fingerprint(data, cfg, "m1", code)
    assert after_code != after_prompt
    (data / "user_identities.csv").write_text("user_id\n")                     # dataset table
    fp = run_fingerprint(data, cfg, "m1", code)
    assert fp != after_code
    (data / "evidence").mkdir()
    (data / "evidence" / "x.log").write_text("line")                            # evidence file
    assert run_fingerprint(data, cfg, "m1", code) != fp
    a, b = {"case_id": "case_a", "x": "1"}, {"case_id": "case_b", "x": "1"}
    assert case_fingerprint(fp, a) == case_fingerprint(fp, dict(a))              # an unchanged case is reusable
    assert case_fingerprint(fp, {**a, "x": "2"}) != case_fingerprint(fp, a)      # only the edited row moves
    assert case_fingerprint(fp, b) == case_fingerprint(fp, dict(b))


# --- support caps (S5 C5.2): an ambiguity or an unknown never leaves a case resolved ---

def test_any_ownership_ambiguity_caps_support_at_weak():
    own = _own(("account_1", "explicit"), ("search_1", "explicit"))
    own.ambiguities.append("search_1: supporting record also carries identifiers of ['user_9']")
    p = plan_case("case_t", AUDIT, YES, SUBJECT, own, {
        "account_1": _a("account_1", "account_service", "compliant", "DELETE", DEL),
        "search_1": _a("search_1", "search_service", "violation", "DELETE", DEL)}, TIMES)
    assert p.status == "INCOMPLETE" and p.support == "weak"


def test_an_unknown_retained_record_in_an_incomplete_case_is_unresolved():
    own = _own(("account_1", "explicit"), ("search_1", "explicit"), ("audit_record_1", "explicit"))
    p = plan_case("case_t", AUDIT, YES, SUBJECT, own, {
        "account_1": _a("account_1", "account_service", "compliant", "DELETE", DEL),
        "search_1": _a("search_1", "search_service", "violation", "DELETE", DEL),
        "audit_record_1": _a("audit_record_1", "security_service", "unknown", "RETAIN", RET)}, TIMES)
    assert p.status == "INCOMPLETE" and p.support == "unresolved"
    assert any("audit_record_1" in r and "unknown" in r for r in p.reasons)


def test_every_ambiguity_producer_in_ownership_reaches_the_cap():
    # Derived: every `ambiguities.append` in ownership.py feeds Ownership.ambiguities, which the planner caps
    # without reading its text; the count pins the producers so a new one is noticed.
    src = (CODE / "ghostaudit" / "ownership.py").read_text()
    assert src.count("ambiguities.append(") >= 5
    for text in ("anything at all", ""):
        own = _own(("account_1", "explicit"))
        own.ambiguities.append(text or "x")
        p = plan_case("case_t", AUDIT, YES, SUBJECT, own,
                      {"account_1": _a("account_1", "account_service", "compliant", "DELETE", DEL)}, TIMES)
        assert p.support != "resolved"


def test_agent_scope_non_resolved_never_sends_a_resolved_case_to_the_model(tmp_path, monkeypatch):
    # S5 C5.7: with scope non_resolved a resolved proposal is published as is; replay guarantees no provider.
    # The intent batch is replaced by the deterministic rule so only the scope gate is under test (a replayed
    # batch for a different subset of cases misses the cache and would lower intent confidence).
    import ghostaudit.intent as intent_mod
    from ghostaudit.config import load_config
    from ghostaudit.runner import run
    monkeypatch.setattr(intent_mod, "classify_all",
                        lambda rows, gw, cfg: {r["case_id"]: intent_mod.classify(r["request_text"]) for r in rows})
    det = run(DATASET, "samples", tmp_path / "det", engine="deterministic")
    resolved = sorted(json.loads(l)["case_id"] for l in open(tmp_path / "det" / "decisions.jsonl")
                      if json.loads(l)["support"] == "resolved")
    assert det["support"]["resolved"] == len(resolved) >= 1
    cfg = load_config()
    cfg["agent"] = {**cfg["agent"], "scope": "non_resolved"}
    s = run(DATASET, "samples", tmp_path / "agent", engine="agent", gateway_mode="replay", cases=set(resolved),
            run_id="scope-test", config=cfg)
    assert s["agent"]["skipped_resolved"] == len(resolved) and s["agent"].get("model_calls", 0) == 0
    det_rows = {r["case_id"]: r for r in read_csv(tmp_path / "det" / "output.csv")}
    assert all(det_rows[r["case_id"]] == r for r in read_csv(tmp_path / "agent" / "output.csv"))


def test_a_nearest_anchor_account_keeps_its_heuristic_label_after_the_plan_is_rebuilt():
    """S7 C7.4 defect: the agent's recompiled plan dropped the A34 label while the row still asserted the pick."""
    from ghostaudit.ownership import Link, Ownership
    from ghostaudit.planner import Plan
    from ghostaudit.runner import label_nearest_anchor
    step = {"step_no": 1, "phase": "VERIFICATION", "system_id": "account_service", "resource_id": "account_7",
            "operation": "VERIFY_RECORD_ABSENT", "state": "ABSENT", "evidence_id": "ev_1"}
    own = Ownership("c", account=Link("account_7", "account_service", "workflow", ("r#1",),
                                       note="nearest anchor to reported_at (12 min); weak"))
    rebuilt = Plan("c", "COMPLETE", [step], "weak", ["agent: left the account as it was"])
    assert label_nearest_anchor(rebuilt, own) and rebuilt.support == "unresolved"
    assert rebuilt.reasons[0].startswith("HEURISTIC PREDICTION (A34)")
    assert label_nearest_anchor(rebuilt, own) and sum(r.startswith("HEURISTIC") for r in rebuilt.reasons) == 1
    # close negatives: an agent-attributed account, or a plan that no longer uses the pick
    agent = Ownership("c", account=Link("account_7", "account_service", "explicit", ("ev#1",), note="agent"))
    other = Plan("c", "COMPLETE", [step], "resolved", [])
    assert not label_nearest_anchor(other, agent) and other.support == "resolved"
    unused = Plan("c", "COMPLETE", [{**step, "resource_id": "search_1"}], "weak", [])
    assert not label_nearest_anchor(unused, own) and unused.support == "weak"
