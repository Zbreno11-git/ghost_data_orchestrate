"""Read-only investigation tools for the agent, one case at a time, over that case's CaseView only.

Every result is JSON-able and names observations by obs_id; the session remembers every obs_id it returned, and
the agent may cite only those (PRIMER boundary "Agent"). Activity rows are labelled as claims. Searches are
paginated and say how many results were omitted, so the model never mistakes a page for the whole.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from .evidence import Observation, normalize_identifier
from .identity import Subject
from .ownership import Ownership, WorkflowAssignment, canonical_system
from .policy import assess, copy_states, categorize, treatment
from .temporal import CaseView

PAGE_SIZE = 8
FIELD_CHARS = 400


def summarize(o: Observation, full: bool = False) -> dict:
    fields = o.fields if full else {k: (v[:120] if isinstance(v, str) else v) for k, v in list(o.fields.items())[:12]}
    out = {"obs_id": o.obs_id, "source_id": o.source_id, "kind": o.kind, "claim": o.kind == "activity",
           "captured_at": o.captured_at.isoformat(), "system_id": o.system_id, "resource_id": o.resource_id,
           "container": o.container, "topology": o.topology, "result": o.result, "fields": fields}
    if o.wrapper:
        out["wrapper_not_record_content"] = o.wrapper
    return out


@dataclass
class CaseTools:
    case_id: str
    view: CaseView
    subject: Subject
    ownership: Ownership
    workflow: WorkflowAssignment
    rules: dict
    resource_re: object
    seen: set = field(default_factory=set)
    calls: list = field(default_factory=list)

    def _ret(self, obs: list[Observation], full=False) -> list[dict]:
        self.seen.update(o.obs_id for o in obs)
        return [summarize(o, full) for o in obs]

    # --- tools ------------------------------------------------------------------------------------
    def resolve_identity(self) -> dict:
        """The subject's current and historical identifiers as of audit_at (exact values; names are weak)."""
        return {"user_id": self.subject.user_id, "request_email_role": self.subject.request_email_role,
                "identifiers": [{"type": i.type, "value": i.raw, "role": i.role, "strong": i.strong}
                                for i in self.subject.identifiers]}

    def search_evidence(self, query: str, page: int = 0) -> dict:
        """Admissible observations containing an exact identifier or resource id, paginated with an omitted count."""
        q = query.strip()
        hits: list[Observation] = []
        if self.resource_re.fullmatch(q):
            hits = self.view.by_resource(q)
        else:
            key = normalize_identifier("email" if "@" in q else ("phone" if q[:1] == "+" else "value"), q)
            key = key or (("user_id", q) if q.startswith("user_") else None)
            if key:
                hits = [h[0] for h in self.view.by_identifier(key)]
        hits = sorted({o.obs_id: o for o in hits}.values(), key=lambda o: (o.captured_at, o.obs_id))
        start = max(0, page) * PAGE_SIZE
        chunk = hits[start:start + PAGE_SIZE]
        return {"query": q, "total": len(hits), "page": page, "results": self._ret(chunk),
                "omitted": max(0, len(hits) - start - len(chunk)),
                "note": "" if hits else "no admissible observation matches this exact value (no fuzzy matching)"}

    def inspect_evidence(self, obs_id: str) -> dict:
        """One admissible observation in full: business fields, plus wrapper fields that are not record content."""
        o = self.view.get(obs_id)
        if o is None:
            return {"error": f"{obs_id} is unknown or captured after audit_at"}
        out = self._ret([o], full=True)[0]
        out["fields"] = {k: (v[:FIELD_CHARS] if isinstance(v, str) else v) for k, v in o.fields.items()}
        return out

    def resource_timeline(self, resource_id: str) -> dict:
        """Every admissible observation of a resource in time order; activity rows are claims, not state."""
        obs = sorted(self.view.by_resource(resource_id), key=lambda o: (o.captured_at, o.obs_id))
        return {"resource_id": resource_id, "system_id": canonical_system(resource_id, obs),
                "events": self._ret(obs[-20:]), "omitted_older": max(0, len(obs) - 20)}

    def compare_replicas(self, resource_id: str) -> dict:
        """State of each physical copy (primary, replicas, documents) from its own latest admissible evidence."""
        obs = self.view.by_resource(resource_id)
        system = canonical_system(resource_id, obs)
        cat = categorize(resource_id, system, self.view)
        if cat.name is None:
            return {"resource_id": resource_id, "error": cat.reason}
        copies = copy_states(resource_id, system, treatment(cat.name, self.rules), self.view, self.subject)
        self.seen.update(c.obs_id for c in copies)
        return {"resource_id": resource_id, "system_id": system, "copies": [
            {"copy": list(c.copy), "state": c.state, "obs_id": c.obs_id, "basis": c.basis,
             "captured_at": c.captured_at.isoformat(), "detail": c.detail} for c in copies]}

    def inspect_flows_restores(self) -> dict:
        """Policy verdicts for the subject's data flows and backups (can they recreate deleted data?)."""
        out = []
        for r, link in sorted(self.ownership.links.items()):
            system = link.system_id
            if system not in ("integration_service", "backup_service"):
                continue
            a = assess(r, system, self.view, self.rules, self.subject)
            if a.proof:
                self.seen.add(a.proof.obs_id)
            out.append({"resource_id": r, "system_id": system, "verdict": a.verdict, "reason": a.reason,
                        "proof": a.proof.obs_id if a.proof else None})
        return {"flows_and_backups": out}

    def evaluate_policy(self, resource_id: str) -> dict:
        """Deterministic policy verdict for one resource: category, required treatment, compliance, proof."""
        obs = self.view.by_resource(resource_id)
        system = canonical_system(resource_id, obs)
        a = assess(resource_id, system, self.view, self.rules, self.subject)
        if a.proof:
            self.seen.add(a.proof.obs_id)
        return {"resource_id": resource_id, "system_id": system, "category": a.category.name,
                "category_reason": a.category.reason, "treatment": a.treatment, "verdict": a.verdict,
                "reason": a.reason, "proof": a.proof.obs_id if a.proof else None,
                "operations": [op for op in a.ops if op]}

    def check_coverage(self, system_id: str) -> dict:
        """Admissible snapshots that cover a system, for proving absence by scope."""
        scopes = [o for o in self.view.observations if o.kind == "scope" and o.system_id == system_id]
        return {"system_id": system_id, "admissible_snapshots": len(scopes),
                "snapshots": self._ret(sorted(scopes, key=lambda o: o.captured_at)[-PAGE_SIZE:]),
                "omitted": max(0, len(scopes) - PAGE_SIZE)}

    def workflow_candidates(self) -> dict:
        """Primary-profile rows that could belong to this request's deletion run; candidates, never proof."""
        q = self.workflow.requests.get(self.case_id)
        assigned = self.workflow.assigned.get(self.case_id)
        rows = [r for r in self.workflow.rows if q and self.workflow.feasible(q, r)]
        taken = {row.obs_id: c for c, (row, _, _) in self.workflow.assigned.items()}
        self.seen.update(r.obs_id for r in rows)
        return {"assigned": None if not assigned else {"obs_id": assigned[0].obs_id, "account": assigned[0].resource_id,
                                                      "how": assigned[1]},
                "candidates": [{"obs_id": r.obs_id, "account": r.resource_id, "event_time": r.captured_at.isoformat(),
                                "minutes_before_report": round((q.reported_at - r.captured_at).total_seconds() / 60),
                                "worker_result_claim": r.result, "taken_by": taken.get(r.obs_id)} for r in rows],
                "note": "time and status only make candidates; they never prove ownership (A20)"}

    # --- dispatch -----------------------------------------------------------------------------------
    def call(self, name: str, args: dict) -> dict:
        fn = TOOLS.get(name)
        if fn is None:
            return {"error": f"unknown tool {name}"}
        try:
            out = fn(self, **(args or {}))
        except TypeError as exc:
            out = {"error": f"bad arguments for {name}: {exc}"}
        self.calls.append(name)
        return out


