# case_113: COMPLETE

## Verdict and certainty (kept apart)

- Best-effort status: **COMPLETE**
- Evidential support: **resolved** (no workflow-only link, ambiguity or unknown state)
- Run integrity: verified (output.csv, decisions.jsonl and provenance.jsonl match their recorded sha256 and each other; run fingerprint b0f0247857e1)

## Request

- Requested 2026-08-01T11:00:00Z; the workflow claimed **PARTIALLY_COMPLETE** at 2026-08-02T11:00:00Z (a claim, never proof)
- Cutoff (audit_at): 2026-08-22T11:00:00+00:00; request email: `sami-elsayed@gmail.com`
- Intent: authorizes deletion = True, confidence high, source llm batch cross-checked with the rule; reason: rule and LLM agree (en)

## Person

- `user_111`; the request email is a **current** identifier

| type | value | role at the cutoff | source |
|---|---|---|---|
| email | `sami-elsayed@gmail.com` | current | user_identities |
| email_hash | `4045984f85943f27298ee6071cee7f18299596edc62272a5ce352d15701f210d` | current | derived:sha256 |
| name | `Sami El-Sayed` | current | user_identities |
| phone | `+971 55 598 4636` | current | user_identities |
| user_id | `user_111` | current | user_identities |

## Ownership: the chain from the person to each resource

- Account `account_6697`: tier **explicit**, deduced by explicit_account; evidence `activity_3061#row`, `evidence_88#trace:rb-084131-008`
- `account_6697` (account_service): tier **explicit**
  - linked by `activity_3061#row` — csv activity in `activity_3061`, system account_service, captured 2026-08-02T10:03:02+00:00, observed 2026-08-02T10:03:02+00:00, basis observed
  - linked by `evidence_88#trace:rb-084131-008` — log lookup in `evidence/logs/resource_lookup_trace_20260822_103910.log`, system account_service, captured 2026-08-22T10:39:10+00:00, observed 2026-08-22T08:41:31+00:00, basis observed
- `audit_record_1127` (security_service): tier **explicit**
  - linked by `evidence_88#trace:rb-083955-007` — log record in `evidence/logs/resource_lookup_trace_20260822_103910.log`, system security_service, captured 2026-08-22T10:39:10+00:00, observed 2026-08-22T08:39:55+00:00, basis observed

### Rejected links and open questions

- no exclusions recorded
- no ownership ambiguity recorded

## Each copy and its state at the cutoff

- `account_6697`: verdict **compliant** (7 copies compliant); proof `evidence_88#trace:rb-084131-008` — log lookup in `evidence/logs/resource_lookup_trace_20260822_103910.log`, system account_service, captured 2026-08-22T10:39:10+00:00, observed 2026-08-22T08:41:31+00:00, basis observed
  - account_service/inventory: **ABSENT** from scope; `evidence_87#table:customer_profiles` — sql scope in `evidence/databases/customer_data_inventory_20260817.sql`, system account_service, captured 2026-08-17T09:42:50+00:00, observed none stated, basis captured
  - account_service/primary: **ABSENT** from direct; `evidence_88#trace:rb-084131-008` — log lookup in `evidence/logs/resource_lookup_trace_20260822_103910.log`, system account_service, captured 2026-08-22T10:39:10+00:00, observed 2026-08-22T08:41:31+00:00, basis observed
  - account_service/read_replica: **ABSENT** from scope; `evidence_15#table:customer_data_read_replica` — sql scope in `evidence/databases/customer_data_read_replica_20260802.sql`, system ?, captured 2026-08-02T07:00:00+00:00, observed 2026-08-02T07:00:00+00:00, basis observed
  - account_service/regional_replica:ap_south: **ABSENT** from scope; `evidence_29#table:customer_data_replica_ap_south` — sql scope in `evidence/databases/customer_data_regional_replicas_20260519.sql`, system ?, captured 2026-05-19T06:00:00+00:00, observed 2026-05-19T06:00:00+00:00, basis observed
  - account_service/regional_replica:eu_west: **ABSENT** from scope; `evidence_33#table:customer_data_replica_eu_west` — sql scope in `evidence/databases/customer_data_regional_replicas_20260424.sql`, system ?, captured 2026-04-24T08:00:00+00:00, observed 2026-04-24T08:00:00+00:00, basis observed
  - account_service/reporting_replica: **ABSENT** from scope; `evidence_43#table:customer_data_reporting_replica` — sql scope in `evidence/databases/customer_data_reporting_replica_20260305.sql`, system ?, captured 2026-03-05T12:00:00+00:00, observed 2026-03-05T12:00:00+00:00, basis observed
  - account_service/scope: **ABSENT** from scope; `evidence_87#scope:account_service` — sql scope in `evidence/databases/customer_data_inventory_20260817.sql`, system account_service, captured 2026-08-17T09:42:50+00:00, observed 2026-08-17T09:42:50+00:00, basis observed
- `audit_record_1127`: verdict **compliant** (1 copies compliant); proof `evidence_88#trace:rb-083955-007` — log record in `evidence/logs/resource_lookup_trace_20260822_103910.log`, system security_service, captured 2026-08-22T10:39:10+00:00, observed 2026-08-22T08:39:55+00:00, basis observed
  - security_service/primary: **PRESENT** from direct; `evidence_88#trace:rb-083955-007` — log record in `evidence/logs/resource_lookup_trace_20260822_103910.log`, system security_service, captured 2026-08-22T10:39:10+00:00, observed 2026-08-22T08:39:55+00:00, basis observed

## Policy behind each action

- `account_6697`: category USER_PROFILE (system account_service) → rule rule_01 → treatment **DELETE**
- `audit_record_1127`: category SECURITY_AUDIT_LOG (system security_service) → rule rule_12 → treatment **RETAIN**

## Limits and reasons recorded by the run

- none recorded

## Final status and ordered steps

**COMPLETE**, 2 steps

| # | phase | system | resource | operation | state | evidence | basis |
|---|---|---|---|---|---|---|---|
| 1 | VERIFICATION | account_service | account_6697 | VERIFY_RECORD_ABSENT | ABSENT | evidence_88 | direct observation |
| 2 | VERIFICATION | security_service | audit_record_1127 | VERIFY_RECORD_PRESENT | PRESENT | evidence_88 | direct observation |

_Generated by `main.py explain` from `final-r2/decisions.jsonl` and its saved provenance. No model was called._
