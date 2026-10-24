"""Policy: which treatment each resource needs, and whether every physical copy of it has that treatment now.

State is reconstructed per physical copy (system × topology; no topology = the live primary). A newer clean
primary never clears an older dirty replica: each copy is judged by its own latest admissible evidence, and the
resource is compliant only if every copy is (A20). Activity rows are claims and never set a state; the
deletion worker's *action type* is used only as a category hint where content cannot separate two categories
(it matched the sample treatment family for 85/85 resources, 2026-10-24).
"""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass

from .evidence import Observation
from .identity import Subject
from .temporal import CaseView

# canonical system → (default category, alternative category or None)
SYSTEM_CATEGORY = {
    "account_service": ("USER_PROFILE", None),
    "search_service": ("SEARCH_INDEX_ENTRY", None),
    "cache_service": ("CACHE_ENTRY", None),
    "analytics_platform": ("ANALYTICS_PROFILE", "MARKETING_PROFILE"),
    "marketing_platform": ("MARKETING_PROFILE", None),
    "support_platform": ("SUPPORT_MESSAGE", "SUPPORT_ATTACHMENT"),
    "object_storage": ("SUPPORT_ATTACHMENT", None),
    "export_service": ("USER_EXPORT", None),
    "email_delivery_service": ("EMAIL_DELIVERY_LOG", None),
    "security_service": ("SECURITY_AUDIT_LOG", None),
    "legal_service": ("LEGAL_HOLD_RECORD", None),
    "backup_service": ("BACKUP_ARCHIVE", None),
    "identity_service": ("ACCOUNT_TOMBSTONE", None),
    "telemetry_service": ("PRODUCT_TELEMETRY", None),
    "integration_service": ("DATA_FLOW", None),     # AGENTS §6.5: an active flow is a recreation risk
}
# Rule categories no participant source holds, with the reason; re-checked against the raw files by a test.
UNMAPPED = {"SECONDARY_IDENTIFIER": "no evidence file names a secondary identifier record (raw search 2026-10-24)"}
PREFIX_SYSTEM = {"account": "account_service", "search": "search_service", "analytics": "analytics_platform",
                 "support": "support_platform", "export": "export_service", "data_flow": "integration_service",
                 "backup": "backup_service", "audit_record": "security_service", "tombstone": "identity_service",
                 "legal_hold": "legal_service", "cache": "cache_service", "email_delivery": "email_delivery_service",
                 "marketing": "marketing_platform", "object": "object_storage"}
WORKER_ACTION = {"DELETE_RECORD": "DELETE", "ANONYMIZE_RECORD": "ANONYMIZE", "REDACT_RECORD": "REDACT"}

DIRECT_KEYS = ("email", "phone", "name", "email_hash", "matched_value")      # substrings of field names
LINK_KEYS = ("user_id", "customer_reference", "subject_reference", "subject_selector")
NULLS = {None, "", "null", "none", "[redacted]", "redacted"}

# treatment → (finding op, remediation op, verification op) — contract.OPERATIONS names
TREATMENT_OPS = {
    "DELETE": ("REPORT_REMAINING_RECORD", "DELETE_RECORD", "VERIFY_RECORD_ABSENT"),
    "ANONYMIZE": ("REPORT_EXPOSED_PII", "ANONYMIZE_RECORD", "VERIFY_RECORD_ANONYMIZED"),
    "REDACT": ("REPORT_EXPOSED_PII", "REDACT_RECORD", "VERIFY_RECORD_REDACTED"),
    "RETAIN": (None, None, "VERIFY_RECORD_PRESENT"),
    "DISABLE_FLOW": ("REPORT_ACTIVE_DATA_FLOW", "DISABLE_DATA_FLOW", "VERIFY_DATA_FLOW_DISABLED"),
    "BLOCK_RESTORE": ("REPORT_RESTORE_RISK", "BLOCK_RESTORE", "VERIFY_RESTORE_BLOCKED"),
}


def load_rules(rows: list[dict]) -> dict[str, dict]:
    """data_category → rule row. Every category must be reachable from SYSTEM_CATEGORY (tested)."""
    return {r["data_category"]: r for r in rows}


