"""CaseView: the evidence store as it stood at one case's audit_at. Every engine and tool read goes through it.

Two clocks per observation (both kept, with their provenance in ingest):
- `captured_at`: when the artifact was captured, which is the manifest time for files. For activity and audit
  rows it is the event time.
- `observed_at`: when the event or record inside the artifact happened, if the source states one:
  - SQL row: `captured_at`/`observed_at` column, else the snapshot's file time;
  - log line or trace: the line's `ts`;
  - JSON lookup: `recorded_at`; JSON bundle record: its `observed_at`, else the bundle time;
  - PDF table row: its timestamp column;
  - txt record: the file time;
  - activity/audit row: the event time;
  - screen panels and PDF free text: none (a screen shows the state at its capture).

Time policy (S7 C7.1T, `[time] historical_snapshots`, set once on the store so identity, ownership, state, tools
and citations all read the same semantics):
- `manifest` (the A26 baseline): as below;
- `snapshot_capture`: additionally, an observation from a snapshot envelope with its own explicit capture time
  (`snapshot_dated`, ≤ its export's capture) is readable when that capture time is ≤ audit_at, even inside an
  export captured later. Nothing else is: a later record's or line's claimed time, a lookup's `recorded_at`, or a
  screen never qualifies. It is readable, never citable: `citable()` keeps AGENTS §6.6 (an evidence item captured
  after audit_at is never cited).

Admissible (S5 C5.3b) means `captured_at <= audit_at` (AGENTS §6.6: never an item captured after audit_at, even
if it holds older timestamps) **and** `event_time <= audit_at` (an observation of something after the cutoff
is rejected even inside an admissible artifact). Inclusive at both ends. An observation timed after its own
artifact's capture is contradictory; it is admitted only for cutoffs after its observation time, which is what
this rule already gives (2 such observations in the data, measured 2026-10-24 ~22:02 UTC).
"""
from __future__ import annotations

from datetime import datetime

from .evidence import EvidenceStore, Observation


def event_time(obs: Observation) -> datetime:
    """The time an observation describes: its own observation time, or its capture time when the source states
    none (screens, PDF free text), the only justified fallback. Used to order states within one copy."""
    return obs.observed_at or obs.captured_at


def time_basis(obs: Observation) -> str:
    return "observed" if obs.observed_at is not None else "captured"


class CaseView:
    def __init__(self, store: EvidenceStore, audit_at: datetime):
        self._store = store
        self.audit_at = audit_at
        self.policy = getattr(store, "time_policy", "manifest")
        if self.policy not in ("manifest", "snapshot_capture"):
            raise ValueError(f"unknown time policy {self.policy!r}")

    def admissible(self, obs: Observation) -> bool:
        if event_time(obs) > self.audit_at:
            return False
        return obs.captured_at <= self.audit_at or (self.policy == "snapshot_capture" and obs.snapshot_dated)

    def citable(self, obs_id: str) -> bool:
        """The evidence item behind an admissible observation may be cited: its artifact was captured by audit_at."""
        for o in self._store.by_source.get(obs_id.split("#", 1)[0], ()):
            if o.obs_id == obs_id:
                return o.captured_at <= self.audit_at
        return False

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
