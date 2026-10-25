"""C3.3: ownership tiers. Workflow links are candidates (A20): interleaved runs, a repeated person and a tie are
resolved only by deduction, never forced; link strength and supporting obs_ids survive."""
import json
from datetime import datetime, timedelta, timezone

import pytest

from conftest import DATASET, read_csv
from ghostaudit.evidence import Observation
from ghostaudit.identity import IdentityIndex, Subject, email_hash
from ghostaudit.ownership import OwnerIndex, WorkflowAssignment, _Req, build_requests, link_case
from ghostaudit.temporal import CaseView
from ghostaudit.timeutil import parse_ts

T = datetime(2026, 9, 1, 12, 0, tzinfo=timezone.utc)
FAR = datetime(2100, 1, 1, tzinfo=timezone.utc)


def _row(aid, minutes, resource, system="account_service", source="deletion_worker", etype="DELETE_RECORD"):
    t = T + timedelta(minutes=minutes)
    return Observation(obs_id=f"{aid}#row", source_id=aid, source_kind="csv", kind="activity", captured_at=t,
                       observed_at=t, system_id=system, resource_id=resource, record_type=etype, result="SUCCESS",
                       container="system_activity", fields={"source_system": source, "target_system": system},
                       locator="row")


def _req(case, user, start, report, explicit=None):
    s = Subject(user, f"{user}@x.com", "current", ())
    return _Req(case, s, T + timedelta(minutes=start), T + timedelta(minutes=report), FAR, explicit or {})


def test_interleaved_runs_are_assigned_by_deduction_not_proximity():
    # Two concurrent workflows: A's account row comes *after* B's, so "nearest to report" would swap them.
    rows = [_row("a1", 0, "account_B"), _row("a2", 10, "account_A"), _row("a3", 30, "search_A", "search_service")]
    a = _req("case_A", "user_a", -60, 50, explicit={"search_A": ["ev#1"]})
    b = _req("case_B", "user_b", -60, 50, explicit={"account_B": ["ev#2"]})
    wf = WorkflowAssignment(rows, [a, b])
    assert wf.assigned["case_B"][0].resource_id == "account_B" and wf.assigned["case_B"][1] == "explicit_account"
    assert wf.assigned["case_A"][0].resource_id == "account_A"      # the only row left after B's fixed pair
    assert wf.assigned["case_A"][1] in ("only_feasible_row", "corroborated_run", "forced_matching")


def test_a_repeated_person_does_not_inherit_the_earlier_requests_account():
    rows = [_row("old", 0, "account_old"), _row("new", 60 * 24 * 90, "account_new")]
    first = _req("case_first", "user_7", -60, 30, explicit={"account_old": ["ev#old"]})
    second = _req("case_second", "user_7", 60 * 24 * 90 - 60, 60 * 24 * 90 + 30, explicit={"account_old": ["ev#old"]})
    wf = WorkflowAssignment(rows, [first, second])
    assert wf.assigned["case_first"][0].resource_id == "account_old"
    assert wf.assigned["case_second"][0].resource_id == "account_new"
    owners = OwnerIndex(IdentityIndex([], []))
    from ghostaudit.evidence import EvidenceStore
    own = link_case(second, CaseView(EvidenceStore(), FAR), wf, owners)
    assert own.account.resource_id == "account_new" and "account_old" not in own.links
    assert "case_first" in own.excluded["account_old"]


@pytest.mark.parametrize("mode", ["strict", "scored"])
def test_a_tie_stays_ambiguous_and_is_never_forced(mode):
    rows = [_row("r1", 0, "account_1"), _row("r2", 20, "account_2")]
    a, b = _req("case_A", "user_a", -60, 10), _req("case_B", "user_b", -60, 10)   # same window, same report
    wf = WorkflowAssignment(rows, [a, b])
    assert wf.assigned == {} and set(wf.ambiguous) == {"case_A", "case_B"}
    from ghostaudit.evidence import EvidenceStore
    owners = OwnerIndex(IdentityIndex([], []))
    for q in (a, b):
        own = link_case(q, CaseView(EvidenceStore(), FAR), wf, owners, mode)
        if mode == "strict":
            assert own.account is None and own.ambiguities
        else:   # scored may rank a weak candidate, but it is never explicit and the case is weak
            assert own.account is None or (own.account.tier == "workflow" and own.weak)