def treatment(category: str, rules: dict[str, dict]) -> str:
    if category == "DATA_FLOW":
        return "DISABLE_FLOW"
    action = rules[category]["required_action"]
    if category == "BACKUP_ARCHIVE":
        return "BLOCK_RESTORE"          # rule_14: retain the archive, block restore of the subject's data
    return action                        # DELETE | REDACT | ANONYMIZE | RETAIN


@dataclass(frozen=True)
class Category:
    name: str | None
    reason: str


def categorize(resource_id: str, system_id: str | None, view: CaseView) -> Category:
    system = system_id or PREFIX_SYSTEM.get(resource_id.rsplit("_", 1)[0])
    if system not in SYSTEM_CATEGORY:
        return Category(None, f"no policy category for system {system!r}")
    default, alt = SYSTEM_CATEGORY[system]
    if alt is None:
        return Category(default, f"system {system}")
    obs = view.by_resource(resource_id)
    content = None
    if alt == "MARKETING_PROFILE" and any("opt_in" in k or "marketing" in k for o in obs if o.resource_id == resource_id
                                          for k in o.fields):
        content = alt
    if alt == "SUPPORT_ATTACHMENT" and (
            any("belongs only to" in str(o.fields.get("details", "")) for o in obs)
            or any("attachment" in str(v).lower() for o in obs if o.kind == "text"
                   for s in view.by_source(o.source_id) for v in s.fields.values())):
        content = alt   # a catalog row, or the document that mentions it describes an uploaded attachment
    worker = {WORKER_ACTION.get(o.record_type) for o in obs
              if o.kind == "activity" and o.fields.get("source_system") == "deletion_worker"} - {None}
    hint = None
    if worker == {"DELETE"}:
        hint = alt
    elif worker and "DELETE" not in worker:
        hint = default
    if content and hint and content != hint:
        return Category(None, f"content says {content}, workflow action says {hint}")
    if content:
        return Category(content, "record content")
    if hint:
        return Category(hint, f"workflow action type {sorted(worker)} (claimed result ignored)")
    return Category(default, f"system {system} default; no content or workflow signal")


# --- per-copy state -------------------------------------------------------------------------------

def copy_key(obs: Observation) -> tuple[str | None, str]:
    return (obs.system_id, obs.topology or "primary")


DIRECT = "direct"      # an observation of the row itself
INFERRED = "scope"     # a capture that covers the system and lacks the row


def _present(v) -> bool:
    return not (v is None or (isinstance(v, str) and v.strip().lower() in NULLS))


def exposure(obs: Observation, treat: str, subject: Subject | None = None) -> list[str]:
    """Field keys (never wrapper keys, FR-11) that still identify the subject under this treatment."""
    keys = []
    for k, v in obs.fields.items():
        leaf = k.rsplit(".", 1)[-1].lower()
        if leaf in ("events", "resource_id", "source_resource_id"):
            continue
        if any(d in leaf for d in DIRECT_KEYS) and _present(v):
            keys.append(k)
        elif treat in ("ANONYMIZE",) and leaf in LINK_KEYS and _present(v):
            keys.append(k)
        elif treat == "REDACT" and leaf not in LINK_KEYS and isinstance(v, str) and "@" in v and _present(v):
            keys.append(k)
    return keys


@dataclass(frozen=True)
class CopyState:
    copy: tuple[str | None, str]
    state: str              # ABSENT PRESENT PRESENT_EXPOSED PRESENT_CLEAN REDACTED ANONYMIZED ACTIVE DISABLED
                            # RESTORABLE BLOCKED UNKNOWN
    obs_id: str
    source_id: str
    captured_at: object
    detail: str = ""
    basis: str = DIRECT


