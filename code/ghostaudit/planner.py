"""Planner: typed decisions → contract steps → a validated row, plus how well that row is supported.

Step-set rules (AGENTS §6.3–6.6; measured on the samples 2026-10-24):
- INCOMPLETE: a cited finding, a remediation and a future verification for every violation; plus a future
  check that the account is absent and that every retained record is present. Already-compliant resources are
  not listed, and future steps use an empty evidence_id.
- COMPLETE: one cited verification per relevant resource, proving its state at audit_at.
- NOT_APPLICABLE: no steps.
A row that validates is not a supported verdict (A20): each row carries `resolved`, `weak` (it depends on a
workflow-only link or a low-confidence intent) or `unresolved`, with the reasons.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from .contract import OPERATIONS
from .identity import Subject
from .intent import Intent
from .ownership import Ownership
from .policy import Assessment
from .serialize import canonical_sort, dumps
from .validate import validate_row


@dataclass
class Plan:
    case_id: str
    status: str
    steps: list[dict]
    support: str                        # resolved | weak | unresolved
    reasons: list[str] = field(default_factory=list)
    decisions: list[dict] = field(default_factory=list)
    trace: dict = field(default_factory=dict)   # what `main.py explain` prints (S6 C6.2); never read by planning


def _step(op: str, system: str, resource: str, evidence: str) -> dict:
    phase, state, _rank = OPERATIONS[op]
    return {"step_no": 0, "phase": phase, "system_id": system, "resource_id": resource, "operation": op,
            "state": state, "evidence_id": evidence}


def plan_case(case_id: str, audit_at: datetime, intent: Intent, subject, own: Ownership | None,
              assessments: dict[str, Assessment], evidence_times: dict[str, datetime],
              include_weak: bool = True) -> Plan:
    reasons: list[str] = []
    if intent.authorizes_deletion is False:
        p = Plan(case_id, "NOT_APPLICABLE", [], "resolved" if intent.confidence == "high" else "weak",
                 [] if intent.confidence == "high" else [f"intent: {intent.reason}"])
        return _finish(p, audit_at, evidence_times)
    if intent.authorizes_deletion is None:
        reasons.append(f"intent unknown: {intent.reason}")
    elif intent.confidence != "high":
        reasons.append(f"intent low confidence: {intent.reason}")
    if not isinstance(subject, Subject) or own is None:
        return _finish(Plan(case_id, "INCOMPLETE", [], "unresolved", reasons + [f"identity: {subject!r}"]),
                       audit_at, evidence_times)

    links = {r: l for r, l in own.links.items() if include_weak or l.tier == "explicit"}
    weak_used = [r for r, l in links.items() if l.tier == "workflow"]
    if weak_used:
        reasons.append("weak links used: " + ", ".join(sorted(weak_used)))
    reasons += own.ambiguities
    account = own.account.resource_id if own.account and own.account.resource_id in links else None
    if account is None:
        reasons.append("no account resource attributed")

    decisions, violations, compliant, unknown = [], [], [], []
    for r in sorted(links):
        a = assessments[r]
        decisions.append({"resource_id": r, "system_id": a.system_id, "tier": links[r].tier,
                          "link_reasons": list(links[r].reasons), "category": a.category.name,
                          "category_reason": a.category.reason, "treatment": a.treatment, "verdict": a.verdict,
                          "reason": a.reason, "proof": a.proof.obs_id if a.proof else None,
                          "copies": [[list(c.copy), c.state, c.obs_id, c.basis] for c in a.copies]})
        {"violation": violations, "compliant": compliant, "unknown": unknown}[a.verdict].append(a)

    steps: list[dict] = []
    if violations:
        status = "INCOMPLETE"
        for a in violations:
            find, fix, check = a.ops
            steps += [_step(find, a.system_id, a.resource_id, a.proof.source_id),
                      _step(fix, a.system_id, a.resource_id, ""), _step(check, a.system_id, a.resource_id, "")]
        listed = {a.resource_id for a in violations}
        if account and account not in listed:
            steps.append(_step("VERIFY_RECORD_ABSENT", "account_service", account, ""))
        for a in compliant + unknown:
            if a.treatment == "RETAIN" and a.resource_id not in listed:
                steps.append(_step("VERIFY_RECORD_PRESENT", a.system_id, a.resource_id, ""))
        for a in unknown:
            reasons.append(f"{a.resource_id}: state unknown ({a.reason})")
    else:
        status = "COMPLETE"
        for a in compliant:
            steps.append(_step(a.ops[2], a.system_id, a.resource_id, a.proof.source_id))
        for a in unknown:
            reasons.append(f"{a.resource_id}: state unknown, cannot be verified ({a.reason})")
    support = support_of(intent, account is not None, bool(unknown), bool(weak_used), bool(own.ambiguities))
    return _finish(Plan(case_id, status, steps, support, reasons, decisions), audit_at, evidence_times)


def support_of(intent: Intent, account: bool, unknown: bool, weak_links: bool, ambiguous: bool) -> str:
    """The one place a support level is decided (S5 C5.2). Unresolved: no intent, no account, or any resource in
    an unknown state (a retained record included). Weak: a workflow-only link, any ownership ambiguity (whatever
    its text), or a low-confidence intent. Only a case with none of these is resolved."""
    if intent.authorizes_deletion is None or not account or unknown:
        return "unresolved"
    if weak_links or ambiguous or intent.confidence != "high":
        return "weak"
    return "resolved"


def _finish(p: Plan, audit_at: datetime, evidence_times: dict[str, datetime]) -> Plan:
    p.steps = canonical_sort(p.steps)
    bad = validate_row(p.case_id, p.status, dumps(p.steps), audit_at, evidence_times)
    if bad:
        p.support = "unresolved"
        p.reasons.append("row fails validation: " + "; ".join(f"{v.code} {v.detail}" for v in bad))
    return p
