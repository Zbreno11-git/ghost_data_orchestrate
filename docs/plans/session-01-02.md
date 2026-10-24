# S1+S2 merged — contract core, validator, evaluator, ingestion and evidence store

> The approved overall plan is frozen at `docs/plans/MASTER_PLAN.md`; this file plans **only** the merged
> S1+S2 session (A15). Its first deliverable on disk is `docs/plans/session-01-02.md` (skill format), and it
> will carry this content.

## Context

Breno merged S1 and S2 (A15, 19:46 UTC) to recover a ~1h45 slip. Nothing in the engine (S3+) can be measured
until a **contract/validator/evaluator** exists, and nothing can be investigated until **every one of the 94
evidence files** is turned into provenance-carrying, indexed Observations. This session delivers both. It makes
no ownership or policy decisions; those belong to S3.

**Timebox:** 19:55–22:50 UTC. **Spend:** ≈$0.05 (vision only). **Owner input needed during the session:** none.

## Opening measurements (2026-10-24 19:50 UTC; the disk agrees with the resume block)

| Check | Result |
|---|---|
| `git status --short` | empty |
| HEAD / origin/main | both `d2d5a3c` |
| upstream/main | `0eddbbd`, unchanged (D1 trigger not fired) |
| ledger totals | settled $0.0005345, outstanding $0 |
| `code/ghostaudit` | `__init__.py config.py llm` (+ ignored `__pycache__`) |

Minor notes, none blocking:
- `state/usage_ledger.lock` exists. It is the persistent fcntl lock file: gitignored, not a held process lock.
- PRIMER names `llm/gateway.py`, which doesn't exist until S4. Until then the only paid path is `llm/gemini.py`.
  I'll fix the PRIMER wording.

**Owner decisions in this turn:**
- **Transcript:** `CHAT_GPT_TRANSCRIPT_PRE_CLAUDE.md` stays in the repo, to be organized into the final
  transcript delivery. Record as A16 and drop it from "Depends on Breno".
- **Schedule:** the re-timed schedule is not confirmed yet. It doesn't change this session's work, so it stays
  pending.

**Formats measured for the adapters (inspection just now):**
- **SQL:**
  - topology comes from the `-- Database topology:` header;
  - tables are suffixed `_primary` / `_read_replica` / `_failover_replica` / `_replica_<region>` /
    `_reporting_replica`;
  - JSON payload columns appear in `customer_data_*` tables;
  - inventory files use `snapshot_scope(origin_system, captured_at)` plus 8 typed tables with `customer_reference`.
- **JSON** comes in 4 shapes:
  - `snapshots[]{captured_at,data_store,collection,records}`, nested business docs such as `document{…}`;
  - `service_exports{system:{collection:[…observed_at…]}}`, which includes 404 `profile:null` and search `hits.documents[]`;
  - `records[]{recorded_at,system,resource_id,record_type,result,subject_reference}` plus `record_count`;
  - `collection` + `records[]`.
- **Logs:** 7 line grammars, all starting with an ISO timestamp:
  - kv;
  - JSON;
  - syslog `<15>1 host svc trace - -`;
  - pipe `| LEVEL | svc | trace | event |`;
  - bracket `[LEVEL] [svc] [trace]`;
  - cloud `requestId=… message="k=\"v\""`;
  - `record_lookup` one-liners.
  Key names vary: `lookup_key`, `match_key`, `correlation_key`, `subject_key`, `subject_ref`.
- **Canonical order** (problem_statement L126): phase, then operation in table order, then system_id, then
  resource_id, all ascending.

## Design (one module per concern; reused existing code)

**Reused:**
- `ghostaudit/config.py` (`REPO_ROOT`, `load_config`, `price_for`);
- `ghostaudit/llm/gemini.py` `Gemini.generate`, which handles reserve → call → settle and is the only paid path;
- `ghostaudit/llm/ledger.py`;
- the S0 smoke (c) request shape for PNG extraction (`scripts/smoke_gemini.py`).

