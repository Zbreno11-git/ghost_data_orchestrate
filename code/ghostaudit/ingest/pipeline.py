"""ingest_all: every manifest file through its adapter, plus the CSV tables, into one EvidenceStore."""
from __future__ import annotations

import json
from pathlib import Path

from ..config import load_config
from ..evidence import EvidenceStore, resource_prefixes
from .coverage import Coverage, FileCoverage
from .csv_tables import add_activity_and_audit, load_tables
from .images import ingest_png
from .json_records import collection_systems, ingest_json
from .logs import ingest_log
from .manifest import load_manifest
from .pdf_text import ingest_pdf, ingest_txt
from .sql_snapshot import ingest_sql


def ingest_all(dataset: Path, allow_paid: bool = False, cfg: dict | None = None) -> tuple[EvidenceStore, Coverage]:
    cfg = cfg or load_config()
    dataset = Path(dataset)
    tables = load_tables(dataset)
    # Free-text resource mentions are indexed by the prefixes the global activity stream actually uses.
    store, coverage = EvidenceStore(resource_prefixes(r["resource_id"] for r in tables.get("activity", []))), Coverage()
    coverage.tables = {k: len(v) for k, v in tables.items()}
    add_activity_and_audit(store, tables)
    entries = load_manifest(dataset)
    systems = collection_systems(json.loads(e.path.read_text(encoding="utf-8")) for e in entries
                                 if e.kind == "json" and e.path.exists())
    for e in entries:
        cov = FileCoverage(e.file_id, e.rel_path, e.kind)
        coverage.files.append(cov)
        if not e.path.exists():
            cov.notes.append("file listed in the manifest is missing")
            continue
        try:
            if e.kind == "sql":
                ingest_sql(e, store, cov)
            elif e.kind == "json":
                ingest_json(e, store, cov, systems)
            elif e.kind == "log":
                ingest_log(e, store, cov)
            elif e.kind == "pdf":
                ingest_pdf(e, store, cov)
            elif e.kind == "txt":
                ingest_txt(e, store, cov)
            elif e.kind == "png":
                ingest_png(e, store, cov, cfg, allow_paid)
            else:
                cov.notes.append(f"no adapter for .{e.kind}")
        except Exception as exc:  # one bad file must not hide the others; it is reported as failed
            cov.status = "failed"
            cov.notes.append(f"{type(exc).__name__}: {exc}")
    return store, coverage


def write_coverage(coverage: Coverage, out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    rows = sorted(coverage.files, key=lambda c: (c.kind, c.file_id))
    status = {s: sum(c.status == s for c in rows) for s in ("processed", "partial", "failed")}
    lines = ["# Ingestion coverage", "",
             f"{len(rows)} manifest files: {status['processed']} processed, {status['partial']} partial, "
             f"{status['failed']} failed. Tables: " + ", ".join(f"{k}={v}" for k, v in coverage.tables.items()), "",
             "| file_id | kind | adapter | status | observations | lines | unparsed | notes |",
             "|---|---|---|---|---|---|---|---|"]
    for c in rows:
        notes = "; ".join(c.notes).replace("|", "\\|")
        lines.append(f"| {c.file_id} | {c.kind} | {c.adapter} | {c.status} | {c.observations} | {c.lines} | "
                     f"{c.unparsed} | {notes} |")
    md = out_dir / "coverage.md"
    md.write_text("\n".join(lines) + "\n")
    (out_dir / "coverage.json").write_text(json.dumps(
        {"tables": coverage.tables, "files": [c.__dict__ for c in rows]}, indent=1) + "\n")
    return md
