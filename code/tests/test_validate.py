"""C1.3: every violation code has a fixture that is rejected for exactly that code."""
import copy
import csv
import json

import pytest

from conftest import DATASET
from ghostaudit.ingest.manifest import evidence_times
from ghostaudit.serialize import dumps
from ghostaudit.timeutil import parse_ts
from ghostaudit.validate import CODES, validate_file, validate_row


@pytest.fixture(scope="module")
def times():
    return evidence_times(DATASET)


def _base(sample_gold, sample_requests, status):
    cid = sorted(c for c, (st, _) in sample_gold.items() if st == status)[0]
    return cid, copy.deepcopy(sample_gold[cid][1]), parse_ts(sample_requests[cid]["audit_at"])


def _renumber(steps):
    return [dict(s, step_no=i) for i, s in enumerate(steps, 1)]


# Each fixture: (base status, mutate(steps) -> (status, steps_json)). Mutations change one rule only.
ROW_FIXTURES = {
    "BAD_STATUS": ("COMPLETE", lambda s: ("DONE", dumps(s))),
    "BAD_JSON": ("COMPLETE", lambda s: ("COMPLETE", dumps(s)[:-1])),
    "NOT_ARRAY": ("COMPLETE", lambda s: ("COMPLETE", json.dumps(s[0]))),
    "KEYSET": ("COMPLETE", lambda s: ("COMPLETE", json.dumps([dict(x, note="x") for x in s]))),
    "EMPTY_FIELD": ("COMPLETE", lambda s: ("COMPLETE", json.dumps([dict(s[0], resource_id="")] + s[1:]))),
    "BAD_PAIR": ("COMPLETE", lambda s: ("COMPLETE", json.dumps([dict(s[0], state="PRESENT" if s[0]["state"] != "PRESENT" else "ABSENT")] + s[1:]))),
    "STEP_NO": ("COMPLETE", lambda s: ("COMPLETE", json.dumps([dict(x, step_no=x["step_no"] + 1) for x in s]))),
    "NOT_CANONICAL": ("INCOMPLETE", lambda s: ("INCOMPLETE", json.dumps(_renumber(list(reversed(s)))))),
    "DUPLICATE_STEP": ("INCOMPLETE", lambda s: ("INCOMPLETE", dumps(_renumber(s[:1] + s)))),
    "NA_WITH_STEPS": ("COMPLETE", lambda s: ("NOT_APPLICABLE", dumps(s))),
    "DECIDED_EMPTY": ("COMPLETE", lambda s: ("COMPLETE", "[]")),
    "COMPLETE_NON_VERIFY": ("INCOMPLETE", lambda s: ("COMPLETE", dumps([x for x in s if x["phase"] != "FINDING"] and
                                                                        _renumber([x for x in s if x["phase"] == "REMEDIATION"])))),
    "INCOMPLETE_NO_FINDING": ("INCOMPLETE", lambda s: ("INCOMPLETE", dumps(_renumber([x for x in s if x["phase"] != "FINDING"])))),
    "FINDING_UNCITED": ("INCOMPLETE", lambda s: ("INCOMPLETE", dumps([dict(s[0], evidence_id="")] + s[1:]))),
    "COMPLETE_VERIFY_UNCITED": ("COMPLETE", lambda s: ("COMPLETE", dumps([dict(s[0], evidence_id="")] + s[1:]))),
    "FUTURE_STEP_CITED": ("INCOMPLETE", lambda s: ("INCOMPLETE", dumps([dict(x, evidence_id=s[0]["evidence_id"]) if x["phase"] == "REMEDIATION" else x for x in s]))),
    "UNKNOWN_EVIDENCE": ("COMPLETE", lambda s: ("COMPLETE", dumps([dict(s[0], evidence_id="evidence_999")] + s[1:]))),
    "EVIDENCE_AFTER_AUDIT": ("COMPLETE", lambda s: ("COMPLETE", dumps([dict(s[0], evidence_id="evidence_50")] + s[1:]))),
}
FILE_CODES = {"HEADER", "DUPLICATE_CASE", "MISSING_CASE", "EXTRA_CASE", "ROW_ORDER"}


def test_every_code_has_a_fixture():
    # Derived denominator: a new code without a fixture fails here.
    assert set(CODES) == set(ROW_FIXTURES) | FILE_CODES


@pytest.mark.parametrize("code", sorted(ROW_FIXTURES))
def test_row_fixture_rejected_for_named_reason(code, sample_gold, sample_requests, times):
    base_status, mutate = ROW_FIXTURES[code]
    cid, steps, audit_at = _base(sample_gold, sample_requests, base_status)
    assert validate_row(cid, base_status, dumps(steps), audit_at, times) == []  # control: the base row is clean
    status, steps_json = mutate(steps)
    got = {v.code for v in validate_row(cid, status, steps_json, audit_at, times)}
    assert got == {code}


def test_admissibility_is_inclusive(times):
    # case_11 cites evidence_03 captured exactly at audit_at (measured in S0): equal is admissible.
    t = times["evidence_03"]
    step = dict(step_no=1, phase="VERIFICATION", system_id="account_service", resource_id="account_1",
                operation="VERIFY_RECORD_ABSENT", state="ABSENT", evidence_id="evidence_03")
    assert validate_row("c", "COMPLETE", dumps([step]), t, times) == []
    from datetime import timedelta
    assert [v.code for v in validate_row("c", "COMPLETE", dumps([step]), t - timedelta(seconds=1), times)] == ["EVIDENCE_AFTER_AUDIT"]


def test_activity_and_audit_ids_are_citable(times):
    assert "activity_01" in times and "audit_01" in times
    assert sum(k.startswith("evidence_") for k in times) == 94


def _write(tmp_path, header, rows):
    p = tmp_path / "o.csv"
    with open(p, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(header)
        w.writerows(rows)
    return p


@pytest.fixture()
def gold_rows(sample_gold):
    return [(c, st, dumps(ss)) for c, (st, ss) in sorted(sample_gold.items())]


H = ("case_id", "deletion_status", "steps_json")


@pytest.mark.parametrize("code,build", [
    ("HEADER", lambda r: (("case_id", "status", "steps_json"), r)),
    ("DUPLICATE_CASE", lambda r: (H, r[:1] + r)),
    ("MISSING_CASE", lambda r: (H, r[1:])),
    ("EXTRA_CASE", lambda r: (H, r + [("case_999", "NOT_APPLICABLE", "[]")])),
    ("ROW_ORDER", lambda r: (H, list(reversed(r)))),
])
def test_file_fixture_rejected_for_named_reason(code, build, gold_rows, sample_requests, times, tmp_path):
    assert validate_file(_write(tmp_path, H, gold_rows), sample_requests, times) == []
    header, rows = build(gold_rows)
    got = {v.code for v in validate_file(_write(tmp_path, header, rows), sample_requests, times)}
    assert got == {code}


def test_sample_output_validates_clean(sample_requests, times):
    assert validate_file(DATASET / "sample_output.csv", sample_requests, times) == []
