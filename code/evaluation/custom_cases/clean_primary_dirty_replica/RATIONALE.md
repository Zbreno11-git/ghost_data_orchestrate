# custom_05: clean_primary_dirty_replica

**Expected: INCOMPLETE, 3 steps.** All people and domains are fictional.

## What it tests
1. **Copy-level state.** There are three account_service snapshots:

   | file | captured_at | topology | `account_9111` |
   |---|---|---|---|
   | `evidence_c111` | 2026-08-28T06:00Z | `reporting_replica` | **present**: full name, email, phone, ACTIVE |
   | `evidence_c112` | 2026-09-05T06:00Z | `primary_only` | absent (only the decoy row) |
   | `evidence_c113` | 2026-09-14T06:00Z | `reporting_replica` | absent. **Captured after audit_at 2026-09-10** |

   The newer clean primary (`evidence_c112`) says nothing about the reporting replica, which is a separate physical
   copy. The latest admissible observation of the replica is `evidence_c111`, and it still holds the USER_PROFILE.
   An engine that takes "latest snapshot of account_service wins" across copies would wrongly clear it.
2. **The audit_at cutoff.** `evidence_c113` shows the replica clean. If it were admitted, the replica would read as
   deleted, the case would flip to COMPLETE, and VERIFY_RECORD_ABSENT would cite `evidence_c112` and `evidence_c113`.
   It must be ignored. A negative control was run: citing `evidence_c113` makes the validator report
   `EVIDENCE_AFTER_AUDIT`.
3. **Claims are not proof.** `activity_c111` (DELETE_RECORD SUCCESS, "from account_service primary") and
   `reported_status=COMPLETE` are only true of the primary.

## Why each step exists
| # | Step | Reason |
|---|------|--------|
| 1 | FINDING `account_service/account_9111` REPORT_REMAINING_RECORD PRESENT `evidence_c111` | The reporting replica still holds the profile. rule_01: USER_PROFILE, Always, DELETE. Cite the replica snapshot, not the primary. |
| 2 | REMEDIATION `account_service/account_9111` DELETE_RECORD ABSENT `""` | rule_01 requires a full delete. Nothing here is a tombstone, a retained log or a legal hold. |
| 3 | VERIFICATION `account_service/account_9111` VERIFY_RECORD_ABSENT ABSENT `""` | Future check after remediation, so `evidence_id` is empty. |

There are no data-flow or restore steps. The only SYNC_RECORD (`activity_c112`) concerns the decoy.

## Decoy (must not count)
`user_9112`, "Ravinder Castellano", `r.castellano@tidewharf.example`, an active customer. They are present as
`account_9112` in all three snapshots, and `activity_c112` syncs them. Fuzzy name matching would report or delete
`account_9112`, or turn the nightly sync into a REPORT_ACTIVE_DATA_FLOW. The correct link is exact:
`user_id=user_9111` and the email `ravi.castellanos@tidewharf.example`.

## Post-cutoff trap
`evidence_c113` (captured 2026-09-14, after audit_at) is the one item that would change the answer. Using it gives
COMPLETE with absence verifications, when the correct answer is INCOMPLETE with a remaining replica record.

## Contract choices
- The replica copy uses `system_id=account_service` and the same `resource_id` as the primary. This follows custom_01:
  the contract has no separate system_id for replicas.
- The clean primary gets no step of its own. The case is INCOMPLETE, and the post-remediation VERIFY_RECORD_ABSENT
  covers every copy of `account_9111`.
