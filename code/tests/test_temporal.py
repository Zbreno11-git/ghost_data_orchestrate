"""C3.2: the cutoff holds in every CaseView accessor (derived by introspection, so a new accessor needs a case here)."""
import inspect
from datetime import datetime, timedelta, timezone

from ghostaudit.evidence import EvidenceStore, Observation
from ghostaudit.temporal import CaseView

AUDIT = datetime(2026, 9, 15, 12, 0, tzinfo=timezone.utc)


def _obs(name, captured):
    return Observation(obs_id=f"{name}#trace:t1", source_id=name, source_kind="log", kind="record",
                       captured_at=captured, observed_at=captured, system_id="search_service",
                       resource_id="search_1", fields={"email": "a@x.com"}, locator="trace:t1")


def _view():
    store = EvidenceStore(resource_prefixes=["search"])
    store.add(_obs("at_cutoff", AUDIT))
    store.add(_obs("after_cutoff", AUDIT + timedelta(seconds=1)))
    return CaseView(store, AUDIT)


# accessor → how to call it and how to read the source_ids it exposes
CALLS = {
    "observations": lambda v: [o.source_id for o in v.observations],
    "by_resource": lambda v: [o.source_id for o in v.by_resource("search_1")],
    "by_identifier": lambda v: [h[0].source_id for h in v.by_identifier(("email", "a@x.com"))],
    "by_source": lambda v: [o.source_id for o in v.by_source("at_cutoff") + v.by_source("after_cutoff")],
    "by_trace": lambda v: [o.source_id for o in (v.by_trace("at_cutoff", "t1"), v.by_trace("after_cutoff", "t1")) if o],
    "resources": lambda v: ["at_cutoff"] if v.resources() == ["search_1"] else [],
    "get": lambda v: [o.source_id for o in (v.get("at_cutoff#trace:t1"), v.get("after_cutoff#trace:t1")) if o],
    "admissible": lambda v: [o.source_id for o in v._store.observations if v.admissible(o)],
    "citable": lambda v: [n for n in ("at_cutoff", "after_cutoff") if v.citable(f"{n}#trace:t1")],
}


def test_every_public_accessor_is_covered():
    public = {n for n, _ in inspect.getmembers(CaseView) if not n.startswith("_")}
    assert public == set(CALLS), f"new CaseView accessor without a cutoff case: {public - set(CALLS)}"


def test_inclusive_cutoff_in_every_accessor():
    v = _view()
    for name, call in CALLS.items():
        assert call(v) == ["at_cutoff"], name


def test_a_resource_seen_only_after_the_cutoff_does_not_exist_for_the_case():
    store = EvidenceStore(resource_prefixes=["search"])
    store.add(_obs("after_cutoff", AUDIT + timedelta(seconds=1)))
    v = CaseView(store, AUDIT)
    assert v.resources() == [] and v.by_resource("search_1") == []


# --- S5 C5.3b: capture time vs observation time (Breno, 2026-10-24 21:59:56 UTC) ---

def _rec(name, captured, observed, oid=None):
    return Observation(obs_id=oid or f"{name}#r", source_id=name, source_kind="json", kind="record",
                       captured_at=captured, observed_at=observed, system_id="search_service",
                       resource_id="search_1", fields={"email": "a@x.com"}, locator="r")


def test_an_observation_of_an_event_after_audit_at_is_rejected_even_inside_an_admissible_artifact():
    store = EvidenceStore(resource_prefixes=["search"])
    store.add(_rec("contradictory", AUDIT - timedelta(days=2), AUDIT + timedelta(hours=1)))   # observed > captured
    store.add(_rec("boundary", AUDIT - timedelta(days=2), AUDIT, "boundary#r2"))
    v = CaseView(store, AUDIT)
    assert [o.source_id for o in v.observations] == ["boundary"]           # observed == audit_at is admissible


def test_an_older_observation_does_not_admit_an_artifact_captured_after_audit_at():
    store = EvidenceStore(resource_prefixes=["search"])
    store.add(_rec("late_export", AUDIT + timedelta(days=1), AUDIT - timedelta(days=3)))
    assert CaseView(store, AUDIT).observations == []      # AGENTS §6.6: never an item captured after audit_at


def test_a_missing_observation_time_falls_back_to_the_capture_time():
    from ghostaudit.temporal import event_time
    store = EvidenceStore(resource_prefixes=["search"])
    o = _rec("screen", AUDIT - timedelta(days=1), None)
    store.add(o)
    assert CaseView(store, AUDIT).observations == [o] and event_time(o) == o.captured_at


# --- S7 C7.1T: historical snapshots inside later exports (Breno amendment 2), behind [time] historical_snapshots ---

EXPORTED = AUDIT + timedelta(days=2)


