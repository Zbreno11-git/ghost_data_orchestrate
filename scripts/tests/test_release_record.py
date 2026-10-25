"""S7 C7.7: the release record and checksums describe exactly the files in the release folder, and nothing is
written when those are not the accepted archive and the final run's output. Scratch release and docs folders."""
import hashlib
import importlib.util
import json
import shutil
import subprocess
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[1]
REPO = SCRIPTS.parent
spec = importlib.util.spec_from_file_location("release_record", SCRIPTS / "release_record.py")
rr = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rr)


def _sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


@pytest.fixture
def world(tmp_path):
    run, samples, rel, docs = (tmp_path / n for n in ("run", "samples", "release", "docs"))
    for d in (run, samples, rel):
        d.mkdir()
    (run / "output.csv").write_text("case_id,deletion_status,steps_json\ncase_1,COMPLETE,[]\n")
    (run / "summary.json").write_text(json.dumps({
        "engine": "agent", "model": "m", "agent_scope": "non_resolved", "ownership": "strict",
        "asserted_mechanisms": ["only_feasible_row"], "time_policy": "snapshot_capture", "rows": 1,
        "status": {"COMPLETE": 1}, "support": {"resolved": 1}, "fingerprints": {"run": "f" * 64},
        "artifacts": {"output.csv": _sha(run / "output.csv")}}))
    shutil.copy(REPO / "dataset" / "sample_output.csv", samples / "output.csv")        # a perfect samples run
    (rel / "code.zip").write_bytes(b"PK-accepted")
    shutil.copy(run / "output.csv", rel / "output.csv")
    (rel / "log.txt").write_text("## log\n")
    (rel / "agent-trace.zip").write_bytes(b"PK-trace")
    report = tmp_path / "package_report.json"
    report.write_text(json.dumps({
        "build": {"problems": [], "entries": 3, "bytes": 11, "manifests": {"runs/cache/llm/MANIFEST.json": "a" * 64}},
        "check": {"returncode": 0, "network": "none (unshare -rn)", "provider_client_blocked": True,
                  "identical": True, "viewer_identical": True, "not_accepted_because": [],
                  "validate": {"returncode": 0, "last": "0 violations in out.csv against 1 targets requests"},
                  "sha256": {"code.zip": _sha(rel / "code.zip")}}}))
    args = ["--run", str(run), "--samples", str(samples), "--package-report", str(report),
            "--release-dir", str(rel), "--docs-dir", str(docs)]
    return rel, docs, args, tmp_path


def test_the_checksums_and_record_cover_exactly_the_four_upload_files(world):
    rel, docs, args, _ = world
    assert rr.main(args) == 0
    sums = (rel / "SHA256SUMS").read_text()
    assert sums == (docs / "SHA256SUMS").read_text()
    assert sorted(l.split("  ")[1] for l in sums.strip().split("\n")) == sorted(rr.FILES)
    check = subprocess.run(["sha256sum", "-c", "SHA256SUMS"], cwd=rel, capture_output=True, text=True)
    assert check.returncode == 0 and check.stdout.count(": OK") == 4
    rec = (docs / "RELEASE_RECORD.md").read_text()
    assert all(_sha(rel / f) in rec for f in rr.FILES)
    assert "whole-case 32/32" in rec and "**PENDING**" in rec                     # no Mac notes given


def test_the_mac_notes_are_recorded_when_given(world):
    rel, docs, args, tmp = world
    mac = tmp / "mac.md"
    mac.write_text("macOS 15.1, Apple M2: IDENTICAL, 0 violations, 310 passed, VIEWER-IDENTICAL")
    assert rr.main(args + ["--mac", str(mac)]) == 0
    rec = (docs / "RELEASE_RECORD.md").read_text()
    assert "VIEWER-IDENTICAL" in rec and "PENDING" not in rec


@pytest.mark.parametrize("change,reason", [
    (lambda rel: (rel / "code.zip").write_bytes(b"PK-other"), "code.zip"),          # not the accepted archive
    (lambda rel: (rel / "output.csv").write_text("case_id\n"), "output.csv"),       # not the final run's output
    (lambda rel: (rel / "agent-trace.zip").unlink(), "missing"),
])
def test_nothing_is_written_for_a_release_that_is_not_the_checked_one(world, capsys, change, reason):
    rel, docs, args, _ = world
    change(rel)
    assert rr.main(args) == 1
    assert reason in capsys.readouterr().out
    assert not (rel / "SHA256SUMS").exists() and not docs.exists()
