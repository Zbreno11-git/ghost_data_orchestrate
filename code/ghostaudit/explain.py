"""Explain one case from its decision trace (S6 C6.2/C6.5, S7 C7.2). No model call, no key, no network.

`case_view()` is the one representation shared by `main.py explain` (Markdown) and the evidence viewer (HTML), so
the two cannot disagree. Everything in it comes from the run's files:
- `decisions.jsonl` for the verdict, the trace and the steps;
- `provenance.jsonl` for each cited observation's source, locator, both clocks and an excerpt, **only** when
  `provenance.verify_run` confirms its sha256 and its run fingerprint. A legacy run, or one whose provenance fails
  the check, is shown with a warning and no provenance. Today's dataset is never re-ingested to describe an older
  run (an unchanged obs_id does not prove unchanged content).

A fact the trace does not hold is printed as "not recorded in the trace" and is never re-derived or inferred.
Each step carries its basis (direct observation, inference, heuristic, proposed remediation, check to run), kept
apart from the case's status and its support level.
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


def load_provenance(run: Path) -> tuple[str, dict, str]:
    from .provenance import verify_run
    status, index, msg = verify_run(run)
    return status, index or {}, msg


def _heuristic_resources(d: dict) -> set[str]:
    t = d.get("trace") or {}
    if not t.get("heuristic"):
        return set()
    out = {x["resource_id"] for x in d.get("decisions") or [] if str(x.get("reason", "")).startswith("heuristic:")}
    if any(r.startswith("HEURISTIC PREDICTION (A34)") for r in d.get("reasons") or []):
        out |= {x["resource_id"] for x in d.get("decisions") or [] if x.get("tier") == "workflow"}
    return out


def step_basis(step: dict, dec: dict | None, heuristic: set[str]) -> str:
    if step["phase"] == "REMEDIATION":
        return "proposed remediation (not executed)"
    if step["phase"] == "VERIFICATION" and not step["evidence_id"]:
        return "check to run after remediation"
    if step["resource_id"] in heuristic:
        return "heuristic prediction"
    if dec is None:
        return MISSING
    if dec.get("tier") == "workflow":
        return "inference: workflow deduction (timing / one-to-one)"
    proof = next((c for c in dec.get("copies") or [] if c[2] == dec.get("proof")), None)
    if proof is not None and proof[3] == "scope":
        return "inference: a capture covering the system lacks the record"
    return "direct observation"


def case_view(run: Path, case_id: str, prov: tuple[str, dict, str] | None = None, decision: dict | None = None) -> dict:
    d = decision if decision is not None else load_decision(run, case_id)
    status, index, msg = prov if prov is not None else load_provenance(run)
    t = d.get("trace") or {}
    heur = _heuristic_resources(d)
    decs = {x["resource_id"]: x for x in d.get("decisions") or []}

    def p(oid):
        if not oid:
            return None
        if status != "verified":
            return {"obs_id": oid, "unavailable": msg}
        return index.get(oid) or {"obs_id": oid, "unavailable": "not in the run's saved provenance"}

    steps = json.loads(d.get("steps_json") or "[]")
    return {
        "case_id": case_id, "status": d["status"], "support": d.get("support"), "heuristic": bool(t.get("heuristic")),
        "has_trace": bool(t), "provenance": {"status": status, "message": msg},
        "request": {k: t.get(k) for k in ("requested_at", "reported_status", "reported_at", "audit_at", "request_email")}
        if t else None,
        "intent": t.get("intent"), "person": t.get("subject"),
        "account": t.get("account", MISSING) if t else MISSING, "account_source": t.get("account_source"),
        "account_candidates": t.get("account_candidates") or [], "uncertain": t.get("uncertain_candidates") or {},
        "excluded": t.get("excluded") or {}, "ambiguities": t.get("ambiguities") or [],
        "resources": [{
            "resource_id": x["resource_id"], "system_id": x.get("system_id"), "tier": x.get("tier"),
            "links": [p(o) for o in x.get("link_reasons") or []], "verdict": x.get("verdict"), "reason": x.get("reason"),
            "category": x.get("category"), "category_reason": x.get("category_reason"),
            "rule": x.get("rule_id") or x.get("rule_note"), "treatment": x.get("treatment"),
            "heuristic": x["resource_id"] in heur, "proof": p(x.get("proof")),
            "copies": [{"copy": "/".join(str(c0) for c0 in c[0]), "state": c[1], "basis": c[3], "obs": p(c[2])}
                       for c in x.get("copies") or []]} for x in d.get("decisions") or []],
        "reasons": d.get("reasons") or [],
        "steps": [{**s, "basis": step_basis(s, decs.get(s["resource_id"]), heur)} for s in steps],
    }


def _prov(o: dict | None) -> str:
    if not o:
        return MISSING
    if "unavailable" in o:
        return f"`{o['obs_id']}` (⚠ provenance not attached: {o['unavailable']})"
    return (f"`{o['obs_id']}` — {o['source_kind']} {o['kind']} in `{o.get('file') or o['source_id']}`, system "
            f"{o.get('system_id') or '?'}, captured {o['captured_at']}, observed {o.get('observed_at') or 'none stated'}, "
            f"basis {o['time_basis']}" + (" (snapshot envelope: observed = its own capture time)"
                                          if o.get("snapshot_dated") else ""))


def explain(run: Path, case_id: str, dataset: Path | None = None, index: dict | None = None) -> str:
    """`dataset` is accepted for CLI compatibility and never read (provenance comes from the run)."""
    prov = ("verified", index, "supplied by the caller") if index is not None else None
    v = case_view(run, case_id, prov)
    g = lambda m, k: (m or {}).get(k, MISSING) if isinstance(m, dict) else MISSING  # noqa: E731
    L = [f"# {case_id}: {v['status']}", ""]
    L += ["## Verdict and certainty (kept apart)", "",
          f"- Best-effort status: **{v['status']}**",
          f"- Evidential support: **{v.get('support') or MISSING}**"
          + ("" if v.get("support") != "resolved" else " (no workflow-only link, ambiguity or unknown state)")]
    if v["heuristic"]:
        L.append("- **HEURISTIC PREDICTION**: part of this row is not a reconstructed state; see the limits below")
    elif not v["has_trace"]:
        L.append(f"- Heuristic flag: {MISSING}")
    L.append(f"- Provenance: {v['provenance']['status']} ({v['provenance']['message']})")
    r = v["request"]
    L += ["", "## Request", "",
          f"- Requested {g(r, 'requested_at')}; the workflow claimed **{g(r, 'reported_status')}** at {g(r, 'reported_at')} (a claim, never proof)",
          f"- Cutoff (audit_at): {g(r, 'audit_at')}; request email: `{g(r, 'request_email')}`"]
    it = v["intent"]
    L.append(f"- Intent: authorizes deletion = {g(it, 'authorizes_deletion')}, confidence {g(it, 'confidence')}, "
             f"source {g(it, 'source')}; reason: {g(it, 'reason')}")
    s = v["person"]
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
    acc = v["account"]
    if acc == MISSING:
        L.append(f"- Account deduction: {MISSING}")
    elif acc is None:
        L.append(f"- Account: **none attributed**; candidates left by the deduction: {v['account_candidates'] or 'none'}")
    else:
        L.append(f"- Account `{acc['resource_id']}`: tier **{acc['tier']}**, deduced by {acc.get('how') or MISSING}"
                 f"{' (' + v['account_source'] + ')' if v['account_source'] else ''}; "
                 f"evidence {', '.join(f'`{x}`' for x in acc.get('reasons', [])) or MISSING}")
    for x in v["resources"]:
        L.append(f"- `{x['resource_id']}` ({x['system_id']}): tier **{x['tier']}**")
        L += [f"  - linked by {_prov(o)}" for o in x["links"]] or [f"  - linked by: {MISSING}"]
    L += ["", "### Rejected links and open questions", ""]
    if not v["has_trace"]:
        L.append(f"- {MISSING}")
    else:
        L += [f"- excluded `{k}`: {why}" for k, why in sorted(v["excluded"].items())] or ["- no exclusions recorded"]
        L += [f"- ambiguity: {a}" for a in v["ambiguities"]] or ["- no ownership ambiguity recorded"]
        L += [f"- uncertain investigation candidate `{k}`: {why} (no step generated)"
              for k, why in sorted(v["uncertain"].items())]
    L += ["", "## Each copy and its state at the cutoff", ""]
    for x in v["resources"]:
        L.append(f"- `{x['resource_id']}`: verdict **{x['verdict']}** ({x['reason']}); proof {_prov(x['proof'])}")
        L += [f"  - {c['copy']}: **{c['state']}** from {c['basis']}; {_prov(c['obs'])}" for c in x["copies"]]
    if not v["resources"]:
        L.append("- no resource decisions (nothing linked, or no deletion authorized)")
    L += ["", "## Policy behind each action", ""]
    L += [f"- `{x['resource_id']}`: category {x['category']} ({x['category_reason']}) → rule {x['rule'] or MISSING} → "
          f"treatment **{x['treatment']}**" for x in v["resources"]] or ["- none"]
    L += ["", "## Limits and reasons recorded by the run", ""]
    L += [f"- {x}" for x in v["reasons"]] or ["- none recorded"]
    L += ["", "## Final status and ordered steps", "", f"**{v['status']}**, {len(v['steps'])} steps", ""]
    if v["steps"]:
        L += ["| # | phase | system | resource | operation | state | evidence | basis |", "|---|---|---|---|---|---|---|---|"]
        L += [f"| {x['step_no']} | {x['phase']} | {x['system_id']} | {x['resource_id']} | {x['operation']} | "
              f"{x['state']} | {x['evidence_id'] or '—'} | {x['basis']} |" for x in v["steps"]]
    L += ["", f"_Generated by `main.py explain` from `{run.name}/decisions.jsonl` and its saved provenance. "
          "No model was called._"]
    return "\n".join(L) + "\n"
