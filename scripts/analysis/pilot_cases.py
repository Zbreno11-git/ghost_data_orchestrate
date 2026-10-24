"""Pick the S5 pilot: 30 target cases stratified by support level and earliest failure class (fixed seed).

Reads only a run's decisions.jsonl. Usage: python3 -I scripts/analysis/pilot_cases.py runs/<id> [n]
"""
import json
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from classify_failures import ORDER, classify, source_kinds  # noqa: E402

QUOTA = {"unresolved": 14, "weak": 8, "resolved": 8}     # authorized deletions only (NA rows skip the agent)


def main(argv):
    rows = [json.loads(l) for l in open(Path(argv[1]) / "decisions.jsonl", encoding="utf-8")]
    n = int(argv[2]) if len(argv) > 2 else 30
    kinds, rng, picked = source_kinds(), random.Random(20261024), []
    for support, quota in QUOTA.items():
        pool = [r for r in rows if r["support"] == support and r["status"] != "NOT_APPLICABLE"]
        by_class = {}
        for r in pool:
            cls = classify(r, kinds)
            by_class.setdefault(next((c for c in ORDER if c in cls), "-"), []).append(r["case_id"])
        take = []
        while len(take) < min(quota, len(pool)):           # round-robin over classes, random within each
            for c in sorted(by_class):
                left = sorted(set(by_class[c]) - set(take))
                if left and len(take) < quota:
                    take.append(rng.choice(left))
        picked += take
    picked = sorted(picked[:n], key=lambda c: int(c.split("_")[1]))
    print(",".join(picked))


if __name__ == "__main__":
    main(sys.argv)
