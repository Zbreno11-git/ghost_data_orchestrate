"""SQLite-compatible snapshot exports, executed in a sandboxed in-memory database.

The authorizer refuses ATTACH/DETACH, extension loading and every PRAGMA except foreign_keys, so an evidence
file can only create and fill tables in its own throwaway connection.
"""
from __future__ import annotations

import json
import re
import sqlite3

from ..evidence import EvidenceStore, Observation, flatten
from ..timeutil import parse_ts
from .coverage import FileCoverage
from .manifest import ManifestEntry

ROLE_SUFFIXES = (("_failover_replica", "failover_replica"), ("_read_replica", "read_replica"),
                 ("_reporting_replica", "reporting_replica"), ("_primary", "primary"))
_DENY = {sqlite3.SQLITE_ATTACH, sqlite3.SQLITE_DETACH}


def _authorizer(action, arg1, arg2, dbname, source):
    if action in _DENY:
        return sqlite3.SQLITE_DENY
    if action == sqlite3.SQLITE_PRAGMA and arg1 != "foreign_keys":
        return sqlite3.SQLITE_DENY
    if action == sqlite3.SQLITE_FUNCTION and arg2 == "load_extension":
        return sqlite3.SQLITE_DENY
    return sqlite3.SQLITE_OK


def sandboxed_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(":memory:")
    conn.enable_load_extension(False)
    conn.set_authorizer(_authorizer)
    return conn


def table_role(table: str) -> str:
    for suffix, role in ROLE_SUFFIXES:
        if table.endswith(suffix):
            return role
    m = re.search(r"_replica_([a-z_]+)$", table)
    if m:
        return f"regional_replica:{m.group(1)}"
    return "scope" if table == "snapshot_scope" else "inventory"


def ingest_sql(entry: ManifestEntry, store: EvidenceStore, cov: FileCoverage) -> None:
    text = entry.path.read_text(encoding="utf-8")
    header = dict(re.findall(r"^-- ([A-Za-z ]+): (.+)$", text, flags=re.M))
    topology = header.get("Database topology", "inventory").strip()
    file_time = parse_ts(header["Captured at"]) if "Captured at" in header else None
    expected_rows = len(re.findall(r"^INSERT INTO ", text, flags=re.M))
    conn = sandboxed_connection()
    conn.executescript(text)
    tables = [r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")]
    loaded = 0
    for table in tables:
        role = table_role(table)
        cur = conn.execute(f'SELECT * FROM "{table}"')
        cols = [d[0] for d in cur.description]
        rows = cur.fetchall()
        loaded += len(rows)
        if role != "scope":
            # The table's existence is itself a fact: absence is only provable inside a table in the snapshot.
            store.add(Observation(
                obs_id=f"{entry.file_id}#table:{table}", source_id=entry.file_id, source_kind="sql", kind="scope",
                captured_at=entry.captured_at, observed_at=file_time, system_id=_system_for(table), resource_id=None,
                container=table, topology=role, fields={"table": table, "row_count": len(rows),
                                                        "columns": ",".join(cols), "file_topology": topology},
                locator=f"table:{table}"))
        for row in rows:
            rec = dict(zip(cols, row))
            if role == "scope":
                store.add(Observation(
                    obs_id=f"{entry.file_id}#scope:{rec['origin_system']}", source_id=entry.file_id,
                    source_kind="sql", kind="scope", captured_at=entry.captured_at,
                    observed_at=parse_ts(rec["captured_at"]), system_id=rec["origin_system"], resource_id=None,
                    container="snapshot_scope", topology="scope", fields=rec, locator=f"scope:{rec['origin_system']}"))
                continue
            fields = {}
            for k, v in rec.items():
                if isinstance(v, str) and v.startswith("{") and k.endswith("_json"):
                    fields.update(flatten(json.loads(v)))
                else:
                    fields[k] = v
            observed = rec.get("updated_at") or rec.get("indexed_at")
            store.add(Observation(
                obs_id=f"{entry.file_id}#{table}:{rec['resource_id']}", source_id=entry.file_id, source_kind="sql",
                kind="record", captured_at=entry.captured_at, observed_at=parse_ts(observed) if observed else file_time,
                system_id=rec.get("origin_system") or _system_for(table), resource_id=rec["resource_id"],
                record_type=rec.get("collection_name"), container=table, topology=role, fields=fields,
                locator=f"{table}:{rec['resource_id']}"))
    conn.close()
    cov.adapter = "sql_snapshot"
    cov.observations = len(store.by_source[entry.file_id])
    cov.lines = expected_rows
    if loaded != expected_rows:
        cov.status = "partial"
        cov.notes.append(f"{expected_rows} INSERT statements but {loaded} rows loaded")
    else:
        cov.status = "processed"
    cov.notes.append(f"topology={topology}; tables={len(tables)}; rows={loaded}")


# Inventory tables name the store, not the service; the mapping is read off the table names in the files.
_TABLE_SYSTEM = {
    "customer_profiles": "account_service", "customer_search_documents": "search_service",
    "customer_analytics_profiles": "analytics_platform", "support_records": "support_platform",
    "customer_exports": "export_service", "connector_subscriptions": "integration_service",
    "backup_restore_entries": "backup_service", "security_audit_records": "security_service",
    "search_documents": "search_service",
}


def _system_for(table: str) -> str | None:
    base = table
    for suffix, _ in ROLE_SUFFIXES:
        if base.endswith(suffix):
            base = base[: -len(suffix)]
    return _TABLE_SYSTEM.get(base)
