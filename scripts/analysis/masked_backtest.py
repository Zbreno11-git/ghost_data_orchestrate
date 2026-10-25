"""Masked-identity backtest of the existing workflow-account mechanisms (S7 C7.1, Breno amendment 1; evaluator side).

Question: when a request's account is *not* named by explicit evidence, how often do the mechanisms we already
use to deduce it (the one-to-one workflow solver and the strict→scored nearest-anchor fallback) pick the right
one? We cannot measure that on genuinely anonymous accounts, so we measure it on accounts whose ownership *is*
established by explicit admissible evidence, after hiding that evidence.

Masking:
- **population**: requests whose account the unmasked solver fixes by `explicit_account` at their own cutoff;
  that account is the hidden truth, held only in this script, never passed back to the engine;
- **cohorts**, two definitions, each masked **together** so elimination by still-visible neighbours cannot make
  the test artificially easy:
  - *competitors*: the request plus every request that competes for one of its feasible rows at its cutoff;
  - *component*: every request in a connected group of overlapping run windows ([requested_at, reported_at +
    slack]); on this dataset that is nearly everyone, i.e. all explicit accounts hidden at once (the hardest case);
- **what is hidden**: every `account_*` resource (and the truth account) in each masked request's explicit links,
  in the as-of solve for every cutoff (the `relink` path recomputes explicit links from the store, so it is masked
  too). Non-account explicit links stay: they are evidence the real anonymous cases also have;
- **control**: after masking, (a) no masked request is solved by `explicit_account`, and (b) `link_case` for the
  masked request does not link the truth account at the explicit tier. A leak is reported and fails the script.

Mechanisms measured (existing only; no new rule): corroborated_run, only_feasible_row, only_feasible_request,
forced_matching, and the nearest-anchor ranking used by the strict→scored fallback. Outcomes: correct, incorrect,
abstain, by mechanism, by candidate count and by cohort size.

Selection bias: accounts that were explicitly identifiable may differ from genuinely anonymous ones (their
windows, their neighbours, the deletion worker's behaviour). This is supporting evidence about the mechanisms,
not an estimate of hidden-target accuracy.

Usage: python scripts/analysis/masked_backtest.py [--out md] [--json path]
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from dataclasses import replace
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "code"))


def _components(reqs, slack):
    """Connected components of overlapping run windows (union-find over a sweep)."""
    parent = {q.case_id: q.case_id for q in reqs}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    spans = sorted((q.requested_at, q.reported_at + slack, q.case_id) for q in reqs)
    cur_end, cur = None, None
    for start, end, c in spans:
        if cur is not None and start <= cur_end:
            parent[find(c)] = find(cur)
            cur_end = max(cur_end, end)
        else:
            cur, cur_end = c, end
    groups = defaultdict(list)
    for q in reqs:
        groups[find(q.case_id)].append(q.case_id)
    return list(groups.values())


def _bucket(n: int) -> str:
    return str(n) if n <= 3 else "4-6" if n <= 6 else "7-10" if n <= 10 else ">10"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", type=Path, default=ROOT / "dataset")
    ap.add_argument("--out", type=Path)
    ap.add_argument("--json", type=Path)
    a = ap.parse_args(argv)
    from ghostaudit.identity import IdentityIndex
    from ghostaudit.ingest.csv_tables import load_tables
    from ghostaudit.ingest.pipeline import ingest_all
    from ghostaudit.ownership import (REPORT_SLACK, AssignmentsAsOf, OwnerIndex, build_requests, link_case,
                                      request_at)
    from ghostaudit.temporal import CaseView

    tables = load_tables(a.dataset)
    store, _ = ingest_all(a.dataset, allow_paid=False)
    identity = IdentityIndex(tables["identities"], tables["audit"])
    owners = OwnerIndex(identity)
    everyone = tables.get("requests", []) + tables.get("sample_requests", [])
    reqs, _ = build_requests(everyone, identity, store, store.resource_re, owners)
    by_row = {r["case_id"]: r for r in everyone}
    split = {r["case_id"]: "samples" for r in tables.get("sample_requests", [])}
    relinked: dict = {}

    def relink(q, at):
        k = (q.case_id, at)
        if k not in relinked:
            relinked[k] = request_at(by_row[q.case_id], at, identity, store, store.resource_re, owners)[0]
        return relinked[k]

    base = AssignmentsAsOf(store.observations, reqs, relink)
    truth = {}
    for q in reqs:
        got = base.for_case(q.case_id).assigned.get(q.case_id)
        if got and got[1] == "explicit_account":
            truth[q.case_id] = got[0].resource_id

    def mask(q, hidden: set[str]):
        if q is None or q.case_id not in hidden:
            return q
        drop = {r for r in q.explicit if r.startswith("account_")} | {truth[q.case_id]}
        return replace(q, explicit={r: v for r, v in q.explicit.items() if r not in drop})

    comps = _components(reqs, REPORT_SLACK)
    comp_of = {c: comp for comp in comps for c in comp}
    leaks = []

    def evaluate(groups, label):
        """groups: [(hidden set, cases to score)]; one masked as-of solve per group."""
        out = []
        for hidden, score in groups:
            masked = AssignmentsAsOf(store.observations, [mask(q, hidden) for q in reqs],
                                     lambda q, at, h=hidden: mask(relink(q, at), h))
            for c in sorted(score):
                wf = masked.for_case(c)
                q = wf.requests[c]
                cands = [r for r in wf.rows if wf.feasible(q, r)]
                got = wf.assigned.get(c)
                if got and got[1] == "explicit_account":
                    leaks.append(f"{label} {c}: still solved by explicit_account")
                own = link_case(q, CaseView(store, q.audit_at), wf, owners, "strict")
                l = own.links.get(truth[c])
                if l is not None and l.tier == "explicit":
                    leaks.append(f"{label} {c}: {truth[c]} still linked at the explicit tier")
                if got and got[0].record_type != "CLASSIFY_REQUEST":
                    mech, pick = got[1], got[0].resource_id
                elif got:
                    mech, pick = got[1] + " (intake row)", None
                else:
                    mech, pick = "unassigned", None
                ranked = wf.ranked.get(c)
                rpick = ranked[0].resource_id if ranked and ranked[0].record_type != "CLASSIFY_REQUEST" else None
                out.append({"case_id": c, "split": split.get(c, "targets"), "truth": truth[c], "mechanism": mech,
                            "pick": pick, "outcome": "abstain" if pick is None else
                            ("correct" if pick == truth[c] else "incorrect"),
                            "fallback_pick": rpick if pick is None else None,
                            "fallback_outcome": None if pick is not None else "abstain" if rpick is None else
                            ("correct" if rpick == truth[c] else "incorrect"),
                            "candidates": len(cands), "truth_feasible": any(r.resource_id == truth[c] for r in cands),
                            "cohort_masked": len(hidden)})
        return out

    comp_groups = [({c for c in comp if c in truth}, {c for c in comp if c in truth}) for comp in comps
                   if any(c in truth for c in comp)]
    comp_groups = [(h, h) for h, _ in comp_groups]
    compet_groups = []
    for c in sorted(truth):
        wf = base.for_case(c)
        mine = {r.obs_id for r in wf.rows if wf.feasible(wf.requests[c], r)}
        rivals = {d for d, q in wf.requests.items() if d != c and any(wf.feasible(q, r) for r in wf.rows if r.obs_id in mine)}
        compet_groups.append(({c} | (rivals & set(truth)), {c}))
    variants = {"competitors": evaluate(compet_groups, "competitors"), "component": evaluate(comp_groups, "component"),
                "single": evaluate([({c}, {c}) for c in sorted(truth)], "single")}

    # The legacy links themselves (unmasked), for comparison: how each published workflow account was deduced and
    # among how many feasible rows.
    legacy = []
    for q in reqs:
        wf = base.for_case(q.case_id)
        got = wf.assigned.get(q.case_id)
        if got and got[1] != "explicit_account" and got[0].record_type != "CLASSIFY_REQUEST":
            legacy.append((q.case_id, got[1], len([r for r in wf.rows if wf.feasible(q, r)])))

    L = ["# Masked-identity backtest of the workflow-account mechanisms (C7.1)", "",
         f"Population: {len(truth)} requests whose account is fixed by explicit admissible evidence at their own cutoff "
         f"({sum(1 for c in truth if split.get(c) == 'samples')} samples, {sum(1 for c in truth if split.get(c) != 'samples')} "
         f"targets). The truth mapping exists only in this script.", "",
         f"**Control:** {'PASSED: no masked request is solved by explicit_account and no truth account stays linked at the explicit tier, in either variant' if not leaks else 'FAILED: ' + '; '.join(leaks[:10])}.", ""]
    for name, rows in variants.items():
        L += render(name, rows, comps if name == "component" else None)
    L += ["## The legacy links (unmasked), for comparison", "",
          "| case | mechanism | feasible rows |", "|---|---|---|"]
    L += [f"| {c} | {m} | {n} |" for c, m, n in sorted(legacy)]
    L += ["", "## Reading", "",
          "- Selection bias: these accounts were identifiable, so their windows and neighbours may differ from the genuinely "
          "anonymous accounts the legacy links concern. This is supporting evidence about the mechanisms, **not** hidden-target accuracy.",
          "- Only existing mechanisms were run; no cadence, status or guess rule was added.",
          "- The nearest-anchor fallback row is what the strict→scored fallback would pick on the solver's abstentions; "
          "the engine uses it only when a row would otherwise have no steps."]
    md = "\n".join(L) + "\n"
    (a.out.write_text(md) if a.out else print(md))
    if a.json:
        a.json.write_text(json.dumps({"variants": variants, "legacy": legacy, "leaks": leaks}, indent=1) + "\n")
    for name, rows in variants.items():
        print(name, dict(Counter(r["outcome"] for r in rows)), "fallback", dict(Counter(r["fallback_outcome"] for r in rows if r["fallback_outcome"])))
    print("leaks", len(leaks))
    return 1 if leaks else 0


def render(name, rows, comps):
    by_mech, by_cand, by_cohort = defaultdict(Counter), defaultdict(Counter), defaultdict(Counter)
    for r in rows:
        by_mech[r["mechanism"]][r["outcome"]] += 1
        by_cand[_bucket(r["candidates"])][r["outcome"]] += 1
        by_cohort[_bucket(r["cohort_masked"])][r["outcome"]] += 1
    tot = Counter(r["outcome"] for r in rows)
    fb = Counter(r["fallback_outcome"] for r in rows if r["fallback_outcome"])
    fbc = defaultdict(Counter)
    for r in rows:
        if r["fallback_outcome"]:
            fbc[_bucket(r["candidates"])][r["fallback_outcome"]] += 1
    order = [k for k in ("1", "2", "3", "4-6", "7-10", ">10")]

    def table(title, d, keys=None):
        out = [f"| {title} | correct | incorrect | abstain | n |", "|---|---|---|---|---|"]
        for k in [k for k in (keys or sorted(d)) if k in d]:
            c = d[k]
            out.append(f"| {k} | {c['correct']} | {c['incorrect']} | {c['abstain']} | {sum(c.values())} |")
        return out

    head = {"competitors": "Variant 1: each request masked together with every request competing for its feasible rows",
            "component": "Variant 2: every connected cohort of overlapping windows masked at once",
            "single": "Reference only (artificially easy, not evidence): one request masked at a time, neighbours visible"}[name]
    L = [f"## {head}", ""]
    if comps:
        L.append(f"Cohorts: {len(comps)} (sizes {sorted(len(c) for c in comps)}).")
    L += [f"Truth account still feasible after masking: {sum(r['truth_feasible'] for r in rows)}/{len(rows)}.", "",
          "### Solver, by mechanism", ""] + table("mechanism", by_mech) + [
          "", f"Totals: correct {tot['correct']}, incorrect {tot['incorrect']}, abstain {tot['abstain']} of {len(rows)}.", "",
          "### Nearest-anchor fallback on the solver's abstentions, by candidate count", ""] + table("candidates", fbc, order) + [
          "", f"Fallback totals: correct {fb['correct']}, incorrect {fb['incorrect']}, no pick {fb['abstain']}.", "",
          "### Solver, by feasible-candidate count", ""] + table("candidates", by_cand, order) + [
          "", "### Solver, by masked cohort size", ""] + table("masked together", by_cohort, order) + [""]
    return L


if __name__ == "__main__":
    sys.exit(main())
