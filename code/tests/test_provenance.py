"""S7 C7.2: provenance is saved with the run and verified before it is shown (Breno amendment 5).

An unchanged obs_id does not prove unchanged content, so an explanation attaches provenance only from the run's own
`provenance.jsonl`, and only when its sha256 and run fingerprint match `summary.json`. A modified, foreign or
missing provenance file is reported, never shown as verified.
"""
import json
import shutil
import subprocess
import sys

import pytest

from conftest import CODE
from ghostaudit.explain import case_view, explain
from ghostaudit.provenance import referenced_obs_ids, sha256_file, verify_run
from ghostaudit.runner import run_deterministic

CASE = CODE / "evaluation" / "custom_cases" / "historical_email_replica" / "dataset"
OTHER = CODE / "evaluation" / "custom_cases" / "success_claim_contradicted" / "dataset"


@pytest.fixture(scope="module")
def runs(tmp_path_factory):
    a, b = tmp_path_factory.mktemp("a"), tmp_path_factory.mktemp("b")
    run_deterministic(CASE, "targets", a)
    run_deterministic(OTHER, "targets", b)
    cid = json.loads((a / "decisions.jsonl").read_text().splitlines()[0])["case_id"]
    return a, b, cid


def _copy(run, tmp_path, name):
    dst = tmp_path / name
    shutil.copytree(run, dst)
    return dst


def test_the_run_saves_every_referenced_observation_with_hashes_and_fingerprints(runs):
    a, _, cid = runs
    s = json.loads((a / "summary.json").read_text())
    assert set(s["fingerprints"]) == {"code", "dataset", "extraction", "config", "run"}
    assert s["artifacts"]["provenance.jsonl"] == sha256_file(a / "provenance.jsonl")
    lines = (a / "provenance.jsonl").read_text().splitlines()
    saved = {json.loads(l)["obs_id"] for l in lines[1:]}
    wanted = set().union(*(referenced_obs_ids(json.loads(l)) for l in (a / "decisions.jsonl").read_text().splitlines()))
    assert wanted and wanted == saved                                   # no more, no less
    assert verify_run(a)[0] == "verified"
    v = case_view(a, cid)
    shown = [o for x in v["resources"] for o in x["links"] + [x["proof"]] + [c["obs"] for c in x["copies"]] if o]
    assert shown and all("unavailable" not in o and o["file"] for o in shown)


def test_a_modified_provenance_file_is_never_shown_as_verified(runs, tmp_path):
    a, _, cid = runs
    r = _copy(a, tmp_path, "tampered")
    lines = (r / "provenance.jsonl").read_text().splitlines()
    rec = json.loads(lines[1])
    rec["captured_at"] = "1999-01-01T00:00:00+00:00"                       # one field of one record
    lines[1] = json.dumps(rec, sort_keys=True)
    (r / "provenance.jsonl").write_text("\n".join(lines) + "\n")
    status, _, msg = verify_run(r)
    assert status == "integrity_failed" and "sha256" in msg
    text = explain(r, cid)
    assert "1999-01-01" not in text and "provenance not attached" in text and "integrity_failed" in text


def test_a_provenance_file_from_another_run_is_rejected_even_with_a_matching_hash(runs, tmp_path):
    a, b, cid = runs
    r = _copy(a, tmp_path, "foreign")
    shutil.copy(b / "provenance.jsonl", r / "provenance.jsonl")
    s = json.loads((r / "summary.json").read_text())
    s["artifacts"]["provenance.jsonl"] = sha256_file(r / "provenance.jsonl")     # the hash alone would pass
    (r / "summary.json").write_text(json.dumps(s))
    status, _, msg = verify_run(r)
    assert status == "integrity_failed" and "another run" in msg
    assert all("unavailable" in o for x in case_view(r, cid)["resources"] for o in x["links"])


def test_a_legacy_run_without_saved_provenance_gets_a_warning_not_a_reingest(runs, tmp_path):
    a, _, cid = runs
    r = _copy(a, tmp_path, "legacy")
    (r / "provenance.jsonl").unlink()
    s = json.loads((r / "summary.json").read_text())
    s.pop("artifacts")
    (r / "summary.json").write_text(json.dumps(s))
    assert verify_run(r)[0] == "legacy"
    assert "provenance not attached" in explain(r, cid)


def test_explain_reads_no_dataset_and_imports_no_ingest_model_or_provider(runs):
    a, _, cid = runs
    code = (f"import sys; sys.path.insert(0, {str(CODE)!r}); from ghostaudit.explain import explain; "
            f"from pathlib import Path; t = explain(Path({str(a)!r}), {cid!r}); assert 'linked by `' in t; "
            "bad = [m for m in sys.modules if m.startswith(('ghostaudit.ingest', 'ghostaudit.llm', 'google'))]; "
            "assert not bad, bad")
    r = subprocess.run([sys.executable, "-c", code], env={"PATH": "/usr/bin:/bin"}, capture_output=True, text=True)
    assert r.returncode == 0, r.stderr[-800:]
