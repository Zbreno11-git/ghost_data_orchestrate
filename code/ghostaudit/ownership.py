"""Which resources belong to a request's subject, with link strength and the observations that support it.

Tiers (A5, A20):
- explicit: an admissible observation carries a strong identifier of the subject in its fields or wrapper
  (a lookup made for the subject counts; exposure is decided elsewhere, FR-11), or a catalog row names them.
- workflow: a *candidate* from the request's deletion-workflow run. Time and status only produce candidates;
  a workflow link is never upgraded to explicit, and a case that depends on one is reported as weak.

The primary-profile assignment is one-to-one because the stream has one `deletion_worker` account_service
row per authorized request (539 rows, all distinct accounts, for 540 authorized requests; measured
2026-10-24). It is solved by deduction only: an explicitly linked account fixes its request, corroborated runs
fix theirs, and a request with a single feasible row (or a row feasible for a single request) is assigned.
Anything still tied stays ambiguous and is never forced.
"""
from __future__ import annotations

import re
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta

from .evidence import Observation
from .identity import IdentityIndex, Subject
from .temporal import CaseView
from .timeutil import parse_ts

WORKER = "deletion_worker"
ACCOUNT_SYSTEM = "account_service"
# The primary-profile row lands at most 8 min after reported_at on the samples (measured 2026-10-24); 15 min of
# slack keeps the window a superset without reaching the next request's run.
REPORT_SLACK = timedelta(minutes=15)


@dataclass(frozen=True)
class Link:
    resource_id: str
    system_id: str | None
    tier: str                       # explicit | workflow
    reasons: tuple[str, ...]        # obs_ids that support the link
    note: str = ""


@dataclass
class Ownership:
    case_id: str
    links: dict[str, Link] = field(default_factory=dict)
    account: Link | None = None
    excluded: dict[str, str] = field(default_factory=dict)      # resource → why it is not the subject's
    ambiguities: list[str] = field(default_factory=list)

    @property
    def weak(self) -> bool:
        return any(l.tier == "workflow" for l in self.links.values())


def canonical_system(resource_id: str, observations: list[Observation]) -> str | None:
    """The owning system: the deletion worker's target, else the record's own system, else any activity target.

    Plain activity targets are not enough (support tickets are indexed *into* search_service, audit records are
    archived *into* archive_service); a replica container (support_replica) is never the logical system."""
    mine = [o for o in observations if o.resource_id == resource_id and o.system_id]
    for pick in (lambda o: o.kind == "activity" and o.fields.get("source_system") == WORKER,
                 lambda o: o.kind != "activity",
                 lambda o: o.kind == "activity"):
        c = Counter(o.system_id for o in mine if pick(o))
        if c:
            return c.most_common(1)[0][0]
    return None


class OwnerIndex:
    """Strong identifier → user_ids that ever held it, used to recognize records that belong to someone else."""

    def __init__(self, identity: IdentityIndex, far_future: datetime):
        self.owners: dict[tuple[str, str], set[str]] = defaultdict(set)
        for uid in identity.snapshot:
            for i in identity.identifiers(uid, far_future):
                if i.strong:
                    self.owners[i.key].add(uid)

    @staticmethod
    def keys_in_text(text: str) -> set[tuple[str, str]]:
        from .evidence import EMAIL_RE, normalize_identifier
        keys = {("email", e.lower()) for e in EMAIL_RE.findall(text)}
        keys |= {("user_id", u) for u in re.findall(r"\buser_\d+\b", text)}
        keys |= {("email_hash", h.lower()) for h in re.findall(r"\b[0-9a-fA-F]{64}\b", text)}
        keys |= {k for p in re.findall(r"\+\d[\d ()\-]{7,}\d", text) if (k := normalize_identifier("phone", p))}
        return keys

    def others_in_text(self, text: str, user_id: str) -> set[str]:
        found = set()
        for key in self.keys_in_text(text):
            found |= self.owners.get(key, set()) - {user_id}
        return found

    def others(self, obs: Observation, user_id: str) -> set[str]:
        from .evidence import identifiers_in
        found = set()
        for k, v in obs.fields.items():
            for key in identifiers_in(k.rsplit(".", 1)[-1], v):
                found |= self.owners.get(key, set()) - {user_id}
        return found


ROW_KEY = re.compile(r"^rows\.\d+\.(row \d+):")


