# Session 06 (S6): evidence-backed recall at preserved precision

> The frozen plan is `docs/plans/MASTER_PLAN.md` §S6 (C6.1–C6.4, plus "+2 custom cases"). SESSIONS §S6 adds C6.5
> (explain a case). This file plans S6 as approved at 01:35 UTC, and integrates Breno's mid-turn message
> (2026-10-25, the JSONL event right after :6605, "Please strengthen the S6 plan…") into the same session.
> MASTER_PLAN stays untouched. The mapping is in brackets in the checkpoint table.

## Goal (Breno's words)

"Recover evidence-backed missing steps while preserving precision."
- The S5 numbers (step P 162/163, R 162/193, whole-case 12/32, status 32/32) are **public-sample results**, not
  hidden-target accuracy or production readiness.
- The 32 samples have been inspected since S0, so they are **not a held-out set**. New rules get independently
  specified synthetic cases instead.

## Opening measurements (times from `date -u`)

| Check (before 01:35:06Z, the first log write) | Result |
|---|---|
| `git status --short`; HEAD vs origin/main | empty; both `16183c2f…` "Checkpoint before compact (S6 next)…" |
| CI by head_sha | `tests completed success 2026-10-25T01:24:28Z` |
| `main.py status` | `settled $1.870528  outstanding $0.004447  ceiling $4.50  rows 4155` |
| pytest | `225 passed` |
| root `output.csv` sha256 | `ee9504d517fb…8c4c` (the S5 safety package; preserved) |

**Frozen S5 baselines** (they never change in S6):
- **Deterministic:** `runs/s6/base-*`, rebuilt from HEAD at 01:36Z. Samples output is byte-identical to
  `runs/s5/final-samples2`:

  | Measure | Value |
  |---|---|
  | status | 32/32 |
  | whole | 12/32 |
  | P | 162/163 |
  | R | 162/193 |
  | F1 | 0.9101 |
  | evidence on matched | 162/162 |
  | cited recall | 61/75 |
  | sequence | 12/32 |

  Targets: 0 violations, support 172 / 20 / 326.
- **Published agent run:** `runs/s5/final`, support 175 / 18 / 325, 0 violations.

**Pre-measurement (scratchpad scripts, read-only, before 01:35:06Z):**
- **Lineage.** 0/23 missing association steps share an admissible observation with a subject identifier or an
  already-linked resource. These are only the observations the engine extracted, which is exactly what C6.1
  must audit.
- **Timing.** It cannot separate requests reported at the same hour. Scored mode swaps case_27 and case_29, and
  adds 13 wrong steps for 6 right ones (pre-A26/A30 code).
- **Status compatibility** (reported_status vs the run's reported_result) excludes 0/31 sample gold rows and
  makes more candidates unique.
- **Raw-byte search defect (ours).** All 4 PDFs are FlateDecode-compressed (`grep -c FlateDecode`), so
  `diagnose.py`'s "absent from supplied evidence" verdict cannot see PDF text. Its 3 "absent" items are
  therefore unproven.

## Owner rules for S6 (Breno, mid-turn)

- No link from timing alone, naming patterns, sample labels or **assumed one-to-one assignments**.
  Ambiguities stay unresolved.
- An anonymized record may be attributable through **documented lineage** in the supplied evidence, without
  exposing PII.
- A supported disagreement with the sample is documented separately, never auto-counted as a false positive.
  Nothing is deleted only to raise the score.
- No new full paid run without a concrete hypothesis and a cost estimate.
- Deterministic and agent contributions are reported separately.
- The S5 safety package stays in place. Export and upload come after S7's release checks (A31).

**Consequences for the approved plan:**
- **A32 (status compatibility) is rejected.** It produces a link only by narrowing a time window and feeding
  the one-to-one solver: "timing + assumed one-to-one".
- **Scored mode cannot be adopted** (timing-only accounts). C6.6 still measures it, for transparency.
- **Not changed by S6:** the engine's existing workflow-tier accounts (A20/A24: one-to-one deduction, labelled
  weak, never explicit). They are reported as such. Removing them is Breno's call, and is listed under
  "Depends on Breno" at the close.

## Checkpoint map

