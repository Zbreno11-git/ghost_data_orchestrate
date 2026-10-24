"""C2.1–C2.6: every evidence file ingested with provenance; adapters pinned to real lines and records."""
import re
import sqlite3
from pathlib import Path

import pytest

from conftest import CODE, DATASET
from ghostaudit.evidence import EvidenceStore, Observation, flatten, normalize_identifier
from ghostaudit.ingest.logs import parse_line
from ghostaudit.ingest.manifest import load_manifest
from ghostaudit.ingest.pipeline import ingest_all
from ghostaudit.ingest.sql_snapshot import sandboxed_connection


@pytest.fixture(scope="module")
def ingested():
    return ingest_all(DATASET, allow_paid=False)  # PNGs come from the committed cache; no network


def _cov(ingested, kind):
    return [c for c in ingested[1].files if c.kind == kind]


def test_manifest_paths_resolve_inside_dataset():
    entries = load_manifest(DATASET)
    assert len(entries) == 94
    assert all(e.path.exists() and (DATASET / "evidence").resolve() in e.path.parents for e in entries)


def test_manifest_rejects_path_escape(tmp_path):
    (tmp_path / "evidence").mkdir()
    (tmp_path / "evidence_files.csv").write_text(
        "file_id,file_path,origin,captured_at\nevidence_x,../secret.txt,o,2026-01-01T00:00:00Z\n")
    with pytest.raises(ValueError, match="escapes"):
        load_manifest(tmp_path)


def test_tables_loaded_with_row_counts(ingested):
    assert ingested[1].tables == {"requests": 518, "sample_requests": 32, "identities": 850, "audit": 306,
                                  "activity": 4011, "rules": 15}


@pytest.mark.parametrize("kind,count", [("sql", 24), ("json", 28), ("log", 26), ("pdf", 4), ("txt", 1), ("png", 11)])
def test_every_file_of_each_kind_processed(ingested, kind, count):
    covs = _cov(ingested, kind)
    assert len(covs) == count
    assert [(c.file_id, c.status, c.notes) for c in covs if c.status != "processed"] == []
    assert all(c.observations > 0 for c in covs)


def test_coverage_totals(ingested):
    files = ingested[1].files
    assert len(files) == 94 and {c.status for c in files} == {"processed"}
    assert sum(c.unparsed for c in files) == 0


def test_sql_sandbox_denies_attach_and_other_pragmas(tmp_path):
    conn = sandboxed_connection()
    conn.execute("PRAGMA foreign_keys=ON")  # used by the snapshot files; allowed
    with pytest.raises(sqlite3.DatabaseError, match="not authorized"):
        conn.execute(f"ATTACH DATABASE '{tmp_path / 'x.db'}' AS x")
    with pytest.raises(sqlite3.DatabaseError, match="not authorized"):
        conn.execute("PRAGMA writable_schema=ON")
    assert not (tmp_path / "x.db").exists()


def test_sql_rows_keep_topology_and_payload(ingested):
    store = ingested[0]
    rows = [o for o in store.by_source["evidence_54"] if o.kind == "record"]
    assert {(o.container, o.topology, o.system_id) for o in rows if o.resource_id == "account_005"} == {
        ("customer_profiles_failover_replica", "failover_replica", "account_service")}
    payload = next(o for o in store.by_source["evidence_05"] if o.resource_id == "analytics_1738")
    assert payload.fields["user_id"] == "user_52" and payload.fields["metrics.sessions_30d"] is not None
    scope = [o for o in store.by_source["evidence_90"] if o.kind == "scope" and o.container == "snapshot_scope"]
    assert [o.system_id for o in scope] == ["account_service"]


def test_json_wrapper_fields_are_not_business_fields(ingested):
    # FR-11: a ledger's subject_reference locates the record for the auditor; it is not record content.
    store = ingested[0]
    lk = next(o for o in store.by_source["evidence_50"] if o.resource_id == "account_1733")
    assert lk.kind == "lookup" and lk.result == "FOUND"
    assert lk.wrapper["subject_reference"] == "haruka-kato@gmail.com" and "subject_reference" not in lk.fields
    hits = store.by_identifier[("email", "haruka-kato@gmail.com")]
    assert ("wrapper", "subject_reference") in {(role, key) for o, role, key in hits if o is lk}
    # A nested business document keeps its email as a field.
    doc = next(o for o in store.observations if o.source_id == "evidence_02" and o.resource_id == "search_8168")
    assert doc.fields["document.email"] == "smartinez6461.jr@gmail.com" and doc.wrapper == {}


