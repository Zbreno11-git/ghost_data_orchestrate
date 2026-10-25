"""Deterministic engine run: every request of a split → a validated row, a decision trace and a support level.

Writes runs/<run_id>/{output.csv, decisions.jsonl, unresolved.md, summary.json}. Never the root output.csv:
publishing a validated output is a separate, explicit step (S5/S7). Never reads the public sample answers.
"""
from __future__ import annotations

import hashlib
import json
from collections import Counter
from dataclasses import asdict
from pathlib import Path

from .identity import IdentityIndex, Subject
from .ingest.csv_tables import TABLES, load_tables
from .ingest.manifest import evidence_times
from .ingest.pipeline import ingest_all
from .intent import classify
from .ownership import AssignmentsAsOf, OwnerIndex, build_requests, link_case, request_at
from .planner import Plan, plan_case
from .policy import assess, heuristic_assess, load_rules
from .serialize import dumps, write_output_csv
from .temporal import CaseView

SPLITS = {"targets": "requests", "samples": "sample_requests"}


def _heuristic(cid, audit_at, intent, subject, own, assessments, view, rules, times, plan: Plan) -> Plan:
    """A29 (owner decision): a row with no grounded proposal gets flagged heuristic predictions for its unknown
    resources, and stays unresolved; if no rule applies, the empty row stays as it is (and fails validation)."""
    guessed = {r: heuristic_assess(r, own.links[r].system_id, view, rules, subject) if a.verdict == "unknown" else a
               for r, a in assessments.items()}
    used = [a for r, a in guessed.items() if a.reason.startswith("heuristic:") and a is not assessments[r]]
    if not used:
        return plan
    out = plan_case(cid, audit_at, intent, subject, own, guessed, times)
    out.support = "unresolved"
    out.reasons.insert(0, "HEURISTIC PREDICTION (A29), not a reconstructed state: " + "; ".join(
        f"{a.resource_id}: {a.reason[len('heuristic: '):]}" for a in used) + " | " + " | ".join(plan.reasons[:3]))
    return out


def _trace(row: dict, intent, llm_used: bool, subject, own, workflow, mode: str, rules: dict, plan: Plan,
           audit_at) -> dict:
    """The facts behind a row, as the run decided them (S6 C6.2), so an explanation never has to re-derive or
    guess them: request, intent and its source, the identified person with every identifier used (role and
    source), the account deduction, exclusions and ambiguities, the heuristic flag, the rule per decision."""
    t = {"audit_at": audit_at.isoformat() if audit_at else None, "requested_at": row.get("requested_at"),
         "reported_status": row.get("reported_status"), "reported_at": row.get("reported_at"),
         "request_email": row.get("email"), "ownership_mode": mode,
         "intent": {"authorizes_deletion": intent.authorizes_deletion, "confidence": intent.confidence,
                    "reason": intent.reason, "source": "llm batch cross-checked with the rule" if llm_used else "rule"},
         "heuristic": any(r.startswith("HEURISTIC PREDICTION") for r in plan.reasons)}
    if isinstance(subject, Subject):
        t["subject"] = {"user_id": subject.user_id, "request_email_role": subject.request_email_role,
                        "identifiers": [{"type": i.type, "value": i.raw, "role": i.role, "source": i.source}
                                        for i in subject.identifiers]}
    else:
        t["subject"] = {"unresolved": repr(subject)}
    if own is not None:
        a = own.account
        t["account"] = ({"resource_id": a.resource_id, "tier": a.tier, "how": a.note, "reasons": list(a.reasons)}
                        if a else None)
        t["account_candidates"] = list(workflow.ambiguous.get(plan.case_id, [])) if workflow is not None else []
        t["excluded"] = dict(own.excluded)
        t["ambiguities"] = list(own.ambiguities)
    for d in plan.decisions:
        rule = rules.get(d.get("category"))
        d.setdefault("rule_id", rule["rule_id"] if rule else None)
        if not rule:
            d.setdefault("rule_note", "no deletion_rules row for this category; the engine's built-in treatment")
    return t


def run_deterministic(dataset: Path, split: str, out_dir: Path, mode: str = "strict") -> dict:
    return run(dataset, split, out_dir, mode)


