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
from .ownership import ACCOUNT_SYSTEM, Link, Ownership, canonical_system
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


def brief(row: dict, tools: CaseTools, det: Plan) -> dict:
    """The case as the model sees it: request, subject, proposal with obs_ids, and the open questions."""
    proposal = []
    for d in det.decisions:
        proposal.append({k: d[k] for k in ("resource_id", "system_id", "tier", "link_reasons", "category",
                                            "treatment", "verdict", "reason", "proof")})
        tools.seen.update(d["link_reasons"])
        if d["proof"]:
            tools.seen.add(d["proof"])
    return {"case_id": row["case_id"], "request_email": row["email"], "requested_at": row["requested_at"],
            "reported_status_claim": row["reported_status"], "reported_at": row["reported_at"],
            "audit_at": row["audit_at"], "request_text": row["request_text"],
            "subject": tools.resolve_identity(), "proposal": proposal,
            "proposed_status": det.status, "support": det.support, "open_questions": det.reasons}


def validate_submission(sub: dict, tools: CaseTools) -> list[str]:
    errs = []
    cited = [e for part in ([sub.get("account") or {}] + list(sub.get("exclude") or []) + list(sub.get("add") or []))
             for e in (part.get("evidence") or [])]
    unknown = sorted({e for e in cited if e not in tools.seen})
    if unknown:
        errs.append(f"these obs_ids were never returned by a tool: {unknown[:5]}")
    acc = (sub.get("account") or {}).get("resource_id")
    if acc:
        cands = {c["account"] for c in tools.workflow_candidates()["candidates"]}
        if acc not in cands and acc not in tools.ownership.links:
            errs.append(f"account {acc} is neither a workflow candidate nor a linked resource")
    for x in sub.get("exclude") or []:
        if x.get("resource_id") not in tools.ownership.links:
            errs.append(f"cannot exclude {x.get('resource_id')}: not in the proposal")
    for x in sub.get("add") or []:
        r = x.get("resource_id", "")
        if not tools.resource_re.fullmatch(r or ""):
            errs.append(f"{r!r} is not a resource id")
            continue
        named = [e for e in x.get("evidence") or [] if (o := tools.view.get(e)) is not None
                 and (o.resource_id == r or r in json.dumps(o.fields, default=str))]
        if not named:
            errs.append(f"none of the evidence cited for {r} mentions it")
    return errs


def apply_submission(sub: dict, tools: CaseTools) -> Ownership:
    own = Ownership(tools.case_id, links=dict(tools.ownership.links), account=tools.ownership.account,
                    excluded=dict(tools.ownership.excluded), ambiguities=list(tools.ownership.ambiguities))
    strong = tools.subject.keys(strong_only=True)

    def tier_for(evidence: list[str]) -> str:
        from .evidence import identifiers_in
        for e in evidence:
            o = tools.view.get(e)
            if o and any(k in strong for kk, v in o.fields.items() for k in identifiers_in(kk.rsplit(".", 1)[-1], v)):
                return "explicit"
        return "workflow"

    for x in sub.get("exclude") or []:
        own.links.pop(x["resource_id"], None)
        own.excluded[x["resource_id"]] = f"agent: {x.get('reason', '')}"
        if own.account and own.account.resource_id == x["resource_id"]:
            own.account = None
    for x in sub.get("add") or []:
        r = x["resource_id"]
        own.links[r] = Link(r, canonical_system(r, tools.view.by_resource(r)), tier_for(x["evidence"]),
                            tuple(x["evidence"]), note="agent")
    acc = (sub.get("account") or {}).get("resource_id")
    if acc and (own.account is None or own.account.resource_id != acc):
        ev = list((sub.get("account") or {}).get("evidence") or [])
        if own.account:
            own.links.pop(own.account.resource_id, None)
        prior = tools.ownership.links.get(acc)
        tier = prior.tier if prior else tier_for(ev)
        own.account = Link(acc, ACCOUNT_SYSTEM, tier, tuple(ev) or (prior.reasons if prior else ()), note="agent")
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
