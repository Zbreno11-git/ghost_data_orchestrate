# custom_03: post_cutoff_evidence_ignored

**Expected: COMPLETE, 3 verification steps.** All people and domains are fictional.

## What it tests
1. **The audit_at cutoff.** audit_at is 2026-06-20T00:00:00Z. Two items fall after it:
   - `activity_c23` (2026-06-27): an INDEX_RECORD backfill that targets `search_9021`;
   - `evidence_c23` (log, captured 2026-06-28): it shows `search_9021` as `FOUND` for the requester.
   Both must be ignored. Using them would flip the case to INCOMPLETE, with a spurious remaining record and data flow.
2. **COMPLETE verifications must cite proof.** `evidence_c21` (privacy sweep ledger, 2026-06-10) shows
   `account_9021` (USER_PROFILE) and `search_9021` (SEARCH_INDEX_ENTRY) as `NOT_FOUND` for
   `ingrid.solvhaug@fjordnote.example`.
3. **Records that policy retains.** `evidence_c22` (security audit snapshot bundle, 2026-06-12) holds
   `audit_record_9021`, a SECURITY_AUDIT_LOG for `user_9021` with `retention_until=2027-04-22`. That is within the
   supplied retention period, so rule_12 (RETAIN) applies. Deleting it would be a violation, and its presence has to be
   verified. It holds only the stable `user_id` and no direct identifiers, so nothing needs redacting.
4. **Request in another language.** The request is in French and asks for definitive deletion, so it authorizes
   deletion.

## Why each step exists (canonical order: ABSENT ops before PRESENT, then system_id, then resource_id)
| # | Step | Evidence | Rule |
|---|------|----------|------|
| 1 | VERIFY_RECORD_ABSENT `account_service/account_9021` | `evidence_c21` | rule_01 USER_PROFILE DELETE |
| 2 | VERIFY_RECORD_ABSENT `search_service/search_9021` | `evidence_c21` | rule_03 SEARCH_INDEX_ENTRY DELETE |
| 3 | VERIFY_RECORD_PRESENT `security_service/audit_record_9021` | `evidence_c22` | rule_12 SECURITY_AUDIT_LOG RETAIN |

The DELETE_RECORD SUCCESS activities (`activity_c21`, `activity_c22`) are claims. They are not cited, because the
ledger is the evidence that establishes the state.

## Decoy (must not count)
`user_9022`, "Ingrid Solhaug", `ingrid.solhaug@fjordnote.example` (missing one letter). Their `account_9022` is
`FOUND` in both `evidence_c21` and `evidence_c23`, and `audit_record_9022` is in `evidence_c22`. None of these belong to
the requester, so none should produce a step.

## Contract choices
- The account was fully deleted and no tombstone exists. rule_15 (ACCOUNT_TOMBSTONE, REDACT) sets how an existing
  tombstone must be treated. It does not require one to be created, and the retained security log references
  `user_9021` directly. So there is no tombstone step.
- The security log's retention fields are taken as "the supplied retention period" that rule_12 asks for.
- A negative control was run: citing `evidence_c23` makes the validator report `EVIDENCE_AFTER_AUDIT`.

## Edit by the main agent (2026-10-24)

Renamed the retained security record from `security_audit_service`/`secaudit_9021` to the dataset convention `security_service`/`audit_record_9021` (data store and expected output), so the case tests the cutoff rule rather than an invented naming scheme. The expected statuses and steps are otherwise unchanged. The manifest origin string `security_audit_service_retention_review` is left as authored.
