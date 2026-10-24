"""C3.1: identity fixed point as of audit_at (current + history, exact normalized matching, ambiguity, rollback)."""
from datetime import datetime, timezone

import pytest

from conftest import DATASET, read_csv
from ghostaudit.identity import Ambiguity, IdentityIndex, Subject, email_hash
from ghostaudit.timeutil import parse_ts


@pytest.fixture(scope="module")
def index():
    return IdentityIndex(read_csv(DATASET / "user_identities.csv"), read_csv(DATASET / "user_audit_log.csv"))


def _resolve(index, sample_requests, case_id):
    q = sample_requests[case_id]
    return index.resolve(q["email"], parse_ts(q["audit_at"]))


def test_email_hash_rule_holds_on_every_snapshot_row():
    rows = read_csv(DATASET / "user_identities.csv")
    assert len(rows) >= 850
    assert sum(email_hash(r["email"]) == r["email_hash"] for r in rows) == len(rows)


def test_case_10_old_yahoo_address_resolves_with_current_and_historical(index, sample_requests):
    s = _resolve(index, sample_requests, "case_10")
    assert isinstance(s, Subject) and s.user_id == "user_10"
    assert s.request_email_role == "historical"
    roles = {(i.type, i.norm): i.role for i in s.identifiers}
    assert roles[("email", "nadia.ionescu@yahoo.com")] == "historical"
    current_emails = [i.norm for i in s.identifiers if i.type == "email" and i.role == "current"]
    assert len(current_emails) == 1 and current_emails[0] != "nadia.ionescu@yahoo.com"
    assert roles[("email_hash", email_hash("nadia.ionescu@yahoo.com"))] == "historical"


def test_case_12_old_address_and_its_hash_belong_to_the_subject(index, sample_requests):
    s = _resolve(index, sample_requests, "case_12")
    assert s.user_id == "user_12"
    historical = {i.key for i in s.identifiers if i.role == "historical"}
    old_emails = [k for k in historical if k[0] == "email"]
    assert old_emails, "case_12 has an audited email change"
    for _, e in old_emails:
        assert ("email_hash", email_hash(e)) in s.keys()


def test_case_28_look_alike_address_is_nobody_for_user_28(index, sample_requests):
    s = _resolve(index, sample_requests, "case_28")
    assert s.user_id == "user_28"
    assert ("email", "smartinez6461.jr@gmail.com") not in s.keys()
    decoy = index.resolve("smartinez6461.jr@gmail.com", parse_ts(sample_requests["case_28"]["audit_at"]))
    assert not (isinstance(decoy, Subject) and decoy.user_id == "user_28")


def test_matching_is_case_insensitive_but_exact(index, sample_requests):
    q = sample_requests["case_01"]
    t = parse_ts(q["audit_at"])
    assert index.resolve(q["email"].upper(), t).user_id == index.resolve(q["email"], t).user_id
    local, domain = q["email"].split("@")
    assert index.resolve(f"{local[:-1]}@{domain}", t) is None


@pytest.mark.parametrize("split", ["sample_deletion_requests.csv", "deletion_requests.csv"])
def test_every_request_email_resolves_to_exactly_one_user(index, split):
    rows = read_csv(DATASET / split)
    assert len(rows) in (32, 518)
    results = [index.resolve(q["email"], parse_ts(q["audit_at"])) for q in rows]
    assert [type(r).__name__ for r in results].count("Subject") == len(rows)


T0 = datetime(2026, 1, 1, tzinfo=timezone.utc)


def _synthetic(audit):
    ids = [{"user_id": "user_1", "name": "Ana Lima", "email": "b@x.com", "phone": "+1 555 0100",
            "email_hash": email_hash("b@x.com"), "updated_at": "2026-02-01T00:00:00Z"}]
    return IdentityIndex(ids, audit)


def test_identity_changes_after_audit_at_are_rolled_back():
    idx = _synthetic([{"audit_id": "audit_9", "user_id": "user_1", "event_time": "2026-01-10T00:00:00Z",
                       "field_name": "email", "old_value": "a@x.com", "new_value": "b@x.com"}])
    s = idx.resolve("a@x.com", T0)                       # audit_at is before the change
    assert s.request_email_role == "current"
    assert ("email", "b@x.com") not in s.keys()           # the future address is not the subject's yet
    assert idx.resolve("b@x.com", T0) is None
    later = idx.resolve("a@x.com", datetime(2026, 3, 1, tzinfo=timezone.utc))
    assert later.request_email_role == "historical" and ("email", "b@x.com") in later.keys()


def test_shared_address_is_an_ambiguity_not_a_guess():
    ids = [{"user_id": u, "name": n, "email": e, "phone": p, "email_hash": email_hash(e), "updated_at": ""}
           for u, n, e, p in (("user_1", "Ana", "a@x.com", "+1 555 0100"), ("user_2", "Bo", "c@x.com", "+1 555 0101"))]
    audit = [{"audit_id": "audit_1", "user_id": "user_2", "event_time": "2025-06-01T00:00:00Z",
              "field_name": "email", "old_value": "a@x.com", "new_value": "c@x.com"}]
    r = IdentityIndex(ids, audit).resolve("A@x.com", T0)
    assert isinstance(r, Ambiguity) and r.candidates == ("user_1", "user_2")


def test_names_are_weak_identifiers(index, sample_requests):
    s = _resolve(index, sample_requests, "case_01")
    assert any(i.type == "name" for i in s.identifiers)
    assert not any(k[0] == "name" for k in s.keys(strong_only=True))
