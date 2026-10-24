"""JSON evidence, dispatched by document shape (never by file name). An unknown shape fails loudly.

Shapes measured on 2026-10-24 (28 files): snapshot bundles, service resource exports, record-lookup ledgers
(`records` + `record_count`), and single-collection captures (`collection` + `records`).
"""
from __future__ import annotations

import json

from ..evidence import EvidenceStore, Observation, flatten
from ..timeutil import parse_ts
from .coverage import FileCoverage
from .manifest import ManifestEntry

LOOKUP_KEYS = {"record_type", "result", "resource_id", "system"}


def shape_of(doc) -> str | None:
    if not isinstance(doc, dict):
        return None
    if "snapshots" in doc:
        return "snapshot_bundle"
    if "service_exports" in doc:
        return "service_export"
    if "records" in doc and "record_count" in doc:
        return "lookup_ledger"
    if "records" in doc and "collection" in doc:
        return "collection_capture"
    return None


def collection_systems(docs) -> dict[str, str]:
    """collection → data_store, learned from the bundles' own envelopes (used for single-collection captures)."""
    out = {}
    for doc in docs:
        if shape_of(doc) == "snapshot_bundle":
            for s in doc["snapshots"]:
                out.setdefault(s["collection"], s["data_store"])
    return out


def _ts(v):
    return parse_ts(v) if isinstance(v, str) and v else None


class _Adder:
    def __init__(self, entry: ManifestEntry, store: EvidenceStore):
        self.entry, self.store, self.n = entry, store, 0

    def __call__(self, locator: str, **kw):
        self.n += 1
        self.store.add(Observation(obs_id=f"{self.entry.file_id}#{locator}", source_id=self.entry.file_id,
                                   source_kind="json", captured_at=self.entry.captured_at, locator=locator, **kw))


def _lookup(add, loc, r, recorded_by, subject_key):
    subject = {k: r[k] for k in (subject_key,) if k in r}
    add(loc, kind="lookup", observed_at=_ts(r.get("recorded_at")), system_id=r["system"], resource_id=r["resource_id"],
        record_type=r["record_type"], result=r["result"], container=recorded_by,
        wrapper={**subject, "recorded_by": recorded_by})


def ingest_json(entry: ManifestEntry, store: EvidenceStore, cov: FileCoverage, systems: dict[str, str]) -> None:
    doc = json.loads(entry.path.read_text(encoding="utf-8"))
    shape = shape_of(doc)
    cov.adapter = f"json:{shape}"
    if shape is None:
        cov.status = "failed"
        cov.notes.append(f"unknown JSON shape with keys {sorted(doc) if isinstance(doc, dict) else type(doc).__name__}")
        return
    add = _Adder(entry, store)
    if shape == "snapshot_bundle":
        for si, snap in enumerate(doc["snapshots"]):
            ds, coll, t = snap["data_store"], snap["collection"], _ts(snap["captured_at"])
            add(f"snap{si}", kind="scope", observed_at=t, system_id=ds, resource_id=None, container=coll,
                fields={"collection": coll, "record_count": len(snap["records"])})
            for ri, r in enumerate(snap["records"]):
                loc = f"snap{si}:{ri}:{r.get('resource_id')}"
                if LOOKUP_KEYS <= set(r) and ("lookup_value" in r or "subject_reference" in r):
                    _lookup(add, loc, r, ds, "lookup_value" if "lookup_value" in r else "subject_reference")
                else:
                    add(loc, kind="record", observed_at=t, system_id=ds, resource_id=r.get("resource_id"),
                        container=coll, fields=flatten(r))
    elif shape == "service_export":
        t_file = _ts(doc.get("exported_at"))
        for sysid, colls in doc["service_exports"].items():
            for coll, rows in colls.items():
                for ri, r in enumerate(rows):
                    t = _ts(r.get("observed_at")) or t_file
                    base = f"{sysid}/{coll}:{ri}:{r.get('resource_id')}"
                    body = {k: v for k, v in r.items() if k != "observed_at"}
                    if "status_code" in r:  # profile lookups: a 404 is an absence claim, a 200 carries the record
                        if r.get("profile") is None:
                            add(base, kind="lookup", observed_at=t, system_id=sysid, resource_id=r["resource_id"],
                                result="NOT_FOUND", container=coll, wrapper={"status_code": r["status_code"]})
                        else:
                            add(base, kind="record", observed_at=t, system_id=sysid, resource_id=r["resource_id"],
                                container=coll, fields={"resource_id": r["resource_id"], **flatten(r["profile"])},
                                wrapper={"status_code": r["status_code"]})
                    elif "hits" in r:  # search queries: the query is the auditor's input, hits are the records
                        docs = r["hits"].get("documents") or []
                        if not docs:
                            add(base, kind="lookup", observed_at=t, system_id=sysid, resource_id=r.get("resource_id"),
                                result="NOT_FOUND", container=coll, wrapper={"query": r.get("query"), "total": 0})
                        for di, d in enumerate(docs):
                            add(f"{base}:hit{di}", kind="record", observed_at=t, system_id=sysid,
                                resource_id=d.get("resource_id") or r.get("resource_id"), container=coll,
                                fields=flatten(d), wrapper={"query": r.get("query"), "total": r["hits"].get("total")})
                    else:
                        add(base, kind="record", observed_at=t, system_id=sysid, resource_id=r.get("resource_id"),
                            container=coll, fields=flatten(body))
    elif shape == "lookup_ledger":
        origin = doc.get("origin")
        for ri, r in enumerate(doc["records"]):
            _lookup(add, f"rec{ri}:{r['resource_id']}", r, origin, "subject_reference")
        if doc["record_count"] != len(doc["records"]):
            cov.notes.append(f"record_count {doc['record_count']} != {len(doc['records'])} records")
    elif shape == "collection_capture":
        coll = doc["collection"]
        sysid = systems.get(coll)
        if sysid is None:
            cov.notes.append(f"collection {coll!r} has no data_store in any bundle; system_id left empty")
        t = _ts(doc.get("captured_at"))
        add("scope", kind="scope", observed_at=t, system_id=sysid, resource_id=None, container=coll,
            fields={"collection": coll, "record_count": len(doc["records"]), "source": doc.get("source")})
        for ri, r in enumerate(doc["records"]):
            add(f"rec{ri}:{r.get('resource_id')}", kind="record", observed_at=t, system_id=sysid,
                resource_id=r.get("resource_id"), container=coll, fields=flatten(r))
    cov.observations = add.n
    cov.status = "partial" if cov.notes else "processed"
    cov.notes.insert(0, f"shape={shape}")
