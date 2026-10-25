"""S7 C7.2: the offline evidence viewer shows exactly what explain shows, embeds untrusted text inertly, needs no
network, model or dataset, and its canonical HTML is byte-identical across run directories (Breno amendment 5)."""
import json
import re
import shutil
import subprocess
import sys

import pytest

from conftest import CODE
from ghostaudit.explain import case_view
from ghostaudit.runner import run_deterministic

sys.path.insert(0, str(CODE))
from viewer.build import PAGE, build, build_data, render, script_safe_json  # noqa: E402

CASE = CODE / "evaluation" / "custom_cases" / "historical_email_replica" / "dataset"
HOSTILE = '</script><img src=x onerror="window.__pwned=1"><!--   & </SCRIPT >'
BLOCK = re.compile(r'<script type="application/json" id="data">(.*?)</script>', re.S)


@pytest.fixture(scope="module")
def run(tmp_path_factory):
    out = tmp_path_factory.mktemp("run")
    run_deterministic(CASE, "targets", out)
    return out


def test_hostile_text_round_trips_as_data_and_cannot_close_the_script(run):
    data = build_data(run)
    data["cases"][0]["reasons"].append(HOSTILE)
    html = render(data)
    blocks = BLOCK.findall(html)
    assert len(blocks) == 1                                   # the hostile </script> did not end the block early
    block = blocks[0]
    assert "<" not in block and ">" not in block and "&" not in block and " " not in block
    assert json.loads(block) == json.loads(script_safe_json(data)) and HOSTILE in json.loads(block)["cases"][0]["reasons"]


def test_the_page_renders_text_only_and_reaches_no_network():
    assert "innerHTML" not in PAGE and "outerHTML" not in PAGE and "insertAdjacentHTML" not in PAGE
    assert not re.search(r"https?://", PAGE) and "fetch(" not in PAGE and "XMLHttpRequest" not in PAGE
    assert "default-src 'none'" in PAGE


def test_every_case_in_the_viewer_equals_explains_case_view(run):
    data = build_data(run)
    lines = (run / "decisions.jsonl").read_text().splitlines()
    assert len(data["cases"]) == len(lines) >= 1

    def resolve(x):
        if isinstance(x, dict):
            return data["prov"][x["ref"]] if set(x) == {"ref"} else {k: resolve(v) for k, v in x.items()}
        return [resolve(v) for v in x] if isinstance(x, list) else x
    for c in data["cases"]:
        assert resolve(c) == case_view(run, c["case_id"])
    assert data["run"]["provenance"]["status"] == "verified" and data["prov"]


def test_a_run_without_trace_or_provenance_is_labelled_not_verified(run, tmp_path):
    r = tmp_path / "legacy"
    shutil.copytree(run, r)
    d = json.loads((r / "decisions.jsonl").read_text().splitlines()[0])
    d.pop("trace")
    (r / "decisions.jsonl").write_text(json.dumps(d) + "\n")
    data = build_data(r)
    assert data["run"]["provenance"]["status"] == "damaged"   # decisions.jsonl no longer matches its hash
    assert data["cases"][0]["has_trace"] is False and data["prov"] == {}


def test_canonical_html_is_byte_identical_across_run_directories(run, tmp_path):
    a, b = tmp_path / "x" / "first-run", tmp_path / "y" / "another-name"
    shutil.copytree(run, a)
    shutil.copytree(run, b)
    ma, mb = build(a, tmp_path / "a.html"), build(b, tmp_path / "b.html")
    assert (tmp_path / "a.html").read_bytes() == (tmp_path / "b.html").read_bytes()
    assert ma["html_sha256"] == mb["html_sha256"] and ma["run_dir"] != mb["run_dir"]   # paths only in the sidecar
    html = (tmp_path / "a.html").read_text()
    assert str(tmp_path) not in html and "first-run" not in html


def test_building_imports_no_model_provider_or_ingest(run, tmp_path):
    code = (f"import sys; sys.path.insert(0, {str(CODE)!r}); from pathlib import Path; from viewer.build import build; "
            f"build(Path({str(run)!r}), Path({str(tmp_path / 'v.html')!r})); "
            "bad = [m for m in sys.modules if m.startswith(('ghostaudit.ingest', 'ghostaudit.llm', 'google'))]; "
            "assert not bad, bad")
    r = subprocess.run([sys.executable, "-c", code], env={"PATH": "/usr/bin:/bin"}, capture_output=True, text=True)
    assert r.returncode == 0, r.stderr[-800:]
