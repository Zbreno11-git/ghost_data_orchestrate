"""Declared, hash-verified replay artifacts (S5 C5.11, amendment 4).

A cache root (the vision extracts in state/vision_cache/, the LLM responses in runs/cache/llm/) may carry a
MANIFEST.json, {relative path: sha256}. When it does, every read under that root must be a declared file with
that hash; anything else is a loud error, never a silent re-call or a wrong answer. Without a manifest (a
working checkout) files are read as they are. The packaged code.zip ships both roots with their manifests.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

MANIFEST = "MANIFEST.json"


class ArtifactMismatch(RuntimeError):
    pass


def read_text(root: Path, path: Path) -> str:
    data = path.read_bytes()
    m = root / MANIFEST
    if m.exists():
        declared = json.loads(m.read_text())
        rel = path.relative_to(root).as_posix()
        if rel not in declared:
            raise ArtifactMismatch(f"{rel} is not declared in {m}")
        if hashlib.sha256(data).hexdigest() != declared[rel]:
            raise ArtifactMismatch(f"{rel} does not match its sha256 in {m}")
    return data.decode("utf-8")


def write_manifest(root: Path, files: list[Path]) -> dict[str, str]:
    declared = {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(files)}
    (root / MANIFEST).write_text(json.dumps(declared, indent=1, sort_keys=True) + "\n")
    return declared
