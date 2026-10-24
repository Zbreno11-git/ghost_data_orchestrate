"""PDF documents (pypdf, pure Python) and plain-text records.

PDFs are business artifacts (statements, registers, journal extracts). Each page becomes a text Observation
with the identifiers it names; pipe-delimited register rows become one Observation each. The TXT handover is a
list of `ts | system | resource | record_type | result | subject` lookup lines.
"""
from __future__ import annotations

import re
import shutil
import subprocess

from pypdf import PdfReader

from ..evidence import EMAIL_RE, EvidenceStore, Observation
from ..timeutil import parse_ts
from .coverage import FileCoverage
from .manifest import ManifestEntry

PHONE_TEXT = re.compile(r"\+\d[\d ()\-]{7,}\d")
USER_TEXT = re.compile(r"\buser_\d+\b")
SPLIT_TIME = re.compile(r"\b(\d{2})\n(\d{2} UTC)")  # pypdf breaks "08:00 UTC" at the colon
REGISTER_COLS = ("order_reference", "subject_reference", "reason", "recorded_on", "amount", "retain_until", "owner")


def pdf_text(path) -> list[str]:
    return [SPLIT_TIME.sub(r"\1:\2", p.extract_text() or "") for p in PdfReader(str(path)).pages]


def identifiers_from_text(text: str, resource_re) -> dict:
    out = {}
    for name, rx in (("email", EMAIL_RE), ("phone", PHONE_TEXT), ("user_id", USER_TEXT), ("resource", resource_re)):
        for i, v in enumerate(dict.fromkeys(rx.findall(text))):
            out[f"ids.{name}.{i}" if name != "phone" else f"ids.phone.{i}"] = v
    return out


def _identifier_set(text: str, resource_re) -> set[str]:
    return set(identifiers_from_text(text, resource_re).values())


def ingest_pdf(entry: ManifestEntry, store: EvidenceStore, cov: FileCoverage) -> None:
    pages = pdf_text(entry.path)
    cov.adapter = "pdf_text:pypdf"
    n = 0
    for pi, text in enumerate(pages, start=1):
        cov.lines += len(text.splitlines())
        if not text.strip():
            cov.notes.append(f"page {pi} has no extractable text")
            continue
        title = text.strip().splitlines()[0]
        store.add(Observation(
            obs_id=f"{entry.file_id}#page:{pi}", source_id=entry.file_id, source_kind="pdf", kind="text",
            captured_at=entry.captured_at, observed_at=None, system_id=None, resource_id=None, container=title,
            fields={"text": text, **identifiers_from_text(text, store.resource_re)}, locator=f"page:{pi}"))
        n += 1
        for li, line in enumerate(text.splitlines(), start=1):
            cells = [c.strip() for c in line.split("|")]
            if len(cells) == len(REGISTER_COLS) and cells[0].startswith("ORD-"):
                store.add(Observation(
                    obs_id=f"{entry.file_id}#page:{pi}:line:{li}", source_id=entry.file_id, source_kind="pdf",
                    kind="text", captured_at=entry.captured_at, observed_at=None, system_id=None, resource_id=None,
                    container=title, fields={**dict(zip(REGISTER_COLS, cells)), "text": line},
                    locator=f"page:{pi}:line:{li}"))
                n += 1
    cov.observations = n
    # A8 trigger: pypdf must find every identifier that poppler's pdftotext finds.
    if shutil.which("pdftotext"):
        ref = subprocess.run(["pdftotext", "-layout", str(entry.path), "-"], capture_output=True, text=True).stdout
        missing = _identifier_set(ref, store.resource_re) - _identifier_set("\n".join(pages), store.resource_re)
        cov.notes.append(f"pdftotext parity: {len(missing)} identifiers missing from pypdf"
                         + (f" {sorted(missing)}" if missing else ""))
        if missing:
            cov.status = "partial"
            return
    else:
        cov.notes.append("pdftotext not installed; parity check skipped")
    cov.status = "processed" if n else "failed"


TXT_LINE = re.compile(r"^- (\S+) \| (\S+) \| (\S+) \| (\S+) \| (\S+) \| (.+)$")  # subject may be prose


def ingest_txt(entry: ManifestEntry, store: EvidenceStore, cov: FileCoverage) -> None:
    cov.adapter = "txt:pipe_lookup"
    n = 0
    for i, line in enumerate(entry.path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        cov.lines += 1
        m = TXT_LINE.match(line)
        if not m:
            if line.startswith("- "):
                cov.unparsed += 1
                cov.notes.append(f"unparsed data line {i}: {line[:100]}")
            continue  # headings and narrative lines carry no record
        ts, system, res, rtype, result, subject = m.groups()
        store.add(Observation(
            obs_id=f"{entry.file_id}#line:{i}", source_id=entry.file_id, source_kind="txt", kind="lookup",
            captured_at=entry.captured_at, observed_at=parse_ts(ts), system_id=system, resource_id=res,
            record_type=rtype, result=result, container=entry.origin,
            wrapper={"subject_reference": subject, "recorded_by": entry.origin}, locator=f"line:{i}"))
        n += 1
    cov.observations = n
    cov.status = "partial" if cov.unparsed else ("processed" if n else "failed")
