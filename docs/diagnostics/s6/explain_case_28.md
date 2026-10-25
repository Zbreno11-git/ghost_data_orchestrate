# case_28: COMPLETE

## Verdict and certainty (kept apart)

- Best-effort status: **COMPLETE**
- Evidential support: **unresolved**

## Request

- Requested 2026-08-28T12:00:00Z; the workflow claimed **NOT_STARTED** at 2026-08-30T12:00:00Z (a claim, never proof)
- Cutoff (audit_at): 2026-09-15T12:00:00+00:00; request email: `smartinez6461@gmail.com`
- Intent: authorizes deletion = True, confidence high, source rule; reason: deletion instruction 'deleted'

## Person

- `user_28`; the request email is a **current** identifier

| type | value | role at the cutoff | source |
|---|---|---|---|
| email | `smartinez6461@gmail.com` | current | user_identities |
| email_hash | `5951510123a31517eee05595926fe7c9784e0f7fc16bb3a913b5768375486ea1` | current | derived:sha256 |
| name | `Sofía Martínez` | current | user_identities |
| phone | `+34 744 502 860` | current | user_identities |
| user_id | `user_28` | current | user_identities |

## Ownership: the chain from the person to each resource

- Account: **none attributed**; candidates left by the deduction: ['account_7643', 'account_1378', 'account_5715', 'account_1298', 'account_9862', 'account_2176', 'account_5482', 'account_3866', 'account_9321', 'account_7012']
- `audit_record_9265` (security_service): tier **explicit**
  - linked by `evidence_92#security_service/audit_records:4:audit_record_9265` — json record, system security_service, captured 2026-09-15T11:44:55+00:00, observed 2026-09-15T09:52:37+00:00, basis observed
- `backup_838` (backup_service): tier **explicit**
  - linked by `evidence_92#backup_service/restore_entries:2:backup_838` — json record, system backup_service, captured 2026-09-15T11:44:55+00:00, observed 2026-09-15T09:04:41+00:00, basis observed
- `data_flow_2337` (integration_service): tier **explicit**
  - linked by `evidence_92#integration_service/connectors:1:data_flow_2337` — json record, system integration_service, captured 2026-09-15T11:44:55+00:00, observed 2026-09-15T09:35:32+00:00, basis observed
- `support_2351` (support_platform): tier **explicit**
  - linked by `evidence_92#support_platform/tickets:0:support_2351` — json record, system support_platform, captured 2026-09-15T11:44:55+00:00, observed 2026-09-15T10:51:49+00:00, basis observed

### Rejected links and open questions

- no exclusions recorded
- ambiguity: primary profile unassigned; candidates ['account_7643', 'account_1378', 'account_5715', 'account_1298', 'account_9862', 'account_2176', 'account_5482', 'account_3866', 'account_9321', 'account_7012']

## Each copy and its state at the cutoff

- `audit_record_9265`: verdict **compliant** (1 copies compliant); proof `evidence_92#security_service/audit_records:4:audit_record_9265` — json record, system security_service, captured 2026-09-15T11:44:55+00:00, observed 2026-09-15T09:52:37+00:00, basis observed
  - security_service/primary: **PRESENT** from direct; `evidence_92#security_service/audit_records:4:audit_record_9265` — json record, system security_service, captured 2026-09-15T11:44:55+00:00, observed 2026-09-15T09:52:37+00:00, basis observed
- `backup_838`: verdict **compliant** (1 copies compliant); proof `evidence_92#backup_service/restore_entries:2:backup_838` — json record, system backup_service, captured 2026-09-15T11:44:55+00:00, observed 2026-09-15T09:04:41+00:00, basis observed
  - backup_service/primary: **BLOCKED** from direct; `evidence_92#backup_service/restore_entries:2:backup_838` — json record, system backup_service, captured 2026-09-15T11:44:55+00:00, observed 2026-09-15T09:04:41+00:00, basis observed
- `data_flow_2337`: verdict **compliant** (1 copies compliant); proof `evidence_92#integration_service/connectors:1:data_flow_2337` — json record, system integration_service, captured 2026-09-15T11:44:55+00:00, observed 2026-09-15T09:35:32+00:00, basis observed
  - integration_service/primary: **DISABLED** from direct; `evidence_92#integration_service/connectors:1:data_flow_2337` — json record, system integration_service, captured 2026-09-15T11:44:55+00:00, observed 2026-09-15T09:35:32+00:00, basis observed
- `support_2351`: verdict **compliant** (1 copies compliant); proof `evidence_92#support_platform/tickets:0:support_2351` — json record, system support_platform, captured 2026-09-15T11:44:55+00:00, observed 2026-09-15T10:51:49+00:00, basis observed
  - support_platform/primary: **REDACTED** from direct; `evidence_92#support_platform/tickets:0:support_2351` — json record, system support_platform, captured 2026-09-15T11:44:55+00:00, observed 2026-09-15T10:51:49+00:00, basis observed

## Policy behind each action

- `audit_record_9265`: category SECURITY_AUDIT_LOG (system security_service) → rule rule_12 → treatment **RETAIN**
- `backup_838`: category BACKUP_ARCHIVE (system backup_service) → rule rule_14 → treatment **BLOCK_RESTORE**
- `data_flow_2337`: category DATA_FLOW (system integration_service) → rule no deletion_rules row for this category; the engine's built-in treatment → treatment **DISABLE_FLOW**
- `support_2351`: category SUPPORT_MESSAGE (workflow action type ['REDACT'] (claimed result ignored)) → rule rule_05 → treatment **REDACT**

## Limits and reasons recorded by the run

- primary profile unassigned; candidates ['account_7643', 'account_1378', 'account_5715', 'account_1298', 'account_9862', 'account_2176', 'account_5482', 'account_3866', 'account_9321', 'account_7012']
- no account resource attributed

## Final status and ordered steps

**COMPLETE**, 4 steps

| # | phase | system | resource | operation | state | evidence |
|---|---|---|---|---|---|---|
| 1 | VERIFICATION | security_service | audit_record_9265 | VERIFY_RECORD_PRESENT | PRESENT | evidence_92 |
| 2 | VERIFICATION | support_platform | support_2351 | VERIFY_RECORD_REDACTED | REDACTED | evidence_92 |
| 3 | VERIFICATION | integration_service | data_flow_2337 | VERIFY_DATA_FLOW_DISABLED | DISABLED | evidence_92 |
| 4 | VERIFICATION | backup_service | backup_838 | VERIFY_RESTORE_BLOCKED | BLOCKED | evidence_92 |

_Generated by `main.py explain` from `c62-samples/decisions.jsonl`; provenance from an offline re-ingest. No model was called._
