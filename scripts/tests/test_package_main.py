"""S7: a refused build never replaces the released code.zip (the last accepted archive stays the deliverable).

`scripts/package_code.py` builds into `<out>.candidate`, checks that file, and moves it onto `<out>` only when the
inventory is clean and the replay is accepted. The build and the replay are stubbed: this tests the decision, the
checks themselves are tested in code/tests/test_release.py. Repository-only (scripts/ is not shipped in code.zip),
so it lives here and not in code/tests, which the unpacked package must be able to run.
"""
import importlib.util
import json

from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("package_code", SCRIPTS / "package_code.py")
pc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pc)

GOOD = {"returncode": 0, "identical": True, "viewer_identical": True, "isolated": True, "provider_client_blocked": True,
        "validate": {"returncode": 0, "last": "0 violations in out.csv against 2 targets requests"},
        "scan": {"developer path": [], "credential": [], "undeclared_cache_files": []}}


@pytest.fixture
def setup(tmp_path, monkeypatch):
    run = tmp_path / "run"
    run.mkdir()
    (run / "summary.json").write_text(json.dumps({"rows": 2}))
    (run / "output.csv").write_text("case_id,deletion_status,steps_json\n")
    out = tmp_path / "code.zip"
    out.write_bytes(b"RELEASED")
    seen = {}

    def build(r, path):
        seen["built"] = path
        path.write_bytes(b"NEW")
        return {"problems": seen.get("problems", []), "entries": 1, "bytes": 3}

    def replay(path, r, skip):
        seen["checked"] = path
        return dict(seen.get("check", GOOD))
    monkeypatch.setattr(pc, "build", build)
    monkeypatch.setattr(pc, "replay_check", replay)
    return run, out, seen


def test_an_accepted_build_replaces_the_release_and_leaves_no_candidate(setup):
    run, out, seen = setup
    assert pc.main(["--run", str(run), "--out", str(out)]) == 0
    assert seen["built"] == seen["checked"] != out                 # the check ran on the candidate, not the release
    assert out.read_bytes() == b"NEW" and not seen["built"].exists()


@pytest.mark.parametrize("bad", ["replay", "inventory"])
def test_a_refused_build_leaves_the_released_archive_untouched(setup, bad):
    run, out, seen = setup
    if bad == "replay":
        seen["check"] = {**GOOD, "identical": False}
    else:
        seen["problems"] = [("code/.env", "environment or credential file")]
    assert pc.main(["--run", str(run), "--out", str(out)]) == 1
    assert out.read_bytes() == b"RELEASED"
    assert seen["built"].read_bytes() == b"NEW"                     # kept for inspection, beside the release
