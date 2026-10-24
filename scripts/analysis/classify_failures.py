"""Classify every non-resolved or invalid case of a run by causal failure class (S5 C5.1).

Reads only the run's decisions.jsonl and the participant evidence manifest (for the source kind of each cited
observation); never reads sample answers. Classes follow the pipeline, so the first one listed is the earliest:
extraction, identity, temporal, ownership, category, state, citation, planning.

Usage: python3 -I scripts/analysis/classify_failures.py runs/<id> [--sample N]
"""
from __future__ import annotations

import csv
import json
import random
import sys
from collections import Counter
from pathlib import Path

ORDER = ["extraction", "identity", "temporal", "ownership", "category", "state", "citation", "planning"]
ROOT = Path(__file__).resolve().parents[2]
TEXT_KINDS = {"png", "pdf"}


def source_kinds() -> dict[str, str]:
    with open(ROOT / "dataset" / "evidence_files.csv", newline="", encoding="utf-8") as fh:
        return {r["file_id"]: Path(r["file_path"]).suffix.lstrip(".").lower() for r in csv.DictReader(fh)}


def classify(row: dict, kinds: dict[str, str]) -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}

    def add(cls: str, why: str) -> None:
        out.setdefault(cls, []).append(why)

    for why in row["reasons"]:
        if why.startswith(("identity:", "intent")):
            add("identity", why)
        elif "no account resource attributed" in why or "primary profile" in why:
            add("ownership", "account not attributable")
        elif why.startswith("weak links used") or "strict ownership attributed nothing" in why:
            add("ownership", why[:80])
        elif "carries identifiers of" in why or "run windows" in why:
            add("ownership", why[:80])
        elif why.startswith("row fails validation"):
            add("planning", why[:80])
    for d in row["decisions"]:
        if d["category"] is None:
            add("category", f"{d['resource_id']}: {d['category_reason']}")
        if d["verdict"] != "unknown":
            continue
        undetermined = [c for c in d["copies"] if c[1] not in (
            "ABSENT", "PRESENT", "PRESENT_EXPOSED", "REDACTED", "ANONYMIZED", "ACTIVE", "DISABLED", "RESTORABLE",
            "BLOCKED")]
        if not d["copies"]:
            add("state", f"{d['resource_id']}: no admissible evidence of its state")
        for c in d["copies"] or []:
            src = (c[2] or "").split("#", 1)[0]
            if c in undetermined or c[1] not in ("ABSENT",):
                if kinds.get(src) in TEXT_KINDS and c[1] not in ("ABSENT", "ACTIVE", "DISABLED", "BLOCKED",
                                                                  "RESTORABLE"):
                    add("extraction", f"{d['resource_id']}: {kinds[src]} copy {c[0]} read as {c[1]} ({src})")
        if d["resource_id"] not in " ".join(sum(out.values(), [])):
            add("state", f"{d['resource_id']}: {d['reason']}")
    return out


def main(argv: list[str]) -> int:
    run = Path(argv[1])
    n = int(argv[argv.index("--sample") + 1]) if "--sample" in argv else 20
    kinds = source_kinds()
    rows = [json.loads(line) for line in open(run / "decisions.jsonl", encoding="utf-8")]
    bad = [r for r in rows if r["support"] != "resolved" or any(x.startswith("row fails validation")
                                                                for x in r["reasons"])]
    primary, multi, by_case = Counter(), Counter(), {}
    for r in bad:
        cls = classify(r, kinds)
        by_case[r["case_id"]] = (r, cls)
        first = next((c for c in ORDER if c in cls), "unclassified")
        primary[first] += 1
        for c in cls:
            multi[c] += 1
    print(f"{len(bad)} non-resolved or invalid cases of {len(rows)} in {run}")
    print("earliest class:", dict(sorted(primary.items(), key=lambda kv: ORDER.index(kv[0])
                                          if kv[0] in ORDER else 99)))
    print("any class:     ", dict(sorted(multi.items(), key=lambda kv: ORDER.index(kv[0]))))
    invalid = [c for c, (r, _) in by_case.items() if any(x.startswith("row fails validation") for x in r["reasons"])]
    print("invalid rows:", ", ".join(sorted(invalid)) or "none")
    for c in sorted(invalid):
        print(f"  {c}: " + " | ".join(f"{k}: {'; '.join(v)}" for k, v in by_case[c][1].items()))
    # Stratified sample for hand review: every class, then weak vs unresolved, fixed seed.
    rng = random.Random(5)
    strata: dict[tuple, list[str]] = {}
    for c, (r, cls) in by_case.items():
        strata.setdefault((next((k for k in ORDER if k in cls), "-"), r["support"]), []).append(c)
    picked: list[str] = []
    while len(picked) < min(n, len(by_case)):
        for key in sorted(strata):
            pool = [c for c in strata[key] if c not in picked]
            if pool and len(picked) < n:
                picked.append(rng.choice(sorted(pool)))
    print(f"\nstratified sample ({len(picked)}):")
    for c in sorted(picked, key=lambda x: int(x.split("_")[1])):
        r, cls = by_case[c]
        print(f"  {c} [{r['support']}/{r['status']}] " + " | ".join(f"{k}: {'; '.join(v)[:140]}"
                                                                     for k, v in cls.items()))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