| C | Does | ✅ Closes when (command → expected) |
|---|---|---|
| C6.0 | log; this file; frozen baselines | ✅ above (01:36Z) |
| C6.1 [C6.1] **extraction coverage audit** | for every source implicated in a remaining mismatch (the gold-cited file, plus every file whose content names the resource), compare original content with normalized observations: identifiers, relationships, states, timestamps, retention fields, row/column boundaries. Text comes from pdftotext/pypdf for PDFs, and from the vision extract plus a **visual read of the rendered PNG** for screenshots. `diagnose.py` loses its raw-byte verdict: its search corpus becomes decoded text (raw for txt/json/sql/log/csv, PDF page text, vision extracts), and "absent" becomes three-way: *fact present but missed/misinterpreted* · *no supporting fact found after documented checks* (the checks listed) · *undetermined* | `scripts/analysis/extraction_audit.py` → per source: facts in the original vs facts in observations, skipped or partial records listed explicitly; `docs/plans/session-06.md` Progress holds the table. Every parsing defect found gets a regression test plus a contrasting example (red first, mutation red); otherwise "no defect, checks: …" |
| C6.2 [C6.5, minimal, early] **trace and explain** | `Plan.trace` in decisions.jsonl: intent (label, confidence, source), subject (identifiers with role and source), account deduction (how, candidates), excluded with reasons, ambiguities, heuristic flag, `rule_id` per decision. `main.py explain <case> --run <dir> [--md]` prints person → evidence chain → resource/copy → temporal state → policy → decision, plus rejected links and uncertainty. Provenance comes from an offline re-ingest; no gateway, no key; a missing item prints "not recorded in the trace" | tests: every obs_id printed exists in the run's decisions; the gateway is never imported; an old trace prints "not recorded in the trace"; sample output.csv byte-identical to base |
| C6.3 [C6.1 cont.] **rejected-association diagnosis** | for each association miss (the 7 analytics first, then the 16 accounts), with the extra account_3865 reviewed separately: resource found? admissible or excluded (why)? direct identifiers? explicit intermediate references (customer_reference, source_resource_id, hashes, historical identifiers, transformation or lineage rows)? conflicting owners? **the exact break point**. Bounded: a fixed list of documented checks per resource (store query, decoded-text search for the id and for every subject identifier, rendered read of each gold-cited image or page, lineage fields of every co-named record); a path that yields no new evidence after the list ends as "no supporting fact found after documented checks" | `scripts/analysis/association_paths.py` (evaluator side) → one row per miss with the break point; `explain` output for 3 representative misses saved under `runs/s6/diag/`; extra step classified as engine defect / supported disagreement / undetermined |
| C6.4 [C6.2] **generic fixes only** | only for a defect C6.1/C6.3 show: a parsing rule or an evidence lineage, never timing, naming or labels. Each rule has a positive case and a **close negative** case | per fix: red test first, contrasting negative test, mutation red; `compare.py` vs base: every gained, lost or added step listed; no unexplained regression; `diagnose.py` before/after |
| C6.5 [new, Breno 4] **robustness (metamorphic) tests** | on a synthetic dataset run end to end (`run_deterministic`): shuffled input rows and files → identical output; duplicated identical evidence → no extra steps, same support; another person's record added → the case unchanged; post-cutoff evidence added → the historical answer unchanged | 4 tests, each with its safeguard disabled once (mutation) → red |
| C6.6 [C6.3] **ownership mode by metrics** | strict vs scored on the final code, both measured; adoption bounded by the owner rule (no timing-only links) | table: whole, P/R/F1, wrong additions, flips, support; DECISIONS A32 (rejected) and A33 (strict kept, measured) |
| C6.7 [MASTER_PLAN "+2 custom"] **independent synthetic cases** | a subagent specifies cases from the problem statement and the new rules' descriptions only (never the samples, never our predictions): a tombstone pair, a clean primary with a dirty replica, plus one positive and one close-negative case per C6.4 rule. Expected answers live only in `code/evaluation/custom_cases/` | the cases run through the CLI; whole-case reported as measured; never tuned after the first run (a failure is investigated as an engine defect or a case defect, and the call is written down) |
| C6.8 [C6.4] **targeted recompute + final accuracy gate** | deterministic recompute of samples, targets and custom on the final code; the set of cases whose deterministic record changed. A paid agent re-run only with a written hypothesis and a cost estimate: the changed non-resolved cases × $0.0035. Final candidate vs the frozen S5 baseline | `compare.py` + `evaluation/main.py` + `diagnose.py` on 32 samples and every custom set: P/R/F1, whole, status, citation, sequence, gained/lost correct, incorrect added/removed, flips, support moves, causes before/after; supported disagreements listed apart; det vs agent contribution in separate columns; `validate` 0 violations; fingerprints valid (stale count reported) |
| C6.9 [close] | the representative explanations (COMPLETE, INCOMPLETE, NOT_APPLICABLE, unresolved, heuristic) in `docs/explanations/`; republish only if the candidate wins the gate (else the S5 package stays); reports; package; ritual | `package_code.py` exit 0 (if republished); `log_audit.py` exit 0; DIARY, PROGRESS, SESSIONS, STATUS, REQUIREMENTS_MAP; CI green by head_sha |

