"""Rejected association paths, broken down to the exact break point (S6 C6.3; evaluator side).

For every sample step whose resource the engine did not link (and every predicted resource the answer does not
list), the same documented checks run in the same order:
1. found: in the extracted store at all? In which sources?
2. admissible: observations whose two clocks are ≤ audit_at; the excluded ones are listed with their clock.
3. direct identifiers: identifier values in admissible observations naming the resource, and whose they are
   (this subject, someone else as of the cutoff, nobody).
4. explicit intermediate references: reference-like fields (`*reference*`, `source_resource_id`, `*_id`,
   `user_id`, `*key*`) in those observations, and whether their values reach the subject or one of the
   subject's already-linked resources.
5. decoded co-mention: any decoded source line that names the resource *and* a subject identifier or a
   linked resource. Post-cutoff sources are reported and never used.
The break point is the first check that fails. A path with nothing new after check 5 is "no supporting fact
found after documented checks". Timing, naming patterns, list positions and one-to-one assumptions are never
links here.

Reads `dataset/sample_output.csv` on purpose (it names the resources to examine).
Usage: python scripts/analysis/association_paths.py --run runs/<samples run> [--out md]
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "code"))

REF_KEY = re.compile(r"(reference|source_resource_id|(^|\.)user_id$|_key$|^key$|customer_id|subject)", re.I)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True, type=Path)
    ap.add_argument("--out", type=Path)
    a = ap.parse_args(argv)
    from evaluation.diagnose import World, diagnose
    from ghostaudit.evidence import identifiers_in
    from ghostaudit.identity import IdentityIndex, Subject
    from ghostaudit.ingest.csv_tables import load_tables
    from ghostaudit.ingest.manifest import read_csv
    from ghostaudit.ownership import OwnerIndex
    from ghostaudit.temporal import CaseView, event_time
    from ghostaudit.timeutil import parse_ts

    ds = ROOT / "dataset"
    world = World(ds)
    store, rre = world.store, world.store.resource_re
    tables = load_tables(ds)
    identity = IdentityIndex(tables["identities"], tables["audit"])
    owners = OwnerIndex(identity)
    reqs = {r["case_id"]: r for r in read_csv(ds / "sample_deletion_requests.csv")}
    decs = {json.loads(l)["case_id"]: json.loads(l) for l in open(a.run / "decisions.jsonl", encoding="utf-8")}
    caps = {m["file_id"]: parse_ts(m["captured_at"]) for m in read_csv(ds / "evidence_files.csv")}
    items, _ = diagnose(a.run, ds / "sample_output.csv", world)
    todo = [(it["case_id"], it["kind"], it["step"].split()[-1], it["step"]) for it in items
            if it["cause"] == "identity/resource association"]

    L = ["# Rejected association paths (C6.3)", "", f"Run `{a.run}`; {len(todo)} association mismatches. "
         "Checks in order: found → admissible → direct identifiers → explicit references → decoded co-mention. "
         "Timing, naming patterns, list positions and one-to-one assumptions are never links.", "",
         "| case | kind | step | found in | admissible / excluded | direct ids (whose) | references → reach | decoded co-mention (admissible / post-cutoff) | break point |",
         "|---|---|---|---|---|---|---|---|---|"]
    breaks = {}
    for cid, kind, rid, step in todo:
        q = reqs[cid]
        at = parse_ts(q["audit_at"])
        subj = identity.resolve(q["email"], at)
        if not isinstance(subj, Subject):
            L.append(f"| {cid} | {kind} | `{step}` | — | — | — | — | — | subject not identified |")
            continue
        keys = subj.keys(strong_only=True)
        values = {i.norm for i in subj.identifiers} | {i.raw for i in subj.identifiers} | {subj.user_id}
        linked = {d["resource_id"] for d in decs[cid]["decisions"]} - {rid}
        view = CaseView(store, at)
        allobs = store.by_resource.get(rid, [])
        adm = [o for o in allobs if view.admissible(o)]
        exc = [o for o in allobs if not view.admissible(o)]
        found = sorted({o.source_id for o in allobs})
        ids, refs, reach = set(), [], []
        for o in adm:
            for d in (o.fields, o.wrapper):
                for k, v in d.items():
                    for ident in identifiers_in(k.rsplit(".", 1)[-1], v):
                        holders = owners.holders(ident, at) if hasattr(owners, "holders") else set()
                        whose = "subject" if ident in keys else (",".join(sorted(holders)) or "nobody")
                        ids.add(f"{ident[0]}:{whose}")
                    if REF_KEY.search(k) and v not in (None, "", "null", "None") and k != "resource_id":
                        refs.append(f"{k}={v}")
                        sv = str(v)
                        if sv in values or sv.lower() in values:
                            reach.append(f"{k}→subject")
                        elif set(rre.findall(sv)) & linked:
                            reach.append(f"{k}→linked")
        late_refs = sorted({f"{k}={v}@{o.source_id}" for o in exc for d in (o.fields, o.wrapper) for k, v in d.items()
                            if REF_KEY.search(k) and v not in (None, "", "null", "None") and k != "resource_id"})
        pat = re.compile(r"\b" + re.escape(rid) + r"\b")
        co_adm, co_late = [], []
        for src, texts in world.corpus.items():
            for _, txt in texts:
                for ln in txt.splitlines():
                    if not pat.search(ln):
                        continue
                    lnl = ln.lower()
                    hit = [v for v in values if len(v) > 4 and v.lower() in lnl] + [r for r in linked if r in ln]
                    if hit:
                        late = src in caps and caps[src] > at
                        (co_late if late else co_adm).append(f"{src}:{','.join(sorted(set(hit)))[:40]}")
        if not allobs:
            bp = "not found in the store"
        elif not adm:
            bp = "found only after the cutoff"
        elif "subject" in " ".join(ids) or reach or co_adm:
            bp = "LINK AVAILABLE (engine defect candidate)"
        elif any(":nobody" not in x and ":subject" not in x for x in ids):
            bp = "names another person"
        elif refs:
            bp = "references reach neither the subject nor a linked resource"
        elif any(v.split("=", 1)[1].rsplit("@", 1)[0] in values or v.split("=", 1)[1].rsplit("@", 1)[0].lower() in values
                 for v in late_refs):
            bp = "lineage to the subject exists only in post-cutoff evidence (excluded by the contract)"
        else:
            bp = "record names no identifier or reference (anonymous); no supporting fact found after documented checks"
        breaks[bp] = breaks.get(bp, 0) + 1
        exc_s = ", ".join(sorted({f"{o.source_id}@{event_time(o):%m-%d}" for o in exc}))[:60] or "none"
        L.append(f"| {cid} | {kind} | `{step}` | {', '.join(found)} | {len(adm)} / {len(exc)} ({exc_s}) | "
                 f"{', '.join(sorted(ids)) or 'none'} | {'; '.join(refs)[:80] or 'none'} → {', '.join(reach) or 'none'}"
                 f"{' (post-cutoff refs, unused: ' + '; '.join(late_refs)[:80] + ')' if late_refs else ''} | "
                 f"{'; '.join(co_adm)[:60] or 'none'} / {'; '.join(co_late)[:60] or 'none'} | {bp} |")
    L += ["", "**Break points:** " + "; ".join(f"{k}: {v}" for k, v in sorted(breaks.items()))]
    md = "\n".join(L) + "\n"
    (a.out.write_text(md) if a.out else print(md))
    print(breaks)
    return 0


if __name__ == "__main__":
    sys.exit(main())
