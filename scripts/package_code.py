"""Build code.zip and prove it runs from a clean unpack (S5 C5.11; hardened in S7 C7.3).

The zip holds (D2 layout):
- README.md and code/ (engine, prompts, config, tests, evaluation with its reports, custom cases, viewer source);
- `code/viewer/viewer.html`, the evidence viewer built from the reference run (its execution-metadata sidecar is
  not shipped: it holds local paths);
- the declared replay artifacts, each root with a MANIFEST.json of sha256s that the runtime verifies on every read
  (ghostaudit/artifacts.py): `state/vision_cache/*.json` (the PNG extracts ingest reads) and
  `runs/cache/llm/<k[:2]>/<k>.json` (exactly the LLM responses the reference run used, from its llm_keys.jsonl).

What it may and may not contain, and when the replay counts as accepted, is decided by `code/release/checks.py`.

The check unpacks into an empty directory, creates a fresh virtualenv from code/requirements.txt only, links the
supplied dataset/ from outside the zip, and replays the reference run:
- with GEMINI_API_KEY removed from the environment;
- inside `unshare -rn` (a new network namespace with no interface: the protection actually used on Linux). Where
  unshare is unavailable the run is reported as NOT isolated and refused unless --allow-unisolated is given;
- with `google.genai.Client` replaced by a class that raises before main.py runs, which shows the replay path
  never constructs a provider client (the SDK module itself is imported: the agent builds its request types and
  cache keys with it).
Then it validates the replayed output, compares it byte for byte with the reference, rebuilds the viewer from the
replay run and compares that byte for byte with the shipped one, and scans the unpacked tree.

Usage: python3 -I scripts/package_code.py --run runs/<final> [--out code.zip] [--skip-venv] [--allow-unisolated]
                                          [--report <json>]
Exit 0 only when the inventory is clean and the replay is accepted. The archive is built and checked as
`<out>.candidate` and moved onto `<out>` only then, so a refused build never replaces the released one.
"""
from __future__ import annotations

import argparse
import filecmp
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "code"))
from ghostaudit.artifacts import write_manifest  # noqa: E402
from release.checks import ALLOWLIST, acceptance, inventory, load_allowlist, sha256  # noqa: E402

EXCLUDE_DIRS = {"__pycache__", ".pytest_cache", ".venv", "venv"}
NOT_SOURCE = re.compile(r"\.(pyc|zip|lock)$|^\.env|^code/viewer/.*\.(html|meta\.json)$")
# Replay may import the SDK (the agent builds its request types and cache keys with it) but must never construct
# a provider client: the probe replaces genai.Client with a class that raises before main.py runs.
POISONED = ("import sys, runpy\nfrom google import genai\nclass NoClient:\n"
            "    def __init__(self, *a, **k): raise SystemExit('a provider client was constructed during replay')\n"
            "genai.Client = NoClient\nsys.argv = ['code/main.py'] + sys.argv[1:]\n"
            "runpy.run_path('code/main.py', run_name='__main__')")


def code_files() -> list[Path]:
    out = [ROOT / "README.md"]
    for p in sorted((ROOT / "code").rglob("*")):
        rel = p.relative_to(ROOT).as_posix()
        if p.is_file() and not EXCLUDE_DIRS & set(p.relative_to(ROOT).parts) and not NOT_SOURCE.search(rel) \
                and not NOT_SOURCE.search(p.name):
            out.append(p)
    return out


def stage(run: Path, dst: Path) -> dict:
    for p in code_files():
        (dst / p.relative_to(ROOT)).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(p, dst / p.relative_to(ROOT))
    from viewer.build import build as build_viewer
    vmeta = build_viewer(run, dst / "code" / "viewer" / "viewer.html")
    (dst / "code" / "viewer" / "viewer.html.meta.json").unlink()            # local paths: not shipped
    vdst = dst / "state" / "vision_cache"
    vdst.mkdir(parents=True)
    for p in sorted((ROOT / "state" / "vision_cache").glob("*.json")):
        if p.name != "MANIFEST.json":
            shutil.copy2(p, vdst / p.name)
    vman = write_manifest(vdst, [p for p in vdst.glob("*.json") if p.name != "MANIFEST.json"])
    keys = sorted({json.loads(l)["request_key"] for l in open(run / "llm_keys.jsonl", encoding="utf-8")}) \
        if (run / "llm_keys.jsonl").exists() else []
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
    return {"code_files": len(code_files()), "vision_extracts": len(vman), "llm_responses": len(lman),
            "viewer_sha256": vmeta["html_sha256"], "viewer_bytes": vmeta["bytes"],
            "manifests": {"state/vision_cache/MANIFEST.json": sha256((vdst / "MANIFEST.json").read_bytes()),
                          "runs/cache/llm/MANIFEST.json": sha256((ldst / "MANIFEST.json").read_bytes()) if copied else None}}


