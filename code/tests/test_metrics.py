"""C1.4: metric denominators are defined and the join is by case_id."""
import copy

from evaluation.metrics import evaluate


def _values(m):
    keys = ["status_accuracy", "whole_case_exact", "step_precision", "step_recall", "evidence_accuracy_on_matched",
            "cited_evidence_recall", "sequence_accuracy", "ordered_operations_accuracy"]
    return {k: m[k]["value"] for k in keys} | {f"field.{f}": r["value"] for f, r in m["field_accuracy"].items()}


def test_gold_against_itself_is_perfect(sample_gold):
    m = evaluate(sample_gold, sample_gold)
    assert set(_values(m).values()) == {1.0}
    assert m["step_f1"] == 1.0
    assert (m["cases"], m["step_recall"]["den"], m["cited_evidence_recall"]["den"]) == (32, 193, 75)


def test_empty_prediction_scores_zero_with_counts(sample_gold):
    m = evaluate({}, sample_gold)
    assert m["status_accuracy"] == {"num": 0, "den": 32, "value": 0.0}
    assert m["step_recall"] == {"num": 0, "den": 193, "value": 0.0}
    assert m["step_precision"]["den"] == 0 and m["step_f1"] == 0.0
    assert m["predicted_rows_missing"] == 32 and m["missing_steps"] == 193


def test_join_is_by_case_id_not_position(sample_gold):
    shuffled = dict(reversed(list(sample_gold.items())))
    assert evaluate(shuffled, sample_gold) == evaluate(sample_gold, sample_gold)


def test_one_swapped_evidence_id_literal(sample_gold):
    pred = copy.deepcopy(sample_gold)
    cid = next(c for c, (_, ss) in sorted(pred.items()) if ss and ss[0]["evidence_id"])
    pred[cid][1][0]["evidence_id"] = "evidence_00"
    m = evaluate(pred, sample_gold)
    assert m["cited_evidence_recall"]["num"] == 74 and m["cited_evidence_recall"]["den"] == 75
    assert m["evidence_accuracy_on_matched"]["num"] == 192
    assert m["step_recall"]["value"] == 1.0 and m["status_accuracy"]["value"] == 1.0
    assert m["whole_case_exact"]["num"] == 31


def test_reordered_steps_hit_sequence_not_recall(sample_gold):
    pred = copy.deepcopy(sample_gold)
    cid = next(c for c, (_, ss) in sorted(pred.items()) if len(ss) >= 2)
    pred[cid][1].reverse()
    m = evaluate(pred, sample_gold)
    assert m["step_recall"]["value"] == 1.0
    assert m["sequence_accuracy"]["num"] == 31