**S1 — contract core**
- `code/ghostaudit/contract.py` is the single home of the contract vocabulary:
  - `PHASES`, `STATUSES`, `STEP_KEYS`;
  - `OPERATIONS: op → (phase, state, rank)` in AGENTS §6.4 table order;
  - `EVIDENCE_REQUIRED(status, phase)` rule (D9).
- `code/ghostaudit/serialize.py`:
  - `canonical_sort(steps)`: phase, rank, system_id, resource_id, then renumber from 1;
  - `dumps(steps)`: `sort_keys=True`, `separators=(",",":")`, `ensure_ascii=False`, matching the sample bytes;
  - `write_output_csv(rows, path)`: lexicographic case_id (D5), temp file + `os.replace` (atomic).
- `code/ghostaudit/validate.py`:
  - `Violation(code, case_id, detail)` with a closed `CODES` enum;
  - row checks:
    - `BAD_STATUS`, `BAD_JSON`, `NOT_ARRAY`, `KEYSET`;
    - `BAD_PAIR` (phase/op/state), `STEP_NO`, `NOT_CANONICAL`;
    - `NA_WITH_STEPS`, `DECIDED_EMPTY`;
    - `COMPLETE_NON_VERIFY`, `INCOMPLETE_NO_FINDING`;
    - `FINDING_UNCITED`, `COMPLETE_VERIFY_UNCITED`, `FUTURE_STEP_CITED`;
    - `UNKNOWN_EVIDENCE`, `EVIDENCE_AFTER_AUDIT`;
  - file checks: `HEADER`, `DUPLICATE_CASE`, `MISSING_CASE`, `EXTRA_CASE`, `ROW_ORDER`;
  - evidence times come from `ingest/manifest.py: evidence_times(dataset)`, which covers file_ids plus activity_ids
    plus audit_ids, compared with `≤ audit_at`.
- `code/evaluation/metrics.py` + `code/evaluation/main.py`:
  - metric definitions exactly as in MASTER_PLAN C1.4;
  - joins by case_id and never by position;
  - writes `runs/eval/<ts>/metrics.json` plus a stdout table;
  - takes `--pred`/`--gold`/`--requests` flags, so the custom cases reuse it.
- `code/main.py`: argparse subcommands `validate <csv> [--split samples|targets]`, `ingest [--report]`, `status`.

**S2 — ingestion + evidence store**
- `code/ghostaudit/evidence.py`:
  - frozen `Observation`:
    - identity and provenance: `obs_id`, `source_id` (the citable file_id/activity_id/audit_id), `source_kind`;
    - times: `captured_at` (manifest capture or event time, the admissibility clock), `observed_at` (record/line time);
    - subject: `system_id`, `resource_id`, `record_type`;
    - content: `fields` (business), `wrapper` (envelope), `locator` (table:pk / line range / trace id / page:line);
  - `EvidenceStore` with exact indexes `by_resource`, `by_identifier` (normalized), `by_source`, `by_trace`;
  - `normalize_identifier`: emails lowercased and stripped, raw value kept; phones reduced to digits; hashes lowercased.