def _record_state(o: Observation, treat: str, subject) -> tuple[str, str]:
    f = {k.rsplit(".", 1)[-1].lower(): v for k, v in o.fields.items()}
    res = (o.result or "").upper()
    if treat == "DISABLE_FLOW":
        if res == "ACTIVE" or str(f.get("enabled", "")).lower() in ("true", "1"):
            return "ACTIVE", "enabled"
        if str(f.get("enabled", "")).lower() in ("false", "0"):
            return "DISABLED", "enabled=false"
        return "UNKNOWN", "flow state not stated"
    if treat == "BLOCK_RESTORE":
        allowed = str(f.get("restore_allowed", "")).lower()
        if res == "ACTIVE" or allowed in ("true", "1") or (str(f.get("eligible", "")).lower() == "true"
                                                          and str(f.get("deletion_block", "")).lower() == "false"):
            return "RESTORABLE", "restore allowed"
        if allowed in ("false", "0") or str(f.get("deletion_block", "")).lower() == "true":
            return "BLOCKED", "restore blocked"
        return "UNKNOWN", "restore state not stated"
    if res == "IDENTIFIABLE":
        return "PRESENT_EXPOSED", "lookup reports identifiable"
    if res == "ANONYMIZED":
        return "ANONYMIZED", "lookup reports anonymized"
    if treat in ("DELETE", "RETAIN"):
        return "PRESENT", "record present"
    exposed = exposure(o, treat, subject)
    if exposed:
        return "PRESENT_EXPOSED", "exposed " + ",".join(exposed)
    shown = [k for k in o.fields if any(d in k.lower() for d in DIRECT_KEYS + LINK_KEYS)]
    if not shown:
        return "UNKNOWN", "present, but no identifying fields are shown"
    return ("ANONYMIZED" if treat == "ANONYMIZE" else "REDACTED"), "identifying fields empty"


def scope_covers(scope: Observation, system: str, view: CaseView) -> bool:
    if scope.system_id:
        return scope.system_id == system
    # generic tables (customer_data_*) cover the origin systems of the rows they hold
    return any(o.system_id == system for o in view.by_source(scope.source_id)
               if o.container == scope.container and o.kind == "record")


def copy_states(resource_id: str, system: str | None, treat: str, view: CaseView,
                subject: Subject | None = None) -> list[CopyState]:
    events: dict[tuple, list[tuple]] = defaultdict(list)
    for o in view.by_resource(resource_id):
        if o.kind == "activity" or o.resource_id != resource_id:
            continue
        if o.kind == "lookup" and (o.result or "").upper() == "NOT_FOUND":
            events[copy_key(o)].append((o.captured_at, "ABSENT", o, "lookup not found"))
        elif o.kind in ("record", "lookup"):
            state, why = _record_state(o, treat, subject)
            events[copy_key(o)].append((o.captured_at, state, o, why))
    # A business document (PDF page, screen) that names the resource next to the subject's identifiers is a copy
    # of that record outside its system: present, and exposed where the treatment is redaction/anonymization.
    if subject is not None:
        mine = {i.norm for i in subject.identifiers if i.strong} | {i.raw.lower() for i in subject.identifiers if i.strong}
        for o in view.by_resource(resource_id):
            if o.kind != "text" or o.resource_id == resource_id:
                continue
            # Ownership was decided upstream with single-subject units; for state, the whole document counts.
            whole = " | ".join(v for k, v in o.fields.items() if isinstance(v, str) and not k.startswith("ids."))
            if resource_id in whole and any(x and x in whole.lower() for x in mine):
                state = "PRESENT" if treat in ("DELETE", "RETAIN") else "PRESENT_EXPOSED"
                events[(system or o.system_id, "document")].append((o.captured_at, state, o, "named in a document"))
    # Absence by scope only for deletion targets: a capture that covers the system and lacks the row proves the
    # row is gone (4/75 sample citations). For a retained record, flow or backup a missing row proves nothing,
    # because a capture bundle may hold only some subjects' records.
    if system and treat == "DELETE":
        present_in = {(o.source_id, o.container) for o in view.by_resource(resource_id) if o.resource_id == resource_id}
        direct = set(events)
        inferred: dict[tuple, list[tuple]] = defaultdict(list)
        for s in _scopes(view, system):
            key = (system, s.topology or "primary")
            # inference never overrides a direct observation of the same copy (a later capture may be partial)
            if key not in direct and (s.source_id, s.container) not in present_in and scope_covers(s, system, view):
                inferred[key].append((s.captured_at, "ABSENT", s, "scope lacks the row"))
        events.update(inferred)
    out = []
    for key, evs in events.items():
        evs.sort(key=lambda e: (e[0], e[1] != "ABSENT", e[2].obs_id))   # at a tie, presence wins (conservative)
        t, state, o, why = evs[-1]
        out.append(CopyState(key, state, o.obs_id, o.source_id, t, why, INFERRED if o.kind == "scope" else DIRECT))
    return sorted(out, key=lambda c: (str(c.copy), c.obs_id))


