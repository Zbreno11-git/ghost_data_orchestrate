import csv
import random

from conftest import DATASET
from ghostaudit.contract import OPERATIONS, PHASES, STATES, STEP_KEYS, is_legal
from ghostaudit.serialize import canonical_sort, dumps, write_output_csv


def test_contract_table_shape():
    # Derived from the table itself: 15 operations, every phase used, states drawn from the table.
    assert len(OPERATIONS) == 15
    assert {p for p, _, _ in OPERATIONS.values()} == set(PHASES)
    assert len(STATES) == 7
    ranks = [r for _, _, r in OPERATIONS.values()]
    assert ranks == sorted(ranks) == list(range(15))


def test_every_sample_step_is_legal(sample_gold):
    steps = [s for _, ss in sample_gold.values() for s in ss]
    assert len(steps) == 193
    illegal = [s for s in steps if not is_legal(s["phase"], s["operation"], s["state"])]
    assert illegal == []
    assert all(set(s) == STEP_KEYS for s in steps)


def test_canonical_sort_reproduces_every_sample_array(sample_gold):
    rng = random.Random(7)
    same = 0
    for case_id, (_, steps) in sample_gold.items():
        shuffled = [dict(s, step_no=0) for s in steps]
        rng.shuffle(shuffled)
        if canonical_sort(shuffled) == steps:
            same += 1
    assert same == 32


def _rows():
    with open(DATASET / "sample_output.csv", newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def test_dumps_round_trips_every_sample_row():
    import json
    rows = _rows()
    assert sum(json.loads(dumps(json.loads(r["steps_json"]))) == json.loads(r["steps_json"]) for r in rows) == 32
    # Rows already in contract key order are reproduced byte for byte (24 of 32 in the sample file).
    assert sum(dumps(json.loads(r["steps_json"])) == r["steps_json"] for r in rows) == 24


def test_dumps_ignores_input_key_order():
    a = dict(step_no=1, phase="FINDING", system_id="s", resource_id="r", operation="REPORT_REMAINING_RECORD",
             state="PRESENT", evidence_id="e")
    b = dict(reversed(list(a.items())))
    assert dumps([a]) == dumps([b]) == ('[{"step_no":1,"phase":"FINDING","system_id":"s","resource_id":"r",'
                                        '"operation":"REPORT_REMAINING_RECORD","state":"PRESENT","evidence_id":"e"}]')


def test_write_output_csv_round_trips_samples(sample_gold, tmp_path):
    import json
    rows = [(cid, st, steps) for cid, (st, steps) in reversed(list(sample_gold.items()))]
    out = tmp_path / "out.csv"
    write_output_csv(rows, out)
    with open(out, newline="", encoding="utf-8") as fh:
        back = list(csv.DictReader(fh))
    assert [r["case_id"] for r in back] == sorted(sample_gold)
    assert {r["case_id"]: (r["deletion_status"], json.loads(r["steps_json"])) for r in back} == sample_gold
    assert out.read_bytes().count(b"\r") == 0


def test_rows_are_lexicographic_not_numeric(tmp_path):
    out = tmp_path / "o.csv"
    write_output_csv([("case_100", "NOT_APPLICABLE", []), ("case_33", "NOT_APPLICABLE", []),
                      ("case_4", "NOT_APPLICABLE", [])], out)
    assert [l.split(",")[0] for l in out.read_text().splitlines()[1:]] == ["case_100", "case_33", "case_4"]


def test_sort_tiebreak_literal():
    # Hand-written expectation: same phase+op ordered by system_id then resource_id.
    mk = lambda sys, res, op="DELETE_RECORD", ph="REMEDIATION", st="ABSENT": dict(
        step_no=0, phase=ph, system_id=sys, resource_id=res, operation=op, state=st, evidence_id="")
    got = canonical_sort([mk("search_service", "search_2"), mk("account_service", "account_9"),
                          mk("search_service", "search_10"), mk("x", "y", "DISABLE_DATA_FLOW", st="DISABLED")])
    assert [(s["step_no"], s["resource_id"]) for s in got] == [(1, "y"), (2, "account_9"), (3, "search_10"), (4, "search_2")]