- `code/ghostaudit/ingest/`:
  - `manifest.py`: paths must resolve under `dataset/evidence` (traversal guard); `captured_at` parsed.
  - `csv_tables.py`: requests, samples, identities, audit, activity, rules. Activity and audit rows also become
    Observations; `sample_output.csv` is **not** loaded here.
  - `sql_snapshot.py`:
    - in-memory sqlite3 with `set_authorizer` denying ATTACH, DETACH, PRAGMA writes and `load_extension`;
    - per-table topology role; JSON payload columns flattened;
    - `snapshot_scope` rows become scope observations;
    - loud check: INSERT count == rows loaded.
  - `json_records.py`: dispatch **by shape, not filename**. An unknown shape → `failed`. `record_count` is checked.
    Envelope keys are tagged `wrapper`, and nested business docs (`document`, `profile`, `hits.documents[]`) are
    flattened into `fields`. The first step is a 1-minute key-set survey over all 28 files, to pin which keys are
    envelope keys.
  - `logs.py`:
    - one tokenizer handles the 7 grammars → `(ts, service, trace_id, event, kv)`;
    - every line is either parsed or counted as unparsed per file;
    - trace groups `(file_id, trace_id)` merge into one Observation carrying `resource_id` + lookup keys;
    - `record_lookup` lines become one Observation each.
  - `pdf_text.py`:
    - pypdf page text → line observations, with identifier/resource tokens extracted;
    - parity check against `pdftotext -layout` when poppler exists (A8 trigger), recorded as skip-with-reason otherwise;
    - the TXT handover is parsed with the same pipe grammar as `record_lookup`.
  - `images.py`:
    - one structured vision call per PNG, by content sha256, through `Gemini.generate`:
      `gemini-3.8-flash` (A7), temperature 0, JSON schema `{panels:[{title, rows:[{label, value}]}]}`;
    - plus a **second cheap read** on `gemini-3.1-flash-lite`; the identifier/resource sets of both reads are
      compared, and a disagreement makes the file `partial` (a loud failure instead of a plausible misread);
    - cached in `state/vision_cache/<sha>.<model>.json`, **committed** so that a clean clone, CI and the judge's
      replay need no key. This becomes decision A17, reopened if the organizers forbid derived caches.
  - `__init__.py: ingest_all(dataset) → (EvidenceStore, Coverage)`.
- Coverage → `runs/ingest/coverage.md` and `coverage.json`:
  - per file: file_id, kind, adapter, status (processed/partial/failed), observations, unparsed, notes;
  - non-zero exit if any file failed.

**Side task (background, after C1.3 exists):** an Agent subagent (general-purpose) authors 3 custom cases.
- **Inputs:** it may read only `problem_statement.md`, AGENTS.md §6 and `dataset/deletion_rules.csv`. No engine code
  and no samples.
- **The three cases:**
  1. a historical email still in a replica;
  2. a success claim contradicted by a present record;
  3. post-cutoff evidence that must be ignored.
- **Output:** each case is a self-contained mini-dataset in the dataset's schema, under
  `code/evaluation/custom_cases/<name>/{dataset/…, expected_output.csv, RATIONALE.md}`. All data is fictional.
- **Gate:** each `expected_output.csv` must pass `main.py validate` against its own mini-dataset.

## Checkpoints (command → expected number)

| C | Does | ✅ Closes when | 🐞 Predicted → Debug |
|---|---|---|---|
| C1.1 | contract tables | `pytest code/tests/test_contract.py -q`: 193/193 sample (phase, op, state) triples legal; the op set is derived from the table, not hand-listed | a sample op not in the table → re-read AGENTS §6.4 |
| C1.2 | canonical sort + dumps | same file: 32/32 shuffled arrays re-sort identical; 32/32 rows re-serialize **byte-identical** | not canonical → D6 trigger fires; record it and stop to ask |
| C1.3 | validator | `pytest code/tests/test_validate.py -q`: one fixture **per code in `CODES`** (derived: a test fails if a code has no fixture), each rejected for exactly that code; `main.py validate dataset/sample_output.csv --split samples` → 0 violations | the evidence-time map misses activity/audit ids → UNKNOWN_EVIDENCE on samples |
| C1.4 | evaluator | `pytest code/tests/test_metrics.py -q`: gold vs gold → every metric 1.0; empty pred → 0 with counts 32/193; literal case: one swapped evidence_id → evidence acc = 74/75 | positional join → shuffled rows lower the score |
| C2.1 | manifest + CSVs | `main.py ingest --report`: 94 files, 0 missing, 0 outside dataset/; table row counts 518/32/850/306/4011/15 | — |
| C2.2 | SQL | 24/24 processed; INSERTs == rows for every file; `ATTACH` test → `sqlite3.DatabaseError` (not authorized) | multi-line `CREATE` / quoted names → use `executescript`, never regex |
| C2.3 | JSON | 28/28 processed, 0 unknown shapes; a test pins a real record whose envelope keys are tagged `wrapper` and whose business email sits in `fields` | the shape survey finds a 5th shape → add an adapter, never a default |
| C2.4 | logs | 26/26 processed; unparsed non-noise lines = 0 (per-file counts listed); a test pins one trace in each of the 7 grammars joining lookup_key ↔ resource_id | a grammar variant parses silently wrong → per-grammar fixture from a real line |
| C2.5 | PDF/TXT/PNG | PDF 4/4 (pypdf ⊇ pdftotext identifier set, or diff listed); TXT 1/1; PNG 11/11 with both reads agreeing (or flagged partial); immediate re-run → ledger row count unchanged (0 paid calls) | a model misreads a digit → the dual-read diff flags it; re-ask with a crop prompt |
| C2.6 | coverage | `runs/ingest/coverage.md` shows 94/94 with a status. Evaluation-side recall tests: **111/111** sample step resource_ids are in `by_resource`, and **75/75** sample citations name a file holding an observation of that resource | resource only in an image → C2.5 extraction gap |
| side | custom cases | 3 dirs; each `expected_output.csv` validates 0 violations on its own mini-dataset | subagent uses non-contract ops → the validator rejects it, so send it back |

