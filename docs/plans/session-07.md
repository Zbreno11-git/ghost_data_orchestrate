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