def test_service_export_404_is_an_absence_claim_without_subject(ingested):
    obs = [o for o in ingested[0].by_resource["account_3136"] if o.source_kind == "json" and o.result == "NOT_FOUND"]
    assert obs and all(o.kind == "lookup" and o.wrapper.get("status_code") == 404 for o in obs)


# One real line per grammar (copied from the dataset) → the tokenizer's reading of it.
GRAMMAR_LINES = {
    "kv": ('2026-09-15T08:51:45Z level=DEBUG service=search_service instance=search-2 pod=search-12cc '
           'region=ap-south-1 trace_id=tr-5887496 event=index_query_started match_key="g.silva76.jr@gmail.com" '
           'attempt=1', ("search_service", "tr-5887496", "index_query_started", "match_key", "g.silva76.jr@gmail.com")),
    "json": ('2026-09-10T08:56:17Z {"severity":"DEBUG","logger":"account_service","service":"account_service",'
             '"instance":"account-6","trace_id":"tr-5563868","event":"profile_lookup_started",'
             '"lookup_key":"collins.grace@icloud.com"}',
             ("account_service", "tr-5563868", "profile_lookup_started", "lookup_key", "collins.grace@icloud.com")),
    "syslog": ('2026-08-22T10:51:17Z <15>1 node-1 account_service tr-4973247 - - level=DEBUG instance="account-2" '
               'pod="account-0525" region="eu-west-1" resource_id="account_1785" event="profile_lookup_completed" '
               'rows="1" http_status="200" duration_ms="50"',
               ("account_service", "tr-4973247", "profile_lookup_completed", "resource_id", "account_1785")),
    "pipe": ('2026-07-03T07:51:32Z | DEBUG | security_service | tr-5156005 | audit_record_read_completed | '
             'instance="security-6" resource_id="audit_record_4413" integrity_check="passed" rows="1" '
             'correlation_key="user_211"',
             ("security_service", "tr-5156005", "audit_record_read_completed", "correlation_key", "user_211")),
    "bracket": ('2026-07-28T05:51:18Z [DEBUG] [account_service] [tr-6074163] profile_lookup_started: '
                'instance="account-5" lookup_key="l.nascimento40@gmail.com" attempt="1"',
                ("account_service", "tr-6074163", "profile_lookup_started", "lookup_key", "l.nascimento40@gmail.com")),
    "cloud": ('2026-09-30T11:51:03Z requestId=tr-2263120 level=DEBUG function=profile_service message="instance=\\"'
              'profile-3\\" resource_id=\\"account_66777\\" event=\\"profile_lookup_completed\\" rows=\\"1\\""',
              ("profile_service", "tr-2263120", "profile_lookup_completed", "resource_id", "account_66777")),
    "record_lookup": ('2026-03-15T07:00:00Z INFO service=downstream_delivery_service event=record_lookup seq=2 '
                      'system="account_service" resource_id="account_1538" record_type="USER_PROFILE" '
                      'result="FOUND" subject_reference="n.mokoena70@yahoo.com"',
                      ("downstream_delivery_service", None, "record_lookup", "subject_reference",
                       "n.mokoena70@yahoo.com")),
}


@pytest.mark.parametrize("grammar", sorted(GRAMMAR_LINES))
def test_log_grammar(grammar):
    line, (svc, trace, event, key, value) = GRAMMAR_LINES[grammar]
    got_grammar, rec = parse_line(line)
    assert (got_grammar, rec["service"], rec["trace_id"], rec["event"], rec[key]) == (grammar, svc, trace, event, value)


def test_every_grammar_seen_in_the_dataset(ingested):
    seen = set()
    for c in _cov(ingested, "log"):
        seen |= set(re.findall(r"(\w+):\d+", c.notes[0]))
    assert seen == set(GRAMMAR_LINES)


def test_trace_join_links_lookup_key_to_resource(ingested):
    o = ingested[0].by_trace[("evidence_11", "tr-4973247")]
    assert (o.resource_id, o.result, o.kind) == ("account_1785", "FOUND", "record")
    assert o.wrapper["lookup_key"] == "nana.b9576@outlook.com" and "lookup_key" not in o.fields
    # the cache miss inside the trace is plumbing, not the record's result
    miss = ingested[0].by_trace[("evidence_67", "rb-061801-001")]
    assert (miss.resource_id, miss.result, miss.kind) == ("account_6523", "NOT_FOUND", "lookup")


