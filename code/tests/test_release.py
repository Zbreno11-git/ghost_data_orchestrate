"""S7 C7.3: what code.zip may hold and when its clean-unpack replay is accepted (code/release/checks.py).

Each negative fixture must fail for its own reason (asserted by text), so a check that refuses for another reason
cannot pass the test; each has a close positive.
"""
import hashlib
import json

import pytest

from conftest import CODE, DATASET
from release.checks import ALLOWLIST, REQUIRED, acceptance, inventory, load_allowlist

RULES = (DATASET / "deletion_rules.csv").read_bytes()
DS = {hashlib.sha256(RULES).hexdigest(): "dataset/deletion_rules.csv"}
FIX = "code/evaluation/custom_cases/x/dataset/deletion_rules.csv"


def _clean(**extra):
    e = {r: b"ok\n" for r in REQUIRED}
    e["code/ghostaudit/x.py"] = b"print(1)\n"
    e.update(extra)
    return e


def _reasons(entries, allow=None):
    return {n: why for n, why in inventory(entries, DS, allow or {})}


def test_a_clean_archive_passes():
    assert inventory(_clean(), DS, {}) == []


@pytest.mark.parametrize("name,data,reason", [
    ("code/vendor/deps.tgz", b"x", "nested archive"),
    ("code/notes.ZIP", b"x", "nested archive"),
    ("code/.env", b"GEMINI_API_KEY=x\n", "environment or credential file"),
    ("code/.env.local", b"x", "environment or credential file"),
    ("code/__pycache__/m.cpython-312.pyc", b"x", "directory __pycache__"),
    (".venv/lib/x.py", b"x", "directory .venv"),
    ("code/ghostaudit/m.pyc", b"x", "compiled file"),
    ("code/conf.toml", b"key = 'AIza" + b"A" * 35 + b"'", "credential pattern"),
    ("dataset/deletion_requests.csv", b"case_id\n", "supplied challenge dataset"),
    ("code/data/rules_copy.csv", RULES, "copy of the supplied dataset file dataset/deletion_rules.csv"),
])
def test_each_forbidden_entry_is_refused_for_its_own_reason(name, data, reason):
    got = _reasons(_clean(**{name: data}))
    assert name in got and reason in got[name], got


def test_a_missing_report_is_named():
    e = _clean()
    del e["code/evaluation/usage_report.md"]
    assert _reasons(e) == {"code/evaluation/usage_report.md": "required file missing"}


def test_the_fixture_allowlist_admits_only_the_exact_path_and_content():
    h = hashlib.sha256(RULES).hexdigest()
    assert inventory(_clean(**{FIX: RULES}), DS, {FIX: h}) == []                          # legitimate fixture
    assert FIX in _reasons(_clean(**{FIX: RULES}), {"code/other.csv": h})                 # another path: refused
    other = b"case_id,email\n"                                                           # same path, other dataset file
    ds2 = {**DS, hashlib.sha256(other).hexdigest(): "dataset/deletion_requests.csv"}
    got = {n: w for n, w in inventory(_clean(**{FIX: other}), ds2, {FIX: h})}
    assert "deletion_requests.csv" in got[FIX]


def test_the_shipped_allowlist_matches_the_fixtures_and_covers_every_dataset_copy():
    allow = load_allowlist((CODE.parent / ALLOWLIST).read_bytes())
    for path, h in allow.items():
        assert hashlib.sha256((CODE.parent / path).read_bytes()).hexdigest() == h, path
    ds = {hashlib.sha256(p.read_bytes()).hexdigest() for p in DATASET.rglob("*") if p.is_file()}
    copies = {p.relative_to(CODE.parent).as_posix() for p in CODE.rglob("*")
              if p.is_file() and "__pycache__" not in p.parts and hashlib.sha256(p.read_bytes()).hexdigest() in ds}
    assert copies == set(allow) and len(copies) >= 5                                    # derived, not hand-listed
    doc = (CODE / "evaluation" / "custom_cases" / "FIXTURE_ALLOWLIST.md").read_text()
    assert all(p in doc for p in allow)


GOOD = {"returncode": 0, "identical": True, "viewer_identical": True, "isolated": True, "provider_client_blocked": True,
        "validate": {"returncode": 0, "last": "0 violations in out.csv against 518 targets requests"},
        "scan": {"developer path": [], "credential": [], "undeclared_cache_files": []}}


def test_an_accepted_replay_has_no_reasons():
    assert acceptance(GOOD, 518) == []


@pytest.mark.parametrize("change,reason", [
    ({"validate": {"returncode": 1, "last": "3 violations in out.csv against 518 targets requests"}}, "validator"),
    ({"validate": {"returncode": 0, "last": "10 violations in out.csv against 518 targets requests"}}, "validator"),
    ({"validate": {"returncode": 0, "last": "0 violations in out.csv against 32 samples requests"}}, "validator"),
    ({"validate": None}, "validator"),
    ({"identical": False}, "differs from the reference"),
    ({"viewer_identical": False}, "viewer differs"),
    ({"isolated": False}, "NOT network-isolated"),
    ({"provider_client_blocked": None}, "provider-client"),
    ({"scan": {"developer path": ["code/x.py"], "credential": [], "undeclared_cache_files": []}}, "scan not clean"),
    ({"returncode": 2}, "replay exited 2"),
])
def test_identical_bytes_are_not_acceptance_when_another_check_fails(change, reason):
    why = acceptance({**GOOD, **change}, 518)
    assert len(why) == 1 and reason in why[0], why


def test_an_unisolated_replay_is_accepted_only_when_the_caller_says_so():
    assert acceptance({**GOOD, "isolated": False}, 518, allow_unisolated=True) == []
