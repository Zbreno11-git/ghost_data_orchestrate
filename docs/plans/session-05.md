# Session 05 (S5) — grounded accuracy first, then pilot, full run, reports, package, release kit

> The frozen plan is `docs/plans/MASTER_PLAN.md` §S5 (C5.1–C5.6). This file plans S5 as amended by Breno's
> mid-turn message (2026-10-24 21:34:41 UTC, six items) and his answer on the no-proposal rows (21:41:52 UTC).
> - Its first deliverable on disk is `docs/plans/session-05.md`: checkpoint map, then Does / ✅ / 🐞 per
>   checkpoint, with each MASTER_PLAN checkpoint mapped and every adaptation given its reason.
> - Material decisions go to `docs/DECISIONS.md` (A24+), lessons to `docs/ERRORS.md`, and the release kit to
>   `PROGRESS.md` plus `docs/STATUS.md`.
> - MASTER_PLAN stays untouched.

## Context

S3+S4 delivered a validated deterministic engine and a bounded agent that barely moves it (A23). Breno's
objective for S5 is **evidence-grounded accuracy plus a complete submission**. Before more model spend, he wants:
1. semantically checked agent decisions;
2. extraction and interpretation gaps fixed at their earliest cause;
3. case-by-case measurement that hides no regression;
4. proven temporal isolation and honest support labels;
5. a corrected log record;
6. a trace-delivery plan that survives compaction.

The pilot, full run, reports and package then run on the improved engine.

## Opening measurements (2026-10-24 21:34–21:44 UTC; the disk agrees with the resume block)

| Check | Result |
|---|---|
| `git status --short`; HEAD = origin/main | empty; both `96ffa030…`, subject "Checkpoint before compact (S5 next)…" |
| CI on `96ffa03` (gh api by head_sha) | `tests completed success 2026-10-24T21:17:21Z` |
| `main.py status` | `settled $0.339118  outstanding $0.004447  ceiling $4.50  rows 313` |
| `pytest code/tests -q` | `177 passed` |
| `docs/plans/session-05.md` | does not exist |

**Probe of `runs/s3/targets-strict`** (written 20:53Z, before S4; C5.0 re-measures before anything relies on it):
- **349 non-resolved cases.** 311 of them carry "primary profile unassigned / no account resource attributed".
- **17 resources have an `unknown` verdict:** 7 backups, 3 data flows and 3 support messages show "1 copies in
  an undetermined state"; 4 have no admissible state evidence.
- **The 5 invalid rows** (case_39/46/53/55/61) resolve to data_flow_1121 (its evidence also names user_15),
  tombstone_17, support_1034, backup_9286/87/88/91 and object_19.
- **Extraction gap:**
  - PNG panels become one `kind="text"` observation each, with `system_id=None`.
  - Table panels take the first row's id as `resource_id`. Examples: evidence_32 "Archives" (4 rows of
    Archive ID + Account), Topology (24 rows), Objects (40), Events (42), All exports (20).
  - `ownership.text_units` does split rows, but `policy.copy_states` treats such a panel only as a "document
    copy". That copy is undetermined for flows and backups, and it poisons the verdict.
  - Panels titled by a resource id are never read as state: `data_flow_1121` (Status Healthy, Continuous
    sync), and the Activity line "backup_9286 restored · Completed".
  - No screenshot carries a restore-permission label (label survey over the 11 committed extracts).
- **Agent validation gaps** (`agent.py`):
  - any workflow candidate is accepted as the account;
  - an addition passes if any cited observation mentions the resource;
  - an exclusion needs no evidence;
  - `tier_for` says `explicit` if any cited observation holds any subject identifier, even one that does not
    name the resource.

**Temporal isolation and support (Explore review, 21:45Z).** Each claim gets a red test before its fix.

| # | Claim | Where | Exposure |
|---|---|---|---|
| T1 | `OwnerIndex` is built once with `FAR_FUTURE=2100`. "Another subject's identifier" therefore includes values acquired after the case's cutoff, which can only remove links | `runner.py:25,59`; `ownership.py:82-110,151,341` | latent (no email/phone ever held by two users) |
| T2 | The workflow solver is global. Request Y's later rows, links and matching edges can force or take X's row (`taken`, `_forced`), and `taken_by` shows that claim to the agent | `ownership.py:175-271,305-310`; `tools.py:138,144` | unmeasured; C5.2 counts it |
| T3 | `corroboration` and the scored `inside` windows read worker rows without an admissibility check | `ownership.py:192-199,331-339` | inert today |
| S1 | Ownership ambiguities never demote support | `planner.py:62,101` | 0 resolved target rows carry one (21:44Z) |
| S2 | An unknown RETAIN record in an INCOMPLETE case gets VERIFY_RECORD_PRESENT and no "unknown" reason | `planner.py:87-92` | to measure |
| S3 | The agent path recomputes support, so a loosely "explicit" agent account can lift weak to resolved | `agent.py:108-132,187`; `runner.py:109-118` | to measure |
| S4 | The decoy check keeps a link whose record also names another subject (it only adds an ambiguity) | `ownership.py:350-360` | verify first which path excludes the case_28 decoy |

