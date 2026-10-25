"""Provenance saved with a run, and the fingerprints that tie an explanation to the inputs it came from (S7 C7.2).

An unchanged obs_id does not prove unchanged content: re-ingesting today's dataset to describe yesterday's run can
silently mix versions. So the runner writes `provenance.jsonl` next to `decisions.jsonl`:
- a header line `{"_header": {...}}` with the run fingerprint and the record count;
- then one record per observation the run's decisions reference: source, file path (dataset-relative), kinds,
  locator, both clocks, the time basis, whether it is a snapshot envelope, and a bounded excerpt.

`summary.json` records the fingerprints (code, dataset, extraction, config, run) and the sha256 of `output.csv`,
`decisions.jsonl` and `provenance.jsonl`. `verify_run` re-checks the hashes and the header's run association; a
modified or foreign provenance file is reported, never used as if verified. This guards against mixing versions
by accident, not against someone who rewrites the summary too.
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

EXCERPT_FIELDS = 16
EXCERPT_CHARS = 240
OBS_ID = re.compile(r"^[A-Za-z0-9_.\-]+#\S+$")


def sha256_file(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def _hash_files(files: list[tuple[str, Path]]) -> str:
    h = hashlib.sha256()
    for name, p in sorted(files):
        h.update(name.encode() + b"\0" + hashlib.sha256(p.read_bytes()).digest())
    return h.hexdigest()


def fingerprints(dataset: Path, cfg: dict, model: str | None, code_dir: Path, tables: list[str],
                 vision_dir: Path | None) -> dict:
    """The inputs an answer depends on, hashed separately so a mismatch says which one changed."""
    code = [(p.relative_to(code_dir).as_posix(), p) for sub in ("ghostaudit", "prompts", "config")
            for p in (code_dir / sub).rglob("*")
            if p.is_file() and p.suffix in (".py", ".md", ".toml", ".json") and "__pycache__" not in p.parts]
    data = [(n, dataset / n) for n in (*tables, "evidence_files.csv") if (dataset / n).is_file()]
    data += [(p.relative_to(dataset).as_posix(), p) for p in (dataset / "evidence").rglob("*") if p.is_file()]
    vision = ([(p.name, p) for p in vision_dir.glob("*.json") if p.name != "MANIFEST.json"]
              if vision_dir and vision_dir.is_dir() else [])
    out = {"code": _hash_files(code), "dataset": _hash_files(data), "extraction": _hash_files(vision),
           "config": hashlib.sha256(json.dumps({"cfg": cfg, "model": model}, sort_keys=True,
                                               default=str).encode()).hexdigest()}
    out["run"] = hashlib.sha256(json.dumps(out, sort_keys=True).encode()).hexdigest()
    return out


def referenced_obs_ids(decision: dict) -> set[str]:
    """Every obs_id a published decision record points at (links, proofs, copies, the account's reasons)."""
    ids: set[str] = set()
    for d in decision.get("decisions") or []:
        ids.update(d.get("link_reasons") or [])
        if d.get("proof"):
            ids.add(d["proof"])
        ids.update(c[2] for c in d.get("copies") or [] if len(c) > 2 and c[2])
    acc = (decision.get("trace") or {}).get("account") or {}
    ids.update(acc.get("reasons") or [])
    return {i for i in ids if isinstance(i, str) and OBS_ID.match(i)}


def _excerpt(d: dict) -> dict:
    out = {}
    for k, v in list(d.items())[:EXCERPT_FIELDS]:
        out[k] = v[:EXCERPT_CHARS] + ("…" if len(v) > EXCERPT_CHARS else "") if isinstance(v, str) else v
    return out


def record(o, paths: dict[str, str]) -> dict:
    from .temporal import time_basis
    return {"obs_id": o.obs_id, "source_id": o.source_id, "file": paths.get(o.source_id), "source_kind": o.source_kind,
            "kind": o.kind, "system_id": o.system_id, "resource_id": o.resource_id, "container": o.container,
            "topology": o.topology, "locator": o.locator, "captured_at": o.captured_at.isoformat(),
            "observed_at": o.observed_at.isoformat() if o.observed_at else None, "time_basis": time_basis(o),
            "snapshot_dated": o.snapshot_dated, "result": o.result, "excerpt": _excerpt(o.fields),
            "wrapper_excerpt": _excerpt(o.wrapper)}


def write_provenance(path: Path, decisions: list[dict], store, paths: dict[str, str], run_fp: str) -> list[str]:
    """Writes provenance.jsonl; returns the referenced obs_ids the store does not hold (must be empty)."""
    wanted = set().union(set(), *(referenced_obs_ids(d) for d in decisions))
    index = {o.obs_id: o for o in store.observations if o.obs_id in wanted}
    missing = sorted(wanted - set(index))
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(json.dumps({"_header": {"run_fingerprint": run_fp, "records": len(index)}}, sort_keys=True) + "\n")
        for oid in sorted(index):
            fh.write(json.dumps(record(index[oid], paths), ensure_ascii=False, sort_keys=True, default=str) + "\n")
    return missing


REQUIRED_ARTIFACTS = ("output.csv", "decisions.jsonl", "provenance.jsonl")


def csv_matches_decisions(run: Path) -> str | None:
    """None when output.csv carries exactly the decisions' case ids, statuses and ordered steps; else the first
    difference (the viewer explains decisions.jsonl, so it must describe the submitted CSV)."""
    import csv
    with open(run / "output.csv", newline="", encoding="utf-8") as fh:
        rows = {r["case_id"]: r for r in csv.DictReader(fh)}
    decs = {d["case_id"]: d for d in map(json.loads, open(run / "decisions.jsonl", encoding="utf-8"))}
    if set(rows) != set(decs):
        return f"case ids differ: {sorted(set(rows) ^ set(decs))[:3]}"
    for cid in sorted(rows):
        r, d = rows[cid], decs[cid]
        if r["deletion_status"] != d["status"]:
            return f"{cid}: output.csv says {r['deletion_status']}, decisions.jsonl says {d['status']}"
        if json.loads(r["steps_json"] or "[]") != json.loads(d.get("steps_json") or "[]"):
            return f"{cid}: output.csv steps differ from decisions.jsonl"
    return None


def verify_run(run: Path) -> tuple[str, dict | None, str]:
    """(status, provenance index or None, message). status:
    - verified: output.csv, decisions.jsonl and provenance.jsonl exist, match the sha256s in summary.json, the
      provenance header names this run's fingerprint, and the CSV carries the decisions' ids, statuses and steps;
    - damaged: a run that recorded integrity metadata but fails any of those checks (or lacks an artifact);
    - legacy: a run that recorded no integrity metadata (pre-S7), so nothing can be verified.
    Protection against accidental mixing of versions, not proof of authenticity."""
    summ = run / "summary.json"
    if not summ.exists():
        return "legacy", None, "the run has no summary.json: no integrity metadata to verify against"
    s = json.loads(summ.read_text())
    arts, fps = s.get("artifacts") or {}, s.get("fingerprints") or {}
    if not arts:
        return "legacy", None, "the run recorded no integrity metadata (pre-S7 run)"
    for name in REQUIRED_ARTIFACTS:
        if not (run / name).exists():
            return "damaged", None, f"required artifact {name} is missing"
        if name not in arts:
            return "damaged", None, f"summary.json records no sha256 for {name}"
        if sha256_file(run / name) != arts[name]:
            return "damaged", None, f"{name} does not match the sha256 recorded in summary.json"
    lines = (run / "provenance.jsonl").read_text(encoding="utf-8").splitlines()
    head = json.loads(lines[0]).get("_header") if lines else None
    if not head or head.get("run_fingerprint") != fps.get("run") or head.get("records") != len(lines) - 1:
        return "damaged", None, "provenance.jsonl belongs to another run (header fingerprint or count)"
    if (why := csv_matches_decisions(run)) is not None:
        return "damaged", None, f"output.csv and decisions.jsonl disagree: {why}"
    index = {r["obs_id"]: r for r in map(json.loads, lines[1:])}
    return "verified", index, (f"output.csv, decisions.jsonl and provenance.jsonl match their recorded sha256 and "
                               f"each other; run fingerprint {fps.get('run', '')[:12]}")
