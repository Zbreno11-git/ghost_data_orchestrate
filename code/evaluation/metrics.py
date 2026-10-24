"""Evaluation metrics with explicit denominators. Cases are joined by case_id, never by position.

A missing prediction counts as wrong for every case-level metric and contributes 0 predicted steps.
"""
from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

FIELDS = ("step_no", "phase", "system_id", "resource_id", "operation", "state", "evidence_id")


def match_key(s: dict) -> tuple:
    return (s["phase"], s["system_id"], s["resource_id"], s["operation"], s["state"])


def load_output(path: Path) -> dict[str, tuple[str, list[dict]]]:
    """{case_id: (status, steps)}; an unparseable steps_json becomes None steps (counted, not crashed on)."""
    out = {}
    with open(path, newline="", encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            try:
                steps = json.loads(r["steps_json"])
                if not isinstance(steps, list):
                    steps = None
            except json.JSONDecodeError:
                steps = None
            out[r["case_id"]] = (r["deletion_status"], steps)
    return out


def _ratio(n: int, d: int) -> dict:
    return {"num": n, "den": d, "value": (n / d) if d else None}


def evaluate(pred: dict, gold: dict) -> dict:
    n = len(gold)
    status_ok = exact = seq_ok = ops_ok = 0
    tp = pred_steps = gold_steps = 0
    ev_match = ev_aligned = 0
    cited_ok = cited_total = 0
    field_ok = Counter()
    aligned = missing = extra = 0
    confusion = Counter()
    unparsed = absent = 0
    for cid, (g_status, g_steps) in gold.items():
        p_status, p_steps = pred.get(cid, (None, []))
        if cid not in pred:
            absent += 1
        if p_steps is None:
            unparsed += 1
            p_steps = []
        confusion[(g_status, p_status)] += 1
        status_ok += p_status == g_status
        exact += p_status == g_status and p_steps == g_steps
        seq_ok += [match_key(s) for s in p_steps] == [match_key(s) for s in g_steps]
        ops_ok += [s["operation"] for s in p_steps] == [s["operation"] for s in g_steps]
        pred_steps += len(p_steps)
        gold_steps += len(g_steps)
        # Multiset match on (phase, system, resource, operation, state); evidence compared on matched pairs.
        g_by = {}
        for s in g_steps:
            g_by.setdefault(match_key(s), []).append(s)
        for s in p_steps:
            bucket = g_by.get(match_key(s))
            if bucket:
                g = bucket.pop(0)
                tp += 1
                ev_aligned += 1
                ev_match += s["evidence_id"] == g["evidence_id"]
        p_by_key = Counter((match_key(s), s["evidence_id"]) for s in p_steps)
        for g in g_steps:
            if g["evidence_id"]:
                cited_total += 1
                if p_by_key[(match_key(g), g["evidence_id"])] > 0:
                    p_by_key[(match_key(g), g["evidence_id"])] -= 1
                    cited_ok += 1
        # Field accuracy over position-aligned steps; length mismatch counted separately.
        k = min(len(p_steps), len(g_steps))
        aligned += k
        missing += len(g_steps) - k
        extra += len(p_steps) - k
        for a, b in zip(p_steps[:k], g_steps[:k]):
            for f in FIELDS:
                field_ok[f] += a.get(f) == b.get(f)
    precision = _ratio(tp, pred_steps)
    recall = _ratio(tp, gold_steps)
    p, r = precision["value"] or 0.0, recall["value"] or 0.0
    return {
        "cases": n,
        "predicted_rows_missing": absent,
        "predicted_rows_unparsed": unparsed,
        "status_accuracy": _ratio(status_ok, n),
        "whole_case_exact": _ratio(exact, n),
        "step_precision": precision,
        "step_recall": recall,
        "step_f1": (2 * p * r / (p + r)) if (p + r) else 0.0,
        "evidence_accuracy_on_matched": _ratio(ev_match, ev_aligned),
        "cited_evidence_recall": _ratio(cited_ok, cited_total),
        "field_accuracy": {f: _ratio(field_ok[f], aligned) for f in FIELDS},
        "aligned_steps": aligned, "missing_steps": missing, "extra_steps": extra,
        "sequence_accuracy": _ratio(seq_ok, n),
        "ordered_operations_accuracy": _ratio(ops_ok, n),
        "status_confusion": {f"{g}->{p}": c for (g, p), c in sorted(confusion.items(), key=str)},
    }


def format_table(m: dict) -> str:
    def fmt(x):
        if isinstance(x, dict) and "num" in x:
            v = "n/a" if x["value"] is None else f"{x['value']:.4f}"
            return f"{v}  ({x['num']}/{x['den']})"
        return f"{x:.4f}" if isinstance(x, float) else str(x)
    lines = []
    for k, v in m.items():
        if k == "field_accuracy":
            lines += [f"field_accuracy.{f:<12} {fmt(r)}" for f, r in v.items()]
        elif k == "status_confusion":
            lines.append("status_confusion  " + ", ".join(f"{a}: {c}" for a, c in v.items()))
        else:
            lines.append(f"{k:<29} {fmt(v)}")
    return "\n".join(lines)