**log.txt audit (Explore review against the original JSONL, 21:39Z):**
- **Structure:** 16 entries, all with the four sections and exactly one `tool=Claude Code` and one
  `model=claude-opus-5-5`. 946/946 main-session assistant events report `claude-opus-5-5`. No secret
  patterns.
- **Defect 19:53 (log.txt:337–357):** steps 1–5 of the pasted prompt were replaced by a bracketed summary
  that claims "pasted in full". The original is main JSONL line 749, 19:49:41.976Z, uuid `2d165007…`.
- **Defect 16:57 (log.txt:292–314):** the User Prompt field is an agent-written note. No human message
  exists there; the approval was an ExitPlanMode tool call (JSONL 371, 16:49:20Z).
- **Unlogged human messages:**
  - JSONL 1558, 20:14:38: a mid-turn "wait";
  - JSONL 3666, 21:34:29: the S5 resume prompt;
  - JSONL 3699, 21:34:41: these six items;
  - the 21:41:52 answer on the no-proposal rows (logged in the 21:44:52 entry).
- **Disclosures needed:**
  - header times are write times (5 backfilled entries at 16:51:57);
  - line 406 (20:21) precedes line 426 (20:20);
  - line 492's `[TS_PLACEHOLDER]` was fixed in place by `sed -i` in the same command;
  - the subagent entry at 358 paraphrases its delegation prompt, and `parent_agent=claude-code-main-session`
    is a chosen label, not a runtime id.
- **Trace instructions** (`agent_trace_instructions.md`):
  - L3–13: a zip named `agent-trace.zip`, holding `agent-trace/claude-code/`; original files and folders,
    no summaries; sessions quit first; challenge sessions only; redacted.
  - L28–34: `/export` per session, plus the JSONL.
  - `subagents/` folders must be included: MASTER_PLAN C7.3's top-level-only glob would miss them.
  - `/root/.codex/sessions` has no match for this challenge, so exclude it.

## Owner decisions (recorded in DECISIONS as they land)