TOOLS = {n: getattr(CaseTools, n) for n in (
    "resolve_identity", "search_evidence", "inspect_evidence", "resource_timeline", "compare_replicas",
    "inspect_flows_restores", "evaluate_policy", "check_coverage", "workflow_candidates")}

_STR = {"type": "string"}
PARAMS = {
    "resolve_identity": {},
    "search_evidence": {"query": {**_STR, "description": "an exact email, phone, hash, user_id or resource_id"},
                        "page": {"type": "integer"}},
    "inspect_evidence": {"obs_id": _STR},
    "resource_timeline": {"resource_id": _STR},
    "compare_replicas": {"resource_id": _STR},
    "inspect_flows_restores": {},
    "evaluate_policy": {"resource_id": _STR},
    "check_coverage": {"system_id": _STR},
    "workflow_candidates": {},
}
REQUIRED = {"search_evidence": ["query"], "inspect_evidence": ["obs_id"], "resource_timeline": ["resource_id"],
            "compare_replicas": ["resource_id"], "evaluate_policy": ["resource_id"], "check_coverage": ["system_id"]}


def declarations() -> list[dict]:
    """Gemini function declarations, derived from the registry (a tool without a declaration fails the tests)."""
    out = []
    for name, fn in TOOLS.items():
        params = {"type": "object", "properties": PARAMS[name]}
        if REQUIRED.get(name):
            params["required"] = REQUIRED[name]
        out.append({"name": name, "description": (fn.__doc__ or name.replace("_", " ")).strip().splitlines()[0],
                    "parameters_json_schema": params})
    return out
