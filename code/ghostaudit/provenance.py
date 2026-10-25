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


def verify_run(run: Path) -> tuple[str, dict | None, str]:
    """(status, provenance index or None, message). status: verified | integrity_failed | legacy."""
    summ = run / "summary.json"
    prov = run / "provenance.jsonl"
    if not summ.exists():
        return "legacy", None, "the run has no summary.json, so nothing ties provenance to it"
    s = json.loads(summ.read_text())
    arts, fps = s.get("artifacts") or {}, s.get("fingerprints") or {}
    if not prov.exists() or "provenance.jsonl" not in arts:
        return "legacy", None, "the run saved no provenance (pre-S7 run)"
    for name in ("provenance.jsonl", "decisions.jsonl"):
        if (run / name).exists() and sha256_file(run / name) != arts.get(name):
            return "integrity_failed", None, f"{name} does not match the sha256 recorded in summary.json"
    lines = prov.read_text(encoding="utf-8").splitlines()
    head = json.loads(lines[0]).get("_header") if lines else None
    if not head or head.get("run_fingerprint") != fps.get("run") or head.get("records") != len(lines) - 1:
        return "integrity_failed", None, "provenance.jsonl belongs to another run (header fingerprint or count)"
    index = {r["obs_id"]: r for r in map(json.loads, lines[1:])}
    return "verified", index, f"saved with the run; sha256 and run fingerprint {fps.get('run', '')[:12]} verified"
