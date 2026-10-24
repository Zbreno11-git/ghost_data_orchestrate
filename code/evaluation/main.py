"""Score a predicted output.csv against a gold file (default: the public samples).

  python code/evaluation/main.py --pred runs/<id>/output.csv [--gold dataset/sample_output.csv] [--out DIR]
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

CODE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(CODE))

from evaluation.metrics import evaluate, format_table, load_output  # noqa: E402

REPO = CODE.parent


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pred", required=True)
    ap.add_argument("--gold", default=str(REPO / "dataset" / "sample_output.csv"))
    ap.add_argument("--out", default=None, help="directory for metrics.json (default runs/eval/<utc ts>)")
    a = ap.parse_args(argv)
    gold = load_output(Path(a.gold))
    pred = load_output(Path(a.pred))
    pred_for_gold = {k: v for k, v in pred.items() if k in gold}
    m = evaluate(pred_for_gold, gold)
    m["predicted_rows_outside_gold"] = len(set(pred) - set(gold))
    out = Path(a.out) if a.out else REPO / "runs" / "eval" / datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out.mkdir(parents=True, exist_ok=True)
    (out / "metrics.json").write_text(json.dumps({"pred": a.pred, "gold": a.gold, **m}, indent=2) + "\n")
    print(format_table(m))
    print(f"wrote {out / 'metrics.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
