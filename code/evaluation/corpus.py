"""Decoded text of every participant source, for evaluator-side searches (S6 C6.1; never the prediction path).

A raw-byte search cannot see inside the FlateDecode-compressed PDFs (10/10 of their identifiers are invisible to
it, measured 2026-10-25), so "the id is in no file" is decided on decoded content:
- raw text for txt/json/sql/log/csv;
- pypdf and pdftotext page text for PDFs (both kept, so a decoder disagreement stays visible);
- the cached vision extracts for screenshots, from every model in the cache.
"""
from __future__ import annotations

import csv
import json
import shutil
import subprocess
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def decoded_corpus(dataset: Path, vision_dir: Path | None = None) -> dict[str, list[tuple[str, str]]]:
    """source id (file_id, activity_id, audit_id) → [(decoder, text)]. A source with no text has an empty list."""
    vision = defaultdict(list)
    for p in sorted((vision_dir or ROOT / "state" / "vision_cache").glob("*.json")):
        if p.name == "MANIFEST.json":
            continue
        rec = json.loads(p.read_text())
        vision[rec.get("file")].append((f"vision:{rec.get('model')}", json.dumps(rec, ensure_ascii=False, indent=0)))
    out: dict[str, list[tuple[str, str]]] = {}
    for m in csv.DictReader(open(dataset / "evidence_files.csv", encoding="utf-8")):
        p = dataset / m["file_path"]
        ext = p.suffix.lower()
        texts: list[tuple[str, str]] = []
        if ext == ".pdf":
            from pypdf import PdfReader
            texts.append(("pypdf", "\n".join(pg.extract_text() or "" for pg in PdfReader(str(p)).pages)))
            if shutil.which("pdftotext"):
                r = subprocess.run(["pdftotext", "-layout", str(p), "-"], capture_output=True, text=True)
                if r.returncode == 0:
                    texts.append(("pdftotext", r.stdout))
        elif ext == ".png":
            texts = list(vision.get(m["file_path"], []))
        else:
            texts.append(("raw", p.read_text(encoding="utf-8", errors="replace")))
        out[m["file_id"]] = texts
    for name, key in (("system_activity.csv", "activity_id"), ("user_audit_log.csv", "audit_id")):
        for r in csv.DictReader(open(dataset / name, encoding="utf-8")):
            out[r[key]] = [("raw", ",".join(r.values()))]
    for name in ("user_identities.csv", "deletion_rules.csv", "deletion_requests.csv", "sample_deletion_requests.csv"):
        if (dataset / name).exists():
            out[name] = [("raw", (dataset / name).read_text(encoding="utf-8"))]
    return out


def undecodable(corpus: dict[str, list[tuple[str, str]]]) -> list[str]:
    return sorted(s for s, t in corpus.items() if not any(x.strip() for _, x in t))
