"""C4.2: every registered tool is declared, honours the cutoff, and records the obs_ids it returns (the agent may
cite only those). The tool list is derived from the registry, so a new tool without a case fails here."""
from datetime import datetime, timedelta, timezone

import pytest

from conftest import DATASET, read_csv
from ghostaudit.evidence import EvidenceStore, Observation
from ghostaudit.identity import IdentityIndex, email_hash
from ghostaudit.ownership import Link, Ownership, OwnerIndex, WorkflowAssignment, _Req
from ghostaudit.policy import load_rules
from ghostaudit.temporal import CaseView
from ghostaudit.tools import PAGE_SIZE, TOOLS, CaseTools, declarations

AUDIT = datetime(2026, 9, 15, tzinfo=timezone.utc)
RULES = load_rules(read_csv(DATASET / "deletion_rules.csv"))
IDS = [{"user_id": "user_1", "name": "Ana Lima", "email": "a@x.com", "phone": "+1 555 0100",
        "email_hash": email_hash("a@x.com"), "updated_at": ""}]


def _obs(oid, days, resource, system="search_service", kind="record", fields=None):
    t = AUDIT + timedelta(days=days)
    return Observation(obs_id=f"{oid}#1", source_id=oid, source_kind="json", kind=kind, captured_at=t, observed_at=t,
                       system_id=system, resource_id=resource, container=system,
                       fields=fields if fields is not None else {"email": "a@x.com"}, locator="1")


@pytest.fixture
def tools():
    store = EvidenceStore(resource_prefixes=["search", "account", "data_flow"])
    store.add(_obs("before", -2, "search_1"))
    store.add(_obs("after", 1, "search_1"))                       # captured after audit_at: must be invisible
    for i in range(PAGE_SIZE + 3):
        store.add(_obs(f"many{i:02d}", -5, f"search_{100 + i}"))
    store.add(_obs("flow", -1, "data_flow_1", "integration_service", fields={"enabled": "true", "email": "a@x.com"}))
    store.add(_obs("scope", -1, None, "search_service", kind="scope", fields={"record_count": 0}))
    idx = IdentityIndex(IDS, [])
    subject = idx.resolve("a@x.com", AUDIT)
    own = Ownership("case_t", links={"search_1": Link("search_1", "search_service", "explicit", ("before#1",)),
                                     "data_flow_1": Link("data_flow_1", "integration_service", "explicit", ("flow#1",))})
    q = _Req("case_t", subject, AUDIT - timedelta(days=3), AUDIT - timedelta(days=1), AUDIT, {})
    wf = WorkflowAssignment(store.observations, [q])
    return CaseTools("case_t", CaseView(store, AUDIT), subject, own, wf, RULES, store.resource_re)


CALLS = {
    "resolve_identity": {},
    "search_evidence": {"query": "a@x.com"},
    "inspect_evidence": {"obs_id": "before#1"},
    "resource_timeline": {"resource_id": "search_1"},
    "compare_replicas": {"resource_id": "search_1"},
    "inspect_flows_restores": {},
    "evaluate_policy": {"resource_id": "search_1"},
    "check_coverage": {"system_id": "search_service"},
    "workflow_candidates": {},
}


def test_every_registered_tool_is_declared_and_has_a_case_here():
    assert set(TOOLS) == set(CALLS)
    decl = {d["name"]: d for d in declarations()}
    assert set(decl) == set(TOOLS) and all(d["description"] for d in decl.values())


@pytest.mark.parametrize("name", sorted(CALLS))
def test_no_tool_exposes_post_cutoff_evidence(tools, name):
    out = tools.call(name, CALLS[name])
    assert "error" not in out, out
    assert "after#1" not in repr(out) and "after#1" not in tools.seen


def test_inspecting_a_post_cutoff_observation_is_refused(tools):
    assert "error" in tools.call("inspect_evidence", {"obs_id": "after#1"})


def test_search_is_paginated_with_an_honest_omitted_count(tools):
    first = tools.call("search_evidence", {"query": "a@x.com"})
    total = first["total"]
    assert total == 1 + (PAGE_SIZE + 3) + 1                       # before + many + flow; "after" excluded
    assert len(first["results"]) == PAGE_SIZE and first["omitted"] == total - PAGE_SIZE
    second = tools.call("search_evidence", {"query": "a@x.com", "page": 1})
    assert len(second["results"]) == total - PAGE_SIZE and second["omitted"] == 0


def test_look_alike_values_find_nothing(tools):
    out = tools.call("search_evidence", {"query": "a@x.co"})
    assert out["total"] == 0 and out["note"]


def test_only_returned_observations_become_citable(tools):
    assert tools.seen == set()
    tools.call("resource_timeline", {"resource_id": "search_1"})
    assert tools.seen == {"before#1"}


def test_flow_state_is_reported_with_its_proof(tools):
    out = tools.call("inspect_flows_restores", {})
    assert out["flows_and_backups"] == [{"resource_id": "data_flow_1", "system_id": "integration_service",
                                         "verdict": "violation", "reason": "1/1 copies violate DISABLE_FLOW",
                                         "proof": "flow#1"}]


def test_bad_arguments_and_unknown_tools_are_errors_not_exceptions(tools):
    assert "error" in tools.call("search_evidence", {"nope": 1})
    assert "error" in tools.call("drop_table", {})
