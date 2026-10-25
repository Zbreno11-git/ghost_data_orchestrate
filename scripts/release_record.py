"""Write the release record and the checksum manifest for the final artifact set (S7 C7.7).

Reads only files: the final run (summary.json, output.csv), the package check result saved by
`package_code.py --report`, the evaluation metrics of the samples run, the Mac acceptance notes (if any), and the
release directory holding the four upload files. Writes:
- `<release dir>/SHA256SUMS` and `docs/release/SHA256SUMS` (identical; outside every archive they hash);
- `docs/release/RELEASE_RECORD.md`.

Usage: python3 scripts/release_record.py --run runs/s7/final --samples runs/s7/final-samples
         --package-report runs/s7/package_report.json --release-dir ~/ghost-release [--mac docs/release/mac_acceptance.md]
Exit 1 if an upload file is missing.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "code"))
FILES = ("code.zip", "output.csv", "log.txt", "agent-trace.zip")


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", type=Path, required=True)
    ap.add_argument("--samples", type=Path, required=True)
    ap.add_argument("--package-report", type=Path, required=True)
    ap.add_argument("--release-dir", type=Path, required=True)
    ap.add_argument("--mac", type=Path)
    a = ap.parse_args(argv)
    from evaluation.metrics import evaluate, load_output
    missing = [f for f in FILES if not (a.release_dir / f).exists()]
    if missing:
        print(f"missing upload files in {a.release_dir}: {missing}")
        return 1
    sums = "".join(f"{sha(a.release_dir / f)}  {f}\n" for f in FILES)
    (a.release_dir / "SHA256SUMS").write_text(sums)
    (ROOT / "docs" / "release" / "SHA256SUMS").write_text(sums)
    s = json.loads((a.run / "summary.json").read_text())
    pk = json.loads(a.package_report.read_text())
    m = evaluate(load_output(a.samples / "output.csv"), load_output(ROOT / "dataset" / "sample_output.csv"))
    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True).stdout.strip()
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    r = lambda k: f"{m[k]['num']}/{m[k]['den']}"  # noqa: E731
    L = ["# Release record", "", f"Written {now} by `scripts/release_record.py`; every value is read from a file.", "",
         "## Source and configuration", "",
         f"- Source revision (git HEAD when written): `{head}`",
         f"- Final run: `{a.run}`: engine {s['engine']}, model {s.get('model')}, agent scope {s.get('agent_scope')}, "
         f"ownership {s['ownership']}, asserted mechanisms {s.get('asserted_mechanisms')}, time policy {s.get('time_policy')}",
         "- Fingerprints: " + ", ".join(f"{k} `{v[:16]}…`" for k, v in s.get("fingerprints", {}).items()),
         "- Run artifacts (sha256): " + ", ".join(f"{k} `{v[:16]}…`" for k, v in s.get("artifacts", {}).items()),
         f"- Replay manifests (sha256): " + ", ".join(f"{k} `{(v or 'none')[:16]}…`" for k, v in pk["build"]["manifests"].items()),
         "", "## Results", "",
         f"- Targets: {s['rows']} rows; status {json.dumps(s['status'])}; support {json.dumps(s['support'])}",
         f"- Public samples (full denominators): status {r('status_accuracy')}, whole-case {r('whole_case_exact')}, "
         f"step P {r('step_precision')}, R {r('step_recall')}, F1 {m['step_f1']:.4f}, cited recall "
         f"{r('cited_evidence_recall')}, sequence {r('sequence_accuracy')}. Not a hidden-target estimate.",
         "", "## VPS clean-unpack check", "",
         f"- Inventory problems: {pk['build']['problems'] or 'none'}; entries {pk['build']['entries']}, {pk['build']['bytes']} bytes",
         f"- Replay: exit {pk['check']['returncode']}, network {pk['check']['network']}, provider client blocked "
         f"{pk['check']['provider_client_blocked']}, output identical {pk['check']['identical']}, viewer identical "
         f"{pk['check']['viewer_identical']}, validate: {pk['check']['validate']['last'] if pk['check']['validate'] else None}",
         f"- Not accepted because: {pk['check']['not_accepted_because'] or 'nothing (accepted)'}",
         "", "## Mac acceptance", "",
         (a.mac.read_text().strip() if a.mac and a.mac.exists() else "**PENDING**: not yet run on the Mac."),
         "", "## Upload files (release directory)", "", "| file | bytes | sha256 |", "|---|---|---|"]
    L += [f"| {f} | {(a.release_dir / f).stat().st_size} | `{sha(a.release_dir / f)}` |" for f in FILES]
    L += ["", "`SHA256SUMS` sits beside them and in `docs/release/`, outside every archive it hashes. After the freeze, "
          "any change to one of these files reopens the affected checks and produces a new record.", ""]
    (ROOT / "docs" / "release" / "RELEASE_RECORD.md").write_text("\n".join(L))
    print(sums, end="")
    print(f"wrote docs/release/RELEASE_RECORD.md and {a.release_dir / 'SHA256SUMS'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
