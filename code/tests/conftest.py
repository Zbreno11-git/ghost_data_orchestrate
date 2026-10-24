import csv
import json
import sys
from pathlib import Path

import pytest

CODE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(CODE))
REPO = CODE.parent
DATASET = REPO / "dataset"


def read_csv(path):
    with open(path, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


@pytest.fixture(scope="session")
def dataset_dir():
    return DATASET


@pytest.fixture(scope="session")
def sample_gold():
    """Evaluation-side only: sample_output.csv as {case_id: (status, steps)}."""
    return {r["case_id"]: (r["deletion_status"], json.loads(r["steps_json"]))
            for r in read_csv(DATASET / "sample_output.csv")}


@pytest.fixture(scope="session")
def sample_requests():
    return {r["case_id"]: r for r in read_csv(DATASET / "sample_deletion_requests.csv")}
