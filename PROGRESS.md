# Ghost Data Orchestrate — progress in flight

> Working file: describes the **current** session. Updated at every checkpoint. A delivered and answered
> handoff moves to `docs/HANDOFFS.md`, after relocating what lives only here (open decision → SESSIONS,
> lesson → ERRORS, constraint → PRIMER).

## ⏱ Live — S3+S4 in progress (updated at each checkpoint)

- Plan: `docs/plans/session-03-04.md`, with Breno's six safeguards integrated after approval (A20: weak workflow
  links, copy-level state, resolved/weak/unresolved, provisional ceiling, mixed intent, offline replay). The 4xx
  policy is A21.
- ✅ C3.0 `cc3c490`: resource-id prefixes derived from the activity stream (14, equal to the record prefixes).
  The old hand-written gap changed no index.
- ✅ C3.1: `identity.py`, with identities rolled back to audit_at. Matching is exact normalized only, a shared
  address is an Ambiguity, names are weak, and the derived sha256 holds 850/850. 550/550 request emails resolve
  to exactly one user (32 samples + 518 targets). Mutation (prefix match) → decoy test red.
- ✅ C3.2: `temporal.CaseView` with an inclusive cutoff, and its accessors derived by introspection (8). Both
  mutations turn it red: no filter (2 fail) and an exclusive cutoff (1 fail). Suspected gaps re-checked by a
  literal byte search over 102 dataset files plus 22 vision extracts, pinned by 2 tests: D10/D13 have 0 hits;
  the D12 ids appear only in files captured after their audits.
- ▶️ Next: C3.3 `ownership.py` + `test_ownership.py` (interleaved / repeated-person / tie fixtures, then the
  sample report).

## ▶️ RESUME HERE — 2026-10-24 20:20 UTC (15:20 CDT) — before a compact; S3+S4 next

**Repository state:** tree clean after the "Checkpoint before compact (S3+S4 next)" commit · HEAD = origin/main (check
below) · locks: none (`state/usage_ledger.lock` is the persistent fcntl lock file, not a held lock) · background runs: none.
CI: run `tests` on `0ac781f` = **success** (checked by headSha 20:14 UTC). The checkpoint commit triggers a new run; check
it by its own SHA.

**State of the world (measured 20:16 UTC):**
- Ledger: settled **$0.107400**, outstanding $0, 54 rows.
- `78 passed`. Ingest: 94/94 processed, 7,604 observations.
- Deadline 2026-10-25 12:00 UTC: 15h44m left. **No fixed intermediate time target (Breno, A18).**

**Current goal: S3+S4 merged (A19), one at a time.**
- **S3:** a deterministic, no-LLM proposal for all 32 samples, which validates 32/32 and has baseline metrics.
- **S4:** a tool-using Gemini investigator on top, with the gateway (budget refusal), cache, resume and replay, plus
  the model benchmark.
- S3's checkpoints C3.1–C3.5 must all close before C4.1.

**Exact next step:**
1. Write `docs/plans/session-03-04.md`. Use the skill format; checkpoints C3.1–C3.5, then C4.1–C4.6, come from
   `docs/plans/MASTER_PLAN.md` §S3/§S4; fold in the sample patterns below.
2. `code/ghostaudit/identity.py` + `code/tests/test_identity.py` (C3.1): the request email resolves to a user_id plus
   all current and historical identifiers (identities + audit log, case-insensitive email, phones by digits).
   Expected: case_10 and case_12 resolve historical aliases, and the case_28 look-alike email (another user) is excluded.

**Sample patterns (measured 2026-10-24 20:16 UTC on sample_output.csv; tuning exposure: disclose in the report)**
- **Account:** 32/32 cases verify the account_service account ABSENT.
  - When the account still exists (3 cases): REPORT_REMAINING_RECORD → DELETE_RECORD → VERIFY_RECORD_ABSENT.
  - Otherwise there is only the verification: cited in COMPLETE cases, `""` in INCOMPLETE ones.
- **Retained audit record:** 24/32 cases have VERIFY_RECORD_PRESENT on a security_service `audit_record_*` (rule_12
  RETAIN). Cases 01, 02, 04–08 and 10 have none.
