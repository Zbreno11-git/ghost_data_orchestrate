# S7 (merged S7+S8): final integration, evidence viewer, hardening, Mac acceptance, release

> Plan of record, approved by Breno 2026-10-25 (ExitPlanMode, after the 02:25:16Z message, session JSONL :8596).
> Owner-approved roadmap change: S7 and S8 merged into this one final session; the viewer is a deliverable;
> freeze is the last checkpoint. MASTER_PLAN mapping in brackets in the checkpoint map. Times only from `date -u`.
## Context

S6 closed with the engine frozen. The published rows are reproduced by replay at $0. Breno has now lifted the S7
hold and merged S7 and S8 into one final session (owner-approved roadmap change):
- the evidence viewer becomes a deliverable;
- "deploy" means the exact HackerRank artifacts, with no hosting;
- freeze is the **last** checkpoint, after implementation, tests, docs, Mac acceptance and the final trace;
- the session pauses only for the legacy-link decision, genuinely missing information, or the Mac acceptance.

## Opening checks (2026-10-25 02:25–02:27 UTC; the disk agrees with the resume block)

| Check | Result |
|---|---|
| `git status --short` / HEAD = origin | empty / both `94ebac52…`, "Checkpoint before compact (S6 closed, S7 on hold)…" |
| CI by head_sha | `tests completed success 2026-10-25T02:17:07Z` |
| `main.py status` | settled $1.876497, outstanding $0.004447, rows 4177 |
| `pytest -q` | `244 passed` |
| `sha256sum output.csv` | `ee9504d5…8c4c` |
| `code.zip` sha256 | `f58aaefe…`: the **S5 build**, stale against the S6 code. An unchanged CSV is not an up-to-date deliverable |
| `session-07.md` | absent |

**Time and money:**
- Time: ≈9.5 h to the 12:00 UTC deadline. Target: freeze by ≈09:30 UTC, then Breno uploads, with a ≥2 h margin.
- Money: $2.62 of headroom.
- A31's trigger still holds: if fewer than 2 h remain without a newer validated package, Breno uploads the last
  validated one. The S5 package (`f58aaefe…` + `ee9504d5…`) stays untouched as the fallback.

## C7.1 pre-measurement (read-only, 02:28 UTC, `runs/s6/final` and `final-samples`)