**Mutation proofs (testes-que-provam §3)**, each run once, then restored, with `git diff` checked empty afterwards:
1. swap two ranks in `OPERATIONS` → C1.2 goes red;
2. `≤` → `<` in the admissibility check → the case_11 / evidence_03 fixture goes red;
3. drop the ATTACH denial → C2.2 goes red;
4. put the envelope keys into `fields` → the C2.3 wrapper test goes red.

## Execution order

1. Append a log.txt entry for this turn. Write `docs/plans/session-01-02.md` from this plan. Record A16 in
   DECISIONS and fix the PRIMER gateway wording.
2. Write `code/tests/conftest.py` (sys.path, dataset fixture). Then C1.1 → C1.2 → C1.3, one commit per closed
   checkpoint, staging explicit paths only.
3. Launch the custom-case subagent in the background.
4. C1.4 → C2.1 → C2.2 → C2.3 → C2.4 → C2.5 (paid: ≈$0.05, ledgered) → C2.6.
5. Add `.github/workflows/ci.yml`: pytest only, no key, which works because the vision cache is committed.
6. Collect the subagent's cases and validate them.
7. Close with the ritual:
   1. read the gate output literally;
   2. two review passes with different questions (correctness, then "what did this make false?");
   3. update DIARY, PROGRESS ▶️, SESSIONS, STATUS and REQUIREMENTS_MAP;
   4. commit with the *why*, push, then check `git status` and HEAD = origin;
   5. add the log.txt entry.

## Verification (end of session)

```bash
.venv/bin/python -m pytest code/tests -q                                   # all green, skipped = 0 (or reasoned)
.venv/bin/python code/main.py validate dataset/sample_output.csv --split samples   # 0 violations
.venv/bin/python code/evaluation/main.py --pred dataset/sample_output.csv  # all metrics 1.0
.venv/bin/python code/main.py ingest --report && head -40 runs/ingest/coverage.md  # 94/94
.venv/bin/python code/main.py status                                       # ledger ≤ $0.06 cumulative
git status --short; git rev-parse HEAD origin/main                         # clean; equal
```

## Risks

- **Cost:** the only paid step is C2.5, about 22 small calls with a hard stop in the ledger.
- **Public repo:** stage explicit paths only. The vision cache holds only extracts of the fictional dataset. It is
  reviewed before staging.
- **Scope:** the coverage recall tests read `sample_output.csv` and stay evaluation-side, under `code/tests/` only.
  No prediction module imports that file, and a test asserts this with a grep over `code/ghostaudit/`.
