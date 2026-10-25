"""S6 C6.5: metamorphic robustness, end to end through `run_deterministic` on small synthetic datasets.

Each test changes the inputs in a way that must not change the answer:
- input order;
- an identical duplicate of the evidence;
- another person's record;
- evidence captured after the cutoff.

Each test compares against the unmodified dataset run in the same test, so it pins invariance, not a
hand-written answer. The safeguard behind each is disabled once by a mutation (see session-06.md).
"""
import csv
import json
import shutil

from conftest import CODE
from ghostaudit.runner import run_deterministic

CASES = CODE / "evaluation" / "custom_cases"


def _copy(case: str, tmp_path, name: str):
    dst = tmp_path / name
    shutil.copytree(CASES / case / "dataset", dst)
    return dst


def _run(ds, tmp_path, name):
    out = tmp_path / f"out-{name}"
    summary = run_deterministic(ds, "targets", out)
    assert summary["ingest_failed_files"] == [], summary["ingest_failed_files"]   # a fixture that is never read proves nothing
    rows = list(csv.DictReader(open(out / "output.csv", encoding="utf-8")))
    decs = [json.loads(l) for l in open(out / "decisions.jsonl", encoding="utf-8")]
    return rows, decs


def _shape(rows, decs):
    """What must not move: status, every step but its citation, support, and the copies seen per resource."""
    steps = {r["case_id"]: [{k: v for k, v in s.items() if k != "evidence_id"} for s in json.loads(r["steps_json"])]
             for r in rows}
    return ({r["case_id"]: r["deletion_status"] for r in rows}, steps,
            {d["case_id"]: d["support"] for d in decs},
            {d["case_id"]: {x["resource_id"]: len(x["copies"]) for x in d["decisions"]} for d in decs})


def _append_csv(path, row: dict):
    with open(path, "a", newline="", encoding="utf-8") as fh:
        csv.DictWriter(fh, fieldnames=list(row)).writerow(row)


def _reverse_csv(path):
    lines = path.read_text(encoding="utf-8").splitlines()
    path.write_text("\n".join([lines[0], *reversed(lines[1:])]) + "\n", encoding="utf-8")


def test_shuffled_inputs_give_the_same_answer(tmp_path):
    """A later NOT_FOUND must win over an earlier FOUND whatever the order of records, files and table rows."""
    variants = {}
    for name in ("ordered", "reversed"):
        ds = _copy("success_claim_contradicted", tmp_path, name)
        f = ds / "evidence" / "records" / "search_service_lookup_c11.json"
        doc = json.loads(f.read_text())
        doc["records"].append({"recorded_at": "2026-07-15T11:59:40Z", "system": "search_service",
                               "resource_id": "search_9011", "record_type": "SEARCH_INDEX_ENTRY",
                               "result": "NOT_FOUND", "subject_reference": "teo.valkenburg@quillpost.example"})
        if name == "reversed":
            doc["records"].reverse()
            for p in ds.glob("*.csv"):
                _reverse_csv(p)
        f.write_text(json.dumps(doc, indent=2))
        variants[name] = _run(ds, tmp_path, name)
    (rows_a, decs_a), (rows_b, decs_b) = variants["ordered"], variants["reversed"]
    assert rows_a == rows_b
    assert _shape(rows_a, decs_a) == _shape(rows_b, decs_b)
    assert rows_a[0]["deletion_status"] == "COMPLETE"       # the later NOT_FOUND decided it, in both orders
    control = _run(_copy("success_claim_contradicted", tmp_path, "control"), tmp_path, "control")
    assert control[0][0]["deletion_status"] == "INCOMPLETE"  # without it, the FOUND stands