- **Targets: 19 rows carry a workflow-tier account, and each one is used in that row's published steps.**
  - 18 are weak, by deduction: only_feasible_row 15, forced_matching 2, only_feasible_request 1.
  - case_63 is unresolved and comes from the strict→scored fallback (`runner.py:187`, "nearest anchor 752
    min").
  - Statuses: 15 INCOMPLETE, 4 COMPLETE.
  - `account_source` is none on all 19, so **the agent changed none of them**, and none is an A29 heuristic.
- **Samples: 4 rows.**
  - case_01 and case_04 come from the fallback (0 and 1447 min); case_02 and case_30 are only_feasible_row.
  - 3 of them match the answer; case_04's account_3865 is the extra.
- **Without the account, 4 rows would be left with zero steps:** case_63 in the targets, case_01/02/04 in the
  samples.
  - Those rows fall to `_heuristic` (A29) or become invalid (DECIDED_EMPTY). **That is the A29 interaction**
    to measure, never patch.
  - The other 15 target rows keep 1–13 independently grounded steps.

## Checkpoint map

| C | Does | ✅ Closes when |
|---|---|---|
| C7.0 [new] | log entry; `session-07.md`; SESSIONS (S7 and S8 merged; the old S7 items mapped), PRIMER, PROGRESS, STATUS; dated superseding amendment at the end of `MASTER_PLAN.md` (history kept) | the mapping table in session-07.md lists every old S7/S8 item → new C; `grep -n "S8" docs/SESSIONS.md` shows only "merged into S7" |
| C7.1 [new] | legacy workflow-link comparison → **Breno decides** | decision table delivered; decision recorded in DECISIONS (A34) before C7.4 |
| C7.2 [S8] | provenance integrity + offline viewer | tests below; browser check recorded |
| C7.3 [C7.2 part] | repository review + packaging hardening | regression tests red→green, mutations red |
| C7.4 [C7.1] | final integration on the approved config; rebuilt release candidate; clean-unpack VPS check; viewer in a browser | gate report vs S6; `package_code.py` exit 0 under the hardened checks |
| C7.5 [C7.2 docs, C7.4] | README entry point, REQUIREMENTS_MAP, reports | doc checks below |
| C7.6 [C7.5, C7.6, C7.7] | Mac runbook, walkthrough, interview cheat sheet → **Breno runs the Mac acceptance** | Breno's recorded results; failures fixed before freeze |
| C7.7 [C7.3, C7.4] | final artifacts, trace closure, RELEASE_RECORD, upload checklist, **freeze** | checksums outside the archives; Breno confirms the upload himself |

## C7.0: state refresh and roadmap rewrite

- Write session-07.md from this plan, including the old→new mapping:

  | Old item | New checkpoint |
  |---|---|
  | old C7.1 | C7.4 |
  | old C7.2 | C7.3 + C7.4 + C7.7 |
  | old C7.3 | C7.7 |
  | old C7.4 | C7.7 checklist |
  | old C7.5 | C7.6 |
  | old C7.6 | C7.6 |
  | old C7.7 | C7.6 acceptance |
  | S8 | C7.2 |

- Update SESSIONS: S7 retitled; S8 marked "merged into S7 (Breno, 2026-10-25 ~02:2x UTC; time from the JSONL)".
  Progress becomes "7 of 8" → "7 of 7" pending.
- Update PRIMER (current session; the viewer is no longer "last optional"), PROGRESS (live block) and STATUS.
- **MASTER_PLAN amendment:** an appended section, "Amendment 2026-10-25: S7+S8 merged". It records why, who and
  what it supersedes, and edits no earlier text.
- Record the decision in DECISIONS: **A14 superseded by A35** ("viewer is a deliverable in S7"), with the A14
  row left in place and marked superseded.
- Commit: `pytest -q && git commit` on explicit paths only.

## C7.1: legacy workflow links, measured comparison

**Mechanism (config, not code paths per case):** `config/default.toml` `[ownership] workflow_accounts =
"assert" | "candidate"` (default stays "assert" until Breno decides).
- **"candidate":**
  - `link_case` drops workflow-tier links from the asserted links before `assess`;
  - the runner skips the strict→scored fallback, which is itself timing-only;
  - the trace records each one under `trace.uncertain_candidates` (resource, deduction, why not asserted), and
    explain and the viewer show them as "uncertain investigation candidate".
- **Rules for "candidate":**
  - independently grounded findings and retained records are untouched;
  - an emptied row goes through the existing A29 path, or stays invalid and is counted, never patched;
  - an agent account choice keeps the A27 lineage check, so a workflow-only pick is rejected as before. A test
    pins it.
- **Tests:**
  - a fixture with a workflow-only account gets no steps for it under "candidate", and the account is listed
    as a candidate;
  - an explicit account is unaffected (close positive);
  - mutation: ignore the flag → red.

**Runs (isolated, under `runs/s7/c71-*`, never the root output):**
1. Deterministic, both configurations, on samples, custom (5) and targets: $0.
2. Agent on candidate 2, `--mode live`, scope non_resolved.
   - Cache hits are free; only changed briefs pay.
   - **Hypothesis:** only the 19 targets, plus the 4 samples, change brief.
   - **Estimate:** ≤ 25 cases × $0.0035 ≈ **$0.09**, with a hard stop of $0.20 for this checkpoint.
   - The paid case_ids are printed and checked against the changed set; any paid case outside the set is
     explained.

**Measured, via `gate.py` and `compare.py`:**
- sample status, whole-case, P/R/F1, citation, sequence;
- correct steps removed and incorrect steps removed;
- target status flips;
- support moves;
- validator violations, rows emptied, and A29 rows added.

**Decision table to Breno (AskUserQuestion), with a recommendation.** The table states plainly that the CSV
schema cannot carry confidence: a kept weak account appears in the submission as an asserted step.
- **Recommended** only on the measured numbers. The rule I'll apply: recommend "candidate" unless it creates
  invalid rows or loses more correct sample steps than it removes incorrect ones. In both cases the trade is
  stated.

While the decision is pending, C7.2, C7.3 and C7.5 drafts continue, since they don't depend on it.

## C7.2: provenance integrity and the offline viewer

**Provenance saved with the run.** The runner writes `provenance.jsonl` next to `decisions.jsonl`, holding
every obs_id the run references (links, proofs, copies, account reasons, exclusions). Each record carries:
- source_id, file path, source kind, locator;
- captured_at, observed_at, time basis;
- a bounded field excerpt.

`summary.json` gains `fingerprints`:
- run;
- code;
- dataset (the same allowlist as `run_fingerprint`);
- extraction (the vision MANIFEST sha256).

**`explain.py` order:**
1. Use the run's `provenance.jsonl`, with no re-ingest.
2. Otherwise re-ingest only when the current dataset and extraction fingerprints equal the run's.
3. Otherwise print a ⚠ "provenance not attached: dataset/extraction fingerprint differs from the run" line per
   section, and never mix versions. A legacy run without fingerprints is flagged as "unverified provenance".

- **Tests:**
  - a run with provenance never imports `ghostaudit.ingest`;
  - one mutated dataset file → mismatch flagged, and no provenance printed from the current ingest;
  - a pre-S7 run is flagged;
  - mutation: skip the check → red.

**Viewer:**
- **Generator:** `code/viewer/build.py`, run as `main.py viewer --run <dir> --out <html>`. It produces one
  self-contained HTML file: inline CSS and JS, no CDN, no fetch, no model, no key.
- **Data:** embedded as `<script type="application/json">`, with `<`, `>` and `&` escaped as `<` and the
  like. Every evidence string is rendered with `textContent` only, never `innerHTML`.
- **Reuse:** the trace and provenance shaping lives in `explain.py`, refactored into a data function
  `case_view(...)` used by both the text explain and the viewer, so CLI and viewer cannot disagree.
- **Content:**
  - the run/version header: run id, sha256 of `output.csv`, config, fingerprints, support and status counts,
    and A29 rows;
  - search by case/email/resource, and filters by status and support;
  - per case, with progressive disclosure:
    - status and certainty as separate badges;
    - intent;
    - person and identifiers (current or historical, source);
    - ownership chain;
    - uncertain candidates, rejected links and ambiguities;
    - copies with state, both clocks and the rule/treatment;
    - steps grouped as "Findings (observed)" / "Proposed remediation (not executed)" / "Verification to run"
      for INCOMPLETE, and "Verification evidence" for COMPLETE;
    - evidence ids with locators and excerpts;
  - the A29 rows get a conspicuous "HEURISTIC PREDICTION" banner;
  - an unresolved COMPLETE is labelled "predicted complete, not proven".
- **Packaging:** the viewer is built by `package_code.py` from the reference run into the staged tree, as
  `code/viewer/viewer.html`, gitignored. The clean-unpack check rebuilds it from the replay run and `cmp`s it.
  It ships with the documented command to regenerate it.
- **Tests (`test_viewer.py`):**
  - a hostile excerpt (`</script><img onerror=…>`) round-trips as text: the parsed JSON equals the input, and
    no raw `</script` appears inside the data block;
  - the per-case status, support, steps and obs_ids equal explain's `case_view` for every case of a fixture
    run;
  - the empty-result and no-trace cases render the "not recorded" text;
  - the build never imports `ghostaudit.llm` or `google`.
- **Browser:** run with headless Chrome (`/usr/bin/google-chrome`, plus Playwright in a scratch venv via the
  webapp-testing skill). Screenshots at desktop and phone width; search and filter clicked; a hostile fixture
  page checked for no script execution. The browser and version are recorded.

## C7.3: focused review and packaging hardening (`scripts/package_code.py`)

- **Acceptance requires all of the following:**
  - validate returncode 0 **and** the literal "0 violations";
  - 518 rows;
  - byte-identical output;
  - viewer `cmp`;
  - clean scan;
  - exact report paths `{code/evaluation/evaluation_report.md, code/evaluation/usage_report.md}` ⊆ names,
    replacing the `_report.md` count.
- **Isolation stated truthfully.** `unshare -rn` is the network isolation used on the VPS. Without it the check
  reports "NOT network-isolated" and fails unless `--allow-unisolated` is passed. In addition, a replay probe
  runs with `google`/`google.genai` blocked through `sys.modules` poisoning, and must still succeed, which shows
  replay cannot reach the provider.
- **Inventory rejects:**
  - nested archives (`.zip .tar .gz .tgz .7z .rar .bz2 .xz`);
  - `.env*`, credentials patterns, `.venv`/`venv`/`node_modules`/`__pycache__`/`.pyc`/`.DS_Store`/
    `.pytest_cache`;
  - `dataset/`, plus **any file whose sha256 equals a supplied dataset file**, which catches a copy under another
    path. Custom-case fixtures pass because they are ours.
- Each custom case gets `CASE.md` (scenario, inputs, expected and observed behaviour, why it matters, "authored
  independently; not from the supplied dataset") alongside its existing RATIONALE.md. A
  `custom_cases/README.md` explains their role.
- **Tests (`test_package.py`):** one negative fixture per rule (a nested `.tgz`, a `.env`, a copied
  `dataset/deletion_rules.csv` under `code/`, a missing usage_report, validate failing with identical bytes), each
  asserted to fail **for that reason**. Mutations: drop each guard → red.
- **Review:**
  - stale commands in README, code/README and STATUS (each command executed);
  - conflicting metrics across docs (grep for every headline number vs the gate JSON);
  - broken relative links (a script check);
  - undeclared imports vs `requirements.txt`, checked from a fresh venv.

  No unrelated refactors.

## C7.4: final integration

- On the approved configuration:
  - targeted recompute (fingerprints invalidate the checkpoints; replay first, and live only if C7.1 chose
    "candidate");
  - validate;
  - samples, plus the 5 custom cases;
  - the full suite, which includes the S6 robustness tests;
  - `gate.py` vs the S6 baseline, with every row change explained;
  - the detail lines: full-denominator metrics, support counts, A29 rows, and the det vs agent contribution.
- `package_code.py --run runs/s7/final` → exit 0 under C7.3. That means a fresh venv from requirements only, the
  dataset supplied outside the zip, no key, `unshare -rn`, validate, `cmp`, and the viewer `cmp`.
- The packaged viewer is opened from the unpacked tree in Chrome headless.
- Atomic root `output.csv` (tmp + rename) only if the release candidate differs.

## C7.5: submission documentation

- **Root `README.md`:** the pointer stays (D2).
- **`code/README.md`:** one entry point with these sections:
  1. Setup.
  2. Dataset placement.
  3. **Replay** (offline, free).
  4. **Fresh paid run** (key, ledger).
  5. Evaluation.
  6. Explain.
  7. Viewer.
- Re-read the official contract and update REQUIREMENTS_MAP with the artifact path and the proving command for
  each requirement.
- `make_reports.py`:
  - **evaluation_report** — metrics with full denominators; all 5 custom cases with expected and observed
    behaviour; failures and fixes; bounded claims ("no supporting link found after documented checks";
    "extraction coverage is not proof of perfect interpretation").
  - **usage_report** — the final full run: models, calls, tokens, totals and averages, per-model and overall
    cost. It separates three things: cost recorded with cached provenance, spend newly incurred in this run,
    and cumulative project spend.
  - D2: reports only in `code/evaluation/`; the other official wording is reconciled in the README, with no
    duplicate copies.

## C7.6: Mac Intel handoff, then Breno's acceptance (pause)

**`docs/release/MAC_RUNBOOK.md`:**
- get the revision (git SHA) and transfer `code.zip`, `output.csv` and the checksum file, with the dataset
  supplied separately;
- `shasum -a 256` checks;
- `python3 -m venv` and `pip install -r code/requirements.txt` (online, a separate step);
- the replay with the key unset, and Wi-Fi off **during the run** as the macOS isolation (no `unshare`);
- validate, `cmp` against the VPS reference, `pytest`;
- open the viewer.

Each step carries its expected output and troubleshooting: Python version, certifi/SSL, Intel wheels, the
dataset path, ReplayMiss.

**`docs/release/WALKTHROUGH.md`:** one case each of COMPLETE, INCOMPLETE, NOT_APPLICABLE, unresolved and
heuristic. For each, what to look at: person, evidence, state, policy, uncertainty.

**`docs/release/INTERVIEW_CHEAT_SHEET.md`:**
- architecture and the actual agent with its tools;
- what the deterministic side does;
- the two clocks, retention and tombstones;
- evaluation with full denominators;
- costs, limitations, and one worked case.

Hand over only after all VPS work is complete. **Mac acceptance stays PENDING until Breno reports results.**
Failures are fixed, and the affected checks re-run, before freeze.

## C7.7: final artifacts, trace closure, freeze

- **Rebuild from the final commit:**
  - `code.zip`;
  - `output.csv`: schema, 518 unique sorted rows, canonical steps, citation rules;
  - `log.txt`;
  - `agent-trace.zip`.

  The package inventory lists the shipped LLM and vision replay assets with their MANIFEST sha256s.
- **Log audit:** `log_audit.py`, plus checks that every entry has `tool=` and `model=` and that correction entries
  are transparent.
- **Traces:**
  - include every Claude Code session JSONL with its subagents, and the ChatGPT transcription, labelled as such;
  - the staged copies are redacted; the originals are kept;
  - `stage_traces.py` gets a test for its redaction;
  - the README states the trace ZIP is required per `agent_trace_instructions.md`.
- **Finalization prepared before asking Breno to export or quit.** `scripts/finalize_release.sh` covers, in
  order:
  1. stage the traces;
  2. zip them;
  3. write the checksums, in `docs/release/SHA256SUMS` outside the archives;
  4. write the RELEASE_RECORD.

  The closing turn's log entry is written **before** Breno's export, so nothing needs another session to finish
  logging. Breno's `/export` file is saved into the staged folder, and the script's last step re-zips the
  traces.
- **`docs/release/RELEASE_RECORD.md`:**
  - source SHA, configuration and fingerprints;
  - metrics and limitations;
  - VPS and Mac results;
  - artifact sizes and sha256.
- **Freeze,** then STATUS gets an upload checklist mapped to the official slots: code.zip, output.csv,
  chat_transcript = log.txt, agent-trace.zip, AI interview, with the URL from AGENTS §4.1.
- Breno submits manually. Nothing is reported as submitted until he confirms. After the freeze, any change
  reopens the affected checks and produces a new release record.

## 🐞 Predicted failures → how to debug

- **C7.1 "candidate" changes rows beyond the 19+4.** The workflow solver also feeds the A30 fan-out and the
  agent briefs. Diff the decisions case by case, and explain each extra row.
- **A replay miss after the provenance change.** The brief must not include provenance. If replay misses,
  provenance leaked into a brief: fix that, don't pay.
- **The viewer size balloons.** Cap the excerpts, and deduplicate provenance by obs_id.
- **The viewer `cmp` fails in the clean unpack.** Look for nondeterminism: dict order, timestamps, or absolute
  paths in the HTML. The scan's developer-path rule catches the last.
- **Hollow negative fixtures (ERRORS #4).** Each package test asserts the specific refusal reason, not just
  exit 1.

## Budget

| | Amount |
|---|---|
| Spent | $1.876497 + $0.004447 open |
| C7.1 agent pass (if run) | ≈ $0.09, hard stop $0.20 |
| Everything else | replay, $0 |
| **Projected cumulative** | **≤ $2.10** |

## Verification (end of S7)

```bash
.venv/bin/python -m pytest code/tests -q
.venv/bin/python code/main.py validate runs/s7/final/output.csv
.venv/bin/python code/evaluation/gate.py --set samples:runs/s6/final-samples:runs/s7/final-samples ... --out docs/diagnostics/s7/final_gate.md
.venv/bin/python code/main.py explain case_113 --run runs/s7/final
.venv/bin/python code/main.py viewer --run runs/s7/final --out /tmp/…/viewer.html   # + headless Chrome check
.venv/bin/python scripts/package_code.py --run runs/s7/final      # exit 0: validate, cmp, viewer cmp, scan, isolation
.venv/bin/python scripts/analysis/log_audit.py
.venv/bin/python scripts/stage_traces.py --dry-run
sha256sum -c docs/release/SHA256SUMS; git status --short; CI by head_sha
```

**Rules in force:**
- explicit staging only, and never commit output.csv, code.zip or the built viewer;
- sample_output is evaluator-only;
- no new links from timing, naming, labels or one-to-one;
- gateway and ledger for every paid call;
- times only from `date -u` or the JSONL;
- `pytest -q && git commit`; `.venv/bin/python`; kill by PID;
- a log entry every turn;
- commit after each closed checkpoint.

## Progress (measured; times from `date -u`)

- **C7.0** opened 02:45Z: log entry 02:45:47Z appended; this file written from the approved plan.
- **C7.0 ✅ 02:47Z.** SESSIONS (S7 rewritten, S8 marked merged; the historical timeline lines still name S8 as they were planned), PRIMER (current S7, previous S6; S5 narrative → PRIMER_HISTORY), PROGRESS, STATUS, MASTER_PLAN amendment appended (no earlier text edited), DECISIONS A35 (A14 marked superseded).

## Amendments (Breno, 2026-10-25 02:48Z, completed in his answer at 02:49:07Z; they supersede the clauses named)

Session focus: two **bounded** accuracy investigations (C7.1 and C7.1T), then the viewer, acceptance and release
work already planned. Timeboxes: C7.1 until 04:15Z, C7.1T until 05:15Z. When a timebox ends, the findings stand as
measured and the work moves on. S6 is not restarted.

### A1 → C7.1: masked-identity backtest (added)
- **Population.** Cases (samples and targets) whose account comes from **explicit** admissible evidence
  (`explicit_account`).
- **Masking.**
  - Hide those links **by concurrent request cohort**, not one person at a time: every request whose workflow
    window overlaps the cohort's is masked together, so elimination cannot become artificially easy.
  - Equivalent clues are removed from the derived indexes and cached associations as well: the owner index
    entries, the A30 fan-out, and checkpoints (none are reused).
- **Cutoff and control.**
  - Each case keeps its own cutoff.
  - **Control:** after masking, a probe shows the hidden account is no longer retrievable by the explicit path,
    which then yields nothing.
  - The known mapping is held only in the evaluator script (`scripts/analysis/masked_backtest.py`), never passed
    to the engine.
- **Mechanisms.** Only the existing ones: only_feasible_row, forced_matching, only_feasible_request, and the
  strict→scored nearest-anchor fallback. No new cadence-, status- or guess-based rule.
- **Report.** Correct / incorrect / abstain, broken down by mechanism, by candidate count, and by cohort size.
- **Selection-bias note.** Identifiable accounts may differ from genuinely anonymous ones, so this is supporting
  evidence, not hidden-target accuracy.

### A2 → new C7.1T: temporal interpretation experiment (added, separate from C7.1)
- **Before measuring:**
  - re-read the official time contract (AGENTS §6.2/§6.6, problem_statement) and survey the formats;
  - write down the interpretation and its assumptions, distinguishing three things:
    - (a) a historical snapshot explicitly captured before the audit, inside a later export;
    - (b) a later assertion describing an earlier event;
    - (c) an observation without a reliable internal timestamp;
  - state any remaining ambiguity.
- **Behind config.** `[time] historical_snapshots = "manifest" | "snapshot_capture"`, default `manifest` (the
  A26 baseline).
  - Both timestamps are preserved.
  - No global manifest bypass; an old timestamp alone never proves pre-audit existence.
  - The chosen semantics apply alike to identity, state, agent tools and citation validation, through
    `CaseView`.
- **Synthetic cases:** positive and negative, including a genuine post-audit observation, a retrospective claim,
  and conflicting timestamps.
- **Measurement:**
  - deterministic comparisons first: all samples, custom cases, and the target changes;
  - every recovered step and status flip traced to its evidence;
  - results presented to Breno **before** the variant is promoted;
  - attributed separately from C7.1.

### A3 → C7.1 recommendation rule (replaced)
The automatic rule ("recommend candidate unless … loses more correct sample steps") is **withdrawn**.
- **The recommendation rests on:**
  - evidence quality;
  - the masked backtest;
  - full sample metrics;
  - target changes;
  - structural validity.
- **What it does not do:**
  - no aggregate score, and no assumed grader weights;
  - a valid CSV is not truthful ownership, and a small sample advantage does not turn a heuristic into evidence.
- **The A29 interaction** is shown explicitly.
- **Decision:** the concrete alternatives go to Breno, and he selects the release configuration (A34; it covers
  C7.1T too).

### A4 → C7.3 dataset-hash rule (replaced)
- **Problem:** a blanket hash rejection would reject our own fixtures. `custom_cases/tombstone_pair/dataset/
  deletion_rules.csv` is identical to the official policy file.
- **Rule:**
  - `dataset/` stays excluded;
  - a file whose sha256 equals a supplied dataset file is rejected **unless** it is listed in a documented
    fixture allowlist (`code/evaluation/custom_cases/FIXTURE_ALLOWLIST.md` plus a machine list), with its path
    and the reason it is there;
  - no broad exception.
- **Provenance wording:** the scenarios were independently authored; reused policy content
  (deletion_rules.csv) was not independently invented.
- **Tests:**
  - the allowlisted fixture passes;
  - an unlisted copy of a dataset file (even the same content under another path) is rejected for that reason.

### A5 → C7.2 viewer wording and reproducibility (tightened)
- **Basis per item.** Each item shows its basis: direct observation / inference (scope absence, workflow
  deduction) / heuristic (A29). No blanket "observed" label on findings. Status and support stay separate.
- **Stable identifiers.** Results are identified by stable ids: the output.csv sha256, the canonical content hash,
  the run fingerprint.
- **Canonical vs execution metadata.**
  - Canonical content (embedded data and HTML) excludes local paths, run-directory names and wall-clock times.
  - Those go in a separate execution-metadata block, which is excluded from the byte comparison.
  - The rule for exactly what must match byte for byte is documented.
- **Provenance integrity.**
  - `provenance.jsonl` carries a sha256 recorded in `summary.json`, together with the run fingerprint.
  - explain and the viewer verify the hash and the run association.
  - A modified provenance file prints a ⚠ "provenance integrity failed", never an apparently verified
    explanation.
  - CLI and viewer keep one shared representation.
- **JSON in HTML.** Escaping is script-safe: `<` `>` `&` U+2028 U+2029 become `\uXXXX`. Tested: a hostile
  `</script>` excerpt round-trips as inert text.

### A6 → C7.7 finalization order (replaced)
1. Finish implementation, documentation and Mac acceptance; resolve failures.
2. Record the closing turn in log.txt; Breno exports the conversations (`/export`) and closes the sessions.
3. Copy the complete traces, review and redact the staged copies, then create the final archives.
4. Verify the final artifact set: code.zip, output.csv, log.txt, agent-trace.zip.
5. Write the checksums (`docs/release/SHA256SUMS`, outside every archive it hashes) and the external release
   record; then freeze.
6. Breno transfers and submits exactly those files.

`scripts/finalize_release.sh` is prepared beforehand and runs steps 3–5. Nothing inside a checksummed archive
changes afterwards without a rebuild and a new checksum. The "re-zip after the export" step is removed.
- **C7.1 (measured, decision pending) 03:03Z.**
  - The `[ownership] asserted_mechanisms` switch (default: all, byte-identical to S6 on samples and targets).
  - 3 tests; 2 mutations red.
  - Masked backtest: `docs/diagnostics/s7/masked_backtest.md`. Control passed. Cohort-masked: only_feasible_row 4/4, forced 1/2,
    only_feasible_request 0/1, nearest-anchor 48/168.
  - Comparison A/B/C: `docs/diagnostics/s7/legacy_links.md`. B and C leave case_63 (targets) as an invalid empty COMPLETE; A29 finds nothing.
  - Deviation: the agent pass on the alternatives is deferred to C7.4 on the chosen config. A27 means it cannot re-assert a workflow-only account, so the deterministic comparison decides. $0 spent.
  - Decision to Breno together with C7.1T.
- **C7.1T (measured) 03:20Z.** Interpretation committed first (8c58d55, 03:09Z). v1 was rejected by its own numbers (F1 0.7308, 4 flips). The v2 rule was written before re-measuring (84f591b). v2: samples +5 correct, 0 lost, 0 wrong, 0 flips, whole 14/32, F1 0.9252; targets 59 rows, 0 flips, 0 violations. 7 tests (real JSON adapter, positive and negative: post-audit snapshot, retrospective claim, contradictory dates, uncitable violation); 4 mutations red.
- **Decision ✅ 03:18:25Z (Breno): A34 + A36** (both recommendations). Defaults set.
  - Combined deterministic run `runs/s7/det`: samples status 32/32, whole 14/32, P 167/168, R 167/193, F1 0.9252, 0 violations; custom 5/5; targets 0 violations, 59 rows changed (case_376 among them), 0 flips.
  - HEURISTIC PREDICTION (A34) label on case_63, plus samples case_01 and case_04.
- **C7.2 ✅ 03:30Z.**
  - **Provenance with the run:**
    - `provenance.jsonl` (header with the run fingerprint, plus every referenced observation);
    - `summary.json` gains fingerprints (code, dataset, extraction = the vision extracts, config, run) and artifact sha256s;
    - `verify_run` checks the hashes and the run association;
    - explain no longer re-ingests the dataset (it imports neither `ghostaudit.ingest` nor llm nor google; tested).
    - Deviation from the plan, made safer: there is no "re-ingest when fingerprints match" path at all, because legacy runs carry no fingerprints. They get a warning instead.
  - **Tests:** `test_provenance.py` (5: modified file, foreign run, legacy run, no ingest import; mutations of the hash and association checks red).
  - **Viewer** (`code/viewer/build.py`, `main.py viewer`): one HTML file, CSP `default-src 'none'`, no URL / fetch / innerHTML.
    - It is built on `case_view`, shared with explain, with a basis per step and status and support kept separate.
    - Heuristic banner; "Predicted complete, not proven" for an unresolved COMPLETE.
    - Canonical HTML vs a `.meta.json` sidecar for execution metadata.
    - `test_viewer.py` (6; mutations of the `<` escape and a run-dir leak red).
  - **Browser:** chromium 156.0.8078.4 (Playwright 1.64.1, headless), via `scripts/viewer_browser_check.py` on `runs/s7/det/targets` (4.2 MB).
    - Desktop 1280 and phone 390: no horizontal scroll, 0 console errors, 0 network requests.
    - Search, filters, the empty result and the five case kinds rendered; a hostile excerpt was inert.
    - Screenshots were checked by eye.
- **Breno's review (03:35:10Z) ✅ 03:40Z.** Inspected HEAD first; the review covered f21a996.
  1. Backtest summary corrected: variants are not pooled. case_78/case_94 reviewed in `legacy_links.md`. The forced_matching recommendation went to Breno before any configuration change.
  2. `verify_run` binds output.csv as well; CSV and decisions consistency is checked; legacy and damaged are told apart. 6 new tests; 2 mutations red. `297 passed`.
  3. PROGRESS resume block refreshed.
- **A34a ✅ 03:43:23Z (Breno).** forced_matching demoted; elimination-based only_feasible_row kept, labelled. Combined deterministic run (`runs/s7/det`, re-run): samples 32/32, whole-case 14/32, P 167/168, R 167/193, F1 0.9252, 0 violations; targets 0 violations. It equals the measured no-forced run.
- **C7.4 ✅ 04:00Z. Final integration on the approved configuration (A33 strict, A34+A34a, A36; agent scope non_resolved).**
  - **Paid pass.** A free replay probe found 82 changed agent briefs. The live pass paid **exactly those 82** ($0.353; estimate $0.29). C7.4 total $0.394, under the $0.50 hard stop: targets $0.353, samples $0.041, custom $0.
  - **ERRORS #10.** The agent's recompiled plan dropped the A34 HEURISTIC label on case_63.
    - Fixed with `label_nearest_anchor`, applied before and after the review; test with close negatives.
    - Final runs re-made as `runs/s7/final-r2*`: all 1749 + 100 calls cache hits, $0, CSVs byte-identical, 4 heuristic target rows.
  - **Gate vs S6** (`docs/diagnostics/s7/final_gate.md`):
    - samples: status 32/32, whole-case 12→14, P 167/168, R 167/193, F1 0.9101→0.9252, cited recall 61→62/75, sequence 12→14; correct steps +5 / −0; incorrect +0 / −0; 0 flips; causes 32→27;
    - custom 5/5;
    - targets: 60 rows changed, each attributed (`target_changes.md`): A36 58 + 1, A34/A34a 3; 0 status flips.
  - **Agent contribution:** 0 rows on samples and targets, support moves only. The deterministic gains are separate.
  - **Release candidate:**
    - `package_code.py --run runs/s7/final-r2`: fresh venv, `unshare -rn`, provider-client construction blocked, output and viewer byte-identical, `0 violations … against 518`, inventory clean (1927 entries, 2,578,083 bytes);
    - the credential scan first flagged `sk-` inside Gemini thought_signature base64 (a false positive). Keys must now start a token; test plus mutation.
  - **Published (local, A31):** root `output.csv` `0e04ffe2…` (= `runs/s7/final-r2`), `code.zip` `47df5065…`.
  - **Fallback:** the S5 package is preserved in `/root/ghost-fallback-s5/` (`ee9504d5…`, `f58aaefe…`).
  - **Browser check of the viewer extracted from code.zip:** chromium 156, 1280/390 px, no network, hostile text inert.
  - Reports, diagnostics and explanations (now 7 classes, including A34 and A36 examples) are regenerated from `final-r2`. `303 passed`.
