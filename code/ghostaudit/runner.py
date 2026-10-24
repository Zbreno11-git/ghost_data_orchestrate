"""Deterministic engine run: every request of a split → a validated row, a decision trace and a support level.

Writes runs/<run_id>/{output.csv, decisions.jsonl, unresolved.md, summary.json}. Never the root output.csv:
publishing a validated output is a separate, explicit step (S5/S7). Never reads the public sample answers.
"""
from __future__ import annotations

import json
from collections import Counter
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

from .identity import IdentityIndex, Subject
from .ingest.csv_tables import load_tables
from .ingest.manifest import evidence_times
from .ingest.pipeline import ingest_all
from .intent import classify
from .ownership import OwnerIndex, WorkflowAssignment, build_requests, link_case
from .planner import Plan, plan_case
from .policy import assess, load_rules
from .serialize import dumps, write_output_csv
from .temporal import CaseView

FAR_FUTURE = datetime(2100, 1, 1, tzinfo=timezone.utc)
SPLITS = {"targets": "requests", "samples": "sample_requests"}


def run_deterministic(dataset: Path, split: str, out_dir: Path, mode: str = "strict") -> dict:
    dataset = Path(dataset)
    tables = load_tables(dataset)
    store, coverage = ingest_all(dataset, allow_paid=False)
    failed = [c.file_id for c in coverage.files if c.status == "failed"]
    identity = IdentityIndex(tables["identities"], tables["audit"])
    owners = OwnerIndex(identity, FAR_FUTURE)
    everyone = tables.get("requests", []) + tables.get("sample_requests", [])
    reqs, resolved = build_requests(everyone, identity, store, store.resource_re, owners)
    workflow = WorkflowAssignment(store.observations, reqs)   # one-to-one across every request in the dataset
    by_case = {q.case_id: q for q in reqs}
    rules = load_rules(tables["rules"])
    times = evidence_times(dataset)

    plans: list[Plan] = []
    for row in tables[SPLITS[split]]:
        cid = row["case_id"]
        intent = classify(row["request_text"])
        subject = resolved.get(cid)
        audit_at = by_case[cid].audit_at if cid in by_case else None
        own, assessments = None, {}
        if isinstance(subject, Subject):
            view = CaseView(store, audit_at)
            own = link_case(by_case[cid], view, workflow, owners, mode)
            assessments = {r: assess(r, l.system_id, view, rules, subject) for r, l in own.links.items()}
        if audit_at is None:
            from .timeutil import parse_ts
            audit_at = parse_ts(row["audit_at"])
        plan = plan_case(cid, audit_at, intent, subject, own, assessments, times)
        if mode == "strict" and plan.status != "NOT_APPLICABLE" and not plan.steps and isinstance(subject, Subject):
            # Nothing attributable by deduction: fall back to the scored (weak) candidates for this case only,
            # so the row carries the best grounded proposal; it is reported weak/unresolved, never resolved.
            own = link_case(by_case[cid], view, workflow, owners, "scored")
            assessments = {r: assess(r, l.system_id, view, rules, subject) for r, l in own.links.items()}
            plan = plan_case(cid, audit_at, intent, subject, own, assessments, times)
            plan.reasons.insert(0, "strict ownership attributed nothing; scored candidates used")
            if plan.support == "resolved":
                plan.support = "weak"
        plans.append(plan)

    out_dir.mkdir(parents=True, exist_ok=True)
    write_output_csv([(p.case_id, p.status, p.steps) for p in plans], out_dir / "output.csv")
    with open(out_dir / "decisions.jsonl", "w", encoding="utf-8") as fh:
        for p in sorted(plans, key=lambda p: p.case_id):
            fh.write(json.dumps({"case_id": p.case_id, "status": p.status, "support": p.support,
                                 "reasons": p.reasons, "decisions": p.decisions, "steps_json": dumps(p.steps)},
                                ensure_ascii=False, default=str) + "\n")
    summary = {
        "split": split, "ownership": mode, "engine": "deterministic", "rows": len(plans),
        "status": dict(Counter(p.status for p in plans)),
        "support": dict(Counter(p.support for p in plans)),
        "status_by_support": {f"{s}/{st}": n for (s, st), n in sorted(Counter((p.support, p.status) for p in plans).items())},
        "workflow_assignment": dict(Counter(how for _, how, _ in workflow.assigned.values())),
        "workflow_ambiguous_requests": len(workflow.ambiguous),
        "ingest_failed_files": failed,
    }
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=1) + "\n")
    lines = ["# Cases that are not fully resolved", "",
             "A row that validates is not a supported verdict (A20). `weak` rows depend on a workflow-only link or a "
             "low-confidence intent; `unresolved` rows lack an identity, an account, an intent or a state. Each is "
             "investigated by the agent before publication.", "",
             f"{summary['support']}", "", "| case_id | support | status | reasons |", "|---|---|---|---|"]
    for p in sorted(plans, key=lambda p: p.case_id):
        if p.support != "resolved":
            why = "; ".join(p.reasons).replace("|", "\\|")
            lines.append(f"| {p.case_id} | {p.support} | {p.status} | {why} |")
    (out_dir / "unresolved.md").write_text("\n".join(lines) + "\n")
    return summary
