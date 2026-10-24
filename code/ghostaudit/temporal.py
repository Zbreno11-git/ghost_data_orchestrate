"""CaseView: the evidence store as it stood at one case's audit_at. Every engine and tool read goes through it.

Admissible means `captured_at <= audit_at` (inclusive). For files, captured_at is the manifest capture time; for
activity and audit rows it is the event time (csv_tables sets both clocks the same), so one rule covers all.
"""
from __future__ import annotations

from datetime import datetime

from .evidence import EvidenceStore, Observation


class CaseView:
    def __init__(self, store: EvidenceStore, audit_at: datetime):
        self._store = store
        self.audit_at = audit_at

    def admissible(self, obs: Observation) -> bool:
        return obs.captured_at <= self.audit_at

    @property
    def observations(self) -> list[Observation]:
        return [o for o in self._store.observations if self.admissible(o)]

    def by_resource(self, resource_id: str) -> list[Observation]:
        return [o for o in self._store.by_resource.get(resource_id, ()) if self.admissible(o)]

    def by_identifier(self, key: tuple[str, str]) -> list[tuple[Observation, str, str]]:
        return [hit for hit in self._store.by_identifier.get(key, ()) if self.admissible(hit[0])]

    def by_source(self, source_id: str) -> list[Observation]:
        return [o for o in self._store.by_source.get(source_id, ()) if self.admissible(o)]

    def by_trace(self, source_id: str, trace: str) -> Observation | None:
        o = self._store.by_trace.get((source_id, trace))
        return o if o is not None and self.admissible(o) else None

    def resources(self) -> list[str]:
        return sorted(r for r in self._store.by_resource if self.by_resource(r))

    def get(self, obs_id: str) -> Observation | None:
        for o in self._store.by_source.get(obs_id.split("#", 1)[0], ()):
            if o.obs_id == obs_id:
                return o if self.admissible(o) else None
        return None
