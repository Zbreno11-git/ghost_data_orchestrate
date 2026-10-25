"""Explain one case from its decision trace (S6 C6.2/C6.5). No model call, no key, no network.

Everything printed comes from the run's `decisions.jsonl`. The dataset is re-ingested offline
(`allow_paid=False`) only to print each cited observation's provenance: source, kind, locator, both clocks
and the time basis. A fact the trace does not hold is printed as "not recorded in the trace" and is never
re-derived or inferred. An obs_id the current ingest does not know is flagged, because the run and the
current code or dataset disagree.
"""
from __future__ import annotations

import json
from pathlib import Path

MISSING = "not recorded in the trace"


def load_decision(run: Path, case_id: str) -> dict:
    with open(run / "decisions.jsonl", encoding="utf-8") as fh:
        for line in fh:
            d = json.loads(line)
            if d["case_id"] == case_id:
                return d
    raise SystemExit(f"{case_id} is not in {run / 'decisions.jsonl'}")


def provenance_index(dataset: Path) -> dict:
    from .ingest.pipeline import ingest_all
    store, _ = ingest_all(dataset, allow_paid=False)
    return {o.obs_id: o for o in store.observations}


def _prov(oid: str | None, index: dict) -> str:
    if not oid:
        return MISSING
    o = index.get(oid)
    if o is None:
        return f"`{oid}` (⚠ not in the current ingest: run and code/dataset disagree)"
    from .temporal import time_basis
    obs = o.observed_at.isoformat() if o.observed_at else "none stated"
    return (f"`{oid}` — {o.source_kind} {o.kind}, system {o.system_id or '?'}, captured {o.captured_at.isoformat()}, "
            f"observed {obs}, basis {time_basis(o)}")


def explain(run: Path, case_id: str, dataset: Path, index: dict | None = None) -> str:
    d = load_decision(run, case_id)
    t = d.get("trace") or {}
    index = index if index is not None else provenance_index(dataset)
    g = lambda m, k: (m or {}).get(k, MISSING) if isinstance(m, dict) else MISSING  # noqa: E731
    L = [f"# {case_id}: {d['status']}", ""]
    L += ["## Verdict and certainty (kept apart)", "",
          f"- Best-effort status: **{d['status']}**",
          f"- Evidential support: **{d.get('support', MISSING)}**"
          + ("" if d.get("support") != "resolved" else " (no workflow-only link, ambiguity or unknown state)")]
    if t.get("heuristic"):
        L.append("- **HEURISTIC PREDICTION (A29)**: this row is not a reconstructed state; see the limits below")
    elif not t:
        L.append(f"- Heuristic flag: {MISSING}")
    L += ["", "## Request", "",
          f"- Requested {g(t, 'requested_at')}; the workflow claimed **{g(t, 'reported_status')}** at {g(t, 'reported_at')} (a claim, never proof)",
          f"- Cutoff (audit_at): {g(t, 'audit_at')}; request email: `{g(t, 'request_email')}`"]
    it = t.get("intent")
    L.append(f"- Intent: authorizes deletion = {g(it, 'authorizes_deletion')}, confidence {g(it, 'confidence')}, "
             f"source {g(it, 'source')}; reason: {g(it, 'reason')}")
    s = t.get("subject")
    L += ["", "## Person", ""]
    if not s:
        L.append(f"- {MISSING}")
    elif "unresolved" in s:
        L.append(f"- Not identified: {s['unresolved']}")
    else:
        L.append(f"- `{s['user_id']}`; the request email is a **{s.get('request_email_role', MISSING)}** identifier")
        L += ["", "| type | value | role at the cutoff | source |", "|---|---|---|---|"]
        L += [f"| {i['type']} | `{i['value']}` | {i['role']} | {i['source']} |" for i in s.get("identifiers", [])]
    L += ["", "## Ownership: the chain from the person to each resource", ""]
    acc = t.get("account", MISSING) if t else MISSING
    if acc == MISSING:
        L.append(f"- Account deduction: {MISSING}")
    elif acc is None:
        L.append(f"- Account: **none attributed**; candidates left by the deduction: {t.get('account_candidates') or 'none'}")
    else:
        L.append(f"- Account `{acc['resource_id']}`: tier **{acc['tier']}**, deduced by {acc.get('how') or MISSING}; "
                 f"evidence {', '.join(f'`{r}`' for r in acc.get('reasons', [])) or MISSING}")
    for dec in d.get("decisions", []):
        L.append(f"- `{dec['resource_id']}` ({dec.get('system_id')}): tier **{dec.get('tier')}**")
        for oid in dec.get("link_reasons") or []:
            L.append(f"  - linked by {_prov(oid, index)}")
        if not dec.get("link_reasons"):
            L.append(f"  - linked by: {MISSING}")
    L += ["", "### Rejected links and open questions", ""]
    if not t:
        L.append(f"- {MISSING}")
    else:
        L += [f"- excluded `{r}`: {why}" for r, why in sorted((t.get("excluded") or {}).items())] or ["- no exclusions recorded"]
        L += [f"- ambiguity: {a}" for a in t.get("ambiguities") or []] or ["- no ownership ambiguity recorded"]
    L += ["", "## Each copy and its state at the cutoff", ""]
    for dec in d.get("decisions", []):
        L.append(f"- `{dec['resource_id']}`: verdict **{dec.get('verdict')}** ({dec.get('reason')}); proof {_prov(dec.get('proof'), index)}")
        for copy, state, oid, basis in dec.get("copies") or []:
            L.append(f"  - {'/'.join(copy)}: **{state}** from {basis}; {_prov(oid, index)}")
    if not d.get("decisions"):
        L.append("- no resource decisions (nothing linked, or no deletion authorized)")
    L += ["", "## Policy behind each action", ""]
    for dec in d.get("decisions", []):
        L.append(f"- `{dec['resource_id']}`: category {dec.get('category')} ({dec.get('category_reason')}) → "
                 f"rule {dec.get('rule_id') or dec.get('rule_note') or MISSING} → treatment **{dec.get('treatment')}**")
    if not d.get("decisions"):
        L.append("- none")
    L += ["", "## Limits and reasons recorded by the run", ""]
    L += [f"- {r}" for r in d.get("reasons") or []] or ["- none recorded"]
    steps = json.loads(d.get("steps_json") or "[]")
    L += ["", "## Final status and ordered steps", "", f"**{d['status']}**, {len(steps)} steps", ""]
    if steps:
        L += ["| # | phase | system | resource | operation | state | evidence |", "|---|---|---|---|---|---|---|"]
        L += [f"| {x['step_no']} | {x['phase']} | {x['system_id']} | {x['resource_id']} | {x['operation']} | "
              f"{x['state']} | {x['evidence_id'] or '—'} |" for x in steps]
    L += ["", f"_Generated by `main.py explain` from `{run.name}/decisions.jsonl`; provenance from an offline "
          "re-ingest. No model was called._"]
    return "\n".join(L) + "\n"