- **Ops per system** (findings / remediation / verification):

  | System | Findings | Remediation | Verification |
  |---|---|---|---|
  | search | 12 REMAINING | 12 DELETE | 12 ABSENT |
  | analytics | 5 EXPOSED_PII | 5 ANONYMIZE | 12 ANONYMIZED |
  | support | 5 EXPOSED_PII | 5 REDACT | 8 REDACTED |
  | integration | 6 ACTIVE_DATA_FLOW | 6 DISABLE | 9 DISABLED |
  | backup | 3 RESTORE_RISK | 3 BLOCK | 6 BLOCKED |
  | export | 2 REMAINING | 2 DELETE | 2 ABSENT |
  | identity_service `tombstone_*` | 1 EXPOSED_PII | 1 REDACT | 2 REDACTED |

  Exceptions:
  - case_12 analytics_9914: REMAINING → DELETE → ABSENT (likely a marketing/contact profile: `contact_lookup_completed
    email_opt_in`, rule_10 DELETE).
  - Support: 3 cases go REMAINING → DELETE → ABSENT, all subject-only attachments/records (rule_06): case_07 PDF
    `evidence_58`, case_10 `support_replica.log` `evidence_61`, case_13.
- **INCOMPLETE verification set** = account ABSENT + audit PRESENT (if any) + one verification per remediated resource,
  all with `""`.
- **COMPLETE** = verification of every relevant resource, each citing proof:
  - an analytics record that is already anonymized gets VERIFY_RECORD_ANONYMIZED;
  - a connector already disabled gets VERIFY_DATA_FLOW_DISABLED;
  - a backup with `restore_allowed=false` gets VERIFY_RESTORE_BLOCKED;
  - support already redacted gets VERIFY_RECORD_REDACTED.
- **Citations:** 31/32 cases cite exactly one file for all steps (the comprehensive latest admissible snapshot:
  `evidence_92`/`94`/`51`/`54`/`03`/`01`/`05`). case_04 cites two (`evidence_54` account, `evidence_56` analytics report).
  Hypothesis for S3: "latest admissible file that covers the resource's state".
- **Gap:** `evidence.RESOURCE_RE` lacks `tombstone_`, so free-text mentions of tombstones are not indexed (record
  resource_ids still are). Add it in S3.

**Don't forget (measured 2026-10-24, still true):**
- **Absence by scope:** 4/75 citations are ABSENT checks on a snapshot covering the system without the row (`evidence_54`
  SQL tables, `evidence_51` bundle scope). evidence_90 `snapshot_scope` covers only account_service and has 0 rows.
- **D10:** `audit_record_5569/6645` are unobservable. The ceiling is 109/111 resources and 191/193 steps. Never invent them.
- **Lookup claims:** ledger / `operational_record_history` / `record_lookup` / TXT rows put `system`+`resource_id`+
  `result` in the observation and the subject in `wrapper`. Results include FOUND, NOT_FOUND, ANONYMIZED, IDENTIFIABLE
  and ACTIVE.
- **Logs:** `profile_service` is the account service's function name. The payload events are `*_pii_scan`,
  `connector_heartbeat`, `restore_candidate_evaluated` and `deletion_marker_check`.
- **Ownership baseline:** 82/111 explicitly linked (`scripts/analysis/linkaudit.py`). A5: strict vs scored, decided in S6.
- **Gemini:**
  - `3.8-flash` rejects `thinking_level=MINIMAL`, so it runs at LOW;
  - append the model `Content` unchanged (`thought_signature`);
  - every call needs `max_output_tokens`.
- **S4's first step:** the 4xx settlement policy. `gemini.py` settles any exception at the reservation; one 400 cost
  $0.0176 in the ledger.

**Re-read, in this order:**
1. `AGENTS.md`: contract and logging (log.txt every turn: `tool=Claude Code`, `model=claude-opus-5-5`)
2. `docs/PRIMER.md`: rules and boundaries (wrapper vs fields, absence proof, D10)
3. this block
4. `docs/plans/MASTER_PLAN.md` §S3 and §S4
5. `docs/DECISIONS.md`: A4, A5, A6, A7, A10, A17–A19, D6, D9, D10
6. the skills `software-build` and `testes-que-provam`; `integracoes` before S4's gateway
7. code: `ghostaudit/evidence.py`, `ingest/pipeline.py`, `validate.py`, `serialize.py`, `evaluation/metrics.py`,
   `llm/gemini.py`, `llm/ledger.py`

**Depends on Breno:**
- Keep the session running with unattended permissions overnight.
- (Answered: no fixed time target, A18; S3+S4 merged and run one at a time, A19; transcript stays in the repo, A16.)

**Risks of the next step:**
- S3 costs $0.
- S4 spends ≈$0.30 (intent batch + benchmark of 10 samples × 2 models), all through the ledger. The hard stop is $4.50.

**Before trusting this block, check:**
- `git status --short` → empty; `git rev-parse HEAD origin/main` → identical; `git log -1 --format=%s` starts
  "Checkpoint before compact (S3+S4"
- `.venv/bin/python code/main.py status` → settled $0.107400, outstanding $0.000000
- `.venv/bin/python -m pytest code/tests -q` → `78 passed`
- `ls code/ghostaudit` → no `identity.py` yet

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