def test_workflow_links_keep_their_tier_and_supporting_rows():
    rows = [_row("r1", 0, "account_9"), _row("r2", 15, "analytics_9", "analytics_platform")]
    q = _req("case_A", "user_a", -60, 30)
    wf = WorkflowAssignment(rows, [q])
    from ghostaudit.evidence import EvidenceStore
    own = link_case(q, CaseView(EvidenceStore(), FAR), wf, OwnerIndex(IdentityIndex([], [])), "scored")
    assert own.account.tier == "workflow" and own.account.reasons == ("r1#row",)
    assert own.links["analytics_9"].tier == "workflow" and own.links["analytics_9"].reasons == ("r1#row", "r2#row")
    assert own.weak


# --- on the real data (evaluation side: compares with sample_output.csv, full 111 denominator) ---

@pytest.fixture(scope="module")
def linked(store):
    ids, audit = read_csv(DATASET / "user_identities.csv"), read_csv(DATASET / "user_audit_log.csv")
    idx = IdentityIndex(ids, audit)
    owners = OwnerIndex(idx)
    rows = read_csv(DATASET / "sample_deletion_requests.csv") + read_csv(DATASET / "deletion_requests.csv")
    reqs, _ = build_requests(rows, idx, store, store.resource_re, owners)
    from ghostaudit.ownership import AssignmentsAsOf, request_at
    by_row = {r["case_id"]: r for r in rows}
    wfs = AssignmentsAsOf(store.observations, reqs,
                          lambda q, at: request_at(by_row[q.case_id], at, idx, store, store.resource_re, owners)[0])
    byq = {q.case_id: q for q in reqs}
    samples = [r["case_id"] for r in read_csv(DATASET / "sample_deletion_requests.csv")]
    return {m: {c: link_case(byq[c], CaseView(store, byq[c].audit_at), wfs.for_case(c), owners, m) for c in samples}
            for m in ("strict", "scored")}


def test_the_look_alike_record_is_never_the_subjects(linked, sample_requests):
    for mode in ("strict", "scored"):
        assert "search_8168" not in linked[mode]["case_28"].links   # holds smartinez6461.jr@gmail.com


def test_sample_ownership_regression_gates(linked, sample_gold):
    # Measured 2026-10-24 (strict): 78/111 gold resources linked, 2 extras (object_19, tombstone_17: the
    # subject's own, not listed in the answers). A drop or a new extra must be explained, not absorbed.
    # S5 C5.2 (as-of solver): case_17 also keeps account_6523, linked by a profile lookup keyed with the
    # subject's email (NOT_FOUND). Only case_63's *later* deduction had claimed its worker row, which case_17
    # cannot know at its cutoff; it is compliant (absent) in an INCOMPLETE case, so no step changes.
    gold = {c: {s["resource_id"] for s in steps} for c, (_, steps) in sample_gold.items()}
    assert sum(map(len, gold.values())) == 111
    strict = linked["strict"]
    found = sum(len(gold[c] & set(strict[c].links)) for c in gold)
    extra = sorted((c, r) for c in gold for r in set(strict[c].links) - gold[c])
    assert found >= 78, found
    assert extra == [("case_07", "object_19"), ("case_17", "account_6523"), ("case_17", "tombstone_17")], extra
    assert all(l.reasons for own in strict.values() for l in own.links.values())


# --- temporal isolation of the global helpers (S5 C5.2): nothing after a case's audit_at may change it ---

def test_an_identifier_acquired_by_someone_else_after_the_cutoff_does_not_change_an_earlier_case():
    from ghostaudit.evidence import EvidenceStore
    from ghostaudit.ownership import explicit_links
    audit_x = T
    later_a, later_b = T + timedelta(days=10), T + timedelta(days=20)
    ids = [{"user_id": "user_a", "name": "A", "email": "a.new@x.com", "phone": "", "email_hash": "", "updated_at": ""},
           {"user_id": "user_b", "name": "B", "email": "shared@x.com", "phone": "", "email_hash": "", "updated_at": ""}]
    audit = [{"audit_id": "au1", "user_id": "user_a", "field_name": "email", "old_value": "shared@x.com",
              "new_value": "a.new@x.com", "event_time": later_a.isoformat()},
             {"audit_id": "au2", "user_id": "user_b", "field_name": "email", "old_value": "b.old@x.com",
              "new_value": "shared@x.com", "event_time": later_b.isoformat()}]
    idx = IdentityIndex(ids, audit)
    store = EvidenceStore(resource_prefixes=["support"])
    t = audit_x - timedelta(days=1)
    store.add(Observation(obs_id="doc#p1", source_id="doc", source_kind="pdf", kind="text", captured_at=t,
                          observed_at=t, system_id=None, resource_id=None, container="doc",
                          fields={"text": "Ticket support_7 from shared@x.com about a late parcel"}, locator="p1"))
    subject = idx.resolve("shared@x.com", audit_x)
    assert isinstance(subject, Subject) and subject.user_id == "user_a"   # A held it at the cutoff
    links = explicit_links(subject, CaseView(store, audit_x), store.resource_re, OwnerIndex(idx))
    assert links == {"support_7": ["doc#p1"]}       # B only acquires the address 20 days later


