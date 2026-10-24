"""Output validator: every rule of the contract that can be checked without knowing the right answer.

Each violation carries one code from CODES, so a test can assert that a malformed row fails for the named reason.
"""
from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from .contract import OUTPUT_HEADER, PHASES, STATUSES, STEP_KEYS, evidence_required, is_legal
from .serialize import canonical_sort
from .timeutil import parse_ts

CODES = (
    # row level
    "BAD_STATUS", "BAD_JSON", "NOT_ARRAY", "KEYSET", "EMPTY_FIELD", "BAD_PAIR", "STEP_NO", "NOT_CANONICAL", "DUPLICATE_STEP",
    "NA_WITH_STEPS", "DECIDED_EMPTY", "COMPLETE_NON_VERIFY", "INCOMPLETE_NO_FINDING",
    "FINDING_UNCITED", "COMPLETE_VERIFY_UNCITED", "FUTURE_STEP_CITED", "UNKNOWN_EVIDENCE", "EVIDENCE_AFTER_AUDIT",
    # file level
    "HEADER", "DUPLICATE_CASE", "MISSING_CASE", "EXTRA_CASE", "ROW_ORDER",
)


@dataclass(frozen=True)
class Violation:
    code: str
    case_id: str
    detail: str

    def __post_init__(self):
        if self.code not in CODES:
            raise ValueError(f"unknown violation code {self.code}")


def validate_row(case_id: str, status: str, steps_json: str, audit_at: datetime | None,
                 evidence_times: dict[str, datetime]) -> list[Violation]:
    v: list[Violation] = []
    add = lambda code, detail: v.append(Violation(code, case_id, detail))
    if status not in STATUSES:
        add("BAD_STATUS", repr(status))  # the step rules depend on the status, so stop here
        return v
    try:
        steps = json.loads(steps_json)
    except (json.JSONDecodeError, TypeError) as exc:
        add("BAD_JSON", str(exc))
        return v
    if not isinstance(steps, list):
        add("NOT_ARRAY", type(steps).__name__)
        return v
    if status == "NOT_APPLICABLE":
        if steps:
            add("NA_WITH_STEPS", f"{len(steps)} steps")
        return v
    if status in ("COMPLETE", "INCOMPLETE") and not steps:
        add("DECIDED_EMPTY", status)
        return v
    shape_ok = True
    for i, s in enumerate(steps, start=1):
        if not isinstance(s, dict) or set(s) != STEP_KEYS:
            add("KEYSET", f"step {i}: {sorted(s) if isinstance(s, dict) else type(s).__name__}")
            shape_ok = False
            continue
        for k in ("phase", "system_id", "resource_id", "operation", "state"):
            if not isinstance(s[k], str) or not s[k].strip():
                add("EMPTY_FIELD", f"step {i}: {k}")
                shape_ok = False
        if not isinstance(s["evidence_id"], str):
            add("EMPTY_FIELD", f"step {i}: evidence_id is not a string")
            shape_ok = False
        elif shape_ok and not is_legal(s["phase"], s["operation"], s["state"]):
            add("BAD_PAIR", f"step {i}: {s['phase']}/{s['operation']}/{s['state']}")
            shape_ok = False
    if not shape_ok:
        return v
    if [s["step_no"] for s in steps] != list(range(1, len(steps) + 1)) or any(
            type(s["step_no"]) is not int for s in steps):
        add("STEP_NO", str([s["step_no"] for s in steps]))
    elif canonical_sort(steps) != steps:
        add("NOT_CANONICAL", "steps are not in phase → operation → system_id → resource_id order")
    keys = [(s["phase"], s["operation"], s["system_id"], s["resource_id"]) for s in steps]
    if len(keys) != len(set(keys)):
        add("DUPLICATE_STEP", str(sorted({k for k in keys if keys.count(k) > 1})))
    phases = {s["phase"] for s in steps}
    if status == "COMPLETE" and phases != {"VERIFICATION"}:
        add("COMPLETE_NON_VERIFY", str(sorted(phases - {"VERIFICATION"})))
    if status == "INCOMPLETE" and "FINDING" not in phases:
        add("INCOMPLETE_NO_FINDING", str(sorted(phases)))
    for s in steps:
        ev, ph, i = s["evidence_id"], s["phase"], s["step_no"]
        if evidence_required(status, ph):
            if ev == "":
                add("FINDING_UNCITED" if ph == "FINDING" else "COMPLETE_VERIFY_UNCITED", f"step {i}")
                continue
        elif ev != "":
            add("FUTURE_STEP_CITED", f"step {i} ({ph}) cites {ev}")
            continue
        if ev == "":
            continue
        if ev not in evidence_times:
            add("UNKNOWN_EVIDENCE", f"step {i}: {ev}")
        elif audit_at is not None and evidence_times[ev] > audit_at:
            add("EVIDENCE_AFTER_AUDIT", f"step {i}: {ev} available {evidence_times[ev].isoformat()} > audit_at")
    return v


def validate_file(path: Path, requests: dict[str, dict], evidence_times: dict[str, datetime]) -> list[Violation]:
    """requests = {case_id: request row with audit_at}. Checks the header, row set, order, and every row."""
    with open(path, newline="", encoding="utf-8") as fh:
        reader = csv.reader(fh)
        header = next(reader, None)
        rows = list(reader)
    v: list[Violation] = []
    if tuple(header or ()) != OUTPUT_HEADER:
        v.append(Violation("HEADER", "", repr(header)))
        return v
    seen: set[str] = set()
    ids = []
    for r in rows:
        if len(r) != 3:
            v.append(Violation("BAD_JSON", r[0] if r else "", f"row has {len(r)} columns"))
            continue
        cid, status, steps = r
        ids.append(cid)
        if cid in seen:
            v.append(Violation("DUPLICATE_CASE", cid, "repeated row"))
            continue
        seen.add(cid)
        if cid not in requests:
            v.append(Violation("EXTRA_CASE", cid, "not in the request file"))
            continue
        v.extend(validate_row(cid, status, steps, parse_ts(requests[cid]["audit_at"]), evidence_times))
    for cid in sorted(set(requests) - seen):
        v.append(Violation("MISSING_CASE", cid, "no output row"))
    if ids != sorted(ids):
        v.append(Violation("ROW_ORDER", "", "rows are not in lexicographic case_id order (D5)"))
    return v