- **No-proposal rows (Breno, 2026-10-24 21:41:52 UTC, answer to the agent's question):**
  - Don't block the full run on them. Re-count after the fixes, then investigate each remaining one
    directly: source excerpts, current and historical identifiers, resource lineage, candidate account
    states. A bounded stronger-model review is allowed within budget.
  - Ownership evidence stays separate from state evidence: proving that an account exists or is absent
    never proves it is this person's. Timing proximity never silently becomes a proven link.
  - If any stay ambiguous, show **one compact table before final publication**: case, candidates,
    evidence, missing link, recommended prediction and its limits. Continue everything else meanwhile.
  - Provisional results are kept separate. No invented identifiers, citations or steps.
  - The reports distinguish structural validity, evidence support and heuristic predictions.
- **Agent scope for the full run:** after the pilot I recommend and **wait** (resume-block rule), doing the
  reports, package and log work in the meantime.
- **Publication:** root `output.csv` is written atomically only at final publication. That requires a fully
  validated full run and Breno's answer on the ambiguous-case table. Until then the validated provisional
  output lives at `runs/s5/provisional/output.csv`, and STATUS names that path for a safety upload.

## Checkpoint map (MASTER_PLAN mapping in brackets)

| C | Does | ✅ Closes when (command → expected) |
|---|---|---|
| C5.0 | log this turn and the unlogged turns (literal); write `session-05.md`; fresh baselines | `main.py run --split samples --out runs/s5/base-samples`, targets, and the 3 custom datasets → `validate` 0 violations on samples/custom; targets invalid count and support counts re-measured (with time), and listed |
| C5.1 | failure classification | `scripts/analysis/classify_failures.py runs/s5/base-targets` (reads decisions.jsonl only) → every non-resolved/invalid target case by **earliest** causal class (extraction / identity / ownership / temporal / category / state / citation / planning), plus a hand-reviewed stratified 20 with source excerpts; sample mismatches classed on the evaluator side |
| C5.2 | temporal isolation + support cap (T1–T3, S1–S4) | tests red first: (i) a later audit row giving user B an identifier A once held leaves A's earlier case identical (links, excluded, ambiguities); (ii) a request Y with rows/links after X's audit_at leaves `assigned[X]`, `excluded`, `taken_by` unchanged; (iii) a worker row after audit_at is no corroboration; (iv) one `support_of()` caps: any ownership ambiguity → ≤ weak, any unknown (RETAIN included) → unresolved, any workflow/agent-only link → ≤ weak, agent plan ≤ deterministic unless its new links pass C5.4's explicit rule; a derived test enumerates every reason producer. Fix: owners and solver **as of each cutoff** (requests `requested_at ≤ T_X`, rows `≤ T_X`, links at `min(T_Y,T_X)`), cached per cutoff, runtime measured. Every case whose output changes is listed and explained; mutation of each guard → red |
| C5.3 | extraction + explicit state interpretation | failing tests first. **Measured gaps (C5.1):** lookup results `BLOCKED`/`DISABLED`/`REDACTED` (5 each) fall through `_record_state` to UNKNOWN; a restore-policy trace `decision: deny` (5) is unread; a `[REDACTED]` marker in `message_text` (30) is not read as redacted; a screen naming a flow/backup is treated as a separate *physical copy* whose state is undetermined, which poisons the verdict (a screen is a view of the process, not a copy of personal data). Fix: read those explicit results; a document is a copy only for record treatments (DELETE/REDACT/ANONYMIZE/RETAIN); for DISABLE_FLOW/BLOCK_RESTORE a screen contributes state **only with an explicit enablement/permission label** (amendment 1): "Healthy" (health), "Continuous" (configuration) and a completed restore (a past event) never prove a flow or restore path enabled at audit_at. Screen tables split per row (resource from its id column, that row's fields, locator `panel:N/row:M`, panel title kept) so state and ownership stay row-bound. Tests include a healthy-but-disabled connector (→ DISABLED) and a completed restore followed by a restore block (→ BLOCKED). Ingest gate 94/94 files, 75/75 citations; samples: **no unexplained regression** (amendment 3); the vision cache is untouched (re-parse, no paid re-read); A24 records the rule |
| C5.4 | semantic validation of agent decisions | negatives red first in `test_agent.py`: an exclusion without evidence; an exclusion of an explicit violating resource without another-owner evidence (it must not turn INCOMPLETE into COMPLETE); an addition of another person's resource; a genuine but irrelevant citation; an account chosen by candidacy/timing only. Positives that must pass: a historical-email link; multi-observation lineage (obs A names r with a key, obs B ties the key to the subject); an anonymized record reached through lineage; a wrapper-only identifier as discovery, never exposure. Rule: a link is `explicit` only through a chain of cited admissible units, each naming both ends, ending at a subject identifier, and reusing `ownership.text_units` / `OwnerIndex` (as of cutoff); otherwise `workflow`. A rejected decision is repaired or dropped, never applied |
| C5.5 | stale-checkpoint guard, then case-by-case comparison | (amendment 2, first) each `cases/<cid>.json` carries a fingerprint = sha256 of the case's inputs (request row, the dataset files' hashes), code version (hash of `code/ghostaudit/**/*.py`), prompt + schema + tool declarations, model and the `[agent]/[intent]/[gateway]` config; resume reuses only an equal fingerprint. Tests: a relevant change (code, prompt, model, config, dataset row) forces recomputation; an unchanged case is reused. Then `code/evaluation/compare.py --base A --cand B` → per case: whole-case match, steps kept / correct removed / added, citation correctness, status flips (INCOMPLETE→COMPLETE flagged red), support moves, $ per improvement; an added step not in the gold answer is classed **"not in gold"** separately from **"unsupported by evidence"** (it is checked against its cited observation). On samples (32) and custom (3), full official denominators; det-before vs det-after and det vs agent (10-case bench re-run: only cases whose fingerprint changed are called, measured from ledger case_ids). A lower count is accepted only with the per-case explanation written down (amendment 3) |
| C5.6 | no-proposal investigation (Breno's rule) | re-count; for each remaining case a note with source excerpts, identifiers, lineage, candidate account states (ownership vs state evidence separated); bounded 3.8-flash review only where useful (≤ $0.10 total); the compact table prepared for Breno |
| C5.7 [C5.1] | pilot: 30 stratified targets, agent live | `main.py run --engine agent --mode live --split targets --cases <30> --out runs/s5/pilot` → $/case, support moves per stratum, projection; **recommend scope, wait for Breno**; meanwhile C5.9–C5.12 |
| C5.8 [C5.2] | full 518 run | `validate` → 518 rows, unique, sorted, JSON valid, 0 violations; unresolved listed; copied to `runs/s5/provisional/`; root `output.csv` only at final publication |
| C5.9 [C5.3] | `code/evaluation/evaluation_report.md` | status, step, field, sequence and evidence metrics; confusion matrix; the 3 custom cases; the C5.5 comparison; failures found and fixes; tuning exposure; the D10/D12/D13 ceiling beside full denominators; separate sections for structural validity, evidence support and heuristic predictions |
| C5.10 [C5.4] | `code/evaluation/usage_report.md` | generated from this run's ledger rows: providers, models, calls, in/out tokens, totals and averages per request, per model and overall, cache provenance; cumulative project spend including the $0.0176 S2 row and the open $0.004447 |
| C5.11 [C5.5] | `scripts/package_code.py` + clean-unpack replay | (amendment 4) zip = `README.md` + `code/` + **declared replay artifacts**: `state/vision_cache/*.json` (the 22 committed extracts; read by `ingest/images.py` today) and `replay/llm/<request_key>.json` for exactly the final run's cached responses (read by `llm/gateway.py` in replay mode), plus `replay/MANIFEST.json` with each file's sha256; the runtime verifies the hash on read and a mismatch is a loud error. Excluded: dataset/, .env, .venv, `runs/` (except the declared subset), pickled stores, nested archives. Test: unzip into an empty temp dir, install only `code/requirements.txt` into a fresh venv, link the supplied `dataset/`, `env -u GEMINI_API_KEY` replay → `cmp` identical to the published output.csv; `unzip -l` reviewed. If any artifact must come from outside the zip, the README says so and no "self-contained offline replay" is claimed (A25) |
| C5.12 | log audit + correction records | `scripts/analysis/log_audit.py` (reads the JSONL, prints no content) → every human message matched to an entry. Appended `CORRECTION` entries, nothing rewritten: **19:53** quotes the recovered original (JSONL 3f2c5c59…:749, event 19:49:41.976Z, uuid 2d165007…); **16:57** (amendment 5) states that **no human message exists** for it and documents what it records: the plan approval was the ExitPlanMode tool event (JSONL :371, 16:49:20Z) following the queued "I've approve the repo layout setup" (:363, 16:47:01.801Z, already logged at log.txt:273); the unlogged 20:14:38 "wait" (:1558) is recovered literally. Every correction separates **event time** (from the JSONL) from **recording time** (the header) and discloses: backfilled header times, the 20:21/20:20 order, the in-command `sed -i` placeholder fix at log.txt:492, the subagent paraphrase at log.txt:358 |
| C5.13 | release kit + trace staging tool | PROGRESS + STATUS "Release kit": the files, staging `~/agent-trace/` (outside repo and code.zip), collected-now vs at-closure, Breno's actions; `scripts/stage_traces.py --dry-run` lists the challenge JSONL **and `subagents/`**, redaction scan of staged copies only (`AIza`, `gho_`, `ghp_`, `sk-`, private keys, `.env` values) → 0 hits; final run at closure |
| C5.14 [C5.6] | commit/push; close S5 | CI green by head_sha; DIARY, PROGRESS, SESSIONS, STATUS, REQUIREMENTS_MAP updated; resume block; final report to Breno |

🐞 **Predicted failures, and how to debug them:**
- **C5.2:** per-cutoff solving is slow (550 requests) → group by cutoff and reuse prefix state; measure first.
- **C5.3:** per-row splitting duplicates by_resource entries or breaks the 75/75 citation gate → dedupe per
  obs, keep the panel observation for whole-document state.
- **C5.4:** the stricter rule rejects the bench's valid additions → print the chain for each rejection before
  loosening anything.
- **C5.5:** a status flip INCOMPLETE→COMPLETE → stop and investigate before adoption.

## Execution order

C5.0 → C5.1 → C5.2 → C5.3 → C5.4 → C5.5 (adopt each change only if C5.5 shows no unexplained regression) →
C5.6 → C5.7 → while waiting for Breno: C5.9 draft, C5.10, C5.11, C5.12, C5.13 → C5.8 after his scope answer →
regenerate C5.9/C5.10 from the full run → compact table to Breno if ambiguous cases remain → C5.14.

Rules throughout:
- Commit after each closed checkpoint, staging explicit paths only.
- Log every turn in log.txt.
- Kill by PID.
- Read the clock before writing any time.

## Budget

- **Spent:** $0.339 settled + $0.004 open.
- **Planned spend:**

  | Item | Estimate |
  |---|---|
  | Bench re-run of changed cases | ≤ $0.05 |
  | No-proposal review | ≤ $0.10 |
  | Pilot | ≈ $0.11 |
  | Full run | $1.2–1.8 |

- **Projected total ≤ $2.5**, under the $4.50 hard stop.

## Risks

- **Overfitting to the 32 samples.** Mitigations:
  - the rules are generic (per-row tables, state labels, lineage);
  - no ids, labels or case families appear in code;
  - the tuning exposure is disclosed;
  - the custom cases come from an independent subagent (A13).
- **The as-of solver changes many accounts.** C5.5 lists every change; strict mode still never guesses.
- **A paid full run before Breno's scope answer.** It never happens: the full run waits for his answer.
- **Public repo.** Corrections quote only Breno's prompts, which are already in log.txt-style content; the
  redaction scan runs before any write.

## Verification (end of S5)

```bash
.venv/bin/python -m pytest code/tests -q                          # all green, count reported
.venv/bin/python code/main.py validate runs/s5/full/output.csv    # 0 violations, 518 rows
.venv/bin/python code/evaluation/compare.py --base runs/s3/samples-strict --cand runs/s5/samples-final
.venv/bin/python scripts/package_code.py && unzip -l code.zip     # replay cmp identical in a temp dir
.venv/bin/python scripts/stage_traces.py --dry-run                # inventory + 0 redaction hits
.venv/bin/python code/main.py status                              # cumulative spend
git status --short; git rev-parse HEAD origin/main                # clean; equal; CI green by head_sha
```

## Amendments (Breno, mid-turn 2026-10-24 21:45:51 UTC, JSONL :4129)

Integrated into C5.3, C5.5, C5.11 and C5.12 above, without new modules:
1. No current activity inferred from ambiguous labels: health, configuration and a past restore are not enablement; explicit permission or a corroborated transition is required (tests: healthy-but-disabled; restore then block).
2. Case checkpoints are reused only with an equal fingerprint (dataset, code, prompt/schema, model, config).
3. "No count lower" becomes "no unexplained regression"; full denominators kept; "not in gold" ≠ "unsupported by evidence".
4. Replay artifacts in code.zip are declared, hash-verified at read, and exercised from a clean unpack; no self-contained claim if anything external is needed.
5. The 16:57 log entry gets no invented prompt: its relation to the approval tool event is documented; event vs recording times are distinguished.

## Progress (measured; times from `date -u`)

- **C5.0 ✅ 21:45Z (commit 5b5d464).** Log entry 21:44:52Z (three literal messages from the session JSONL). Fresh baselines in
  `runs/s5/base-*` equal S3's:
  - samples strict: status 32/32, whole 11/32, P 161/162, R 161/193, evidence 161/161, cited recall 61/75;
  - custom 3/3 whole-case;
  - targets: 518 rows, 169 resolved / 34 weak / 315 unresolved, 5 violations (DECIDED_EMPTY case_39/46/53/55/61).
  - Note: the plan-mode draft carried two estimated times ("21:5x", "…21:50"); this file uses the measured
    ones (ERRORS #5).
- **C5.1 ✅ 21:48Z.** `python3 -I scripts/analysis/classify_failures.py runs/s5/base-targets`:
  - `349 non-resolved or invalid cases of 518`; earliest class
    `{'extraction': 2, 'identity': 2, 'ownership': 342, 'state': 3}`.
  - *identity* = 2 NOT_APPLICABLE rows with a low-confidence intent (weak).
  - **Hand review (stratified 20, plus 5 accounts traced to the raw activity CSV):** the candidate accounts
    of case_180/218/276/300/410 appear only in deletion-worker DELETE_RECORD rows (plus lookups that name no
    person). The activity stream has no run or trace id
    (`activity_id,event_time,event_type,source_system,target_system,resource_id,reported_result,details`),
    so no lineage can tie an account to the subject's explicitly linked resources. This ownership limit is a
    property of the data (A23); it stays unresolved and is never guessed.
  - **Fixable classes (state/extraction), measured over the whole store:**
    - lookups `BLOCKED`/`DISABLED`/`REDACTED` (5 each) are unread;
    - `decision: deny` restore traces (5) are unread;
    - `message_text: [REDACTED]` (30) is not read as redacted;
    - screens naming a flow or backup become a fake "physical copy" (case_39, case_55).
  - Cases 41/264/390 are the state class, caused by the first three.
  - Sample mismatches (31 missing steps, 1 extra) are classed evaluator-side in C5.5.