def text_units(obs: Observation) -> list[str]:
    """Finer units of a text observation: one screen row (`rows.N.row K: …`), one line of a page."""
    groups: dict[str, list[str]] = defaultdict(list)
    for k, v in obs.fields.items():
        if not isinstance(v, str) or k.startswith("ids."):
            continue
        m = ROW_KEY.match(k)
        if m:
            groups[m.group(1)].append(v)
        elif k == "text":
            groups.update({f"line:{i}": [line] for i, line in enumerate(v.splitlines())})
        else:
            groups[k].append(v)
    return [" | ".join(vs) for vs in groups.values()]


def _whole_text(obs: Observation) -> str:
    return " | ".join(v for k, v in obs.fields.items() if isinstance(v, str) and not k.startswith("ids."))


def explicit_links(subject: Subject, view: CaseView, resource_re, owners: "OwnerIndex") -> dict[str, list[str]]:
    """resource → supporting obs_ids, from observations carrying a strong identifier of the subject.

    For free text (PDF pages, screen panels) co-occurrence is a link only inside a unit that names this subject
    and nobody else: a single-subject document links at page level; a screen listing several customers splits into
    rows (measured: a connector panel otherwise tied user_14's flow to user_15's case)."""
    out: dict[str, set[str]] = defaultdict(set)
    mine = subject.keys(strong_only=True)
    for key in mine:
        for obs, _role, _k in view.by_identifier(key):
            if obs.kind != "text":
                if obs.resource_id:
                    out[obs.resource_id].add(obs.obs_id)
                continue
            whole = _whole_text(obs)
            units = [whole] if not owners.others_in_text(whole, subject.user_id) else text_units(obs)
            for unit in units:
                if owners.keys_in_text(unit) & mine and not owners.others_in_text(unit, subject.user_id):
                    for r in resource_re.findall(unit):
                        out[r].add(obs.obs_id)
    return {r: sorted(v) for r, v in out.items()}


@dataclass
class _Req:
    case_id: str
    subject: Subject
    requested_at: datetime
    reported_at: datetime
    audit_at: datetime
    explicit: dict[str, list[str]]


