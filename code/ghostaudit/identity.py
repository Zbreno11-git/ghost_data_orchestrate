"""Subject identity as of a case's audit_at: the current snapshot rolled back past later changes, plus history.

Matching is exact on normalized values only (no fuzzy or prefix matching), so a look-alike address belongs to
nobody unless it is literally one of the subject's identifiers. An email that maps to two users is an Ambiguity,
never a guess. Names are kept as weak identifiers: three names are shared by two users in the snapshot.
"""
from __future__ import annotations

import hashlib
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime

from .evidence import normalize_identifier
from .timeutil import parse_ts

FIELDS = ("email", "phone", "email_hash", "name")
WEAK_TYPES = {"name"}


def email_hash(email: str) -> str:
    """sha256 of the lowercased address; holds for 850/850 snapshot rows and 107/107 audited changes (2026-10-24)."""
    return hashlib.sha256(email.strip().lower().encode()).hexdigest()


@dataclass(frozen=True)
class Identifier:
    type: str          # email | email_hash | phone | user_id | name
    norm: str          # normalized value, the index key in EvidenceStore.by_identifier
    raw: str
    role: str          # current | historical (as of audit_at)
    source: str        # user_identities | audit_id | derived:sha256

    @property
    def key(self) -> tuple[str, str]:
        return (self.type, self.norm)

    @property
    def strong(self) -> bool:
        return self.type not in WEAK_TYPES


@dataclass(frozen=True)
class Subject:
    user_id: str
    request_email: str
    request_email_role: str
    identifiers: tuple[Identifier, ...]

    def keys(self, strong_only: bool = False) -> set[tuple[str, str]]:
        return {i.key for i in self.identifiers if i.strong or not strong_only}

    def role_of(self, key: tuple[str, str]) -> str | None:
        roles = {i.role for i in self.identifiers if i.key == key}
        return "current" if "current" in roles else (roles.pop() if roles else None)


@dataclass(frozen=True)
class Ambiguity:
    email: str
    candidates: tuple[str, ...]
    reason: str


class IdentityIndex:
    def __init__(self, identities: list[dict], audit: list[dict]):
        self.snapshot = {r["user_id"]: r for r in identities}
        self.changes: dict[str, list[dict]] = defaultdict(list)
        for a in audit:
            self.changes[a["user_id"]].append({**a, "t": parse_ts(a["event_time"])})
        for rows in self.changes.values():
            rows.sort(key=lambda a: (a["t"], a["audit_id"]))
        # Every user who ever held an address, at any time: the candidate set before the as-of check.
        self.ever: dict[str, set[str]] = defaultdict(set)
        for r in identities:
            self.ever[r["email"].strip().lower()].add(r["user_id"])
        for a in audit:
            if a["field_name"] == "email":
                for v in (a["old_value"], a["new_value"]):
                    self.ever[v.strip().lower()].add(a["user_id"])

    def as_of(self, user_id: str, audit_at: datetime) -> tuple[dict, list[tuple[str, str, str]]]:
        """(field → value at audit_at, [(field, historical value, audit_id)]). Later changes are rolled back."""
        current = {f: self.snapshot[user_id].get(f, "") for f in FIELDS}
        history = []
        for a in reversed(self.changes.get(user_id, [])):
            if a["t"] > audit_at and current.get(a["field_name"]) == a["new_value"]:
                current[a["field_name"]] = a["old_value"]
        for a in self.changes.get(user_id, []):
            if a["t"] <= audit_at:
                for v in (a["old_value"], a["new_value"]):
                    if v and v != current.get(a["field_name"]):
                        history.append((a["field_name"], v, a["audit_id"]))
        return current, history

    def identifiers(self, user_id: str, audit_at: datetime) -> tuple[Identifier, ...]:
        current, history = self.as_of(user_id, audit_at)
        out: dict[tuple[str, str, str], Identifier] = {}

        def add(field_name, value, role, source):
            n = normalize_identifier(field_name, value)
            if n and (n[0], n[1], "current") not in out:
                out[(n[0], n[1], role)] = Identifier(n[0], n[1], value, role, source)
            if n and n[0] == "email":
                h = email_hash(value)
                if ("email_hash", h, "current") not in out:
                    out.setdefault(("email_hash", h, role), Identifier("email_hash", h, h, role, "derived:sha256"))

        add("user_id", user_id, "current", "user_identities")
        for f in FIELDS:
            add(f, current[f], "current", "user_identities")
        for f, v, audit_id in history:
            add(f, v, "historical", audit_id)
        # A value that is current must not also be listed as historical.
        cur = {(k[0], k[1]) for k in out if k[2] == "current"}
        return tuple(sorted((i for k, i in out.items() if k[2] == "current" or (k[0], k[1]) not in cur),
                            key=lambda i: (i.role, i.type, i.norm)))

    def resolve(self, email: str, audit_at: datetime) -> Subject | Ambiguity | None:
        target = normalize_identifier("email", email)
        if not target:
            return None
        matches: dict[str, str] = {}
        for uid in sorted(self.ever.get(target[1], ())):
            for i in self.identifiers(uid, audit_at):
                if i.key == target:
                    matches[uid] = i.role
        if len(matches) > 1:
            return Ambiguity(email, tuple(sorted(matches)), "request email belongs to more than one user")
        if not matches:
            return None
        uid, role = next(iter(matches.items()))
        return Subject(uid, email, role, self.identifiers(uid, audit_at))
