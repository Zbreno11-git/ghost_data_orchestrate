"""Build code.zip and prove it runs from a clean unpack (S5 C5.11, MASTER_PLAN C5.5, amendment 4).

The zip holds (D2 layout):
- README.md and code/ (engine, prompts, config, tests, evaluation with its reports);
- the declared replay artifacts, each root with a MANIFEST.json of sha256s that the runtime verifies on every
  read (ghostaudit/artifacts.py):
  - state/vision_cache/*.json, the PNG extracts that ingest reads (committed in the repo too);
  - runs/cache/llm/<k[:2]>/<k>.json, exactly the LLM responses the final run used (from its llm_keys.jsonl),
    which the gateway reads in replay mode.

It never holds dataset/, .env, a virtualenv, other caches, runs, or nested archives.

The check unpacks into an empty directory, creates a fresh virtualenv from code/requirements.txt only, links
the supplied dataset/, and replays the final run with no API key in the environment, comparing output.csv byte
for byte. If anything outside the zip is needed, the check fails, and we do not claim a self-contained replay.

Usage: python3 -I scripts/package_code.py --run runs/<final> [--out code.zip] [--skip-venv]
"""
from __future__ import annotations

import argparse
import filecmp
import json
import os
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "code"))
from ghostaudit.artifacts import write_manifest  # noqa: E402

EXCLUDE_DIRS = {"__pycache__", ".pytest_cache", ".venv", "venv"}
FORBIDDEN = (".env", ".zip", ".pyc", ".lock")


def code_files() -> list[Path]:
    out = [ROOT / "README.md"]
    for p in sorted((ROOT / "code").rglob("*")):
        if p.is_file() and not EXCLUDE_DIRS & set(p.relative_to(ROOT).parts) and not p.name.endswith(FORBIDDEN):
            out.append(p)
    return out


def stage(run: Path, dst: Path) -> dict:
    for p in code_files():
        (dst / p.relative_to(ROOT)).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(p, dst / p.relative_to(ROOT))
    vision = sorted((ROOT / "state" / "vision_cache").glob("*.json"))
    vdst = dst / "state" / "vision_cache"
    vdst.mkdir(parents=True)
    for p in vision:
        if p.name != "MANIFEST.json":
            shutil.copy2(p, vdst / p.name)
    vman = write_manifest(vdst, [p for p in vdst.glob("*.json") if p.name != "MANIFEST.json"])
    keys = sorted({json.loads(l)["request_key"] for l in open(run / "llm_keys.jsonl", encoding="utf-8")})
    ldst = dst / "runs" / "cache" / "llm"
    copied = []
    for k in keys:
        src = ROOT / "runs" / "cache" / "llm" / k[:2] / f"{k}.json"
        if not src.exists():
            raise SystemExit(f"response {k[:12]} used by {run} is missing from the cache")
        (ldst / k[:2]).mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, ldst / k[:2] / f"{k}.json")
        copied.append(ldst / k[:2] / f"{k}.json")
    lman = write_manifest(ldst, copied) if copied else {}
    return {"code_files": len(code_files()), "vision_extracts": len(vman), "llm_responses": len(lman)}


def build(run: Path, out: Path) -> dict:
    with tempfile.TemporaryDirectory() as td:
        info = stage(run, Path(td))
        with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
            for p in sorted(Path(td).rglob("*")):
                if p.is_file():
                    z.write(p, p.relative_to(td))
    with zipfile.ZipFile(out) as z:
        names = z.namelist()
    bad = [n for n in names if n.startswith(("dataset/", ".venv/")) or n.endswith(FORBIDDEN)
           or "/.env" in n or n.startswith(".env")]
    return {**info, "entries": len(names), "bytes": out.stat().st_size, "forbidden": bad,
            "reports": [n for n in names if n.startswith("code/evaluation/") and n.endswith("_report.md")]}


def replay_check(zip_path: Path, run: Path, skip_venv: bool) -> dict:
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        with zipfile.ZipFile(zip_path) as z:
            z.extractall(td / "unpacked")
        u = td / "unpacked"
        os.symlink(ROOT / "dataset", u / "dataset")                         # the supplied dataset, not in the zip
        if skip_venv:
            py = Path(sys.executable).parent / "python"
        else:
            subprocess.run([sys.executable, "-m", "venv", str(td / "venv")], check=True)
            py = td / "venv" / "bin" / "python"
            subprocess.run([str(py), "-m", "pip", "install", "-q", "-r", str(u / "code" / "requirements.txt")],
                           check=True)
        summary = json.loads((run / "summary.json").read_text())
        env = {k: v for k, v in os.environ.items() if k != "GEMINI_API_KEY"}
        cmd = [str(py), "code/main.py", "run", "--engine", summary["engine"], "--mode", "replay",
               "--split", summary["split"], "--ownership", summary["ownership"], "--out", str(td / "replay")]
        if summary["engine"] == "agent":
            cmd += ["--agent-scope", summary.get("agent_scope", "all")]
            if summary.get("model"):
                cmd += ["--model", summary["model"]]
        r = subprocess.run(cmd, cwd=u, env=env, capture_output=True, text=True)
        same = r.returncode == 0 and filecmp.cmp(td / "replay" / "output.csv", run / "output.csv", shallow=False)
        tail = (r.stdout + r.stderr).strip().splitlines()[-4:]
        return {"returncode": r.returncode, "identical": same, "tail": tail}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True, type=Path)
    ap.add_argument("--out", type=Path, default=ROOT / "code.zip")
    ap.add_argument("--skip-venv", action="store_true", help="reuse the current interpreter (faster, less clean)")
    a = ap.parse_args(argv)
    info = build(a.run, a.out)
    print(json.dumps(info, indent=1))
    if info["forbidden"] or len(info["reports"]) != 2:
        print("refusing: forbidden entries or missing reports")
        return 1
    check = replay_check(a.out, a.run, a.skip_venv)
    print(json.dumps(check, indent=1))
    return 0 if check["identical"] else 1


if __name__ == "__main__":
    sys.exit(main())
