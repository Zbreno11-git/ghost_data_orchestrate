"""Custom evaluation cases (A13): each is a self-contained mini-dataset whose expected output obeys the contract
and whose evidence every adapter can ingest. The case list is derived from the directory, with a floor of 3."""
from pathlib import Path

import pytest

from conftest import CODE
from ghostaudit.ingest.manifest import evidence_times, read_csv
from ghostaudit.ingest.pipeline import ingest_all
from ghostaudit.validate import validate_file

CASES = sorted(p for p in (CODE / "evaluation" / "custom_cases").iterdir() if (p / "expected_output.csv").exists())


def test_at_least_three_custom_cases():
    assert len(CASES) >= 3


@pytest.mark.parametrize("case", CASES, ids=lambda p: p.name)
def test_expected_output_is_contract_valid(case):
    ds = case / "dataset"
    requests = {r["case_id"]: r for r in read_csv(ds / "deletion_requests.csv")}
    assert len(requests) == 1
    assert validate_file(case / "expected_output.csv", requests, evidence_times(ds)) == []


@pytest.mark.parametrize("case", CASES, ids=lambda p: p.name)
def test_mini_dataset_ingests_cleanly(case):
    store, cov = ingest_all(case / "dataset")
    assert cov.files and {c.status for c in cov.files} == {"processed"} and len(store) > 0
