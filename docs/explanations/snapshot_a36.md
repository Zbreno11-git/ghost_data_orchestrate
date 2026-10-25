# case_123: INCOMPLETE

## Verdict and certainty (kept apart)

- Best-effort status: **INCOMPLETE**
- Evidential support: **unresolved**
- Run integrity: verified (output.csv, decisions.jsonl and provenance.jsonl match their recorded sha256 and each other; run fingerprint b0f0247857e1)

## Request

- Requested 2026-08-06T10:00:00Z; the workflow claimed **COMPLETE** at 2026-08-08T10:00:00Z (a claim, never proof)
- Cutoff (audit_at): 2026-08-17T10:00:00+00:00; request email: `m.mercier28@gmail.com`
- Intent: authorizes deletion = True, confidence high, source llm batch cross-checked with the rule; reason: rule and LLM agree (fr)

## Person

- `user_121`; the request email is a **current** identifier

| type | value | role at the cutoff | source |
|---|---|---|---|
| email | `m.mercier28@gmail.com` | current | user_identities |
| email_hash | `f86e324feaff7a751e9cf6813fd1bcf8b483d698eadded1b1e8d5b6c39a10132` | current | derived:sha256 |
| name | `Mathis Mercier` | current | user_identities |
| phone | `+33 6 36 37 41 61` | current | user_identities |
| user_id | `user_121` | current | user_identities |

## Ownership: the chain from the person to each resource

- Account: **none attributed**; candidates left by the deduction: ['account_7927', 'account_1034', 'account_9511', 'account_2988', 'account_8951']
- `audit_record_5645` (security_service): tier **explicit**
  - linked by `evidence_12#snap7:0:audit_record_5645` — json record in `evidence/records/customer_data_snapshot_bundle_20260819.json`, system security_service, captured 2026-08-19T10:00:00+00:00, observed 2026-08-17T10:00:00+00:00, basis observed (snapshot envelope: observed = its own capture time)
- `backup_8742` (backup_service): tier **explicit**
  - linked by `evidence_12#snap3:0:backup_8742` — json record in `evidence/records/customer_data_snapshot_bundle_20260819.json`, system backup_service, captured 2026-08-19T10:00:00+00:00, observed 2026-08-17T10:00:00+00:00, basis observed (snapshot envelope: observed = its own capture time)
  - linked by `evidence_87#backup_restore_entries:backup_8742` — sql record in `evidence/databases/customer_data_inventory_20260817.sql`, system backup_service, captured 2026-08-17T09:42:50+00:00, observed 2026-08-17T06:50:20+00:00, basis observed

### Rejected links and open questions

- no exclusions recorded
- ambiguity: primary profile unassigned; candidates ['account_7927', 'account_1034', 'account_9511', 'account_2988', 'account_8951']

## Each copy and its state at the cutoff

- `audit_record_5645`: verdict **unknown** (compliant only by an export captured after audit_at (not citable)); proof not recorded in the trace
  - security_service/primary: **PRESENT** from direct; `evidence_12#snap7:0:audit_record_5645` — json record in `evidence/records/customer_data_snapshot_bundle_20260819.json`, system security_service, captured 2026-08-19T10:00:00+00:00, observed 2026-08-17T10:00:00+00:00, basis observed (snapshot envelope: observed = its own capture time)
- `backup_8742`: verdict **violation** (1/2 copies violate BLOCK_RESTORE); proof `evidence_87#backup_restore_entries:backup_8742` — sql record in `evidence/databases/customer_data_inventory_20260817.sql`, system backup_service, captured 2026-08-17T09:42:50+00:00, observed 2026-08-17T06:50:20+00:00, basis observed
  - backup_service/inventory: **RESTORABLE** from direct; `evidence_87#backup_restore_entries:backup_8742` — sql record in `evidence/databases/customer_data_inventory_20260817.sql`, system backup_service, captured 2026-08-17T09:42:50+00:00, observed 2026-08-17T06:50:20+00:00, basis observed
  - backup_service/primary: **RESTORABLE** from direct; `evidence_12#snap3:0:backup_8742` — json record in `evidence/records/customer_data_snapshot_bundle_20260819.json`, system backup_service, captured 2026-08-19T10:00:00+00:00, observed 2026-08-17T10:00:00+00:00, basis observed (snapshot envelope: observed = its own capture time)

## Policy behind each action

- `audit_record_5645`: category SECURITY_AUDIT_LOG (system security_service) → rule rule_12 → treatment **RETAIN**
- `backup_8742`: category BACKUP_ARCHIVE (system backup_service) → rule rule_14 → treatment **BLOCK_RESTORE**

## Limits and reasons recorded by the run

- agent: No evidence links any of the candidate accounts to the user's identifiers. I have left the account as null.
- primary profile unassigned; candidates ['account_7927', 'account_1034', 'account_9511', 'account_2988', 'account_8951']
- no account resource attributed
- audit_record_5645: state unknown (compliant only by an export captured after audit_at (not citable))

## Final status and ordered steps

**INCOMPLETE**, 4 steps

| # | phase | system | resource | operation | state | evidence | basis |
|---|---|---|---|---|---|---|---|
| 1 | FINDING | backup_service | backup_8742 | REPORT_RESTORE_RISK | ACTIVE | evidence_87 | direct observation |
| 2 | REMEDIATION | backup_service | backup_8742 | BLOCK_RESTORE | BLOCKED | — | proposed remediation (not executed) |
| 3 | VERIFICATION | security_service | audit_record_5645 | VERIFY_RECORD_PRESENT | PRESENT | — | check to run after remediation |
| 4 | VERIFICATION | backup_service | backup_8742 | VERIFY_RESTORE_BLOCKED | BLOCKED | — | check to run after remediation |

_Generated by `main.py explain` from `final-r2/decisions.jsonl` and its saved provenance. No model was called._
