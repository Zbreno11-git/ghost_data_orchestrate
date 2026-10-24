# Ghost Data Orchestrate — progress in flight

> Working file: describes the **current** session. Updated at every checkpoint. A delivered and answered
> handoff moves to `docs/HANDOFFS.md`, after relocating what lives only here (open decision → SESSIONS,
> lesson → ERRORS, constraint → PRIMER).

## ▶️ RESUME HERE — 2026-10-24 19:50 UTC (14:50 CDT) — before a compact

**Repository state:** tree clean after the checkpoint commit · HEAD = the "Checkpoint before compact" commit on top of
`fe62dce` (same as origin: yes, see check below) · locks: none · background runs: none

**State of the world (measured 19:46 UTC):**
- Ledger `state/usage_ledger.jsonl`: settled $0.0005345, outstanding $0, 8 rows.
- No CI workflow exists yet, so CI has not run (deliberately; `.github/workflows/ci.yml` is still to be written).
- Deadline 2026-10-25 12:00 UTC: **16h14m remaining** at 19:46 UTC.

**Current goal:** **S1+S2 merged** (Breno, 19:46 UTC). Deliver the contract core + validator + evaluator (proven against
sample_output), then every one of the 94 evidence files ingested into provenance-carrying Observations with exact indexes
and a 94/94 coverage report. Also start the background subagent that authors 3 custom cases.

**Exact next step:**
1. Write `docs/plans/session-01-02.md` (skill format: checkpoint map C1.1–C1.4 + C2.1–C2.6, Does / ✅ / 🐞).
2. Write `code/ghostaudit/contract.py` + `code/tests/test_contract.py`.
3. Run `.venv/bin/python -m pytest code/tests/test_contract.py -q`. Expected: 193/193 sample (phase, op, state) legal
   and 32/32 shuffled sample arrays re-sorted identical.

**Checkpoints (full text and commands in `docs/plans/MASTER_PLAN.md` §S1, §S2):**
| C | Closes when | State |
|---|---|---|
| S0 C0.1–C0.7 | setup | ✅ (fe62dce) |
| C1.1 | contract tables; 193/193 sample steps legal | ⬜ |
| C1.2 | canonical sort reproduces 32/32 sample arrays | ⬜ |
| C1.3 | validator rejects ≥9 malformed fixtures for the named reason; sample_output validates clean | ⬜ |
| C1.4 | evaluator metrics (self = 1.0, empty = 0, join by case_id) | ⬜ |
| C2.1 | manifest + CSVs; 94/94 paths resolve | ⬜ |
| C2.2 | SQL 24/24 sandboxed; ATTACH denied | ⬜ |
| C2.3 | JSON 28/28; wrapper fields tagged | ⬜ |
| C2.4 | logs 26/26; trace_id join; unparsed count per file | ⬜ |
| C2.5 | PDF 4/4 (pypdf), TXT 1/1, PNG 11/11 cached (rerun = 0 paid calls) | ⬜ |
| C2.6 | `runs/ingest/coverage.md` 94/94 with status | ⬜ |
| side | subagent: 3 custom cases in `code/evaluation/custom_cases/` (sees only problem_statement, AGENTS §6, rules) | ⬜ |

**Re-read, in this order:**
1. `AGENTS.md`: contract and logging (log.txt every turn: `tool=Claude Code`, `model=claude-opus-5-5`)
2. `docs/PRIMER.md`: inviolable rules and boundaries
3. this block
4. `docs/plans/MASTER_PLAN.md`: §S1 and §S2 checkpoints, plus "Measured at opening"
5. `docs/DECISIONS.md`: D2, D5, D6, D9 (they shape the validator and serializer); A8, A9 (PDF/SQL adapters)
6. the skills `software-build` (session protocol) and `testes-que-provam` (tests that can fail)
7. `code/ghostaudit/llm/gemini.py` + `ledger.py`: the only paid path (PNG extraction in C2.5 must go through it)
8. `scripts/analysis/*.py`: how the S0 numbers were measured (trace_id grouping in `linkaudit.py`)

**Decisions from this conversation (and where they are written):**
- Everything up to S0 → `docs/DECISIONS.md` (D1–D9, A1–A14).
- **S1+S2 merged into one session**: Breno, 2026-10-24 19:46 UTC → `docs/SESSIONS.md` order notes + DECISIONS A15.
- Re-timed schedule after the 1h45 slip: proposed by the agent, **awaiting Breno's confirmation** → SESSIONS timeline.