def build(run: Path, out: Path) -> dict:
    with tempfile.TemporaryDirectory() as td:
        info = stage(run, Path(td))
        with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
            for p in sorted(Path(td).rglob("*")):
                if p.is_file():
                    z.write(p, p.relative_to(td))
    with zipfile.ZipFile(out) as z:
        entries = {n: z.read(n) for n in z.namelist() if not n.endswith("/")}
    dataset_hashes = {sha256(p.read_bytes()): p.relative_to(ROOT).as_posix()
                      for p in (ROOT / "dataset").rglob("*") if p.is_file()}
    problems = inventory(entries, dataset_hashes, load_allowlist(entries.get(ALLOWLIST)))
    return {**info, "entries": len(entries), "bytes": out.stat().st_size,
            "problems": [f"{n}: {why}" for n, why in problems]}


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
        args = ["run", "--engine", summary["engine"], "--mode", "replay", "--split", summary["split"],
                "--ownership", summary["ownership"], "--out", str(td / "replay")]
        if summary["engine"] == "agent":
            args += ["--agent-scope", summary.get("agent_scope", "all")]
            if summary.get("model"):
                args += ["--model", summary["model"]]
        cmd = [str(py), "-c", POISONED] + args
        isolated = bool(shutil.which("unshare")) and subprocess.run(["unshare", "-rn", "true"]).returncode == 0
        if isolated:
            cmd = ["unshare", "-rn"] + cmd                  # no network interface at all during replay
        r = subprocess.run(cmd, cwd=u, env=env, capture_output=True, text=True)
        same = r.returncode == 0 and filecmp.cmp(td / "replay" / "output.csv", run / "output.csv", shallow=False)
        tail = (r.stdout + r.stderr).strip().splitlines()[-4:]
        v = subprocess.run([str(py), "code/main.py", "validate", str(td / "replay" / "output.csv"),
                            "--split", summary["split"]], cwd=u, capture_output=True, text=True) if r.returncode == 0 else None
        viewer_same = False
        if r.returncode == 0:
            vb = subprocess.run([str(py), "code/main.py", "viewer", "--run", str(td / "replay"), "--out",
                                 str(td / "rebuilt.html")], cwd=u, capture_output=True, text=True)
            viewer_same = vb.returncode == 0 and filecmp.cmp(td / "rebuilt.html", u / "code" / "viewer" / "viewer.html",
                                                             shallow=False)
        return {"returncode": r.returncode, "identical": same, "viewer_identical": viewer_same, "isolated": isolated,
                "network": "none (unshare -rn)" if isolated else "NOT isolated (unshare unavailable)",
                "provider_client_blocked": True,
                "validate": {"returncode": v.returncode, "last": (v.stdout.strip().splitlines() or ["?"])[-1]} if v else None,
                "scan": scan(u), "tail": tail}


def scan(u: Path) -> dict:
    """Things a clean unpack must not need or carry: developer paths, credentials, undeclared caches."""
    pats = {"developer path": re.compile(re.escape(str(ROOT)) + "|/root/"),
            "credential": re.compile(r"(?<![A-Za-z0-9_\-+/])(?:AIza[0-9A-Za-z_\-]{30,}|gh[opsu]_[0-9A-Za-z]{30,}|sk-[A-Za-z0-9]{20,})"
                                     r"|-----BEGIN [A-Z ]*PRIVATE KEY")}
    hits = {k: [] for k in pats}
    for p in u.rglob("*"):
        if p.is_file() and not p.is_symlink() and "dataset" not in p.relative_to(u).parts[:1]:
            t = p.read_text(errors="replace")
            for k, pat in pats.items():
                if pat.search(t):
                    hits[k].append(str(p.relative_to(u)))
    declared = set()
    for m in (u / "state" / "vision_cache" / "MANIFEST.json", u / "runs" / "cache" / "llm" / "MANIFEST.json"):
        if m.exists():
            declared |= {str((m.parent / k).relative_to(u)) for k in json.loads(m.read_text())} | {str(m.relative_to(u))}
    undeclared = [str(p.relative_to(u)) for top in ("state", "runs") if (u / top).exists()
                  for p in (u / top).rglob("*") if p.is_file() and str(p.relative_to(u)) not in declared
                  and "replay" not in p.relative_to(u).parts]
    return {**hits, "undeclared_cache_files": undeclared}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True, type=Path)
    ap.add_argument("--out", type=Path, default=ROOT / "code.zip")
    ap.add_argument("--skip-venv", action="store_true", help="reuse the current interpreter (faster, less clean)")
    ap.add_argument("--allow-unisolated", action="store_true", help="accept a replay without network isolation")
    ap.add_argument("--report", type=Path, help="also save {build, check} as JSON here (read by release_record.py)")
    a = ap.parse_args(argv)
    # the released archive is replaced only by an accepted build; a refused one stays beside it for inspection
    cand = a.out.with_name(a.out.name + ".candidate")
    info = build(a.run, cand)
    print(json.dumps(info, indent=1))
    if info["problems"]:
        print(f"refusing: the archive inventory is not clean; {a.out.name} untouched, build left in {cand.name}")
        if a.report:
            a.report.write_text(json.dumps({"build": info, "check": None}, indent=1) + "\n")
        return 1
    check = replay_check(cand, a.run, a.skip_venv)
    rows = json.loads((a.run / "summary.json").read_text())["rows"]
    check["sha256"] = {"code.zip": hashlib.sha256(cand.read_bytes()).hexdigest(),
                       "reference output.csv": hashlib.sha256((a.run / "output.csv").read_bytes()).hexdigest()}
    check["not_accepted_because"] = acceptance(check, rows, a.allow_unisolated)
    print(json.dumps(check, indent=1))
    if a.report:
        a.report.write_text(json.dumps({"build": info, "check": check}, indent=1) + "\n")
    if check["not_accepted_because"]:
        print(f"not accepted; {a.out.name} untouched, build left in {cand.name}")
        return 1
    os.replace(cand, a.out)
    print(f"accepted: {cand.name} → {a.out.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
