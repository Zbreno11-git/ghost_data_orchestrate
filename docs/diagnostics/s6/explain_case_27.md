# case_27: COMPLETE

## Verdict and certainty (kept apart)

- Best-effort status: **COMPLETE**
- Evidential support: **unresolved**

## Request

- Requested 2026-08-29T12:00:00Z; the workflow claimed **COMPLETE** at 2026-08-30T12:00:00Z (a claim, never proof)
- Cutoff (audit_at): 2026-09-15T12:00:00+00:00; request email: `ananya-nair@gmail.com`
- Intent: authorizes deletion = True, confidence high, source rule; reason: deletion instruction 'deletion'

## Person

- `user_27`; the request email is a **current** identifier

| type | value | role at the cutoff | source |
|---|---|---|---|
| email | `ananya-nair@gmail.com` | current | user_identities |
| email_hash | `2fe35cb075df5dbdaf7b1a68a8538956cae8cdfdf875ef2bdc5b5cee75f06510` | current | derived:sha256 |
| name | `Ananya Nair` | current | user_identities |
| phone | `+91 97441 66195` | current | user_identities |
| user_id | `user_27` | current | user_identities |

## Ownership: the chain from the person to each resource

- Account: **none attributed**; candidates left by the deduction: ['account_5482', 'account_3866', 'account_9321', 'account_7012']
- `audit_record_3830` (security_service): tier **explicit**
  - linked by `evidence_92#security_service/audit_records:1:audit_record_3830` — json record, system security_service, captured 2026-09-15T11:44:55+00:00, observed 2026-09-15T09:31:23+00:00, basis observed
- `backup_5970` (backup_service): tier **explicit**
  - linked by `evidence_92#backup_service/restore_entries:1:backup_5970` — json record, system backup_service, captured 2026-09-15T11:44:55+00:00, observed 2026-09-15T10:39:37+00:00, basis observed
- `data_flow_2295` (integration_service): tier **explicit**
  - linked by `evidence_92#integration_service/connectors:0:data_flow_2295` — json record, system integration_service, captured 2026-09-15T11:44:55+00:00, observed 2026-09-15T08:48:09+00:00, basis observed
- `support_4707` (support_platform): tier **explicit**
  - linked by `evidence_92#support_platform/tickets:1:support_4707` — json record, system support_platform, captured 2026-09-15T11:44:55+00:00, observed 2026-09-15T10:48:30+00:00, basis observed

### Rejected links and open questions

- no exclusions recorded
- ambiguity: primary profile unassigned; candidates ['account_5482', 'account_3866', 'account_9321', 'account_7012']

## Each copy and its state at the cutoff

- `audit_record_3830`: verdict **compliant** (1 copies compliant); proof `evidence_92#security_service/audit_records:1:audit_record_3830` — json record, system security_service, captured 2026-09-15T11:44:55+00:00, observed 2026-09-15T09:31:23+00:00, basis observed
  - security_service/primary: **PRESENT** from direct; `evidence_92#security_service/audit_records:1:audit_record_3830` — json record, system security_service, captured 2026-09-15T11:44:55+00:00, observed 2026-09-15T09:31:23+00:00, basis observed
- `backup_5970`: verdict **compliant** (1 copies compliant); proof `evidence_92#backup_service/restore_entries:1:backup_5970` — json record, system backup_service, captured 2026-09-15T11:44:55+00:00, observed 2026-09-15T10:39:37+00:00, basis observed
  - backup_service/primary: **BLOCKED** from direct; `evidence_92#backup_service/restore_entries:1:backup_5970` — json record, system backup_service, captured 2026-09-15T11:44:55+00:00, observed 2026-09-15T10:39:37+00:00, basis observed
- `data_flow_2295`: verdict **compliant** (1 copies compliant); proof `evidence_92#integration_service/connectors:0:data_flow_2295` — json record, system integration_service, captured 2026-09-15T11:44:55+00:00, observed 2026-09-15T08:48:09+00:00, basis observed
  - integration_service/primary: **DISABLED** from direct; `evidence_92#integration_service/connectors:0:data_flow_2295` — json record, system integration_service, captured 2026-09-15T11:44:55+00:00, observed 2026-09-15T08:48:09+00:00, basis observed
- `support_4707`: verdict **compliant** (1 copies compliant); proof `evidence_92#support_platform/tickets:1:support_4707` — json record, system support_platform, captured 2026-09-15T11:44:55+00:00, observed 2026-09-15T10:48:30+00:00, basis observed
  - support_platform/primary: **REDACTED** from direct; `evidence_92#support_platform/tickets:1:support_4707` — json record, system support_platform, captured 2026-09-15T11:44:55+00:00, observed 2026-09-15T10:48:30+00:00, basis observed

## Policy behind each action

- `audit_record_3830`: category SECURITY_AUDIT_LOG (system security_service) → rule rule_12 → treatment **RETAIN**
- `backup_5970`: category BACKUP_ARCHIVE (system backup_service) → rule rule_14 → treatment **BLOCK_RESTORE**
- `data_flow_2295`: category DATA_FLOW (system integration_service) → rule no deletion_rules row for this category; the engine's built-in treatment → treatment **DISABLE_FLOW**
- `support_4707`: category SUPPORT_MESSAGE (workflow action type ['REDACT'] (claimed result ignored)) → rule rule_05 → treatment **REDACT**

## Limits and reasons recorded by the run

- primary profile unassigned; candidates ['account_5482', 'account_3866', 'account_9321', 'account_7012']
- no account resource attributed

## Final status and ordered steps

**COMPLETE**, 4 steps

| # | phase | system | resource | operation | state | evidence |
|---|---|---|---|---|---|---|
| 1 | VERIFICATION | security_service | audit_record_3830 | VERIFY_RECORD_PRESENT | PRESENT | evidence_92 |
| 2 | VERIFICATION | support_platform | support_4707 | VERIFY_RECORD_REDACTED | REDACTED | evidence_92 |
| 3 | VERIFICATION | integration_service | data_flow_2295 | VERIFY_DATA_FLOW_DISABLED | DISABLED | evidence_92 |
| 4 | VERIFICATION | backup_service | backup_5970 | VERIFY_RESTORE_BLOCKED | BLOCKED | evidence_92 |

_Generated by `main.py explain` from `c62-samples/decisions.jsonl`; provenance from an offline re-ingest. No model was called._