def _proof_rank(c: CopyState):
    """Which compliant copy is cited: direct evidence of the row before scope inference, the live primary before
    other copies, then the latest capture."""
    return (c.basis == DIRECT, c.copy[1] == "primary", c.captured_at, c.obs_id)


def _scopes(view: CaseView, system: str) -> list[Observation]:
    return [o for o in view.observations if o.kind == "scope" and (o.system_id in (system, None))]


# --- aggregation ----------------------------------------------------------------------------------

COMPLIANT = {
    "DELETE": {"ABSENT"},
    "ANONYMIZE": {"ANONYMIZED", "ABSENT"},
    "REDACT": {"REDACTED", "ABSENT"},
    "RETAIN": {"PRESENT", "PRESENT_CLEAN", "PRESENT_EXPOSED", "REDACTED", "ANONYMIZED"},
    "DISABLE_FLOW": {"DISABLED", "ABSENT"},
    "BLOCK_RESTORE": {"BLOCKED"},
}
VIOLATION = {
    "DELETE": {"PRESENT", "PRESENT_EXPOSED", "PRESENT_CLEAN", "REDACTED", "ANONYMIZED"},
    "ANONYMIZE": {"PRESENT_EXPOSED"},
    "REDACT": {"PRESENT_EXPOSED"},
    "RETAIN": set(),
    "DISABLE_FLOW": {"ACTIVE"},
    "BLOCK_RESTORE": {"RESTORABLE"},
}


@dataclass(frozen=True)
class Assessment:
    resource_id: str
    system_id: str | None
    category: Category
    treatment: str | None
    verdict: str                 # compliant | violation | unknown
    copies: tuple[CopyState, ...]
    proof: CopyState | None      # the copy whose evidence is cited (violation: the violating copy)
    ops: tuple[str | None, str | None, str | None] = (None, None, None)
    reason: str = ""


def assess(resource_id: str, system_id: str | None, view: CaseView, rules: dict[str, dict],
           subject: Subject | None = None) -> Assessment:
    cat = categorize(resource_id, system_id, view)
    if cat.name is None:
        return Assessment(resource_id, system_id, cat, None, "unknown", (), None, reason=cat.reason)
    treat = treatment(cat.name, rules)
    copies = tuple(copy_states(resource_id, system_id, treat, view, subject))
    ops = TREATMENT_OPS[treat]
    bad = [c for c in copies if c.state in VIOLATION[treat]]
    if bad:
        proof = max(bad, key=lambda c: (c.captured_at, c.obs_id))
        return Assessment(resource_id, system_id, cat, treat, "violation", copies, proof, ops,
                          f"{len(bad)}/{len(copies)} copies violate {treat}")
    if treat == "RETAIN" and copies and all(c.state == "ABSENT" for c in copies):
        return Assessment(resource_id, system_id, cat, treat, "unknown", copies, None, ops,
                          "a record policy requires to retain is absent")
    unknown = [c for c in copies if c.state not in COMPLIANT[treat]]
    if not copies or unknown:
        return Assessment(resource_id, system_id, cat, treat, "unknown", copies, None, ops,
                          "no admissible evidence of its state" if not copies else
                          f"{len(unknown)} copies in an undetermined state")
    proof = max(copies, key=_proof_rank)
    return Assessment(resource_id, system_id, cat, treat, "compliant", copies, proof, ops,
                      f"{len(copies)} copies compliant")