**Don't forget (lives only here; measured 2026-10-24 on upstream 0eddbbd):**
- **Logs:** the lookup key and the resource_id sit on *different* lines, joined by trace id. The trace id appears as
  `trace_id=` (key=value), `"trace_id"` (JSON), field 3 in syslog (`node-1 account_service tr-4973247`), `[tr-…]` in
  application_trace, field 4 in the pipe format, and `requestId=` in cloud_runtime. The key name varies: `lookup_key`,
  `match_key`, `correlation_key`. A log file holds line timestamps *earlier* than its manifest `captured_at`
  (e.g. structured_eu_west captured 09-18 contains 09-10 lines).
- **notification_delivery / search_index_diagnostic logs** are `record_lookup` lines with system, resource_id,
  record_type, result FOUND/NOT_FOUND and subject_reference=email, all on one line. The handover TXT uses the same
  fields, pipe-separated, with **UPPERCASE emails**.
- **service_resource_export JSON:** 404 account lookups carry *no* lookup key. `resource_lookup_trace` logs do carry
  `lookup_key=<email>` even on a 404.
- **Snapshot bundles:** `snapshots[].{captured_at,data_store,collection,records[]}`. Security records carry a wrapper
  `subject_reference` (user_id). Tag wrapper vs business fields (FR-11).
- **SQL:** inventory files have a `snapshot_scope(origin_system, captured_at)` table plus `customer_reference` columns.
  Replica/failover files use `customer_profiles_primary` / `_failover_replica` tables with `user_id`. Topology also
  appears in a `-- Database topology:` comment. Absence counts only within a table proven to be in scope.
- **Activity:** 10 `CLASSIFY_REQUEST … non-deletion` rows; 12 `data_catalog LINK_RESOURCE_IDENTITY` rows (they pair with
  images/PDFs and name email + user_id); 1 `RESTORE_BACKUP` row.
- **PDFs:** text extracts cleanly with `pdftotext -layout` (poppler). The pypdf output must be compared against it
  (A8 trigger). The legal register PDF lists `ORD | user_XX | … | Retain until`.
- **PNGs:** clean UI screens. Flash-lite vision read `account_admin_console` exactly (1,101 input tokens ≈ $0.0004).
  Keep panel associations (e.g. backup list + detail panel).
- **Gemini:** append the model's full `Content` to the history unchanged (the `thought_signature` is on function-call
  parts). `thinking_level="MINIMAL"` → 0 thought tokens. Every call needs `max_output_tokens` (the reservation is the upper bound).
- **Baselines:** 82/111 sample resources explicitly linked (`scripts/analysis/linkaudit.py dataset`, re-run 19:46 UTC).
  Samples: 22 INCOMPLETE / 10 COMPLETE / 0 NA; 75 citations are file_ids (41 findings + 34 COMPLETE verifications), 118 `""`.

**Depends on Breno:**
- Confirm the re-timed schedule (safety package moves from 04:00 to ~05:30 UTC = 00:30 CDT; the freeze stays at 09:00 UTC
  by shrinking S6). If he refuses, cut S3 scope instead.
- Keep the session running with unattended permissions overnight.

**Risks of the next step:** none irreversible. C2.5 makes ~11 paid vision calls, ≈$0.005 projected (ledgered, under the S2
envelope of $0.10).

**Before trusting this block, check:**
- `git status --short` → empty; `git rev-parse HEAD origin/main` → identical
- `.venv/bin/python -c "import sys; sys.path.insert(0,'code'); from ghostaudit.llm.ledger import Ledger; print(Ledger('state/usage_ledger.jsonl', 4.5).totals())"` → settled ≈ 0.0005345, outstanding 0
- `ls code/ghostaudit` → `__init__.py config.py llm` (no engine modules yet)

## Proofs from S0

| Proof | Command | Result (literal) | When |
|---|---|---|---|
| upstream base | `git log --oneline -2` | `d4a8432 Add .gitignore…` / `0eddbbd Update AGENTS.md` | 16:52Z |
| ignores | `git check-ignore .env runs/ .venv/` | `.env` `runs/` `.venv/` | 16:52Z |
| log format | header / tool= / model= / secret counts | 6 / 6 / 6 / 0 | 16:52Z |
| deps | import check | genai 2.33.0, pypdf 6.21.2, pydantic 2.14.1, pytest 9.1.1 | 17:05Z |
| remote | `gh repo view … --json visibility`; `git rev-parse HEAD origin/main` | `PUBLIC`; both equal | 17:20Z |
| smoke | `.venv/bin/python scripts/smoke_gemini.py` | a: `{"authorizes_deletion": true, "language": "es"}`; b: `lookup_resource(account_3136)`, thought_signature true; c: `user_11`/`account_5762` exact; settled $0.0005345 | 17:10Z |
| link audit | `python3 -I scripts/analysis/linkaudit.py dataset` | `sample resources 111 with explicit co-occurring subject link 82` | 19:46Z |