🐞 **Predicted failures, and how to debug them:**
- **C6.1: pypdf and pdftotext disagree on a page.** Keep both texts and diff them. A fact in one only is a
  parser defect candidate, and is read on the rendered page.
- **C6.1: the vision extract omits a panel row.** That is a vision miss, not a parser defect. It is fixable
  only by a paid re-read (≤ $0.01 per image), which needs a hypothesis first.
- **C6.3: an "intermediate reference" exists only in the wrapper** (a lookup key). It is discovery, never
  exposure (FR-11). It can give lineage only if it names the subject and the resource in one unit.
- **C6.4: a lineage fix also links decoys.** The close negative (the same chain naming another subject) must
  stay unlinked; the row-bound rule (A25) applies.
- **C6.5: the duplicate test passes because dedup happens by obs_id collision.** A duplicated file gets a new
  file_id, so the test must assert on steps and support, not on store size.

## Budget

- Planned: $0 for C6.0–C6.7 (deterministic engine plus the subagent).
- C6.8 pays only with a stated hypothesis, at the estimate above; the ceiling is unchanged.

## Progress (measured; times from `date -u`)

- **C6.0 ✅ 01:36Z.** Baselines above; log entry 01:35:06Z.
- **C6.1 ✅ 01:41Z. Extraction coverage audit** (`scripts/analysis/extraction_audit.py --run runs/s6/base-samples`
  → `runs/s6/diag/extraction_audit.md`; 32 mismatch resources; decoders: raw, pypdf, pdftotext, both vision
  models; undecodable sources: none).
  - **Line-level coverage: complete.** Every decoded line naming a mismatch resource has its ids, timestamps and
    state words in an observation of the same source (0 tokens missing in 32 rows). No record was skipped or
    partly read for these sources.
  - **Rendered screenshots read visually:** evidence_19 (analytics, user_20), evidence_37 (Sentinel, user_03),
    evidence_04 (customer ops, user_11), evidence_42 (reference registry, user_17). None of them names a
    mismatch resource or a mismatch subject. The vision extracts hold every token read on the screen (8/8
    extracts, both models). Screenshot text extraction is sufficient for these sources.
  - **Verdicts:**
    - 29 resources are *extracted*: present in observations, so the miss is downstream (association or time);
    - account_004, audit_record_6645 and audit_record_5569 are *no supporting fact found after documented
      checks*: whole-word search of every decoded source, the activity and audit CSVs, and the store;
    - 0 are *present but missed*.
  - **Defect found (ours, ERRORS #8):** `diagnose.py`'s "absent from supplied evidence" was a raw-byte search;
    the 4 PDFs are FlateDecode-compressed (10/10 of their ids invisible to it).
    - Fixed: `code/evaluation/corpus.py` (the decoded corpus shared by both tools); the cause is now "no
      supporting fact found" / "undetermined".
    - `test_diagnose.py`: 2 tests (support_001, the only id that only a PDF carries; a contrast id and a
      prefix). Red before the fix; mutation "PDFs as raw bytes" red. `227 passed`.
  - No parsing defect in the engine's extraction was found, so there is no engine fix here.
- **C6.2 ✅ 01:45Z. Trace and minimal explain** (built early, as Breno asked, to drive C6.3).
  - `Plan.trace` in decisions.jsonl: request times and the workflow claim, intent with its source, the person
    with every identifier (role at the cutoff, source), the account deduction (tier, how, evidence, remaining
    candidates), exclusions, ambiguities, the heuristic flag, and the ownership mode.
  - Each decision carries `rule_id` (or `rule_note` when the category has no deletion_rules row: DATA_FLOW).
  - `main.py explain <case> --run <dir> [--md]` (`code/ghostaudit/explain.py`): verdict and certainty kept
    apart → request → person → chain per resource with provenance (source, kind, both clocks, basis) →
    rejected links and ambiguities → copies and states → rule → recorded reasons → ordered steps.
  - **Tests** (`test_explain.py`, 4): printed obs_ids ⊆ the trace; the trace keys; a trace-less run prints
    "not recorded in the trace" line by line; no `ghostaudit.llm`/`google` module loads, with no key and a dead
    proxy.
  - **Mutations: 7, all red in the end.** Two survived first, because the missing-trace assert matched MISSING
    on other lines (ERRORS #4, 6th occurrence); it is now line-specific.
  - The sample output.csv is byte-identical to base (`cmp`).