def test_txt_uppercase_email_is_indexed_lowercase(ingested):
    hits = ingested[0].by_identifier[("email", "choi.jihoon94@gmail.com")]
    o = next(o for o, _, _ in hits if o.source_id == "evidence_03")
    assert o.wrapper["subject_reference"] == "CHOI.JIHOON94@GMAIL.COM" and o.result == "NOT_FOUND"


def test_pdf_register_rows_and_identifiers(ingested):
    rows = [o for o in ingested[0].by_source["evidence_27"] if "order_reference" in o.fields]
    assert len(rows) == 6 and rows[0].fields["subject_reference"] == "user_08"
    page = next(o for o in ingested[0].by_source["evidence_55"])
    assert "audit_record_003" in page.fields["text"] and "11:30" not in page.fields["text"]
    assert any(o.source_id == "evidence_55" for o in ingested[0].by_resource["audit_record_003"])


def test_png_extract_keeps_page_subject(ingested):
    # The deleted-account reference screen's subject is its heading; the transcription must keep it.
    obs = ingested[0].by_source["evidence_42"]
    assert any("user_17" in str(v) for o in obs for v in o.fields.values())


def test_identifier_normalization_literals():
    assert normalize_identifier("email", " A.B@X.COM ") == ("email", "a.b@x.com")
    assert normalize_identifier("phone", "+55 41 90257-9346") == ("phone", "5541902579346")
    assert normalize_identifier("customer_reference", "user_52") == ("user_id", "user_52")
    assert normalize_identifier("full_name", "Mariana  Almeida") == ("name", "mariana almeida")
    assert normalize_identifier("status", "ACTIVE") is None
    assert flatten({"a": {"b": [1, {"c": 2}], "e": []}}) == {"a.b.0": 1, "a.b.1.c": 2, "a.e": []}


def test_store_rejects_duplicate_observation_ids(ingested):
    store = EvidenceStore()
    o = ingested[0].observations[0]
    store.add(o)
    with pytest.raises(ValueError, match="duplicate"):
        store.add(o)


# --- C2.6 recall gates (evaluation side: they read sample_output.csv; nothing in ghostaudit/ does) ---

# Measured 2026-10-24: these two sample resources (future VERIFY_RECORD_PRESENT checks in case_18 and case_20)
# appear in no participant file, so no grounded engine can name them (D10). Literal on purpose: if ingestion ever
# finds them, this test must be revisited rather than silently pass.
UNOBSERVABLE_SAMPLE_RESOURCES = ["audit_record_5569", "audit_record_6645"]


def test_every_observable_sample_resource_is_indexed(ingested, sample_gold):
    resources = {s["resource_id"] for _, steps in sample_gold.values() for s in steps}
    assert len(resources) == 111
    unindexed = {r for r in resources if r not in ingested[0].by_resource}
    # A resource proven ABSENT by a scoped snapshot is legitimately never mentioned (account_004, case_04).
    absent_by_scope = {s["resource_id"] for _, steps in sample_gold.values() for s in steps
                       if s["operation"] == "VERIFY_RECORD_ABSENT" and s["evidence_id"]}
    assert sorted(unindexed & absent_by_scope) == ["account_004"]
    assert sorted(unindexed - absent_by_scope) == UNOBSERVABLE_SAMPLE_RESOURCES


def test_every_sample_citation_is_grounded_in_the_cited_file(ingested, sample_gold):
    """71 citations name a file holding an observation of the resource; the 4 ABSENT verifications instead cite a
    snapshot that covers the step's system and lacks the row (absence is proven by scope, not by mention)."""
    store = ingested[0]
    cited = [s for _, steps in sample_gold.values() for s in steps if s["evidence_id"]]
    assert len(cited) == 75
    by_mention, by_scope, ungrounded = 0, 0, []
    for s in cited:
        if any(o.source_id == s["evidence_id"] for o in store.by_resource.get(s["resource_id"], [])):
            by_mention += 1
        elif s["operation"] == "VERIFY_RECORD_ABSENT" and any(
                o.kind == "scope" and o.system_id == s["system_id"] for o in store.by_source[s["evidence_id"]]):
            by_scope += 1
        else:
            ungrounded.append((s["evidence_id"], s["resource_id"], s["operation"]))
    assert (by_mention, by_scope, ungrounded) == (71, 4, [])


