"""S6 C6.2: `main.py explain` prints only what the run recorded, never calls a model, and says so when a fact
is missing from the trace."""
import json
import re
import subprocess
import sys

import pytest

from conftest import CODE
from ghostaudit.explain import MISSING, explain
from ghostaudit.runner import run_deterministic

CASE = CODE / "evaluation" / "custom_cases" / "historical_email_replica" / "dataset"
OBS_ID = re.compile(r"`([A-Za-z0-9_]+#[^`]+)`")


@pytest.fixture(scope="module")
def fixture_run(tmp_path_factory):
    out = tmp_path_factory.mktemp("run")
    run_deterministic(CASE, "targets", out)
    cid = json.loads((out / "decisions.jsonl").read_text().splitlines()[0])["case_id"]
    return out, cid


def test_every_printed_observation_comes_from_the_run_trace(fixture_run):
    out, cid = fixture_run
    text = explain(out, cid, CASE)
    trace = (out / "decisions.jsonl").read_text()
    printed = set(OBS_ID.findall(text))
    assert printed, "the fixture case must cite at least one observation"
    assert {o for o in printed if o not in trace} == set()


def test_the_trace_carries_intent_person_account_and_rules(fixture_run):
    out, cid = fixture_run
    d = json.loads((out / "decisions.jsonl").read_text().splitlines()[0])
    assert {"intent", "subject", "account", "excluded", "ambiguities", "heuristic", "audit_at"} <= set(d["trace"])
    assert d["trace"]["subject"]["identifiers"] and all("role" in i and "source" in i
                                                        for i in d["trace"]["subject"]["identifiers"])
    assert all("rule_id" in x for x in d["decisions"])


def test_a_run_without_a_trace_prints_not_recorded(fixture_run, tmp_path):
    out, cid = fixture_run
    d = json.loads((out / "decisions.jsonl").read_text().splitlines()[0])
    d.pop("trace")
    (tmp_path / "decisions.jsonl").write_text(json.dumps(d) + "\n")
    text = explain(tmp_path, cid, CASE)
    lines = text.splitlines()
    # Each trace-dependent line says so on its own; one MISSING elsewhere must not satisfy this.
    for prefix in ("- Intent", "- Account deduction", "- Heuristic flag"):
        assert MISSING in next(l for l in lines if l.startswith(prefix)), prefix
    person = lines[lines.index("## Person") + 2]
    rejected = lines[lines.index("### Rejected links and open questions") + 2]
    assert person == f"- {MISSING}" and rejected == f"- {MISSING}"


def test_explain_never_loads_the_model_gateway_and_needs_no_key_or_network(fixture_run):
    out, cid = fixture_run
    code = (f"import sys; sys.path.insert(0, {str(CODE)!r}); from ghostaudit.explain import explain; "
            f"from pathlib import Path; explain(Path({str(out)!r}), {cid!r}, Path({str(CASE)!r})); "
            "bad = [m for m in sys.modules if m.startswith(('ghostaudit.llm', 'google'))]; "
            "assert not bad, bad")
    env = {"PATH": "/usr/bin:/bin", "HTTPS_PROXY": "http://127.0.0.1:9", "HTTP_PROXY": "http://127.0.0.1:9"}
    r = subprocess.run([sys.executable, "-c", code], env=env, capture_output=True, text=True)
    assert r.returncode == 0, r.stderr[-800:]