def test_a_later_request_cannot_take_or_force_an_earlier_cases_workflow_row():
    from ghostaudit.ownership import AssignmentsAsOf
    rows = [_row("r1", 0, "account_1"), _row("r2", 10, "account_2")]
    x = _Req("case_X", Subject("user_x", "x@x.com", "current", ()), T - timedelta(minutes=60),
             T + timedelta(minutes=50), T + timedelta(minutes=60), {})
    # Y's explicit link to account_2 comes from evidence captured long after X's audit_at.
    y = _Req("case_Y", Subject("user_y", "y@x.com", "current", ()), T - timedelta(minutes=60),
             T + timedelta(minutes=50), T + timedelta(days=5), {"account_2": ["late#1"]})

    def relink(q, at):      # Y as it could be known at `at`: the late evidence is not admissible yet
        return _Req(q.case_id, q.subject, q.requested_at, min(q.reported_at, at), at, {})

    glob = WorkflowAssignment(rows, [x, y])
    assert glob.assigned["case_X"][0].resource_id == "account_1"     # what the global solver concludes
    asof = AssignmentsAsOf(rows, [x, y], relink)
    wx = asof.for_case("case_X")
    assert "case_X" not in wx.assigned and sorted(wx.ambiguous["case_X"]) == ["account_1", "account_2"]
    assert asof.for_case("case_Y").assigned["case_Y"][0].resource_id == "account_2"   # Y still knows its link


def test_the_as_of_assignment_never_holds_rows_after_the_cutoff():
    from ghostaudit.ownership import AssignmentsAsOf
    rows = [_row("r1", 0, "account_1"), _row("w1", 90, "search_1", "search_service")]
    x = _Req("case_X", Subject("user_x", "x@x.com", "current", ()), T - timedelta(minutes=60),
             T + timedelta(minutes=50), T + timedelta(minutes=60), {"search_1": ["ev#1"]})
    wf = AssignmentsAsOf(rows, [x], lambda q, at: q).for_case("case_X")
    assert all(o.captured_at <= x.audit_at for o in wf.rows)
    assert all(o.captured_at <= x.audit_at for rs in wf.worker_rows.values() for o in rs)


def test_a_table_screen_links_only_the_rows_that_name_the_subject():
    # A results table (case_35's shape): the subject's row and a look-alike row; no other *known* user is named,
    # so a whole-panel unit would link both. A table row belongs to one entity.
    from ghostaudit.evidence import EvidenceStore
    from ghostaudit.ownership import explicit_links
    ids = [{"user_id": "user_1", "name": "G", "email": "g.silva@x.com", "phone": "", "email_hash": "", "updated_at": ""}]
    idx = IdentityIndex(ids, [])
    store = EvidenceStore(resource_prefixes=["search"])
    t = T - timedelta(days=1)
    store.add(Observation(obs_id="ev_s#panel:1", source_id="ev_s", source_kind="png", kind="text", captured_at=t,
                          observed_at=t, system_id=None, resource_id="search_1", container="Results",
                          fields={"panel": "Results (2)", "rows.0.row 1: _id": "search_1",
                                  "rows.1.row 1: Email": "g.silva@x.com", "rows.2.row 2: _id": "search_2",
                                  "rows.3.row 2: Email": "g.silva.jr@x.com"}, locator="panel:1"))
    subject = idx.resolve("g.silva@x.com", T)
    assert explicit_links(subject, CaseView(store, T), store.resource_re, OwnerIndex(idx)) == {"search_1": ["ev_s#panel:1"]}


def test_the_decoy_check_reads_only_the_table_row_that_names_the_resource():
    # case_39's shape: the subject's connector row and another customer's row in one Topology panel.
    from ghostaudit.evidence import EvidenceStore
    ids = [{"user_id": "user_1", "name": "A", "email": "a@x.com", "phone": "", "email_hash": "", "updated_at": ""},
           {"user_id": "user_2", "name": "B", "email": "b@x.com", "phone": "", "email_hash": "", "updated_at": ""}]
    idx = IdentityIndex(ids, [])
    store = EvidenceStore(resource_prefixes=["data_flow"])
    t = T - timedelta(days=1)
    store.add(Observation(obs_id="ev_t#panel:1", source_id="ev_t", source_kind="png", kind="text", captured_at=t,
                          observed_at=None, system_id=None, resource_id="data_flow_1", container="Topology",
                          fields={"rows.0.row 1: Connector": "data_flow_1", "rows.1.row 1: Selector": "a@x.com",
                                  "rows.2.row 2: Connector": "data_flow_2", "rows.3.row 2: Selector": "b@x.com"},
                          locator="panel:1"))
    owners = OwnerIndex(idx)
    subject = idx.resolve("a@x.com", T)
    reqs, _ = build_requests([{"case_id": "case_A", "email": "a@x.com", "requested_at": (T - timedelta(days=3)).isoformat(),
                               "reported_at": (T - timedelta(days=2)).isoformat(), "audit_at": T.isoformat()}],
                             idx, store, store.resource_re, owners)
    own = link_case(reqs[0], CaseView(store, T), WorkflowAssignment([], reqs), owners)
    assert "data_flow_1" in own.links and "data_flow_2" not in own.links
    assert not [a for a in own.ambiguities if "data_flow_1" in a]     # row 2's customer is not this row's