class WorkflowAssignment:
    """One primary-profile row per authorized request, assigned by deduction across all requests."""

    def __init__(self, activity_obs: list[Observation], requests: list[_Req]):
        # Anchor rows: the worker's primary-profile row for a deletion run, or the intake's non-deletion
        # classification (10 rows) for a request that never started one. 549 anchors for 550 requests.
        self.rows = sorted((o for o in activity_obs if o.kind == "activity" and o.resource_id and (
            (o.fields.get("source_system") == WORKER and o.system_id == ACCOUNT_SYSTEM)
            or o.record_type == "CLASSIFY_REQUEST")), key=lambda o: (o.captured_at, o.obs_id))
        self.worker_rows = defaultdict(list)
        for o in activity_obs:
            if o.kind == "activity" and o.fields.get("source_system") == WORKER and o.resource_id:
                self.worker_rows[o.resource_id].append(o)
        self.requests = {q.case_id: q for q in requests}
        self.assigned: dict[str, tuple[Observation, str, tuple[str, ...]]] = {}   # case → (row, how, reasons)
        self.ambiguous: dict[str, list[str]] = {}
        self.ranked: dict[str, tuple[Observation, float]] = {}   # scored mode only: weak best candidate
        self._solve()
        self._rank()

    def feasible(self, q: _Req, row: Observation) -> bool:
        return q.requested_at <= row.captured_at <= q.reported_at + REPORT_SLACK and row.captured_at <= q.audit_at

    def corroboration(self, q: _Req, row: Observation) -> list[str]:
        """Worker rows of the subject's explicitly linked resources inside this run (account row → report)."""
        hits = []
        for r in q.explicit:
            for w in self.worker_rows.get(r, ()):
                if w is not row and row.captured_at <= w.captured_at <= q.reported_at + REPORT_SLACK:
                    hits.append(w.obs_id)
        return sorted(hits)

    def _solve(self) -> None:
        cand = {c: [r for r in self.rows if self.feasible(q, r)] for c, q in self.requests.items()}
        taken: set[str] = set()

        def assign(case_id, row, how, reasons):
            self.assigned[case_id] = (row, how, tuple(reasons))
            taken.add(row.obs_id)

        # 1. an account explicitly linked to the subject fixes the pair
        for c, q in sorted(self.requests.items()):
            fixed = [r for r in cand[c] if r.resource_id in q.explicit]
            if len(fixed) == 1 and fixed[0].obs_id not in taken:
                assign(c, fixed[0], "explicit_account", [fixed[0].obs_id, *q.explicit[fixed[0].resource_id]])
        # 2. propagation: corroborated-unique and feasibility-unique, until nothing changes
        changed = True
        while changed:
            changed = False
            open_cases = [c for c in sorted(self.requests) if c not in self.assigned]
            for c in open_cases:
                rows = [r for r in cand[c] if r.obs_id not in taken]
                q = self.requests[c]
                scored = {r.obs_id: self.corroboration(q, r) for r in rows}
                best = [r for r in rows if scored[r.obs_id]]
                if len(best) == 1:
                    assign(c, best[0], "corroborated_run", [best[0].obs_id, *scored[best[0].obs_id]])
                    changed = True
                elif len(rows) == 1:
                    assign(c, rows[0], "only_feasible_row", [rows[0].obs_id])
                    changed = True
            for r in self.rows:
                if r.obs_id in taken:
                    continue
                who = [c for c in self.requests if c not in self.assigned and r in cand[c]]
                if len(who) == 1:
                    assign(who[0], r, "only_feasible_request", [r.obs_id])
                    changed = True
            if not changed:
                changed = self._forced(cand, taken, assign)
        for c in self.requests:
            if c not in self.assigned:
                left = [r.resource_id for r in cand[c] if r.obs_id not in taken]
                self.ambiguous[c] = left

    def _rank(self) -> None:
        """Weak candidates for unassigned requests: the untaken anchor nearest reported_at, one-to-one, greedy by
        gap. A candidate, never proof (A20); a tie for the same request leaves it unranked."""
        taken = {row.obs_id for row, _, _ in self.assigned.values()}
        options = []
        for c in sorted(self.ambiguous):
            q = self.requests[c]
            gaps = sorted((abs((q.reported_at - r.captured_at).total_seconds()), r.obs_id, r)
                          for r in self.rows if r.obs_id not in taken and self.feasible(q, r))
            if gaps and not (len(gaps) > 1 and gaps[0][0] == gaps[1][0]):
                options.extend((g, c, r) for g, _, r in gaps)
        used_rows, used_cases = set(taken), set()
        for g, c, r in sorted(options, key=lambda x: (x[0], x[1], x[2].obs_id)):
            if c not in used_cases and r.obs_id not in used_rows:
                self.ranked[c] = (r, g)
                used_cases.add(c)
                used_rows.add(r.obs_id)

    def _forced(self, cand, taken, assign) -> bool:
        """Assign pairs present in every maximum matching of the remaining graph (forced under one-to-one)."""
        open_cases = sorted(c for c in self.requests if c not in self.assigned)
        adj = {c: [r.obs_id for r in cand[c] if r.obs_id not in taken] for c in open_cases}
        by_id = {r.obs_id: r for r in self.rows}
        size, match = _max_matching(adj)
        forced = [(c, rid) for rid, c in sorted(match.items()) if _max_matching(adj, banned=(c, rid))[0] < size]
        for c, rid in forced:
            assign(c, by_id[rid], "forced_matching", [rid])
        return bool(forced)

    def run_window(self, case_id: str) -> tuple[datetime, datetime] | None:
        if case_id not in self.assigned:
            return None
        q = self.requests[case_id]
        return self.assigned[case_id][0].captured_at, q.reported_at + REPORT_SLACK


def _max_matching(adj: dict[str, list[str]], banned: tuple[str, str] | None = None) -> tuple[int, dict[str, str]]:
    match: dict[str, str] = {}

    def augment(c, seen):
        for rid in adj[c]:
            if (c, rid) == banned or rid in seen:
                continue
            seen.add(rid)
            if rid not in match or augment(match[rid], seen):
                match[rid] = c
                return True
        return False

    size = sum(augment(c, set()) for c in adj)
    return size, match


