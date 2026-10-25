"""S6 C6.8: the case-by-case comparison counts every kind of change, incorrect steps removed included."""
import csv
import json

from conftest import CODE
from evaluation.compare import compare

CASE = CODE / "evaluation" / "custom_cases" / "historical_email_replica"


def _write(run, steps):
    run.mkdir()
    with open(run / "output.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["case_id", "deletion_status", "steps_json"])
        w.writerow(["custom_01", "INCOMPLETE", json.dumps(steps, separators=(",", ":"))])


def test_removing_a_wrong_step_and_keeping_the_right_ones_is_counted_apart(tmp_path):
    gold = json.loads(next(csv.DictReader(open(CASE / "expected_output.csv", encoding="utf-8")))["steps_json"])
    assert len(gold) == 3
    wrong = {"step_no": 4, "phase": "VERIFICATION", "system_id": "account_service", "resource_id": "account_9002",
             "operation": "VERIFY_RECORD_ABSENT", "state": "ABSENT", "evidence_id": ""}
    _write(tmp_path / "base", gold + [wrong])
    _write(tmp_path / "cand", gold)
    rows, s = compare(tmp_path / "base", tmp_path / "cand", CASE / "expected_output.csv", CASE / "dataset")
    assert (s["incorrect_removed"], s["correct_removed"], s["correct_kept"]) == (1, 0, len(gold))
    assert s["whole_gained"] == 1