def test_a_subject_record_that_names_another_resource_links_it_too():
    # case_06's shape (found by the agent, S5): the subject's search document names the account it was built from.
    from ghostaudit.evidence import EvidenceStore
    from ghostaudit.ownership import explicit_links
    ids = [{"user_id": "user_1", "name": "J", "email": "j@x.com", "phone": "", "email_hash": "", "updated_at": ""},
           {"user_id": "user_2", "name": "K", "email": "k@x.com", "phone": "", "email_hash": "", "updated_at": ""}]
    idx = IdentityIndex(ids, [])
    store = EvidenceStore(resource_prefixes=["search", "account"])
    t = T - timedelta(days=1)
    for oid, res, f in (("ev#1", "search_1", {"email": "j@x.com", "source_resource_id": "account_1"}),
                        ("ev#2", "search_2", {"email": "j@x.com", "cc": "k@x.com", "source_resource_id": "account_2"})):
        store.add(Observation(obs_id=oid, source_id="ev", source_kind="json", kind="record", captured_at=t,
                              observed_at=t, system_id="search_service", resource_id=res, fields=f, locator=oid))
    links = explicit_links(idx.resolve("j@x.com", T), CaseView(store, T), store.resource_re, OwnerIndex(idx))
    assert links.get("account_1") == ["ev#1"]
    assert "account_2" not in links          # the record also names another subject: it links nothing extra


# --- S7 C7.1: which deduction mechanisms are asserted is configuration ----------------------------------------

def _deduced_pair():
    """case_A is fixed by its explicit account; case_B gets the only row left (only_feasible_row)."""
    rows = [_row("r1", 0, "account_A"), _row("r2", 10, "account_B")]
    a = _req("case_A", "user_a", -60, 50, explicit={"account_A": ["ev#a"]})
    b = _req("case_B", "user_b", -60, 50)
    return WorkflowAssignment(rows, [a, b]), a, b


def test_an_unasserted_mechanism_leaves_its_pick_as_an_uncertain_candidate_only():
    from ghostaudit.evidence import EvidenceStore
    wf, a, b = _deduced_pair()
    assert wf.assigned["case_B"][1] == "only_feasible_row"
    owners = OwnerIndex(IdentityIndex([], []))
    own = link_case(b, CaseView(EvidenceStore(), FAR), wf, owners, "strict", frozenset({"forced_matching"}))
    assert own.account is None and "account_B" not in own.links
    assert own.uncertain == {"account_B": own.uncertain["account_B"]} and "only_feasible_row" in own.uncertain["account_B"]
    # close positive: the same deduction is asserted when its mechanism is listed, and by default
    for asserted in (frozenset({"only_feasible_row"}), None):
        own = link_case(b, CaseView(EvidenceStore(), FAR), wf, owners, "strict", asserted)
        assert own.account.resource_id == "account_B" and own.account.tier == "workflow" and not own.uncertain


def test_an_explicit_account_is_asserted_whatever_the_mechanism_list():
    from ghostaudit.evidence import EvidenceStore
    wf, a, _ = _deduced_pair()
    own = link_case(a, CaseView(EvidenceStore(), FAR), wf, OwnerIndex(IdentityIndex([], [])), "strict", frozenset())
    assert own.account.resource_id == "account_A" and own.account.tier == "explicit" and not own.uncertain


def test_the_runner_rejects_an_unknown_mechanism_name(tmp_path):
    from conftest import CODE
    from ghostaudit.config import load_config
    from ghostaudit.runner import run
    cfg = load_config()
    cfg["ownership"] = {"asserted_mechanisms": ["only_feasible_row", "cadence_guess"]}
    with pytest.raises(ValueError, match="cadence_guess"):
        run(CODE / "evaluation" / "custom_cases" / "historical_email_replica" / "dataset", "targets", tmp_path, config=cfg)