def link_case(q: _Req, view: CaseView, wf: WorkflowAssignment, owners: OwnerIndex, mode: str = "strict") -> Ownership:
    own = Ownership(q.case_id)
    for r, reasons in sorted(q.explicit.items()):
        obs = view.by_resource(r)
        own.links[r] = Link(r, canonical_system(r, obs), "explicit", tuple(reasons))
    # The account: the assigned primary-profile row. An explicitly linked account that is another request's
    # row (the same person asked twice) belongs to that request, not this one.
    mine = wf.assigned.get(q.case_id)
    for r in list(own.links):
        if r.startswith("account_") or own.links[r].system_id == ACCOUNT_SYSTEM:
            other = [c for c, (row, _, _) in wf.assigned.items() if row.resource_id == r and c != q.case_id]
            if other and not (mine and mine[0].resource_id == r):
                own.excluded[r] = f"primary profile of {other[0]}'s workflow run"
                del own.links[r]
    if mine and mine[0].record_type == "CLASSIFY_REQUEST":
        own.ambiguities.append(f"anchored to intake row {mine[0].obs_id} (non-deletion classification claim)")
        mine = None
    elif mine:
        row, how, reasons = mine
        tier = "explicit" if how == "explicit_account" else "workflow"
        own.account = Link(row.resource_id, ACCOUNT_SYSTEM, tier, reasons, note=how)
        own.links[row.resource_id] = own.account
    elif mode == "scored" and q.case_id in wf.ranked and wf.ranked[q.case_id][0].record_type != "CLASSIFY_REQUEST":
        row, gap = wf.ranked[q.case_id]
        own.account = Link(row.resource_id, ACCOUNT_SYSTEM, "workflow", (row.obs_id,),
                           note=f"nearest anchor to reported_at ({gap / 60:.0f} min); weak")
        own.links[row.resource_id] = own.account
        own.ambiguities.append(f"primary profile is a weak candidate among {wf.ambiguous.get(q.case_id, [])}")
    else:
        own.ambiguities.append(f"primary profile unassigned; candidates {wf.ambiguous.get(q.case_id, [])}")
    # Workflow candidates for resources with no subject link (already-clean records): scored mode only, and only
    # when exactly one assigned run window contains the worker row and no other subject owns the record.
    if mode == "scored" and mine:
        row = mine[0]
        start, end = wf.run_window(q.case_id)
        windows = {c: wf.run_window(c) for c in wf.assigned}
        for r, rows in sorted(wf.worker_rows.items()):
            if r in own.links or r in own.excluded or any(w.system_id == ACCOUNT_SYSTEM for w in rows):
                continue
            for w in rows:
                if not (start <= w.captured_at <= end) or not view.admissible(w):
                    continue
                inside = [c for c, win in windows.items() if win and win[0] <= w.captured_at <= win[1]]
                obs = view.by_resource(r)
                foreign = set().union(*(owners.others(o, q.subject.user_id) for o in obs)) if obs else set()
                if foreign:
                    own.excluded[r] = f"carries identifiers of {sorted(foreign)}"
                elif inside == [q.case_id]:
                    own.links[r] = Link(r, canonical_system(r, obs), "workflow", (row.obs_id, w.obs_id),
                                        note="unique run window")
                else:
                    own.ambiguities.append(f"{r}: worker row {w.obs_id} inside {len(inside)} run windows")
                break
    # Decoys: an explicit link whose record also carries another subject's identifiers is ambiguous, not owned.
    for r, l in list(own.links.items()):
        if l.tier != "explicit" or l is own.account:
            continue
        foreign = set()
        for oid in l.reasons:
            o = view.get(oid)
            if o is not None:
                foreign |= owners.others(o, q.subject.user_id)
        if foreign:
            own.ambiguities.append(f"{r}: supporting record also carries identifiers of {sorted(foreign)}")
    return own


def build_requests(rows: list[dict], identity: IdentityIndex, store, resource_re,
                   owners: OwnerIndex) -> tuple[list[_Req], dict]:
    """(_Req per resolvable request, {case_id: resolve result}) — explicit links computed in each case's view."""
    reqs, resolved = [], {}
    for q in rows:
        audit = parse_ts(q["audit_at"])
        s = identity.resolve(q["email"], audit)
        resolved[q["case_id"]] = s
        if isinstance(s, Subject):
            view = CaseView(store, audit)
            reqs.append(_Req(q["case_id"], s, parse_ts(q["requested_at"]), parse_ts(q["reported_at"]), audit,
                             explicit_links(s, view, resource_re, owners)))
    return reqs, resolved
