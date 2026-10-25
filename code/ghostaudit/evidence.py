"""Observations: every fact extracted from participant data, with provenance, plus exact-match indexes.

An Observation never says whether a deletion is complete; it records what a source showed and where.
Business fields (what the record itself contains) are kept apart from wrapper fields (how an auditor or
collector located it: lookup keys, ledger subject references). FR-11: an anonymous record must not be blamed
for an identifier that lives only in its wrapper.
"""
from __future__ import annotations

import re
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime

EMAIL_RE = re.compile(r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}")
HASH_RE = re.compile(r"^[0-9a-fA-F]{64}$")
USER_RE = re.compile(r"^user_\d+$")
PHONE_RE = re.compile(r"^\+?[\d\s().\-]{7,}$")
RESOURCE_ID_RE = re.compile(r"^([a-z]+(?:_[a-z]+)*)_\d+$")


def resource_prefixes(resource_ids) -> list[str]:
    """Resource-id prefixes (`account`, `email_delivery`, ...) derived from the data, never hand-listed."""
    return sorted({m.group(1) for r in resource_ids if r and (m := RESOURCE_ID_RE.match(r))})


def resource_regex(prefixes) -> re.Pattern:
    """Matches `<prefix>_<digits>` mentions in free text. No prefixes → matches nothing (loud in the coverage gates)."""
    if not prefixes:
        return re.compile(r"(?!x)x")
    alt = "|".join(re.escape(p) for p in sorted(prefixes, key=len, reverse=True))
    return re.compile(rf"\b(?:{alt})_\d+\b")
NAME_KEYS = {"name", "full_name", "display_name", "requester_name", "customer_name"}

KINDS = ("record", "lookup", "scope", "activity", "audit", "text")


@dataclass(frozen=True, eq=False)
class Observation:
    obs_id: str                 # unique and stable: f"{source_id}#{locator}"
    source_id: str              # the citable id: file_id, activity_id or audit_id
    source_kind: str            # sql | json | log | txt | pdf | png | csv
    kind: str                   # one of KINDS
    captured_at: datetime       # when the source became available (admissibility clock)
    observed_at: datetime | None  # the record/line's own time, if it states one
    system_id: str | None
    resource_id: str | None
    record_type: str | None = None
    result: str | None = None   # FOUND / NOT_FOUND for lookups; None for records (present by construction)
    container: str | None = None  # table / collection / data store as named by the source
    topology: str | None = None   # primary / read_replica / failover_replica / regional_replica:<r> / ...
    fields: dict = field(default_factory=dict)
    wrapper: dict = field(default_factory=dict)
    locator: str = ""
    # S7 C7.1T: observed_at is a snapshot envelope's own explicit `captured_at` (a historical capture carried
    # inside an export), as opposed to a record's or line's claimed time. Only these can be read under the
    # `snapshot_capture` time policy; never serialized into tool output.
    snapshot_dated: bool = False

    def __post_init__(self):
        if self.kind not in KINDS:
            raise ValueError(f"unknown observation kind {self.kind}")


def normalize_identifier(key: str, value) -> tuple[str, str] | None:
    """(type, normalized) for an identifier-looking value, else None. Raw values stay in the Observation."""
    if not isinstance(value, str):
        return None
    v = value.strip()
    if not v:
        return None
    if EMAIL_RE.fullmatch(v):
        return ("email", v.lower())
    if HASH_RE.match(v):
        return ("email_hash", v.lower())
    if USER_RE.match(v):
        return ("user_id", v)
    k = key.lower()
    if "phone" in k and PHONE_RE.match(v):
        return ("phone", re.sub(r"\D", "", v))
    if k in NAME_KEYS:
        return ("name", " ".join(v.casefold().split()))
    return None


def identifiers_in(key: str, value) -> list[tuple[str, str]]:
    """Identifiers in one field value, including emails embedded in free text."""
    one = normalize_identifier(key, value)
    if one:
        return [one]
    if isinstance(value, str):
        return [("email", m.lower()) for m in EMAIL_RE.findall(value)]
    return []


def flatten(obj, prefix: str = "") -> dict:
    """Nested dicts/lists → dotted keys (`document.email`, `recent_activity.0.event`); empty containers kept."""
    if isinstance(obj, dict):
        items = obj.items()
    elif isinstance(obj, list):
        items = enumerate(obj)
    else:
        return {prefix: obj}
    out = {}
    for k, v in items:
        out.update(flatten(v, f"{prefix}.{k}" if prefix else str(k)))
    if not out and prefix:
        out[prefix] = obj
    return out


class EvidenceStore:
    def __init__(self, resource_prefixes=()):
        self.resource_prefixes = list(resource_prefixes)
        self.resource_re = resource_regex(self.resource_prefixes)
        self.observations: list[Observation] = []
        self._ids: set[str] = set()
        self.by_resource: dict[str, list[Observation]] = defaultdict(list)
        self.by_identifier: dict[tuple[str, str], list[tuple[Observation, str, str]]] = defaultdict(list)
        self.by_source: dict[str, list[Observation]] = defaultdict(list)
        self.by_trace: dict[tuple[str, str], Observation] = {}
        self.time_policy = "manifest"     # [time] historical_snapshots, set by the runner (S7 C7.1T)

    def __len__(self):
        return len(self.observations)

    def add(self, obs: Observation) -> None:
        if obs.obs_id in self._ids:
            raise ValueError(f"duplicate observation id {obs.obs_id}")
        self._ids.add(obs.obs_id)
        self.observations.append(obs)
        self.by_source[obs.source_id].append(obs)
        if obs.resource_id:
            self.by_resource[obs.resource_id].append(obs)
        for role, d in (("field", obs.fields), ("wrapper", obs.wrapper)):
            for k, v in d.items():
                for ident in identifiers_in(k.rsplit(".", 1)[-1], v):
                    self.by_identifier[ident].append((obs, role, k))
                if isinstance(v, str) and role == "field":
                    for res in self.resource_re.findall(v):
                        if res != obs.resource_id:
                            self.by_resource[res].append(obs)
        if obs.locator.startswith("trace:"):
            self.by_trace[(obs.source_id, obs.locator[6:])] = obs
