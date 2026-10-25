"""Bounded investigator: the model reviews the deterministic proposal with read-only tools, then submits decisions
that the engine validates and recompiles. The model never writes steps, states or operations (A4).

Loop: at most `max_tool_rounds` rounds of tool calls, then `submit_audit` is forced; an invalid submission gets at
most `max_repairs` corrections. Any failure (budget, provider error, replay miss, no valid submission) returns the
deterministic plan, flagged unresolved: an API error is never a status (A10).
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

from google.genai import types

from .config import CODE_DIR
from .identity import Subject
from .ownership import ACCOUNT_SYSTEM, ROW_KEY, Link, Ownership, canonical_system
from .planner import Plan, plan_case
from .policy import assess
from .tools import CaseTools, declarations

PROMPT = (CODE_DIR / "prompts" / "investigator.md").read_text()

SUBMIT = {
    "name": "submit_audit",
    "description": "Submit your decisions for this case (exactly once). The engine validates and recompiles them.",
    "parameters_json_schema": {
        "type": "object",
        "properties": {
            "account": {"type": "object", "properties": {
                "resource_id": {"type": ["string", "null"]},
                "evidence": {"type": "array", "items": {"type": "string"}}}},
            "exclude": {"type": "array", "items": {"type": "object", "properties": {
                "resource_id": {"type": "string"}, "reason": {"type": "string"},
                "evidence": {"type": "array", "items": {"type": "string"}}}, "required": ["resource_id", "reason"]}},
            "add": {"type": "array", "items": {"type": "object", "properties": {
                "resource_id": {"type": "string"}, "reason": {"type": "string"},
                "evidence": {"type": "array", "items": {"type": "string"}}},
                "required": ["resource_id", "evidence"]}},
            "notes": {"type": "string"},
        },
        "required": ["account", "notes"],
    },
}


@dataclass
class AgentOutcome:
    plan: Plan
    status: str                         # submitted | fallback
    tool_calls: list = field(default_factory=list)
    model_calls: int = 0
    cost_usd: float = 0.0
    cache_hits: int = 0
    errors: list = field(default_factory=list)
    submission: dict | None = None
    ownership: Ownership | None = None      # what the published plan was built from (the trace records it, S6)


def brief(row: dict, tools: CaseTools, det: Plan) -> dict:
    """The case as the model sees it: request, subject, proposal with obs_ids, and the open questions."""
    proposal = []
    for d in det.decisions:
        proposal.append({k: d[k] for k in ("resource_id", "system_id", "tier", "link_reasons", "category",
                                            "treatment", "verdict", "reason", "proof")})
        tools.seen.update(d["link_reasons"])
        if d["proof"]:
            tools.seen.add(d["proof"])
    # No case_id: identifiers that mirror it (case_07 → account_007 on the samples) invite a shortcut the evidence
    # does not support (S5 C5.4: the S4 bench agent picked exactly that account citing a page that never names it).
    return {"request_email": row["email"], "requested_at": row["requested_at"],
            "reported_status_claim": row["reported_status"], "reported_at": row["reported_at"],
            "audit_at": row["audit_at"], "request_text": row["request_text"],
            "subject": tools.resolve_identity(), "proposal": proposal,
            "proposed_status": det.status, "support": det.support, "open_questions": det.reasons}


def _units(o, tools: CaseTools) -> list[tuple[set, set]]:
    """(identifier keys, resource ids) named together by one unit of a cited observation: a structured record
    as a whole (wrapper keys included, as discovery), one row of a table screen, a single-subject page. A unit
    that names another subject at the cutoff links nothing; a scope snapshot (many rows) never links."""
    from .evidence import identifiers_in
    from .ownership import OwnerIndex, text_units, _whole_text
    if o.kind == "scope":
        return []
    at, uid = tools.view.audit_at, tools.subject.user_id
    if o.kind == "text":
        whole = _whole_text(o)
        texts = text_units(o) if any(ROW_KEY.match(k) for k in o.fields) or (
            tools.owners and tools.owners.others_in_text(whole, uid, at)) else [whole]
        out = []
        for t in texts:
            if tools.owners and tools.owners.others_in_text(t, uid, at):
                continue
            out.append((OwnerIndex.keys_in_text(t), set(tools.resource_re.findall(t))))
        return out
    if tools.owners and tools.owners.others(o, uid, at):
        return []
    keys = {k for d in (o.fields, o.wrapper) for kk, v in d.items() for k in identifiers_in(kk.rsplit(".", 1)[-1], v)}
    res = {o.resource_id} if o.resource_id else set()
    res |= {r for v in o.fields.values() if isinstance(v, str) for r in tools.resource_re.findall(v)}
    return [(keys, res)]


def lineage(resource_id: str, evidence: list[str], tools: CaseTools) -> list[str] | None:
    """The cited obs_ids that chain `resource_id` to the subject, or None. Each cited admissible unit links the
    resources and identifiers it names; the chain must reach a strong identifier of the subject (current or
    historical as of audit_at) or a resource already explicitly linked. Several observations may form one chain
    (an anonymized record → the account it names → the lookup keyed by the subject's email)."""
    mine = set(tools.subject.keys(strong_only=True))
    anchors = {r for r, l in tools.ownership.links.items() if l.tier == "explicit"}
    edges = []
    for e in evidence:
        o = tools.view.get(e)
        if o is not None and e in tools.seen:
            edges += [(e, keys, res) for keys, res in _units(o, tools)]
    reached, used, frontier = {("res", resource_id)}, [], True
    while frontier:
        frontier = False
        for e, keys, res in edges:
            nodes = {("key", k) for k in keys} | {("res", r) for r in res}
            if nodes & reached and not nodes <= reached:
                reached |= nodes
                used.append(e)
                frontier = True
            if any(n[0] == "key" and n[1] in mine for n in reached) or any(
                    n[0] == "res" and n[1] in anchors and n[1] != resource_id for n in reached):
                return sorted(set(used + [e for e, _, res in edges if resource_id in res][:1]))
    return None


def _named(resource_id: str, evidence: list[str], tools: CaseTools) -> list:
    return [o for e in evidence if (o := tools.view.get(e)) is not None
            and (o.resource_id == resource_id or resource_id in json.dumps(o.fields, default=str))]


def validate_submission(sub: dict, tools: CaseTools) -> list[str]:
    """What the cited evidence establishes (S5 C5.4), not only that it was seen: an account or an addition needs
    a lineage to the subject; an exclusion needs evidence, and removing an explicit link needs evidence that the
    resource is another subject's. Timing and candidacy are never a link (A20)."""
    errs = []
    cited = [e for part in ([sub.get("account") or {}] + list(sub.get("exclude") or []) + list(sub.get("add") or []))
             for e in (part.get("evidence") or [])]
    unknown = sorted({e for e in cited if e not in tools.seen})
    if unknown:
        errs.append(f"these obs_ids were never returned by a tool: {unknown[:5]}")
    acc = (sub.get("account") or {}).get("resource_id")
    current = tools.ownership.account.resource_id if tools.ownership.account else None
    if acc and acc != current:
        cands = {c["account"] for c in tools.workflow_candidates()["candidates"]}
        home = canonical_system(acc, tools.view.by_resource(acc))
        if acc not in cands and acc not in tools.ownership.links:
            errs.append(f"account {acc} is neither a workflow candidate nor a linked resource")
        elif home != ACCOUNT_SYSTEM:
            # S6: a linked record of another system (a tombstone, a ticket) is never the account; forcing it into
            # account_service would re-categorize it and could delete what policy keeps. Checked after the
            # candidacy rule, whose wording earlier repairs were cached under.
            errs.append(f"{acc} is not an account: its records belong to {home}; keep it as a linked resource")
        elif lineage(acc, list((sub.get("account") or {}).get("evidence") or []), tools) is None:
            errs.append(f"account {acc}: no cited evidence links it to the subject; timing or candidacy is not a "
                        "link, so submit account null when nothing does")
    for x in sub.get("exclude") or []:
        r, ev = x.get("resource_id"), list(x.get("evidence") or [])
        link = tools.ownership.links.get(r)
        if link is None:
            errs.append(f"cannot exclude {r}: not in the proposal")
        elif not ev:
            errs.append(f"exclude {r}: cite the evidence that shows why it is not the subject's")
        elif not _named(r, ev, tools):
            errs.append(f"exclude {r}: none of the cited evidence names it")
        elif link.tier == "explicit" and not any(
                tools.owners and tools.owners.others(o, tools.subject.user_id, tools.view.audit_at)
                for o in _named(r, ev, tools)):
            errs.append(f"exclude {r}: it is explicitly linked to the subject; only evidence naming it with another "
                        "subject's identifier can remove it")
    for x in sub.get("add") or []:
        r = x.get("resource_id", "")
        if not tools.resource_re.fullmatch(r or ""):
            errs.append(f"{r!r} is not a resource id")
            continue
        ev = list(x.get("evidence") or [])
        if not _named(r, ev, tools):
            errs.append(f"none of the evidence cited for {r} mentions it")
        elif lineage(r, ev, tools) is None:
            errs.append(f"{r}: the cited evidence does not tie it to the subject (no identifier of theirs, or it "
                        "names another person)")
    return errs


def apply_submission(sub: dict, tools: CaseTools) -> Ownership:
    own = Ownership(tools.case_id, links=dict(tools.ownership.links), account=tools.ownership.account,
                    excluded=dict(tools.ownership.excluded), ambiguities=list(tools.ownership.ambiguities))

    def link_for(r: str, evidence: list[str]) -> tuple[str, tuple]:
        chain = lineage(r, evidence, tools)
        return ("explicit", tuple(chain)) if chain else ("workflow", tuple(evidence))

    for x in sub.get("exclude") or []:
        own.links.pop(x["resource_id"], None)
        own.excluded[x["resource_id"]] = f"agent: {x.get('reason', '')} ({', '.join(x.get('evidence') or [])})"
        if own.account and own.account.resource_id == x["resource_id"]:
            own.account = None
    for x in sub.get("add") or []:
        r = x["resource_id"]
        tier, reasons = link_for(r, list(x["evidence"]))
        own.links[r] = Link(r, canonical_system(r, tools.view.by_resource(r)), tier, reasons, note="agent")
    acc = (sub.get("account") or {}).get("resource_id")
    if acc and (own.account is None or own.account.resource_id != acc):
        ev = list((sub.get("account") or {}).get("evidence") or [])
        if own.account:
            own.links.pop(own.account.resource_id, None)
        tier, reasons = link_for(acc, ev)
        own.account = Link(acc, canonical_system(acc, tools.view.by_resource(acc)) or ACCOUNT_SYSTEM, tier, reasons,
                           note="agent")
        own.links[acc] = own.account
        own.ambiguities = [a for a in own.ambiguities if "primary profile" not in a]
    return own


def _config(model: str, cfg: dict, force_submit: bool) -> types.GenerateContentConfig:
    a = cfg["agent"]
    fdecl = [types.FunctionDeclaration(**d) for d in declarations() + [SUBMIT]]
    tool_cfg = types.ToolConfig(function_calling_config=types.FunctionCallingConfig(
        mode="ANY", allowed_function_names=["submit_audit"])) if force_submit else None
    return types.GenerateContentConfig(
        tools=[types.Tool(function_declarations=fdecl)], tool_config=tool_cfg, temperature=0,
        max_output_tokens=a["max_output_tokens"],
        automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
        thinking_config=types.ThinkingConfig(thinking_level=a["thinking_level"][model]))


def investigate(row: dict, tools: CaseTools, det: Plan, gateway, model: str, cfg: dict, times: dict,
                intent, audit_at) -> AgentOutcome:
    a = cfg["agent"]
    out = AgentOutcome(det, "fallback")
    text = PROMPT + "\n\nCASE BRIEF (JSON):\n" + json.dumps(brief(row, tools, det), ensure_ascii=False, default=str)
    history = [types.Content(role="user", parts=[types.Part(text=text)])]
    repairs = 0
    for rnd in range(a["max_tool_rounds"] + a["max_repairs"] + 1):
        force = rnd >= a["max_tool_rounds"]
        try:
            resp, usage = gateway.generate(model=model, contents=history, config=_config(model, cfg, force),
                                           purpose="agent", est_input_tokens=a["est_input_tokens"] + 1500 * rnd,
                                           case_id=row["case_id"])
        except Exception as exc:  # budget, provider, replay miss: deterministic plan, flagged
            out.errors.append(f"{type(exc).__name__}: {str(exc)[:160]}")
            break
        out.model_calls += 1
        out.cost_usd += usage["cost_usd"]
        out.cache_hits += int(usage.get("cache", False))
        content = resp.candidates[0].content if resp.candidates and resp.candidates[0].content else None
        calls = resp.function_calls or []
        if content is None or not calls:
            out.errors.append("model answered without a tool call")
            history += [content] if content else []
            history.append(types.Content(role="user", parts=[types.Part(text="Call submit_audit now.")]))
            continue
        history.append(content)                 # unchanged: keeps thought signatures
        replies = []
        for c in calls:
            args = dict(c.args or {})
            if c.name == "submit_audit":
                errs = validate_submission(args, tools)
                if not errs:
                    out.submission = args
                    own = apply_submission(args, tools)
                    out.ownership = own
                    assessments = {r: assess(r, l.system_id, tools.view, tools.rules, tools.subject)
                                   for r, l in own.links.items()}
                    plan = plan_case(row["case_id"], audit_at, intent, tools.subject, own, assessments, times)
                    plan.reasons.insert(0, f"agent: {args.get('notes', '')[:200]}")
                    out.plan, out.status = plan, "submitted"
                    out.tool_calls = list(tools.calls)
                    return out
                repairs += 1
                out.errors.append("; ".join(errs))
                replies.append(types.Part.from_function_response(name=c.name, response={"rejected": errs}))
                if repairs > a["max_repairs"]:
                    out.tool_calls = list(tools.calls)
                    return _fallback(out, "submission rejected after repairs")
            else:
                replies.append(types.Part.from_function_response(name=c.name, response=tools.call(c.name, args)))
        history.append(types.Content(role="user", parts=replies))
    out.tool_calls = list(tools.calls)
    return _fallback(out, "no valid submission")


def _fallback(out: AgentOutcome, why: str) -> AgentOutcome:
    out.plan.support = "unresolved"
    out.plan.reasons.insert(0, f"agent fallback: {why}; {' | '.join(out.errors)[:300]}")
    return out
