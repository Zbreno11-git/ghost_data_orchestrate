"""Canonical step order, byte-stable JSON, and the atomic output.csv writer."""
from __future__ import annotations

import csv
import json
import os
import tempfile
from pathlib import Path

from .contract import OPERATIONS, OUTPUT_HEADER, PHASES, STEP_KEY_ORDER


def sort_key(step: dict) -> tuple:
    return (PHASES.index(step["phase"]), OPERATIONS[step["operation"]][2], step["system_id"], step["resource_id"])


def canonical_sort(steps: list[dict]) -> list[dict]:
    """Phase → operation rank → system_id → resource_id (D6), then step_no renumbered from 1."""
    ordered = sorted(steps, key=sort_key)
    return [{**s, "step_no": i} for i, s in enumerate(ordered, start=1)]


def dumps(steps: list[dict]) -> str:
    """Fixed key order (contract example) and no whitespace, so output bytes never depend on dict history."""
    return json.dumps([{k: s[k] for k in STEP_KEY_ORDER} for s in steps], separators=(",", ":"), ensure_ascii=False)


def write_output_csv(rows: list[tuple[str, str, list[dict]]], path: Path) -> None:
    """rows = (case_id, status, steps). Lexicographic case_id order (D5); written to a temp file then renamed."""
    path = Path(path)
    ordered = sorted(rows, key=lambda r: r[0])
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=".output.", suffix=".csv")
    try:
        with os.fdopen(fd, "w", newline="", encoding="utf-8") as fh:
            w = csv.writer(fh, lineterminator="\n")
            w.writerow(OUTPUT_HEADER)
            for case_id, status, steps in ordered:
                w.writerow((case_id, status, dumps(steps)))
        os.replace(tmp, path)
    except BaseException:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise
