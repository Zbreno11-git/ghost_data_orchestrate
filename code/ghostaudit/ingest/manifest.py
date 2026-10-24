"""evidence_files.csv: file_id → path (confined to dataset/evidence) and capture time."""
from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from ..timeutil import parse_ts


@dataclass(frozen=True)
class ManifestEntry:
    file_id: str
    rel_path: str
    path: Path
    origin: str
    captured_at: datetime

    @property
    def kind(self) -> str:
        return self.path.suffix.lower().lstrip(".")


def read_csv(path: Path) -> list[dict]:
    with open(path, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def load_manifest(dataset: Path) -> list[ManifestEntry]:
    dataset = Path(dataset).resolve()
    root = (dataset / "evidence").resolve()
    out = []
    for r in read_csv(dataset / "evidence_files.csv"):
        p = (dataset / r["file_path"]).resolve()
        if root not in p.parents:
            raise ValueError(f"{r['file_id']}: path escapes dataset/evidence: {r['file_path']!r}")
        out.append(ManifestEntry(r["file_id"], r["file_path"], p, r["origin"], parse_ts(r["captured_at"])))
    ids = [e.file_id for e in out]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate file_id in evidence_files.csv")
    return out


def evidence_times(dataset: Path) -> dict[str, datetime]:
    """Every citable id → the time it became available: file capture, activity or audit event time."""
    dataset = Path(dataset)
    times = {e.file_id: e.captured_at for e in load_manifest(dataset)}
    for name, key in (("system_activity.csv", "activity_id"), ("user_audit_log.csv", "audit_id")):
        p = dataset / name
        if p.exists():
            for r in read_csv(p):
                times[r[key]] = parse_ts(r["event_time"])
    return times
