"""Participant CSV tables. Activity and audit rows also become citable Observations.

The public sample answers are evaluation-only and are deliberately not loaded here.
"""
from __future__ import annotations

from pathlib import Path

from ..evidence import EvidenceStore, Observation
from ..timeutil import parse_ts
from .manifest import read_csv

TABLES = {
    "requests": "deletion_requests.csv",
    "sample_requests": "sample_deletion_requests.csv",
    "identities": "user_identities.csv",
    "audit": "user_audit_log.csv",
    "activity": "system_activity.csv",
    "rules": "deletion_rules.csv",
}


def load_tables(dataset: Path) -> dict[str, list[dict]]:
    dataset = Path(dataset)
    return {name: read_csv(dataset / f) for name, f in TABLES.items() if (dataset / f).exists()}


def add_activity_and_audit(store: EvidenceStore, tables: dict[str, list[dict]]) -> None:
    for r in tables.get("activity", []):
        t = parse_ts(r["event_time"])
        store.add(Observation(
            obs_id=f"{r['activity_id']}#row", source_id=r["activity_id"], source_kind="csv", kind="activity",
            captured_at=t, observed_at=t, system_id=r["target_system"] or r["source_system"],
            resource_id=r["resource_id"] or None, record_type=r["event_type"], result=r["reported_result"] or None,
            container="system_activity", fields={k: r[k] for k in ("event_type", "source_system", "target_system",
                                                                   "reported_result", "details")},
            locator="row"))
    for r in tables.get("audit", []):
        t = parse_ts(r["event_time"])
        store.add(Observation(
            obs_id=f"{r['audit_id']}#row", source_id=r["audit_id"], source_kind="csv", kind="audit",
            captured_at=t, observed_at=t, system_id=None, resource_id=None, record_type=r["field_name"],
            container="user_audit_log",
            fields={"user_id": r["user_id"], "field_name": r["field_name"], f"old_{r['field_name']}": r["old_value"],
                    f"new_{r['field_name']}": r["new_value"]},
            locator="row"))
