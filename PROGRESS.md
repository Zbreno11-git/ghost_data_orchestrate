# Ghost Data Orchestrate — progress in flight

> Working file: describes the **current** session. Updated at every checkpoint. A delivered and answered
> handoff moves to `docs/HANDOFFS.md`, after relocating what lives only here (open decision → SESSIONS,
> lesson → ERRORS, constraint → PRIMER).

## ▶️ RESUME HERE — 2026-10-24 20:15 UTC (15:15 CDT) — S1+S2 closed, S3 next

**Repository state:** tree clean after the "Close S1+S2" commit (HEAD = origin/main; check below) · locks: none ·
background runs: none · CI: `.github/workflows/ci.yml` added in the close commit (offline: pytest, validate, ingest)

**State of the world (measured 20:12 UTC):**
- Ledger: settled **$0.1074**, outstanding $0, 54 rows. S2 spent $0.1069; $0.0176 of that is a 400 error settled at its
  reservation (S4 first step decides that policy).
- Tests: `78 passed`. Ingest: `94 files, 7604 observations, 94 processed, 0 partial, 0 failed`.
- Deadline 2026-10-25 12:00 UTC: 15h45m left. **≈2h35 ahead** of the re-timed plan (S1+S2 was due 22:50).

**Current goal: S3.** Identity fixed point, cutoff in the tool layer, ownership link strength (strict/scored), policy
registry, planner → a deterministic no-LLM proposal for the 32 samples, validated and scored (the baseline S4 must beat).

**Exact next step:**
1. Write `docs/plans/session-03.md` (skill format, C3.1–C3.5 from MASTER_PLAN §S3).
2. `code/ghostaudit/identity.py` + `code/tests/test_identity.py`: resolve request email → user_id + every current and
   historical identifier (identities + audit log; emails case-insensitive). Expected: case_10 and case_12 resolve historical
   aliases; the case_28 look-alike email is excluded.

**What S3 builds on (lives in code; read these):**
- `ghostaudit/evidence.py`: `Observation` (kind record/lookup/scope/activity/audit/text; `fields` vs `wrapper`;
  `captured_at` = admissibility clock) and `EvidenceStore` indexes `by_resource`, `by_identifier[(type, norm)] →
  (obs, role, key)`, `by_source`, `by_trace`.
- `ghostaudit/ingest/pipeline.py: ingest_all(dataset)` (≈0.5 s, no network; PNGs from `state/vision_cache`).
- `ghostaudit/validate.py`, `serialize.py`, `evaluation/metrics.py`: the S3 output goes through these unchanged.

**Don't forget (measured 2026-10-24; not obvious from the code):**
- **Absence is proven by scope:** 4/75 sample citations are ABSENT checks citing a snapshot (`evidence_54` SQL tables,
  `evidence_51` bundle scope) that covers the system and lacks the row. The resource id is not mentioned anywhere
  (account_001/002/004/4857).
- **D10:** `audit_record_5569/6645` (case_18/20, future VERIFY_RECORD_PRESENT) exist in no participant file. The ceiling is
  109/111 resources and 191/193 steps. Never invent them.
- **Lookups are claims about other systems:** ledger/`operational_record_history`/`record_lookup`/TXT rows carry
  `system`+`resource_id`+`result` FOUND/NOT_FOUND, with the subject in the wrapper. Some results are ANONYMIZED,
  IDENTIFIABLE or ACTIVE, and the subject can be prose ("no direct identifier").
- **Inventory SQL `snapshot_scope`** lists which systems a capture covers. evidence_90 covers only account_service and
  holds 0 rows, which proves account absence.
- **Logs:** `profile_service` (cloud grammar) is the account service's function name; payload events also include
  `*_pii_scan` (matched_value), `connector_heartbeat` (enabled, scheduler_registered), `restore_candidate_evaluated`
  (eligible, deletion_block), and `deletion_marker_check`.
- **Ownership baseline:** 82/111 sample resources have an explicit co-occurring subject link (`scripts/analysis/linkaudit.py`).
- **Gemini:** `gemini-3.8-flash` rejects `thinking_level=MINIMAL` (400), so use LOW. Always append the model `Content`
  unchanged (thought_signature).

**Depends on Breno:**
- Confirm the schedule. Proposal: aim for the original 04:00 UTC safety package, with 05:30 UTC as the fallback.
- Keep the session running with unattended permissions overnight.
- (Answered 19:52 UTC: the ChatGPT transcript stays in the repo, A16.)

**Risks of the next step:** none paid or irreversible (S3 is $0). Main correctness risk: ownership of weakly linked
resources (A5).

**Before trusting this block, check:**
- `git status --short` → empty; `git rev-parse HEAD origin/main` → identical; `git log -1 --format=%s` starts "Close S1+S2"
- `.venv/bin/python code/main.py status` → settled $0.107400, outstanding $0.000000
- `.venv/bin/python -m pytest code/tests -q` → `78 passed`

## Proofs from S1+S2

| Proof | Command | Result (literal) | When |
|---|---|---|---|
| contract | `pytest code/tests/test_contract.py -q` | `8 passed` (193/193 legal, 32/32 canonical) | 19:56Z |
| validator | `main.py validate dataset/sample_output.csv --split samples` | `0 violations in dataset/sample_output.csv against 32 samples requests` | 19:55Z |
| evaluator | `evaluation/main.py --pred dataset/sample_output.csv` | every metric `1.0000` (32/32, 193/193, 75/75) | 19:57Z |
| ingest | `main.py ingest --allow-paid --report` | `94 files, 7604 observations, 94 processed, 0 partial, 0 failed` | 20:03Z |
| cache rerun | `main.py ingest` then `main.py status` | ledger rows 54 → 54 | 20:05Z |
| suite | `pytest code/tests -q` | `78 passed` | 20:12Z |
| mutations | rank swap / exclusive cutoff / no ATTACH deny / wrapper→fields | each 1+ test red, then restored green | 19:56–20:08Z |

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
