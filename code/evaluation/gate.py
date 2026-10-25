"""The S6 accuracy gate: a frozen baseline vs a candidate, on every set with answers (evaluator side only).

One report per set (the 32 public samples and each custom case) with full official denominators:
- step precision, recall and F1; whole-case and status accuracy; citation accuracy (on matched steps and
  cited-evidence recall) and sequence accuracy (`evaluation.metrics.evaluate`);
- correct steps gained and lost; incorrect steps added (split into "supported by the evidence it cites"
  and "unsupported") and removed; status flips; support-tier moves (`evaluation.compare.compare`);
- mismatch causes before and after (`evaluation.diagnose`; main dataset only).

A supported disagreement with the answers stays its own column: it is never folded into "false positive".
The public samples have been inspected since S0, so they are not a held-out set; the report says so.

Usage: python code/evaluation/gate.py --set samples:<base run>:<cand run> [--set <name>:<base>:<cand> ...]
                                      [--contrib <det run>:<agent run>] --out <md>
A set named `samples` uses dataset/ and sample_output.csv; any other name is a custom case directory under
code/evaluation/custom_cases/<name>.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "code"))

from evaluation.compare import compare  # noqa: E402
from evaluation.metrics import evaluate, load_output  # noqa: E402

KEYS = [("status_accuracy", "status"), ("whole_case_exact", "whole-case"), ("step_precision", "step precision"),
        ("step_recall", "step recall"), ("evidence_accuracy_on_matched", "citation on matched"),
        ("cited_evidence_recall", "cited-evidence recall"), ("sequence_accuracy", "sequence")]


def _paths(name: str) -> tuple[Path, Path]:
    if name == "samples":
        return ROOT / "dataset" / "sample_output.csv", ROOT / "dataset"
    case = ROOT / "code" / "evaluation" / "custom_cases" / name
    return case / "expected_output.csv", case / "dataset"


def _fmt(m: dict, k: str) -> str:
    r = m[k]
    return f"{r['num']}/{r['den']}"


def gate_set(name: str, base: Path, cand: Path) -> tuple[list[str], dict]:
    gold_path, dataset = _paths(name)
    gold = load_output(gold_path)
    mb, mc = evaluate(load_output(base / "output.csv"), gold), evaluate(load_output(cand / "output.csv"), gold)
    rows, s = compare(base, cand, gold_path, dataset)
    sup = Counter(r["support"] for r in rows if r["support"].split("→")[0] != r["support"].split("→")[1])
    L = [f"### {name} (`{base}` → `{cand}`)", "", "| metric | baseline | candidate |", "|---|---|---|"]
    L += [f"| {label} | {_fmt(mb, k)} | {_fmt(mc, k)} |" for k, label in KEYS]
    L.append(f"| step F1 | {mb['step_f1']:.4f} | {mc['step_f1']:.4f} |")
    L += ["", f"- Correct steps: kept {s['correct_kept']}, gained {s['added_in_gold']}, lost {s['correct_removed']}.",
          f"- Incorrect steps: added {s['added_supported_not_in_gold'] + s['added_unsupported']} "
          f"({s['added_supported_not_in_gold']} supported by their cited evidence — a disagreement with the answer, "
          f"listed apart — and {s['added_unsupported']} unsupported); removed {s['incorrect_removed']}.",
          f"- Whole-case gained {s['whole_gained']}, lost {s['whole_lost']}. Status flips {s['flips']} "
          f"(INCOMPLETE→COMPLETE {s['flips_to_complete']}).",
          f"- Support-tier moves: {dict(sup) or 'none'}."]
    changed = [r for r in rows if r["flip"] or r["correct_removed"] or r["added"] or r["incorrect_removed"]
               or r["whole_base"] != r["whole_cand"]]
    for r in changed:
        L.append(f"  - `{r['case_id']}` {r['status']} support {r['support']}: -{','.join(r['removed']) or '∅'} "
                 f"+{','.join(r['added']) or '∅'}")
    return L + [""], {"base": mb, "cand": mc, "compare": s}


def contribution(det: Path, agent: Path) -> list[str]:
    """Rows where the second run's row differs from the first (e.g. deterministic proposal vs the agent's
    published row), with the support moves."""
    d, a = load_output(det / "output.csv"), load_output(agent / "output.csv")
    sd = {json.loads(l)["case_id"]: json.loads(l)["support"] for l in open(det / "decisions.jsonl")}
    sa = {json.loads(l)["case_id"]: json.loads(l)["support"] for l in open(agent / "decisions.jsonl")}
    diff = sorted(c for c in a if a[c] != d.get(c))
    moves = Counter(f"{sd.get(c)}→{sa.get(c)}" for c in a if sd.get(c) != sa.get(c))
    return [f"### Row contribution (`{det}` → `{agent}`)", "",
            f"- Rows that differ: {len(diff)} of {len(a)}" + (f": {', '.join(diff[:20])}" if diff else "."),
            f"- Support moves: {dict(moves) or 'none'}.", ""]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--set", action="append", required=True, help="name:base_run:cand_run")
    ap.add_argument("--contrib", action="append", default=[], help="first_run:second_run (e.g. det:agent), targets")
    ap.add_argument("--causes", help="base_run:cand_run on the samples, for mismatch causes before/after")
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args(argv)
    L = ["# S6 accuracy gate", "", "Full official denominators. The 32 public samples have been inspected since S0: "
         "they measure regressions, they are not a held-out estimate of hidden-target accuracy. Custom cases were "
         "specified independently of the engine (A13).", ""]
    summary = {}
    for spec in a.set:
        name, base, cand = spec.split(":")
        lines, summary[name] = gate_set(name, Path(base), Path(cand))
        L += lines
    for spec in a.contrib:
        det, agent = spec.split(":")
        L += contribution(Path(det), Path(agent))
    if a.causes:
        from evaluation.diagnose import World, diagnose
        b, c = a.causes.split(":")
        world = World(ROOT / "dataset")
        _, cb = diagnose(Path(b), ROOT / "dataset" / "sample_output.csv", world)
        _, cc = diagnose(Path(c), ROOT / "dataset" / "sample_output.csv", world)
        L += ["### Mismatch causes (samples)", "", "| cause | baseline | candidate |", "|---|---|---|"]
        L += [f"| {k} | {cb.get(k, 0)} | {cc.get(k, 0)} |" for k in sorted(set(cb) | set(cc))]
        L.append(f"| **total** | {sum(cb.values())} | {sum(cc.values())} |")
    a.out.write_text("\n".join(L) + "\n")
    a.out.with_suffix(".json").write_text(json.dumps(summary, indent=1, default=str) + "\n")
    print(f"wrote {a.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
