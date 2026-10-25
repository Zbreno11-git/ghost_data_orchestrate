"""Mismatch diagnostics by earliest responsible stage (S5 C5.15; evaluator side, never the prediction path).

Every difference between a run and the sample answers gets exactly one cause, the earliest stage that can be
shown responsible:

| cause | when |
|---|---|
| no supporting fact found | the answer's resource id occurs in no decoded participant source (raw text, PDF text from two decoders, every vision extract, the activity and audit CSVs): listed with the checks made, never as proof that the evidence is absent; if any source could not be decoded the cause is "undetermined" |
| extraction | the id is in a participant file but in no extracted observation |
| temporal state | the id is extracted, but only from evidence after the case's audit_at (excluded by the contract) |
| identity/resource association | extracted and admissible, but the resource was not linked to the subject (or a predicted resource is not in the answer) |
| policy/treatment | linked, but the treatment family the engine chose differs from the answer's operation family |
| temporal state (state) | linked, same treatment, but the reconstructed state led to a different verdict (finding vs verification) |
| citation | the step matches but cites a different evidence id |
| ordering/serialization | all steps match but the array order differs |
| undetermined | none of the above can be established |

Full official denominators: every answer step and every case is counted. Usage:
  python code/evaluation/diagnose.py --run runs/<final samples> [--before runs/<baseline samples>] [--out md]
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "code"))

from evaluation.metrics import load_output, match_key  # noqa: E402

FAMILY = {"REPORT_REMAINING_RECORD": "DELETE", "DELETE_RECORD": "DELETE", "VERIFY_RECORD_ABSENT": "DELETE",
          "REPORT_EXPOSED_PII": "REDACT|ANONYMIZE", "REDACT_RECORD": "REDACT", "VERIFY_RECORD_REDACTED": "REDACT",
          "ANONYMIZE_RECORD": "ANONYMIZE", "VERIFY_RECORD_ANONYMIZED": "ANONYMIZE", "VERIFY_RECORD_PRESENT": "RETAIN",
          "REPORT_ACTIVE_DATA_FLOW": "DISABLE_FLOW", "DISABLE_DATA_FLOW": "DISABLE_FLOW",
          "VERIFY_DATA_FLOW_DISABLED": "DISABLE_FLOW", "REPORT_RESTORE_RISK": "BLOCK_RESTORE",
          "BLOCK_RESTORE": "BLOCK_RESTORE", "VERIFY_RESTORE_BLOCKED": "BLOCK_RESTORE"}
ORDER = ["no supporting fact found", "extraction", "temporal state", "identity/resource association",
         "policy/treatment", "temporal state (state)", "citation", "ordering/serialization", "undetermined"]


class World:
    """Participant data only: decoded text of every source for the "in no source" search, the store for the rest.

    S6 C6.1: the search used to run over raw bytes, which cannot see inside the compressed PDFs."""

    def __init__(self, dataset: Path):
        from ghostaudit.ingest.pipeline import ingest_all
        from evaluation.corpus import decoded_corpus, undecodable
        self.corpus = decoded_corpus(dataset)
        self.undecodable = undecodable(self.corpus)
        self.text = "\n".join(t for texts in self.corpus.values() for _, t in texts)
        self.store = ingest_all(dataset, allow_paid=False)[0]

    def in_decoded(self, rid: str) -> bool:
        import re
        return re.search(r"\b" + re.escape(rid) + r"\b", self.text) is not None

    def admissible(self, rid: str, audit_at) -> bool:
        from ghostaudit.temporal import event_time
        return any(o.captured_at <= audit_at and event_time(o) <= audit_at for o in self.store.by_resource.get(rid, ()))


def diagnose(run: Path, gold_path: Path, world: World) -> tuple[list[dict], Counter]:
    from ghostaudit.timeutil import parse_ts
    gold, pred = load_output(gold_path), load_output(run / "output.csv")
    decs = {json.loads(l)["case_id"]: json.loads(l) for l in open(run / "decisions.jsonl", encoding="utf-8")}
    audits = {r["case_id"]: parse_ts(r["audit_at"]) for r in
              __import__("csv").DictReader(open(ROOT / "dataset" / "sample_deletion_requests.csv"))}
    items, causes = [], Counter()

    def add(case, kind, step, cause, why):
        items.append({"case_id": case, "kind": kind, "step": step, "cause": cause, "why": why})
        causes[cause] += 1

    for cid, (gstatus, gsteps) in sorted(gold.items()):
        pstatus, psteps = pred.get(cid, (None, []))
        psteps = psteps or []
        d = {x["resource_id"]: x for x in decs.get(cid, {}).get("decisions", [])}
        gk = {match_key(s): s for s in gsteps}
        pk = {match_key(s): s for s in psteps}
        if gstatus != pstatus:
            add(cid, "status", f"{gstatus}→{pstatus}", "undetermined", "status differs; see the step causes below")
        for k, s in gk.items():
            rid = s["resource_id"]
            if k in pk:
                if pk[k]["evidence_id"] != s["evidence_id"]:
                    add(cid, "citation", f"{s['operation']} {rid}", "citation",
                        f"cites {pk[k]['evidence_id'] or '∅'}, answer {s['evidence_id'] or '∅'}")
                continue
            step = f"{s['operation']} {rid}"
            if rid not in d:
                if not world.in_decoded(rid):
                    if world.undecodable:
                        add(cid, "missing", step, "undetermined", f"id in no decoded source; undecodable: {world.undecodable}")
                    else:
                        add(cid, "missing", step, "no supporting fact found",
                            "id in no decoded source (raw text, 2 PDF decoders, vision extracts, CSVs)")
                elif rid not in world.store.by_resource:
                    add(cid, "missing", step, "extraction", "id in a participant file, in no observation")
                elif not world.admissible(rid, audits[cid]):
                    add(cid, "missing", step, "temporal state", "only evidence after audit_at")
                else:
                    add(cid, "missing", step, "identity/resource association", "admissible, not linked")
                continue
            fam, treat = FAMILY.get(s["operation"], "?"), d[rid]["treatment"]
            if treat is None or treat not in fam.split("|"):
                add(cid, "missing", step, "policy/treatment", f"engine treatment {treat}, answer family {fam}")
            elif d[rid]["verdict"] == "unknown":
                add(cid, "missing", step, "temporal state (state)", f"state unknown: {d[rid]['reason']}")
            else:
                add(cid, "missing", step, "temporal state (state)",
                    f"verdict {d[rid]['verdict']} ({d[rid]['reason']}) vs the answer's {s['phase'].lower()}")
        for k, s in pk.items():
            if k in gk:
                continue
            rid = s["resource_id"]
            step = f"{s['operation']} {rid}"
            if rid not in {g["resource_id"] for g in gsteps}:
                add(cid, "extra", step, "identity/resource association", "resource not in the answer for this case")
            elif not any(match_key(g)[2] == rid and match_key(g)[3] == s["operation"] for g in gsteps):
                add(cid, "extra", step, "temporal state (state)", "same resource, different operation")
            else:
                add(cid, "extra", step, "undetermined", "")
        if gk.keys() == pk.keys() and [match_key(s) for s in gsteps] != [match_key(s) for s in psteps]:
            add(cid, "order", "steps", "ordering/serialization", "same steps, different order")
    return items, causes


def to_markdown(run: Path, items: list[dict], causes: Counter, before: tuple | None, gold_steps: int,
                cases: int) -> str:
    L = ["# Mismatch diagnostics by earliest responsible stage", "",
         f"Run `{run}` against the 32 public sample answers ({gold_steps} answer steps, {cases} cases: full "
         "official denominators). Generated by `code/evaluation/diagnose.py` (evaluator only; the prediction path "
         "never reads the answers). Each mismatch has one cause, the earliest stage that can be shown responsible. "
         "\"No supporting fact found\" means the id occurs in no decoded source (raw text, PDF text from pypdf and "
         "pdftotext, every vision extract, the activity and audit CSVs). It records the checks made; it is not "
         "proof that the evidence is absent.", "",
         "| cause | " + ("before | " if before else "") + "now |", "|---|" + ("---|" if before else "") + "---|"]
    for c in ORDER:
        if causes.get(c) or (before and before[1].get(c)):
            L.append(f"| {c} | " + (f"{before[1].get(c, 0)} | " if before else "") + f"{causes.get(c, 0)} |")
    L.append("| **total** | " + (f"**{sum(before[1].values())}** | " if before else "") + f"**{sum(causes.values())}** |")
    if before:
        L += ["", f"Before = `{before[0]}` (session 3 baseline); now = `{run}`."]
    L += ["", "## Examples by cause", ""]
    by = defaultdict(list)
    for it in items:
        by[it["cause"]].append(it)
    for c in ORDER:
        if by.get(c):
            L.append(f"**{c}** ({len(by[c])})")
            for it in by[c][:3]:
                L.append(f"- `{it['case_id']}` {it['kind']} `{it['step']}`: {it['why']}")
            L.append("")
    L += ["## All mismatches", "", "| case | kind | step | cause | why |", "|---|---|---|---|---|"]
    for it in items:
        L.append(f"| {it['case_id']} | {it['kind']} | `{it['step']}` | {it['cause']} | {it['why'][:120]} |")
    return "\n".join(L) + "\n"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True, type=Path)
    ap.add_argument("--before", type=Path)
    ap.add_argument("--gold", type=Path, default=ROOT / "dataset" / "sample_output.csv")
    ap.add_argument("--out", type=Path, default=ROOT / "code" / "evaluation" / "diagnostics.md")
    a = ap.parse_args(argv)
    world = World(ROOT / "dataset")
    items, causes = diagnose(a.run, a.gold, world)
    before = None
    if a.before:
        _, bc = diagnose(a.before, a.gold, world)
        before = (a.before, bc)
    gold = load_output(a.gold)
    a.out.write_text(to_markdown(a.run, items, causes, before, sum(len(g[1]) for g in gold.values()), len(gold)))
    print(dict(causes))
    print(f"wrote {a.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
