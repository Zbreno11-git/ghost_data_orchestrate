# custom_01: historical_email_replica

**Expected: INCOMPLETE, 3 steps.** All people and domains are fictional.

## What it tests
1. **Historical identity resolution.** The request email `m.quintanar@orchidmail.example` is not in
   `user_identities.csv`. It shows up only as `old_value` in `audit_c01`, the 2026-05-10 email change for `user_9001`.
   The engine has to follow that history back to `user_9001` (current email `marisol.q@lumenfield.example`).
2. **Replication drift.** In the SQL snapshot `evidence_c01` (captured 2026-08-12, before audit_at 2026-08-20,
   topology `failover_replica`), `account_9001` is missing from `customer_profiles_primary`. It is still in
   `customer_profiles_failover_replica` with the old email, full name and phone, and it was last updated 2026-04-02,
   before the email change.
3. **Claims are not proof.** `activity_c01` (DELETE_RECORD SUCCESS) and `reported_status=COMPLETE` only describe the
   primary. The replica row proves the deletion is incomplete.

## Why each step exists
| # | Step | Reason |
|---|------|--------|
| 1 | FINDING `account_service/account_9001` REPORT_REMAINING_RECORD PRESENT `evidence_c01` | The replica table in the snapshot still holds the USER_PROFILE. rule_01: USER_PROFILE, Always, DELETE. |
| 2 | REMEDIATION DELETE_RECORD ABSENT `""` | rule_01 requires a full delete. Nothing in the dataset needs a retained record or tombstone (no SECURITY_AUDIT_LOG or legal hold), so rule_15 does not apply. |
| 3 | VERIFICATION VERIFY_RECORD_ABSENT ABSENT `""` | Future check after remediation, so `evidence_id` is empty. |

There are no data-flow or restore steps. The only SYNC_RECORD (`activity_c02`) concerns the decoy.

## Decoy (must not count)
`user_9002`, "Marisol Quintana", `m.quintana@orchidmail.example` (one letter different in both surname and email),
is present in both tables as `account_9002`, and `activity_c02` syncs that account. Matching on name or on a fuzzy
email would wrongly report or delete `account_9002`. The correct link is exact: the old email in the audit log, or
`user_id=user_9001` in the replica row.

## Contract choices
- The replica is cited under `system_id=account_service` with the same `resource_id`. The snapshot is one
  account_service export with two topology tables, and the contract defines no separate replica system_id.