def test_duplicated_evidence_adds_no_steps_and_no_confidence(tmp_path):
    base = _run(_copy("historical_email_replica", tmp_path, "base"), tmp_path, "base")
    ds = _copy("historical_email_replica", tmp_path, "dup")
    src = ds / "evidence" / "databases" / "account_service_snapshot_c01.sql"
    shutil.copy(src, src.with_name("account_service_snapshot_c01_copy.sql"))
    _append_csv(ds / "evidence_files.csv", {"file_id": "evidence_c01b",
                                            "file_path": "evidence/databases/account_service_snapshot_c01_copy.sql",
                                            "origin": "account_service_dba_export", "captured_at": "2026-08-12T09:30:00Z"})
    dup = _run(ds, tmp_path, "dup")
    assert any(s["evidence_id"] == "evidence_c01" for r in base[0] for s in json.loads(r["steps_json"]))
    assert _shape(*dup) == _shape(*base)
    cited = {s["evidence_id"] for r in dup[0] for s in json.loads(r["steps_json"]) if s["evidence_id"]}
    assert cited <= {"evidence_c01", "evidence_c01b"}


def _other_person(tmp_path, name: str, user_id: str, email: str):
    """A profile row in the same snapshot table: someone with the subject's exact name (a weak identifier, kept
    by the SQL adapter as `full_name`) and their own email."""
    ds = _copy("historical_email_replica", tmp_path, name)
    _append_csv(ds / "user_identities.csv", {"user_id": "user_9003", "name": "Marisol Quintanar",
                                             "email": "mq.studio@harborline.example", "phone": "+1-555-0199",
                                             "email_hash": "0" * 64, "updated_at": "2026-06-01T10:00:00Z"})
    sql = ds / "evidence" / "databases" / "account_service_snapshot_c01.sql"
    sql.write_text(sql.read_text() + "INSERT INTO customer_profiles_primary VALUES ('account_9003','" + user_id +
                   "','Marisol Quintanar','" + email + "','+1-555-0199','ACTIVE','2026-07-01T10:00:00Z');\n")
    return _run(ds, tmp_path, name)


def test_another_persons_record_does_not_contaminate_the_case(tmp_path):
    base = _run(_copy("historical_email_replica", tmp_path, "base"), tmp_path, "base")
    other = _other_person(tmp_path, "other", "user_9003", "mq.studio@harborline.example")
    assert other[0] == base[0]
    assert _shape(*other) == _shape(*base)
    assert "account_9003" not in json.dumps(other[1])
    # Control: the same row carrying the subject's historical email (and no other person's id) does reach the case.
    mine = _other_person(tmp_path, "mine", "", "m.quintanar@orchidmail.example")
    assert "account_9003" in json.dumps(mine[1])


def test_post_cutoff_evidence_does_not_change_the_historical_answer(tmp_path):
    """A file captured after audit_at, holding a record of the subject dated before it (the two-clock trap)."""
    base = _run(_copy("historical_email_replica", tmp_path, "base"), tmp_path, "base")
    late = _late_file(tmp_path, "late", "2026-08-25T12:00:00Z")
    assert late[0] == base[0]
    assert _shape(*late) == _shape(*base)
    assert "search_9400" not in json.dumps(late[1])
    # Control: the same file captured before the cutoff does change the case.
    early = _late_file(tmp_path, "early", "2026-08-19T12:00:00Z")
    assert "search_9400" in json.dumps(early[1]) and early[0] != base[0]


def _late_file(tmp_path, name: str, captured: str):
    ds = _copy("historical_email_replica", tmp_path, name)
    (ds / "evidence" / "records").mkdir()
    (ds / "evidence" / "records" / "support_lookup_c92.json").write_text(json.dumps({
        "exported_at": captured, "origin": "support_record_lookup", "record_count": 1, "records": [
            {"recorded_at": "2026-08-18T09:00:00Z", "system": "search_service", "resource_id": "search_9400",
             "record_type": "SEARCH_INDEX_ENTRY", "result": "FOUND",
             "subject_reference": "m.quintanar@orchidmail.example"}]}, indent=2))
    _append_csv(ds / "evidence_files.csv", {"file_id": "evidence_c92", "file_path": "evidence/records/support_lookup_c92.json",
                                            "origin": "support_record_lookup", "captured_at": captured})
    return _run(ds, tmp_path, name)
