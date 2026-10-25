"""Extraction coverage audit for the sources behind remaining sample mismatches (S6 C6.1; evaluator side).

"94/94 files processed" says every file was read, not that every fact in it was extracted. For each resource
in a remaining mismatch, this audit:
- finds every participant file whose *decoded* content names it: raw text for txt/json/sql/log/csv, both
  pdftotext and pypdf page text for PDFs (the PDFs are FlateDecode-compressed, so a raw-byte search cannot
  see them), and the cached vision extracts for screenshots;
- compares each naming line against the observations the engine built from that source: the identifiers,
  resource ids, timestamps and state words on the line must reappear in an observation of that source that
  names the resource.

Verdict for a resource absent from the extracted store:
- *present but missed* (a decoded source names it);
- *no supporting fact found after documented checks* (the checks are printed);
- *undetermined* (a source could not be decoded).

Screenshots also need a visual read of the rendered image, recorded in the session file. This tool lists the
images to read.

Reads `dataset/sample_output.csv` on purpose: it is a measurement of our extraction against the answers' resources.

Usage: python scripts/analysis/extraction_audit.py --run runs/<samples run> [--out md]
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

TS = re.compile(r"\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}(?::\d{2})?Z?")
STATE = re.compile(r"\b(FOUND|NOT_FOUND|ACTIVE|ENABLED|DISABLED|PAUSED|BLOCKED|REDACTED|ANONYMIZED|DELETED|ABSENT|"
                   r"PRESENT|SUCCESS|FAILED|PARTIAL|deny|allow|true|false)\b")
EMAIL = re.compile(r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}")
HASH = re.compile(r"\b[0-9a-f]{64}\b")


def tokens(line: str, resource_re) -> set[str]:
    t = set(resource_re.findall(line)) | {e.lower() for e in EMAIL.findall(line)} | set(HASH.findall(line))
    t |= {x.replace(" ", "T").rstrip("Z")[:16] for x in TS.findall(line)}
    t |= {s.upper() for s in STATE.findall(line)}
    return t


def obs_tokens(o, resource_re) -> set[str]:
    blob = " ".join(str(v) for d in (o.fields, o.wrapper) for v in d.values())
    blob += " " + " ".join(str(x) for x in (o.resource_id, o.result, o.record_type, o.observed_at and o.observed_at.isoformat()))
    return tokens(blob, resource_re)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True, type=Path)
    ap.add_argument("--out", type=Path)
    a = ap.parse_args(argv)
    from evaluation.diagnose import World, diagnose
    dataset = ROOT / "dataset"
    world = World(dataset)
    items, _ = diagnose(a.run, dataset / "sample_output.csv", world)
    corpus, undecodable = world.corpus, world.undecodable
    store, rre = world.store, world.store.resource_re
    gold = {r["case_id"]: json.loads(r["steps_json"]) for r in csv.DictReader(open(dataset / "sample_output.csv"))}
    L = ["# Extraction coverage audit (C6.1)", "",
         f"Run `{a.run}`; {len(items)} mismatches. Decoders: raw (txt/json/sql/log/csv), pypdf + pdftotext (PDF), "
         "cached vision extracts (PNG). Undecodable sources: " + (", ".join(undecodable) or "none") + ".", ""]
    rows, seen = [], set()
    for it in items:
        if it["kind"] not in ("missing", "extra"):
            continue
        rid = it["step"].split()[-1]
        if (it["case_id"], rid) in seen:
            continue
        seen.add((it["case_id"], rid))
        cited = {s["evidence_id"] for s in gold.get(it["case_id"], []) if s["resource_id"] == rid and s["evidence_id"]}
        pat = re.compile(r"\b" + re.escape(rid) + r"\b")
        naming = {f: [(d, ln) for d, txt in texts for ln in txt.splitlines() if pat.search(ln)]
                  for f, texts in corpus.items()}
        naming = {f: v for f, v in naming.items() if v}
        sources = sorted(set(naming) | cited)
        verdict_bits = []
        for f in sources:
            obs = [o for o in store.by_source.get(f, []) if o.resource_id == rid or rid in obs_tokens(o, rre)]
            have = set().union(*(obs_tokens(o, rre) for o in obs)) if obs else set()
            lines = naming.get(f, [])
            missing = sorted(set().union(*(tokens(ln, rre) for _, ln in lines)) - have - {rid}) if lines else []
            verdict_bits.append((f, len(lines), len(obs), missing, f in cited))
        if not naming:
            v = "no supporting fact found after documented checks" if not undecodable else "undetermined"
        elif rid not in store.by_resource:
            v = "present but missed"
        else:
            v = "extracted"
        rows.append((it["case_id"], it["kind"], it["step"], it["cause"], v, verdict_bits))
    L += ["| case | kind | step | diagnose cause | extraction verdict | sources (lines naming it / observations naming it / tokens on those lines not in any observation; * = cited by the answer) |",
          "|---|---|---|---|---|---|"]
    for c, k, s, cause, v, bits in rows:
        src = "; ".join(f"{'*' if cit else ''}{f} {nl}/{no}" + (f" missing {m[:6]}" if m else "") for f, nl, no, m, cit in bits)
        L.append(f"| {c} | {k} | `{s}` | {cause} | {v} | {src or '—'} |")
    L += ["", "Checks behind \"no supporting fact found\": the id searched as a whole word in every decoded source "
          "(all decoders), in the activity and audit CSVs, and in the extracted store; screenshots additionally need "
          "the visual read recorded in session-06.md."]
    md = "\n".join(L) + "\n"
    (a.out.write_text(md) if a.out else print(md))
    if a.out:
        print(f"wrote {a.out}: {len(rows)} resources")
    return 0


if __name__ == "__main__":
    sys.exit(main())
