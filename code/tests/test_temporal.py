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