def test_prediction_code_never_reads_sample_output():
    hits = [p for p in (CODE / "ghostaudit").rglob("*.py") if "sample_output" in p.read_text()]
    assert hits == []


# --- C3.0: resource-id prefixes are derived from the data, never hand-listed ---

def test_resource_prefixes_cover_every_record_and_activity_id(ingested):
    import csv
    import re as _re
    from conftest import DATASET
    store = ingested[0]
    activity = {_re.sub(r"_\d+$", "", r["resource_id"]) for r in csv.DictReader(open(DATASET / "system_activity.csv"))
                if r["resource_id"]}
    records = {_re.sub(r"_\d+$", "", o.resource_id) for o in store.observations if o.resource_id}
    # Derived floor: the measured stream has 14 prefixes; a shrinking set must fail, not go quiet.
    assert len(activity) >= 14
    assert set(store.resource_prefixes) == activity
    assert records <= activity, f"record prefixes missing from the derived set: {records - activity}"
    for prefix in activity:
        assert store.resource_re.fullmatch(f"{prefix}_123"), prefix


def test_free_text_mentions_use_the_derived_prefixes(ingested):
    # Measured 2026-10-24: email_delivery_/tombstone_/object_ ids occur only as a record's own resource_id, so the
    # S2 hand-written gap changed no index. This pins the mechanism with a synthetic mention instead.
    o = ingested[0].observations[0]
    store = EvidenceStore(resource_prefixes=ingested[0].resource_prefixes)
    for i, rid in enumerate(("tombstone_9", "email_delivery_7", "object_3")):
        store.add(Observation(obs_id=f"x#{i}", source_id="x", source_kind="txt", kind="text",
                              captured_at=o.captured_at, observed_at=None, system_id=None, resource_id=None,
                              fields={"text": f"see {rid} and user_1"}, locator=str(i)))
        assert [x.obs_id for x in store.by_resource[rid]] == [f"x#{i}"]
    assert "user_1" not in store.by_resource


# --- A20 safeguard 4: suspected gaps re-checked against the raw participant files on every run ---

def _raw_hits(resource_id):
    from conftest import REPO
    import csv as _csv
    man = {r["file_path"]: r["captured_at"] for r in _csv.DictReader(open(DATASET / "evidence_files.csv"))}
    files = [p for p in DATASET.rglob("*") if p.is_file() and p.name != "sample_output.csv"]
    files += sorted((REPO / "state" / "vision_cache").glob("*.json"))
    assert len(files) >= 100  # derived floor: 102 dataset files + 22 vision extracts measured 2026-10-24
    out = []
    for p in files:
        if resource_id.encode() in p.read_bytes():
            rel = str(p.relative_to(DATASET)) if p.is_relative_to(DATASET) else p.name
            out.append((rel, man.get(rel)))
    return out


def test_suspected_unobservable_ids_are_still_absent_from_every_raw_source():
    # D10 + D13: a literal byte search, not the index, so an extraction or linking gap cannot hide a real source.
    for rid in UNOBSERVABLE_SAMPLE_RESOURCES + ["account_004"]:
        assert _raw_hits(rid) == [], f"{rid} now appears in a participant source: revisit D10/D13"


def test_post_audit_only_ids_are_only_in_sources_captured_after_their_audit(sample_requests):
    from ghostaudit.timeutil import parse_ts
    # D12 (measured 2026-10-24): the only sources naming these are captured after the case's audit_at;
    # account_3960 is also in the activity stream, whose row is admissible.
    for cid, rid in [("case_09", "account_3960"), ("case_09", "audit_record_4902"), ("case_23", "audit_record_4128"),
                     ("case_24", "audit_record_7095"), ("case_29", "audit_record_3954"),
                     ("case_30", "audit_record_1707")]:
        audit = parse_ts(sample_requests[cid]["audit_at"])
        hits = _raw_hits(rid)
        assert hits, rid
        for rel, captured in hits:
            assert rel == "system_activity.csv" or (captured and parse_ts(captured) > audit), (cid, rid, rel)
