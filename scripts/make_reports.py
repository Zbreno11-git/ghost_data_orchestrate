"""Generate code/evaluation/evaluation_report.md and usage_report.md from run artifacts (S5 C5.9/C5.10).

Every number comes from a file: run directories (output.csv, decisions.jsonl, summary.json, llm_keys.jsonl),
the evaluator (code/evaluation/metrics.py), the comparison harness (code/evaluation/compare.py) and the ledger
(state/usage_ledger.jsonl). Hand-written prose explains, it never states a number.

Usage: python3 -I scripts/make_reports.py --final runs/s5/final --samples runs/s5/final-samples
         --custom runs/s5/final-custom-<name> ... --compare base:cand:label ...
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "code"))

from evaluation.compare import compare  # noqa: E402
from evaluation.metrics import evaluate, load_output  # noqa: E402
from ghostaudit.validate import validate_file  # noqa: E402

DATASET = ROOT / "dataset"
CUSTOM = ROOT / "code" / "evaluation" / "custom_cases"


def _r(m: dict) -> str:
    return f"{m['value']:.4f} ({m['num']}/{m['den']})"


def _decisions(run: Path) -> list[dict]:
    return [json.loads(l) for l in open(run / "decisions.jsonl", encoding="utf-8")]


def metrics_block(m: dict) -> list[str]:
    out = ["| metric | value |", "|---|---|"]
    for k in ("status_accuracy", "whole_case_exact", "step_precision", "step_recall", "evidence_accuracy_on_matched",
              "cited_evidence_recall", "sequence_accuracy", "ordered_operations_accuracy"):
        out.append(f"| {k} | {_r(m[k])} |")
    out.append(f"| step_f1 | {m['step_f1']:.4f} |")
    for f, v in m["field_accuracy"].items():
        out.append(f"| field_accuracy.{f} | {_r(v)} |")
    out.append(f"| aligned / missing / extra steps | {m['aligned_steps']} / {m['missing_steps']} / {m['extra_steps']} |")
    return out


def evaluation_report(a) -> str:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    summ = json.loads((a.final / "summary.json").read_text())
    from ghostaudit.ingest.manifest import evidence_times, read_csv
    requests = {r["case_id"]: r for r in read_csv(DATASET / "deletion_requests.csv")}
    vio = validate_file(a.final / "output.csv", requests, evidence_times(DATASET))
    dec = _decisions(a.final)
    heur = [d for d in dec if any(r.startswith("HEURISTIC PREDICTION") for r in d["reasons"])]
    gold = load_output(DATASET / "sample_output.csv")
    ms = evaluate(load_output(a.samples / "output.csv"), gold)
    conf = ms["status_confusion"]
    L = [f"# Evaluation report", "",
         f"Generated {now} by `scripts/make_reports.py` from run artifacts; every number below is read from a file.",
         "", "Final configuration: "
         f"`main.py run --engine {summ['engine']} --agent-scope {summ.get('agent_scope')} --ownership {summ['ownership']}` "
         f"(agent model `{summ.get('model')}`). Run directory `{a.final}`.", "",
         "Three questions are kept apart below, because a row can pass one and fail another: is the output "
         "**structurally valid**, is each verdict **supported by evidence**, and how close are the predictions to "
         "the **public sample answers**.", "",
         "## 1. Structural validity (518 target requests)", "",
         f"`main.py validate` on the submitted output: **{len(vio)} violations**, {summ['rows']} rows "
         "(unique, sorted by case_id, JSON arrays, legal operation/state pairs, canonical order, citations only "
         "where required and never after audit_at).", "",
         "## 2. Evidence support (518 target requests)", "",
         "| support | rows | meaning |", "|---|---|---|",
         f"| resolved | {summ['support'].get('resolved', 0)} | every linked resource is tied to the subject by "
         "explicit evidence and has a reconstructed state; account attributed |",
         f"| weak | {summ['support'].get('weak', 0)} | depends on a workflow-only link, an ownership ambiguity, "
         "or a low-confidence intent |",
         f"| unresolved | {summ['support'].get('unresolved', 0)} | no attributable account, or a resource whose "
         "state the evidence leaves unknown |", "",
         f"Status counts: {json.dumps(summ['status'])}. By support and status: "
         f"{json.dumps(summ['status_by_support'])}.", "",
         "Most unresolved rows lack an account: the candidate accounts appear only in deletion-worker activity rows "
         "(which carry no run identifier), so no evidence ties one to the subject; the engine reports the case "
         "rather than guess. Their other findings remain evidence-backed.", "",
         f"**Heuristic predictions ({len(heur)} rows)**, by the owner's decision (A29), for rows with no grounded "
         "proposal; each is unresolved and says so in its reasons:", ""]
    for d in heur:
        L.append(f"- `{d['case_id']}` {d['status']}: {d['reasons'][0].split('|')[0].strip()}")
    L += ["", "## 3. Public samples (32 cases, full official denominators)", "",
          f"Final configuration on `dataset/sample_deletion_requests.csv` (run `{a.samples}`):", ""]
    L += metrics_block(ms)
    L += ["", "Status confusion (gold → predicted): " + ", ".join(f"{k}: {v}" for k, v in sorted(conf.items())), "",
          "Sequence accuracy counts a case whose full step list matches in order; the grader preserves array order "
          "and ignores key order.", "",
          "### The ceiling of these denominators", "",
          "The step denominator keeps every answer step, including steps no participant-visible evidence can "
          "support (searches recorded in `docs/DECISIONS.md`):", "",
          "- D10: `audit_record_6645` and `audit_record_5569` (cases 18, 20) appear in no evidence file, table or "
          "image extract; a literal byte search of all participant files finds them only in the sample answers.",
          "- D13: `account_004` (case 04) likewise appears only in the sample answers.",
          "- D12: six resources (case 09's `account_3960` and `audit_record_4902`; audit records 4128, 7095, 3954, "
          "1707 in cases 23/24/29/30) are named only by files captured after their case's audit_at; the contract "
          "forbids using them, so the engine never names them (account_3960 stays, named by an admissible row).",
          "- Accounts named only by deletion-worker rows cannot be attributed without guessing (see §2).", "",
          "These are explained beside the score, not removed from it.", "",
          "## 4. Custom evaluation cases (independently authored)", "",
          "Written by a subagent that did not see the engine code (A13); each has its own dataset and expected "
          "output under `code/evaluation/custom_cases/`.", "", "| case | what it tests | status | whole-case | step P | step R |",
          "|---|---|---|---|---|---|"]
    for run in a.custom:
        name = run.name.split("custom-", 1)[1]
        m = evaluate(load_output(run / "output.csv"), load_output(CUSTOM / name / "expected_output.csv"))
        why = (CUSTOM / name / "RATIONALE.md").read_text().splitlines()
        # the "What it tests" list: its bold item titles, e.g. "Historical identity resolution; Replication drift"
        import re as _re
        start = next((i for i, l in enumerate(why) if l.strip().lower() == "## what it tests"), None)
        items = []
        for l in why[start + 1:] if start is not None else []:
            if l.startswith("## "):
                break
            items += _re.findall(r"^\d+\. \*\*(.+?)\*\*", l)
        what = "; ".join(i.rstrip(".") for i in items) or name
        L.append(f"| {name} | {what} | {_r(m['status_accuracy'])} | {_r(m['whole_case_exact'])} | "
                 f"{_r(m['step_precision'])} | {_r(m['step_recall'])} |")
    L += ["", "## 5. Case-by-case comparisons", "",
          "Each line compares two runs on the same cases against the answers. *Not in the answer but supported* "
          "means the added step cites evidence that names the resource; *unsupported* means it does not. A status "
          "flip from INCOMPLETE to COMPLETE is listed separately because it can hide a violation.", "",
          "| comparison | cases | whole-case base → cand | correct steps removed | added: in answer / supported / unsupported | INCOMPLETE→COMPLETE | agent cost paid in that run (replays: $0) |",
          "|---|---|---|---|---|---|---|"]
    for spec in a.compare:
        base, cand, label = spec.split(":", 2)
        gold_path = DATASET / "sample_output.csv"
        rows, s = compare(Path(base), Path(cand), gold_path, DATASET)
        ids = {l.split(",", 1)[0] for l in (Path(cand) / "output.csv").read_text().splitlines()[1:]}
        rows = [r for r in rows if r["case_id"] in ids]
        t = Counter()
        for r in rows:
            for k in ("whole_base", "whole_cand", "correct_removed", "added_in_gold", "added_supported_not_in_gold",
                      "added_unsupported", "flip_to_complete"):
                t[k] += r[k]
            t["cost"] += r["cost_usd"]
        L.append(f"| {label} | {len(rows)} | {t['whole_base']} → {t['whole_cand']} | {t['correct_removed']} | "
                 f"{t['added_in_gold']} / {t['added_supported_not_in_gold']} / {t['added_unsupported']} | "
                 f"{t['flip_to_complete']} | ${t['cost']:.4f} |")
    L += ["", "On the target split (no answers), engine changes moved rows only where the per-case diffs were traced "
          "to raw evidence, and every INCOMPLETE→COMPLETE flip was investigated (`docs/plans/session-05.md`, "
          "C5.2–C5.6). Session 6 changed no row: its audits found no evidence-backed link or parsing defect to fix "
          "(`docs/plans/session-06.md`).", ""]
    diag = ROOT / "code" / "evaluation" / "diagnostics.md"
    if diag.exists():
        t = diag.read_text().splitlines()
        i = next(k for k, l in enumerate(t) if l.startswith("| cause |"))
        j = next(k for k in range(i, len(t)) if not t[k].startswith("|"))
        L += ["## 5b. Mismatch diagnostics by earliest responsible stage", "",
              "Every sample mismatch of the final run, with one cause each (`code/evaluation/diagnose.py`; the full "
              "list with examples is in `code/evaluation/diagnostics.md`). \"No supporting fact found\" means the id "
              "occurs in no decoded source (raw text, PDF text from two decoders, every vision extract, the activity "
              "and audit CSVs); it lists the checks made and is not proof that the evidence is absent.", ""] + t[i:j] + [
              "", t[j + 1] if j + 1 < len(t) and t[j + 1].startswith("Before") else "", ""]
    L += [(ROOT / "code" / "evaluation" / "failures_and_fixes.md").read_text()]
    L += ["", "## Tuning exposure", "",
          "Ownership, citation and screen-reading rules were measured on the 32 public samples, so these scores "
          "are optimistic for the hidden targets. No case id, evidence id, label or case family appears in code "
          "(a test greps the prediction path for the sample answers file); the "
          f"{len(list((ROOT / 'code' / 'evaluation' / 'custom_cases').glob('*/expected_output.csv')))} custom cases "
          "were specified independently of the engine. The samples have been inspected since the first session, so "
          "they are not a held-out set. No hidden-target accuracy is claimed.", ""]
    return "\n".join(L)


def usage_report(a) -> str:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    summ = json.loads((a.final / "summary.json").read_text())
    used = [json.loads(l) for l in open(a.final / "llm_keys.jsonl", encoding="utf-8")]
    rows = [json.loads(l) for l in open(ROOT / "state" / "usage_ledger.jsonl", encoding="utf-8")]
    res = {r["res_id"]: r for r in rows if r["kind"] == "reserve"}
    origin = {}
    for r in rows:
        if r["kind"] == "settle" and r.get("request_key"):
            origin.setdefault(r["request_key"], res.get(r["res_id"], {}).get("run_id"))
    per = defaultdict(Counter)
    for u in used:
        k = (u["model"], u["purpose"])
        us = u.get("usage") or {}
        per[k]["calls"] += 1
        per[k]["live"] += 0 if u["cache"] else 1
        per[k]["input"] += us.get("input_tokens", 0) or 0
        per[k]["output"] += (us.get("output_tokens", 0) or 0) + (us.get("thought_tokens", 0) or 0)
        per[k]["cost_x1e6"] += round((us.get("cost_usd", 0) or 0) * 1e6)
    n = summ["rows"]
    tot = Counter()
    for c in per.values():
        tot.update(c)
    L = ["# Usage report", "", f"Generated {now} by `scripts/make_reports.py` from `{a.final}/llm_keys.jsonl` "
         "(every model response the final run used) and `state/usage_ledger.jsonl` (every paid call of the project).",
         "", "## Final full-dataset run (the one that produced output.csv)", "",
         f"Provider: Google Gemini API. Requests: {n}. Responses are counted once each; *live* ones were paid in "
         "this run, the others were served from the response cache, paid by the earlier run named under "
         "provenance (identical request content).", "",
         "| model | purpose | calls | live | input tokens | output tokens (incl. thinking) | cost (USD) |",
         "|---|---|---|---|---|---|---|"]
    for (model, purpose), c in sorted(per.items()):
        L.append(f"| {model} | {purpose} | {c['calls']} | {c['live']} | {c['input']:,} | {c['output']:,} | "
                 f"{c['cost_x1e6'] / 1e6:.6f} |")
    live_cost = sum(round(((u.get("usage") or {}).get("cost_usd", 0) or 0) * 1e6) for u in used if not u["cache"])
    L += [f"| **all** | | **{tot['calls']}** | {tot['live']} | **{tot['input']:,}** | **{tot['output']:,}** | "
          f"**{tot['cost_x1e6'] / 1e6:.6f}** |", "",
          f"The cost column is what the responses behind this output cost when they were generated (the full price "
          f"of the run); of it, ${live_cost / 1e6:.6f} was paid in this run and the rest earlier (provenance below).", "",
          f"Per request ({n}): {tot['calls'] / n:.2f} calls, {(tot['input'] + tot['output']) / n:,.0f} tokens, "
          f"${tot['cost_x1e6'] / 1e6 / n:.6f}. Total tokens {tot['input'] + tot['output']:,}.", "",
          f"Agent scope `{summ.get('agent_scope')}`: {summ['agent'].get('skipped_resolved', 0)} resolved proposals "
          f"were published without a model call; {summ['agent'].get('submitted', 0)} reviews submitted, "
          f"{summ['agent'].get('fallback', 0)} fell back to the deterministic proposal. Intent is one batched "
          "classification pass over all requests, cross-checked against the deterministic rule.", "",
          "Provenance of cached responses (run that paid for them): " + ", ".join(
              f"`{r}` {c}" for r, c in Counter(origin.get(u["request_key"], "?") for u in used if u["cache"]).most_common()),
          "", "Screenshot extraction (one-time, cached in `state/vision_cache/` and shipped with the code) is part of "
          "ingestion, not of this run; it is in the cumulative table below.", "",
          "## Cumulative project spend (all runs, from the ledger)", "",
          "| purpose | model | settled calls | cost (USD) |", "|---|---|---|---|"]
    cum, calls = Counter(), Counter()
    for r in rows:
        if r["kind"] == "settle":
            rv = res.get(r["res_id"], {})
            cum[(rv.get("purpose"), rv.get("model"))] += round((r.get("cost_usd") or 0) * 1e6)
            calls[(rv.get("purpose"), rv.get("model"))] += 1
    for k in sorted(cum, key=str):
        L.append(f"| {k[0]} | {k[1]} | {calls[k]} | {cum[k] / 1e6:.6f} |")
    open_res = [r for rid, r in res.items() if not any(s["kind"] == "settle" and s["res_id"] == rid for s in rows)]
    L += [f"| **settled total** | | {sum(calls.values())} | **{sum(cum.values()) / 1e6:.6f}** |", "",
          f"Open reservations: {len(open_res)}, ${sum(r['est_usd'] for r in open_res):.6f}, counted against the budget "
          "because they may have been billed (an in-flight call of a run killed on purpose to prove resume). "
          + "".join(f"A {r.get('error')} (HTTP {r.get('code') or '4xx, code not recorded'}) on {res.get(r['res_id'], {}).get('purpose')} was booked at "
                    f"its reservation, ${r.get('cost_usd') or 0:.6f}, before rejected requests were settled at $0 "
                    "(A21); the append-only ledger keeps it. "
                    for r in rows if r["kind"] == "settle" and r.get("status") == "error"
                    and r.get("cost_basis") == "reservation")
          + "Budget ceiling $4.50 (hard stop in the gateway). No key or credential appears in this report.", ""]
    return "\n".join(L)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--final", type=Path, required=True)
    ap.add_argument("--samples", type=Path, required=True)
    ap.add_argument("--custom", type=Path, nargs="+", default=[])
    ap.add_argument("--compare", nargs="*", default=[])
    a = ap.parse_args(argv)
    out = ROOT / "code" / "evaluation"
    (out / "evaluation_report.md").write_text(evaluation_report(a))
    (out / "usage_report.md").write_text(usage_report(a))
    print(f"wrote {out / 'evaluation_report.md'} and {out / 'usage_report.md'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