def _bundle(tmp_path, snapshots, exported=EXPORTED, name="bundle"):
    """Ingest a snapshot bundle through the real JSON adapter; returns the store."""
    import json as _json
    from ghostaudit.ingest.coverage import FileCoverage
    from ghostaudit.ingest.json_records import ingest_json
    from ghostaudit.ingest.manifest import ManifestEntry
    f = tmp_path / f"{name}.json"
    f.write_text(_json.dumps({"exported_at": exported.isoformat(), "source": "t", "snapshots": snapshots}))
    store = EvidenceStore(resource_prefixes=["account", "search"])
    entry = ManifestEntry(name, f.name, f, "t", exported)
    cov = FileCoverage(name, f.name, "json")
    ingest_json(entry, store, cov, {})
    assert cov.status == "processed" and len(store.observations) >= 2      # the fixture reaches the store
    return store


def _snap(captured, rid="account_1", email="a@x.com"):
    return {"captured_at": captured.isoformat(), "data_store": "account_service", "collection": "customer_profiles",
            "records": [{"resource_id": rid, "email": email, "account_status": "ACTIVE"}]}


def _policy(store, policy):
    store.time_policy = policy
    return CaseView(store, AUDIT)


def test_a_snapshot_captured_before_the_audit_inside_a_later_export_is_read_only_under_snapshot_capture(tmp_path):
    store = _bundle(tmp_path, [_snap(AUDIT - timedelta(days=5))])
    assert _policy(store, "manifest").by_resource("account_1") == []                 # A26 baseline unchanged
    v = _policy(store, "snapshot_capture")
    rec = v.by_resource("account_1")
    assert [o.kind for o in rec] == ["record"] and rec[0].snapshot_dated
    assert v.by_identifier(("email", "a@x.com"))                                     # identity reads it too
    assert not v.citable(rec[0].obs_id)                                              # but it is never cited


def test_a_snapshot_captured_after_the_audit_stays_out_under_both_policies(tmp_path):
    store = _bundle(tmp_path, [_snap(AUDIT + timedelta(hours=1))])
    for policy in ("manifest", "snapshot_capture"):
        assert _policy(store, policy).by_resource("account_1") == [], policy


def test_a_snapshot_dated_after_its_own_export_is_contradictory_and_never_read_early(tmp_path):
    store = _bundle(tmp_path, [_snap(AUDIT - timedelta(days=1))], exported=AUDIT - timedelta(days=3) + timedelta(days=5),
                    name="ok")
    late_export = AUDIT + timedelta(days=1)
    bad = _bundle(tmp_path, [_snap(late_export + timedelta(days=1))], exported=late_export, name="bad")
    assert all(not o.snapshot_dated for o in bad.observations)
    assert _policy(bad, "snapshot_capture").by_resource("account_1") == []
    assert _policy(store, "snapshot_capture").by_resource("account_1")              # control: consistent dates read


def test_a_retrospective_claim_with_an_old_timestamp_is_not_a_snapshot(tmp_path):
    """A lookup ledger exported after the audit, whose record says it was recorded before: a later assertion
    about an earlier event. It never qualifies, whatever its timestamp."""
    import json as _json
    from ghostaudit.ingest.coverage import FileCoverage
    from ghostaudit.ingest.json_records import ingest_json
    from ghostaudit.ingest.manifest import ManifestEntry
    f = tmp_path / "ledger.json"
    f.write_text(_json.dumps({"origin": "support_record_lookup", "record_count": 1, "records": [
        {"recorded_at": (AUDIT - timedelta(days=3)).isoformat(), "system": "account_service", "resource_id": "account_1",
         "record_type": "USER_PROFILE", "result": "FOUND", "subject_reference": "a@x.com"}]}))
    store = EvidenceStore(resource_prefixes=["account"])
    cov = FileCoverage("ledger", f.name, "json")
    ingest_json(ManifestEntry("ledger", f.name, f, "t", EXPORTED), store, cov, {})
    assert cov.status == "processed" and len(store.observations) == 1
    assert _policy(store, "snapshot_capture").by_resource("account_1") == []


def test_a_violation_known_only_from_a_later_export_is_unknown_never_cited(tmp_path):
    from conftest import DATASET, read_csv
    from ghostaudit.policy import assess, load_rules
    rules = load_rules(read_csv(DATASET / "deletion_rules.csv"))
    store = _bundle(tmp_path, [_snap(AUDIT - timedelta(days=5))])
    a = assess("account_1", "account_service", _policy(store, "snapshot_capture"), rules)
    assert a.verdict == "unknown" and a.proof is None and "not citable" in a.reason
    # control: the same snapshot in an export captured by the audit is a cited violation
    ok = _bundle(tmp_path, [_snap(AUDIT - timedelta(days=5))], exported=AUDIT, name="on_time")
    b = assess("account_1", "account_service", _policy(ok, "snapshot_capture"), rules)
    assert b.verdict == "violation" and b.proof.source_id == "on_time"


def test_an_unknown_time_policy_fails_loudly():
    import pytest
    store = EvidenceStore()
    store.time_policy = "any_old_timestamp"
    with pytest.raises(ValueError):
        CaseView(store, AUDIT)
