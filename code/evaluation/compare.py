"""Case-by-case comparison of two runs against the answers (S5 C5.5; evaluator side, never the prediction path).

For every case: whole-case match before/after, correct steps kept or removed, steps added (split into "in the
answer", "not in the answer but supported by its cited evidence" and "not in the answer and unsupported"),
citation correctness on matched steps, status flips (INCOMPLETE→COMPLETE is flagged), support moves and agent
cost. Totals keep the full official denominators: every gold step counts, every case counts.

Usage: python code/evaluation/compare.py --base runs/<a> --cand runs/<b> [--gold dataset/sample_output.csv]
                                          [--dataset dataset] [--out runs/<b>/compare.md]
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "code"))

from evaluation.metrics import FIELDS, load_output, match_key  # noqa: E402


def _exact(a: tuple, b: tuple) -> bool:
    return a[0] == b[0] and a[1] is not None and b[1] is not None and \
        [{f: s[f] for f in FIELDS} for s in a[1]] == [{f: s[f] for f in FIELDS} for s in b[1]]


def _support(run: Path) -> dict[str, str]:
    f = run / "decisions.jsonl"
    return {json.loads(l)["case_id"]: json.loads(l)["support"] for l in open(f)} if f.exists() else {}


def _cost(run: Path) -> dict[str, float]:
    out = {}
    for f in (run / "cases").glob("*.json") if (run / "cases").exists() else ():
        a = json.loads(f.read_text()).get("agent") or {}
        out[f.stem] = float(a.get("cost_usd") or 0.0)
    return out


class Evidence:
    """Is a predicted step grounded in the participant evidence it cites? Loads the store once (participant data)."""

    def __init__(self, dataset: Path):
        from ghostaudit.ingest.pipeline import ingest_all
        self.store = ingest_all(dataset, allow_paid=False)[0]

    def cited(self, s: dict) -> bool:
        obs = self.store.by_source.get(s["evidence_id"], [])
        return any(o.resource_id == s["resource_id"] for o in obs) or \
            any(s["resource_id"] in self.store.by_resource and o in self.store.by_resource[s["resource_id"]]
                for o in obs) or \
            (s["operation"] == "VERIFY_RECORD_ABSENT" and any(o.kind == "scope" and o.system_id == s["system_id"]
                                                            for o in obs))

    def supported(self, s: dict, steps: list[dict]) -> bool:
        if s["evidence_id"]:
            return self.cited(s)
        # a future step is grounded by the cited finding on the same resource in the same row
        finds = [f for f in steps if f["phase"] == "FINDING" and f["resource_id"] == s["resource_id"]]
        return bool(finds) and all(self.cited(f) for f in finds)


def compare(base: Path, cand: Path, gold_path: Path, dataset: Path) -> tuple[list[dict], dict]:
    gold, b, c = load_output(gold_path), load_output(base / "output.csv"), load_output(cand / "output.csv")
    sb, sc, cost = _support(base), _support(cand), _cost(cand)
    ev = Evidence(dataset)
    rows, tot = [], Counter()
    for cid in sorted(gold):
        g = gold[cid]
        pb, pc = b.get(cid, (None, None)), c.get(cid, (None, None))
        gk = {match_key(s): s for s in g[1]}
        bk = {match_key(s): s for s in pb[1] or []}
        ck = {match_key(s): s for s in pc[1] or []}
        removed = [k for k in bk if k in gk and k not in ck]
        wrong_removed = [k for k in bk if k not in gk and k not in ck]
        added = [k for k in ck if k not in bk]
        add_gold = [k for k in added if k in gk]
        add_supported = [k for k in added if k not in gk and ev.supported(ck[k], pc[1])]
        add_unsupported = [k for k in added if k not in gk and k not in add_supported]
        cite_ok = sum(1 for k in ck if k in gk and ck[k]["evidence_id"] == gk[k]["evidence_id"])
        row = {"case_id": cid, "whole_base": _exact(pb, g), "whole_cand": _exact(pc, g),
               "status": f"{pb[0]}→{pc[0]}", "flip": pb[0] != pc[0],
               "flip_to_complete": pb[0] == "INCOMPLETE" and pc[0] == "COMPLETE",
               "correct_kept": sum(1 for k in ck if k in gk and k in bk), "correct_removed": len(removed),
               "incorrect_removed": len(wrong_removed),
               "added_in_gold": len(add_gold), "added_supported_not_in_gold": len(add_supported),
               "added_unsupported": len(add_unsupported), "matched_cand": sum(1 for k in ck if k in gk),
               "citation_ok_cand": cite_ok, "support": f"{sb.get(cid, '-')}→{sc.get(cid, '-')}",
               "cost_usd": round(cost.get(cid, 0.0), 6),
               "removed": [k[2] + ":" + k[3] for k in removed],
               "added": [k[2] + ":" + k[3] for k in added]}
        rows.append(row)
        for k in ("correct_kept", "correct_removed", "incorrect_removed", "added_in_gold", "added_supported_not_in_gold",
                  "added_unsupported", "matched_cand", "citation_ok_cand"):
            tot[k] += row[k]
        tot["whole_base"] += row["whole_base"]
        tot["whole_cand"] += row["whole_cand"]
        tot["flips"] += row["flip"]
        tot["flips_to_complete"] += row["flip_to_complete"]
        tot["cost_usd_x1e6"] += round(row["cost_usd"] * 1e6)
    gained = sum(1 for r in rows if r["whole_cand"] and not r["whole_base"])
    lost = sum(1 for r in rows if r["whole_base"] and not r["whole_cand"])
    summary = {"cases": len(gold), "gold_steps": sum(len(g[1]) for g in gold.values()),
               "predicted_steps_base": sum(len(v[1] or []) for v in b.values() if v),
               "predicted_steps_cand": sum(len(v[1] or []) for v in c.values() if v),
               **dict(tot), "whole_gained": gained, "whole_lost": lost,
               "cost_usd": tot["cost_usd_x1e6"] / 1e6,
               "cost_per_whole_gained": (tot["cost_usd_x1e6"] / 1e6 / gained) if gained else None}
    return rows, summary


def to_markdown(rows: list[dict], s: dict, base: Path, cand: Path) -> str:
    out = [f"# Comparison `{base}` → `{cand}`", "",
           f"Cases {s['cases']}, gold steps {s['gold_steps']} (full official denominators).", "",
           "| metric | base | cand |", "|---|---|---|",
           f"| whole-case exact | {s['whole_base']}/{s['cases']} | {s['whole_cand']}/{s['cases']} |",
           f"| predicted steps | {s['predicted_steps_base']} | {s['predicted_steps_cand']} |",
           f"| matched steps (cand) | | {s['matched_cand']}/{s['gold_steps']} |",
           f"| citation correct on matched (cand) | | {s['citation_ok_cand']}/{s['matched_cand']} |", "",
           f"Whole-case gained {s['whole_gained']}, lost {s['whole_lost']}. Correct steps kept {s['correct_kept']}, "
           f"**removed {s['correct_removed']}**; incorrect steps removed {s['incorrect_removed']}. Added: in the answer {s['added_in_gold']}, not in the answer but "
           f"supported by cited evidence {s['added_supported_not_in_gold']}, **unsupported {s['added_unsupported']}**. "
           f"Status flips {s['flips']} (INCOMPLETE→COMPLETE **{s['flips_to_complete']}**). "
           f"Agent cost ${s['cost_usd']:.6f}"
           + (f", ${s['cost_per_whole_gained']:.6f} per whole-case gained." if s["cost_per_whole_gained"] else "."),
           "", "| case | whole | status | support | kept | removed | +gold | +supported | +unsupported | changed |",
           "|---|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        if not (r["flip"] or r["correct_removed"] or r["added"] or r["whole_base"] != r["whole_cand"]
                or r["support"].split("→")[0] != r["support"].split("→")[1]):
            continue
        mark = " ⚠" if r["flip_to_complete"] or r["correct_removed"] or r["added_unsupported"] else ""
        out.append(f"| {r['case_id']}{mark} | {int(r['whole_base'])}→{int(r['whole_cand'])} | {r['status']} | "
                   f"{r['support']} | {r['correct_kept']} | {r['correct_removed']} | {r['added_in_gold']} | "
                   f"{r['added_supported_not_in_gold']} | {r['added_unsupported']} | "
                   f"-{','.join(r['removed']) or '∅'} +{','.join(r['added']) or '∅'} |")
    return "\n".join(out) + "\n"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", required=True, type=Path)
    ap.add_argument("--cand", required=True, type=Path)
    ap.add_argument("--gold", type=Path, default=ROOT / "dataset" / "sample_output.csv")
    ap.add_argument("--dataset", type=Path, default=ROOT / "dataset")
    ap.add_argument("--out", type=Path)
    a = ap.parse_args(argv)
    rows, s = compare(a.base, a.cand, a.gold, a.dataset)
    md = to_markdown(rows, s, a.base, a.cand)
    out = a.out or a.cand / "compare.md"
    out.write_text(md)
    (out.with_suffix(".json")).write_text(json.dumps({"summary": s, "cases": rows}, indent=1) + "\n")
    print(md.split("\n| case |")[0])
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
