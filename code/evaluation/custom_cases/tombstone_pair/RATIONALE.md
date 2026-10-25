# custom_04: tombstone_pair

**Expected: INCOMPLETE, 3 steps.** All people and domains are fictional.

## What it tests
1. **Tombstones are redacted, not deleted.** `evidence_c101` (identity_service SQL snapshot, captured
   2026-09-12T10:00:00Z, before audit_at 2026-09-22, topology `reporting_replica`) holds `tombstone_9101`
   (`record_type=ACCOUNT_TOMBSTONE`, `account_status=DELETED`, `user_id=user_9101`). Its `reference_purpose` says the
   stable user_id is kept for retained invoices and security audit references. That is the condition of rule_15
   (ACCOUNT_TOMBSTONE, REDACT). So the record stays with only `user_id`, and DELETE_RECORD would be wrong.
2. **Tombstone pair: one copy is compliant, one is not.** In `deleted_customer_references_primary` the tombstone keeps
   only `user_id` (name, email, phone and email_hash are NULL). In `deleted_customer_references_reporting_replica` the same
   `tombstone_9101` still exposes:
   - `phone=+47-555-02-110`, the requester's historical phone (`audit_c101`, changed 2026-06-14);
   - `email_hash`, the SHA-256 of the requester's current email.

   AGENTS §6.5 lists both as direct identifiers a tombstone must drop. The clean primary copy does not make the
   resource compliant: the replica copy still breaks policy.
3. **The finding is EXPOSED_PII, not REMAINING_RECORD.** The record is allowed to remain. What breaks policy is the
   identifiers it still exposes.
4. **Claims are not proof.** `activity_c101` (REDACT_RECORD, SUCCESS) and `reported_status=COMPLETE` describe the
   primary only.
5. **Request in another language.** The request is in Portuguese ("excluam a minha conta e apaguem todos os meus
   dados pessoais"). It is an explicit deletion request.

## Why each step exists
| # | Step | Reason |
|---|------|--------|
| 1 | FINDING `identity_service/tombstone_9101` REPORT_EXPOSED_PII PRESENT `evidence_c101` | The replica copy of the tombstone still has `phone` and `email_hash`. rule_15 requires REDACT down to the stable reference. |
| 2 | REMEDIATION `identity_service/tombstone_9101` REDACT_RECORD REDACTED `""` | rule_15: keep `user_id`, remove name, email, phone and email_hash in every copy. |
| 3 | VERIFICATION `identity_service/tombstone_9101` VERIFY_RECORD_REDACTED REDACTED `""` | Future check after remediation, so `evidence_id` is empty. |

There are no data-flow or restore steps. No sync, export or backup activity touches the requester.

## Decoy (must not count)
`user_9102`, "Ottilie Brandvoll", `ottilie.brandvoll@harrowlane.example` (one letter different from "Brandvold" in
both the surname and the email). Their `tombstone_9102` replica row exposes the full name and email, and
`activity_c102` redacts it. A fuzzy name or email match would report, redact or verify `tombstone_9102`. The correct
link is exact: `user_id=user_9101`, which the request email resolves to through `user_identities.csv`.

## Contract choices
- The replica copy uses `system_id=identity_service` and the same `resource_id` as the primary. The snapshot is a
  single identity_service export holding two topology tables. This follows the convention in custom_01.
- The tombstone is not reported as a remaining record and gets no DELETE: rule_15 is the only rule for
  ACCOUNT_TOMBSTONE.
- The compliant primary copy gets no step of its own. The case is INCOMPLETE, and verification covers the remediated
  resource's final state (REDACTED), which includes the primary.
- No retained record (security log, invoice) has evidence of its own here. That is deliberate. In an INCOMPLETE case,
  it is unclear whether a retained record needs a VERIFY_RECORD_PRESENT step, and this case avoids the question. The
  rule_15 condition is grounded in the tombstone's own `reference_purpose` column.
