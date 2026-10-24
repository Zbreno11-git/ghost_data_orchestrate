# custom_02: success_claim_contradicted

**Expected: INCOMPLETE, 3 steps.** All people and domains are fictional.

## What it tests
1. **An operation result is a claim.** `activity_c11` (2026-07-06) reports `DELETE_RECORD` on
   `search_service/search_9011` with `reported_result=SUCCESS`, and the workflow reported COMPLETE on 2026-07-07.
2. **Later admissible evidence overrides the claim.** The record-lookup ledger `evidence_c11` was captured
   2026-07-15, which is after the delete claim and before audit_at 2026-07-25. It shows `search_9011`
   (SEARCH_INDEX_ENTRY) as `FOUND` with `subject_reference=teo.valkenburg@quillpost.example`, the requester's current
   email. The ledger supersedes the activity row.
3. **Request in another language.** The request is in German with an English gloss. It is an unambiguous erasure
   request, so it authorizes deletion.

## Why each step exists
| # | Step | Reason |
|---|------|--------|
| 1 | FINDING `search_service/search_9011` REPORT_REMAINING_RECORD PRESENT `evidence_c11` | rule_03: SEARCH_INDEX_ENTRY, Always, DELETE. The entry still exists. Cite the file that proves presence, not the activity row. |
| 2 | REMEDIATION DELETE_RECORD ABSENT `""` | rule_03. |
| 3 | VERIFICATION VERIFY_RECORD_ABSENT ABSENT `""` | Future post-remediation check. |

## Decoy (must not count)
`user_9012`, "Teodora Valkenburg", `teodora.valkenburg@quillpost.example`. Their entry `search_9012` is also
`FOUND` in the same ledger, and `activity_c12` reindexes it. That reindex is a normal flow for an active
customer, not a data flow for the requester, so it must not become a REPORT_ACTIVE_DATA_FLOW for this case.

## Contract choices
- No other system has any evidence for this user, so no steps are emitted for one. A case should report only what
  participant evidence supports.
