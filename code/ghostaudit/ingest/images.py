"""PNG screenshots → faithful transcription (panels of label/value rows) via a cached, ledgered vision call.

The model is asked for what is displayed, never for a deletion verdict. Two models read each image; their
identifier sets must agree, otherwise the file is marked partial and the difference is listed (a misread digit
becomes visible instead of becoming a plausible wrong fact). A cache miss without --allow-paid fails loudly.
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

from ..config import REPO_ROOT
from ..evidence import EMAIL_RE, HASH_RE, RESOURCE_RE, EvidenceStore, Observation
from .coverage import FileCoverage
from .manifest import ManifestEntry

PROMPT = (
    "This is a screenshot of an internal business application. Transcribe everything it displays, exactly as "
    "shown: keep identifiers, emails, phone numbers, hashes, dates, statuses and toggles verbatim (same case, same "
    "digits). Group the text by visible panel, table or card. For a table, emit one row per table row, with label "
    "= the column header and value = the cell, and prefix every label of that row with the row number as "
    "'row N: <header>'. Do not summarize, infer, translate or add anything that is not visible.")

SCHEMA = {
    "type": "object",
    "properties": {
        "screen_title": {"type": "string"},
        "panels": {"type": "array", "items": {
            "type": "object",
            "properties": {"title": {"type": "string"},
                           "rows": {"type": "array", "items": {
                               "type": "object",
                               "properties": {"label": {"type": "string"}, "value": {"type": "string"}},
                               "required": ["label", "value"]}}},
            "required": ["title", "rows"]}},
        "other_text": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["screen_title", "panels"],
}

USER_TOKEN = re.compile(r"\buser_\d+\b")
PHONE_TOKEN = re.compile(r"\+\d[\d ()\-]{7,}\d")
REFERENCE_TOKEN = re.compile(r"\b[A-Z]{2,4}-\d{3,}(?:-\d+)*\b")  # ORD-20263245, CS-3245, FIN-7742
FILE_TOKEN = re.compile(r"\b[\w\-]+\.(?:pdf|jpg|jpeg|png|zip|csv|json|tar\.zst)\b")


def identifier_tokens(extract: dict) -> set[str]:
    text = json.dumps(extract, ensure_ascii=False)
    toks = {e.lower() for e in EMAIL_RE.findall(text)}
    toks |= set(USER_TOKEN.findall(text)) | set(RESOURCE_RE.findall(text))
    toks |= {re.sub(r"\D", "", p) for p in PHONE_TOKEN.findall(text)}
    toks |= set(REFERENCE_TOKEN.findall(text)) | set(FILE_TOKEN.findall(text))
    toks |= {w.lower() for w in re.findall(r"\b[0-9a-fA-F]{64}\b", text) if HASH_RE.match(w)}
    return toks


# A cached extraction is reused only for the same image bytes, model, prompt and schema.
PROMPT_SHA256 = hashlib.sha256((PROMPT + json.dumps(SCHEMA, sort_keys=True)).encode()).hexdigest()


def _cache_path(cfg: dict, sha: str, model: str) -> Path:
    return REPO_ROOT / cfg["vision"]["cache_dir"] / f"{sha[:16]}.{model}.json"


def read_image(entry: ManifestEntry, model: str, cfg: dict, allow_paid: bool, run_id: str) -> dict | None:
    data = entry.path.read_bytes()
    sha = hashlib.sha256(data).hexdigest()
    path = _cache_path(cfg, sha, model)
    if path.exists():
        cached = json.loads(path.read_text())
        if cached["sha256"] == sha and cached.get("prompt_sha256") == PROMPT_SHA256:
            return cached
    if not allow_paid:
        return None
    from google.genai import types

    from ..llm.gemini import Gemini

    v = cfg["vision"]
    g = Gemini(run_id=run_id, config=cfg)
    resp, measured = g.generate(
        model=model, purpose="vision-extract", est_input_tokens=v["est_input_tokens"],
        contents=[types.Part.from_bytes(data=data, mime_type="image/png"), PROMPT],
        config=types.GenerateContentConfig(
            response_mime_type="application/json", response_json_schema=SCHEMA, temperature=0,
            max_output_tokens=v["max_output_tokens"],
            thinking_config=types.ThinkingConfig(thinking_level=v["thinking_level"][model])))
    finish = str(resp.candidates[0].finish_reason) if resp.candidates else "NO_CANDIDATE"
    record = {"sha256": sha, "prompt_sha256": PROMPT_SHA256, "file": entry.rel_path, "model": model,
              "model_version": getattr(resp, "model_version", None), "finish_reason": finish,
              "usage": measured, "extract": json.loads(resp.text)}
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(record, indent=1, ensure_ascii=False, sort_keys=True) + "\n")
    return record


def ingest_png(entry: ManifestEntry, store: EvidenceStore, cov: FileCoverage, cfg: dict, allow_paid: bool,
               run_id: str = "ingest") -> None:
    v = cfg["vision"]
    cov.adapter = f"png:{v['primary_model']}+{v['check_model']}"
    primary = read_image(entry, v["primary_model"], cfg, allow_paid, run_id)
    check = read_image(entry, v["check_model"], cfg, allow_paid, run_id)
    if primary is None:
        cov.status = "failed"
        cov.notes.append("no cached extraction; rerun `main.py ingest --allow-paid` (ledgered)")
        return
    ex = primary["extract"]
    title = ex.get("screen_title", "")
    n = 0
    for pi, panel in enumerate(ex.get("panels", [])):
        fields = {"screen_title": title, "panel": panel.get("title", "")}
        for ri, row in enumerate(panel.get("rows", [])):
            fields[f"rows.{ri}.{row.get('label', '')}"] = row.get("value", "")
        store.add(Observation(
            obs_id=f"{entry.file_id}#panel:{pi}", source_id=entry.file_id, source_kind="png", kind="text",
            captured_at=entry.captured_at, observed_at=None, system_id=None, resource_id=None,
            container=panel.get("title"), fields=fields, wrapper={"extracted_by": primary["model"]},
            locator=f"panel:{pi}"))
        n += 1
    if ex.get("other_text"):
        store.add(Observation(
            obs_id=f"{entry.file_id}#other", source_id=entry.file_id, source_kind="png", kind="text",
            captured_at=entry.captured_at, observed_at=None, system_id=None, resource_id=None, container=title,
            fields={"screen_title": title, **{f"text.{i}": t for i, t in enumerate(ex["other_text"])}},
            wrapper={"extracted_by": primary["model"]}, locator="other"))
        n += 1
    cov.observations = n
    cov.lines = sum(len(p.get("rows", [])) for p in ex.get("panels", []))
    if "STOP" not in primary["finish_reason"]:
        cov.notes.append(f"primary finish_reason={primary['finish_reason']}")
    if check is None:
        cov.notes.append("cross-check read missing")
    else:
        a, b = identifier_tokens(ex), identifier_tokens(check["extract"])
        diff = sorted(a ^ b)
        cov.notes.append(f"cross-check: {len(a)} identifiers, {len(diff)} disagree" + (f" {diff}" if diff else ""))
        if diff:
            cov.status = "partial"
            return
    cov.status = "processed" if n and not [x for x in cov.notes if "finish_reason" in x or "missing" in x] else "partial"