def run_fingerprint(dataset: Path, cfg: dict, model: str | None, code_dir: Path | None = None) -> str:
    """What a checkpointed answer depends on besides its own request row (S5 C5.5): the engine code, prompts and
    config files, the effective config and model, and every dataset file the prediction path reads (the tables
    `load_tables` loads, the evidence manifest and the evidence tree; an allowlist, so evaluator files never
    enter it)."""
    from .config import CODE_DIR
    code_dir = code_dir or CODE_DIR
    h = hashlib.sha256()
    files = sorted(p for sub in ("ghostaudit", "prompts", "config") for p in (code_dir / sub).rglob("*")
                   if p.is_file() and p.suffix in (".py", ".md", ".toml", ".json") and "__pycache__" not in p.parts)
    dataset = Path(dataset)
    files += sorted(p for p in [dataset / n for n in (*TABLES.values(), "evidence_files.csv")] if p.is_file())
    files += sorted(p for p in (dataset / "evidence").rglob("*") if p.is_file())
    for p in files:
        h.update(str(p.relative_to(code_dir if p.is_relative_to(code_dir) else dataset)).encode() + b"\0")
        h.update(hashlib.sha256(p.read_bytes()).digest())
    h.update(json.dumps({"cfg": cfg, "model": model}, sort_keys=True, default=str).encode())
    return h.hexdigest()


def case_fingerprint(run_fp: str, row: dict) -> str:
    return hashlib.sha256((run_fp + json.dumps(row, sort_keys=True)).encode()).hexdigest()


def _save_case(out_dir: Path, plan: Plan, extra: dict, fingerprint: str = "") -> None:
    d = out_dir / "cases"
    d.mkdir(parents=True, exist_ok=True)
    tmp = d / f".{plan.case_id}.tmp"
    tmp.write_text(json.dumps({"plan": asdict(plan), "fingerprint": fingerprint, **extra}, ensure_ascii=False,
                              default=str))
    tmp.replace(d / f"{plan.case_id}.json")


def _load_case(out_dir: Path, case_id: str, fingerprint: str) -> tuple[Plan, dict] | None:
    """A checkpoint is reused only if it was computed from the same inputs; otherwise the case is recomputed
    (a targeted rerun after a fix must never silently keep a pre-fix answer)."""
    f = out_dir / "cases" / f"{case_id}.json"
    if not f.exists():
        return None
    d = json.loads(f.read_text())
    if d.pop("fingerprint", None) != fingerprint:
        return None
    return Plan(**d.pop("plan")), d


