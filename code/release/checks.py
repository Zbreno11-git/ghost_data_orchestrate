"""What a code.zip must and must not contain, and when a clean-unpack replay counts as accepted (S7 C7.3).

Pure functions over (archive name → bytes) and the replay check's result, so each rule has a test with a fixture
that reaches it. `scripts/package_code.py` builds the archive and runs the replay; these functions decide.

Inventory rules (each refusal names its reason):
- nested archives (`.zip .tar .gz .tgz .7z .rar .bz2 .xz`) are rejected (README: "submissions containing nested
  archive files will be rejected"); so are `.pyc`, `.env*`, `.DS_Store`, private keys and credential patterns;
- environment, dependency and build directories (`.venv`, `venv`, `node_modules`, `__pycache__`, `.pytest_cache`,
  `.git`) and the supplied `dataset/` are rejected;
- a file whose bytes equal a supplied dataset file is rejected wherever it sits, **unless** the documented fixture
  allowlist (`code/evaluation/custom_cases/FIXTURE_ALLOWLIST.json`) names that exact path with that exact sha256;
- the required paths must be present: README.md, code/main.py, code/requirements.txt and the two reports at the
  starter README's explicit paths.

Acceptance of the replay (all required): the replay exits 0; the validator exits 0 **and** prints "0 violations"
for the expected row count; the output is byte-identical to the reference; the rebuilt viewer is byte-identical to
the shipped one; the scan is clean; the run was network-isolated (or the caller explicitly accepted that it was
not, which is then reported as such).
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import PurePosixPath

NESTED_ARCHIVES = (".zip", ".tar", ".gz", ".tgz", ".7z", ".rar", ".bz2", ".xz")
FORBIDDEN_SUFFIXES = NESTED_ARCHIVES + (".pyc", ".pyo")
FORBIDDEN_DIRS = {".venv", "venv", "node_modules", "__pycache__", ".pytest_cache", ".git", ".mypy_cache"}
FORBIDDEN_NAMES = re.compile(r"^(\.env(\..*)?|\.DS_Store|id_rsa|id_ed25519|credentials\.json|auth\.json)$")
# A key starts a token. The look-behind keeps a prefix that occurs by chance inside an opaque base64 value (Gemini's
# `thought_signature` in a shipped response contained "sk-" mid-token, measured 2026-10-25) from counting.
CREDENTIAL = re.compile(rb"(?<![A-Za-z0-9_\-+/])(?:AIza[0-9A-Za-z_\-]{30,}|gh[opsu]_[0-9A-Za-z]{30,}|sk-[A-Za-z0-9]{20,})"
                        rb"|-----BEGIN [A-Z ]*PRIVATE KEY")
REQUIRED = ("README.md", "code/main.py", "code/requirements.txt",
            "code/evaluation/evaluation_report.md", "code/evaluation/usage_report.md")
ALLOWLIST = "code/evaluation/custom_cases/FIXTURE_ALLOWLIST.json"


def sha256(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def load_allowlist(raw: bytes | None) -> dict[str, str]:
    """path → the sha256 it is allowed to have."""
    return {e["path"]: e["sha256"] for e in json.loads(raw)} if raw else {}


def inventory(entries: dict[str, bytes], dataset_hashes: dict[str, str], allowlist: dict[str, str]) -> list[tuple[str, str]]:
    """(archive path, reason) for every entry the archive must not hold, and every required path it lacks."""
    bad = []
    for name, data in sorted(entries.items()):
        parts = PurePosixPath(name).parts
        low = name.lower()
        if parts and parts[0] == "dataset":
            bad.append((name, "the supplied challenge dataset"))
        elif FORBIDDEN_DIRS & set(parts):
            bad.append((name, f"environment/dependency/build directory {sorted(FORBIDDEN_DIRS & set(parts))[0]}"))
        elif low.endswith(NESTED_ARCHIVES):
            bad.append((name, "nested archive"))
        elif low.endswith(FORBIDDEN_SUFFIXES):
            bad.append((name, "compiled file"))
        elif FORBIDDEN_NAMES.match(parts[-1]):
            bad.append((name, "environment or credential file"))
        elif CREDENTIAL.search(data):
            bad.append((name, "credential pattern"))
        elif (h := sha256(data)) in dataset_hashes and allowlist.get(name) != h:
            bad.append((name, f"copy of the supplied dataset file {dataset_hashes[h]} (not in the fixture allowlist)"))
    bad += [(r, "required file missing") for r in REQUIRED if r not in entries]
    return bad


def acceptance(check: dict, expected_rows: int, allow_unisolated: bool = False) -> list[str]:
    """Reasons the clean-unpack replay is NOT accepted (empty = accepted)."""
    why = []
    if check.get("returncode") != 0:
        why.append(f"replay exited {check.get('returncode')}")
    v = check.get("validate") or {}
    if v.get("returncode") != 0 or not re.search(rf"\b0 violations\b.*\bagainst {expected_rows} ", v.get("last", "")):
        why.append(f"validator did not accept {expected_rows} rows: {v}")
    if check.get("identical") is not True:
        why.append("replayed output.csv differs from the reference")
    if check.get("viewer_identical") is not True:
        why.append("rebuilt viewer differs from the shipped viewer")
    if any(check.get("scan", {}).get(k) for k in ("developer path", "credential", "undeclared_cache_files")):
        why.append(f"scan not clean: {check.get('scan')}")
    if not check.get("isolated") and not allow_unisolated:
        why.append("replay was NOT network-isolated (unshare unavailable); pass --allow-unisolated to accept that "
                   "explicitly, and it will be reported")
    if check.get("provider_client_blocked") is not True:
        why.append("replay was not run with provider-client construction blocked")
    return why