def run(dataset: Path, split: str, out_dir: Path, mode: str = "strict", engine: str = "deterministic",
        gateway_mode: str = "live", model: str | None = None, cases: set[str] | None = None,
        run_id: str = "run", config: dict | None = None) -> dict:
    from .config import load_config
    cfg = config or load_config()
    dataset = Path(dataset)
    tables = load_tables(dataset)
    store, coverage = ingest_all(dataset, allow_paid=False)
    failed = [c.file_id for c in coverage.files if c.status == "failed"]
    identity = IdentityIndex(tables["identities"], tables["audit"])
    owners = OwnerIndex(identity)                               # queried as of each case's audit_at
    everyone = tables.get("requests", []) + tables.get("sample_requests", [])
    reqs, resolved = build_requests(everyone, identity, store, store.resource_re, owners)
    by_row = {r["case_id"]: r for r in everyone}
    # One-to-one across every request in the dataset, solved per case from what existed at its audit_at (C5.2).
    workflows = AssignmentsAsOf(store.observations, reqs, lambda q, at: request_at(
        by_row[q.case_id], at, identity, store, store.resource_re, owners)[0])
    by_case = {q.case_id: q for q in reqs}
    rules = load_rules(tables["rules"])
    times = evidence_times(dataset)

    gateway = None
    if engine == "agent":
        from .llm.gateway import Gateway
        gateway = Gateway(run_id, cfg, mode=gateway_mode)
        model = model or cfg["agent"]["model"]
    agent_stats = Counter()
    tool_use = Counter()

    llm_intents = {}
    if engine == "agent":
        from .intent import classify_all
        selected = [r for r in tables[SPLITS[split]] if not cases or r["case_id"] in cases]
        llm_intents = classify_all(selected, gateway, cfg)

    run_fp = run_fingerprint(dataset, cfg, model)
    plans: list[Plan] = []
    how: dict[str, str] = {}                    # case → how its as-of assignment was decided
    for row in tables[SPLITS[split]]:
        cid = row["case_id"]
        if cases and cid not in cases:
            continue
        fp = case_fingerprint(run_fp, row)
        if engine == "agent" and (saved := _load_case(out_dir, cid, fp)):
            plans.append(saved[0])                  # resume: a finished case with equal inputs is not re-run
            agent_stats["resumed"] += 1
            continue
        if engine == "agent" and (out_dir / "cases" / f"{cid}.json").exists():
            agent_stats["stale_checkpoints"] += 1   # recomputed below, then overwritten
        intent = llm_intents.get(cid) or classify(row["request_text"])
        subject = resolved.get(cid)
        audit_at = by_case[cid].audit_at if cid in by_case else None
        own, assessments, workflow = None, {}, None
        if isinstance(subject, Subject):
            view = CaseView(store, audit_at)
            workflow = workflows.for_case(cid)
            how[cid] = workflow.assigned[cid][1] if cid in workflow.assigned else "ambiguous"
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
        if engine == "agent":
            extra = {"agent": None}
            in_scope = cfg["agent"].get("scope", "all") == "all" or plan.support != "resolved"
            if not in_scope:
                agent_stats["skipped_resolved"] += 1
            if in_scope and intent.authorizes_deletion is not False and isinstance(subject, Subject):
                from .agent import investigate
                from .tools import CaseTools
                tools = CaseTools(cid, view, subject, own, workflow, rules, store.resource_re, owners=owners)
                outcome = investigate(row, tools, plan, gateway, model, cfg, times, intent, audit_at)
                plan = outcome.plan
                agent_stats[outcome.status] += 1
                agent_stats["model_calls"] += outcome.model_calls
                agent_stats["cache_hits"] += outcome.cache_hits
                agent_stats["cost_usd_x1e6"] += round(outcome.cost_usd * 1e6)
                tool_use.update(outcome.tool_calls)
                extra["agent"] = {"status": outcome.status, "model": model, "model_calls": outcome.model_calls,
                                  "cost_usd": outcome.cost_usd, "tool_calls": outcome.tool_calls,
                                  "errors": outcome.errors, "submission": outcome.submission}
        if isinstance(subject, Subject) and own is not None and not plan.steps and plan.status != "NOT_APPLICABLE":
            plan = _heuristic(cid, audit_at, intent, subject, own, assessments, view, rules, times, plan)
        plan.trace = _trace(row, intent, cid in llm_intents, subject, own, workflow, mode, rules, plan, audit_at)
        if engine == "agent":
            _save_case(out_dir, plan, extra, fp)
        plans.append(plan)

    out_dir.mkdir(parents=True, exist_ok=True)
    write_output_csv([(p.case_id, p.status, p.steps) for p in plans], out_dir / "output.csv")
    with open(out_dir / "decisions.jsonl", "w", encoding="utf-8") as fh:
        for p in sorted(plans, key=lambda p: p.case_id):
            fh.write(json.dumps({"case_id": p.case_id, "status": p.status, "support": p.support,
                                 "reasons": p.reasons, "decisions": p.decisions, "steps_json": dumps(p.steps),
                                 "trace": p.trace},
                                ensure_ascii=False, default=str) + "\n")
    summary = {
        "split": split, "ownership": mode, "engine": engine, "model": model, "gateway_mode": gateway_mode,
        "agent_scope": cfg["agent"].get("scope", "all"),
        "rows": len(plans), "agent": dict(agent_stats), "tool_use": dict(tool_use),
        "status": dict(Counter(p.status for p in plans)),
        "support": dict(Counter(p.support for p in plans)),
        "status_by_support": {f"{s}/{st}": n for (s, st), n in sorted(Counter((p.support, p.status) for p in plans).items())},
        "workflow_assignment": dict(Counter(v for v in how.values() if v != "ambiguous")),
        "workflow_ambiguous_requests": sum(v == "ambiguous" for v in how.values()),
        "ingest_failed_files": failed,
    }
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=1) + "\n")
    if gateway is not None:     # the responses behind this output, live or cached: usage report and package
        with open(out_dir / "llm_keys.jsonl", "w", encoding="utf-8") as fh:
            for u in gateway.used:
                fh.write(json.dumps(u, sort_keys=True) + "\n")
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
