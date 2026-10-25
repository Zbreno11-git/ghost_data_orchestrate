# case_105: INCOMPLETE

## Verdict and certainty (kept apart)

- Best-effort status: **INCOMPLETE**
- Evidential support: **resolved** (no workflow-only link, ambiguity or unknown state)

## Request

- Requested 2026-08-14T12:00:00Z; the workflow claimed **COMPLETE** at 2026-08-16T12:00:00Z (a claim, never proof)
- Cutoff (audit_at): 2026-08-27T12:00:00+00:00; request email: `h.kang86@yahoo.com`
- Intent: authorizes deletion = True, confidence high, source llm batch cross-checked with the rule; reason: rule and LLM agree (ko)

## Person

- `user_103`; the request email is a **current** identifier

| type | value | role at the cutoff | source |
|---|---|---|---|
| email | `h.kang86@yahoo.com` | current | user_identities |
| email_hash | `54c34ef8c599d7ba67f11641ddd992837505364bd57b399d08846e167ad64157` | current | derived:sha256 |
| name | `Ha-eun Kang` | current | user_identities |
| phone | `+82 10 2780 1520` | current | user_identities |
| user_id | `user_103` | current | user_identities |

## Ownership: the chain from the person to each resource

- Account `account_6345`: tier **explicit**, deduced by explicit_account; evidence `activity_3273#row`, `evidence_10#customer_data_read_replica:account_6345`
- `account_6345` (account_service): tier **explicit**
  - linked by `activity_3273#row` — csv activity, system account_service, captured 2026-08-16T10:58:54+00:00, observed 2026-08-16T10:58:54+00:00, basis observed
  - linked by `evidence_10#customer_data_read_replica:account_6345` — sql record, system account_service, captured 2026-08-27T12:00:00+00:00, observed 2026-08-27T12:00:00+00:00, basis observed
- `audit_record_4520` (security_service): tier **explicit**
  - linked by `evidence_10#customer_data_primary:audit_record_4520` — sql record, system security_service, captured 2026-08-27T12:00:00+00:00, observed 2026-08-27T12:00:00+00:00, basis observed
  - linked by `evidence_10#customer_data_read_replica:audit_record_4520` — sql record, system security_service, captured 2026-08-27T12:00:00+00:00, observed 2026-08-27T12:00:00+00:00, basis observed
- `search_4618` (search_service): tier **explicit**
  - linked by `evidence_10#customer_data_primary:search_4618` — sql record, system search_service, captured 2026-08-27T12:00:00+00:00, observed 2026-08-27T12:00:00+00:00, basis observed
  - linked by `evidence_10#customer_data_read_replica:search_4618` — sql record, system search_service, captured 2026-08-27T12:00:00+00:00, observed 2026-08-27T12:00:00+00:00, basis observed

### Rejected links and open questions

- no exclusions recorded
- no ownership ambiguity recorded

## Each copy and its state at the cutoff

- `account_6345`: verdict **violation** (1/7 copies violate DELETE); proof `evidence_10#customer_data_read_replica:account_6345` — sql record, system account_service, captured 2026-08-27T12:00:00+00:00, observed 2026-08-27T12:00:00+00:00, basis observed
  - account_service/inventory: **ABSENT** from scope; `evidence_87#table:customer_profiles` — sql scope, system account_service, captured 2026-08-17T09:42:50+00:00, observed none stated, basis captured
  - account_service/primary: **ABSENT** from scope; `evidence_12#snap10` — json scope, system account_service, captured 2026-08-19T10:00:00+00:00, observed 2026-08-19T10:00:00+00:00, basis observed
  - account_service/read_replica: **PRESENT** from direct; `evidence_10#customer_data_read_replica:account_6345` — sql record, system account_service, captured 2026-08-27T12:00:00+00:00, observed 2026-08-27T12:00:00+00:00, basis observed
  - account_service/regional_replica:ap_south: **ABSENT** from scope; `evidence_29#table:customer_data_replica_ap_south` — sql scope, system ?, captured 2026-05-19T06:00:00+00:00, observed 2026-05-19T06:00:00+00:00, basis observed
  - account_service/regional_replica:eu_west: **ABSENT** from scope; `evidence_33#table:customer_data_replica_eu_west` — sql scope, system ?, captured 2026-04-24T08:00:00+00:00, observed 2026-04-24T08:00:00+00:00, basis observed
  - account_service/reporting_replica: **ABSENT** from scope; `evidence_43#table:customer_data_reporting_replica` — sql scope, system ?, captured 2026-03-05T12:00:00+00:00, observed 2026-03-05T12:00:00+00:00, basis observed
  - account_service/scope: **ABSENT** from scope; `evidence_87#scope:account_service` — sql scope, system account_service, captured 2026-08-17T09:42:50+00:00, observed 2026-08-17T09:42:50+00:00, basis observed
- `audit_record_4520`: verdict **compliant** (2 copies compliant); proof `evidence_10#customer_data_primary:audit_record_4520` — sql record, system security_service, captured 2026-08-27T12:00:00+00:00, observed 2026-08-27T12:00:00+00:00, basis observed
  - security_service/primary: **PRESENT** from direct; `evidence_10#customer_data_primary:audit_record_4520` — sql record, system security_service, captured 2026-08-27T12:00:00+00:00, observed 2026-08-27T12:00:00+00:00, basis observed
  - security_service/read_replica: **PRESENT** from direct; `evidence_10#customer_data_read_replica:audit_record_4520` — sql record, system security_service, captured 2026-08-27T12:00:00+00:00, observed 2026-08-27T12:00:00+00:00, basis observed
- `search_4618`: verdict **violation** (2/7 copies violate DELETE); proof `evidence_10#customer_data_read_replica:search_4618` — sql record, system search_service, captured 2026-08-27T12:00:00+00:00, observed 2026-08-27T12:00:00+00:00, basis observed
  - search_service/inventory: **ABSENT** from scope; `evidence_87#table:customer_search_documents` — sql scope, system search_service, captured 2026-08-17T09:42:50+00:00, observed none stated, basis captured
  - search_service/primary: **PRESENT** from direct; `evidence_10#customer_data_primary:search_4618` — sql record, system search_service, captured 2026-08-27T12:00:00+00:00, observed 2026-08-27T12:00:00+00:00, basis observed
  - search_service/read_replica: **PRESENT** from direct; `evidence_10#customer_data_read_replica:search_4618` — sql record, system search_service, captured 2026-08-27T12:00:00+00:00, observed 2026-08-27T12:00:00+00:00, basis observed
  - search_service/regional_replica:ap_south: **ABSENT** from scope; `evidence_29#table:customer_data_replica_ap_south` — sql scope, system ?, captured 2026-05-19T06:00:00+00:00, observed 2026-05-19T06:00:00+00:00, basis observed
  - search_service/regional_replica:eu_west: **ABSENT** from scope; `evidence_29#table:customer_data_replica_eu_west` — sql scope, system ?, captured 2026-05-19T06:00:00+00:00, observed 2026-05-19T06:00:00+00:00, basis observed
  - search_service/reporting_replica: **ABSENT** from scope; `evidence_43#table:customer_data_reporting_replica` — sql scope, system ?, captured 2026-03-05T12:00:00+00:00, observed 2026-03-05T12:00:00+00:00, basis observed
  - search_service/scope: **ABSENT** from scope; `evidence_87#scope:search_service` — sql scope, system search_service, captured 2026-08-17T09:42:50+00:00, observed 2026-08-17T09:42:50+00:00, basis observed

## Policy behind each action

- `account_6345`: category USER_PROFILE (system account_service) → rule rule_01 → treatment **DELETE**
- `audit_record_4520`: category SECURITY_AUDIT_LOG (system security_service) → rule rule_12 → treatment **RETAIN**
- `search_4618`: category SEARCH_INDEX_ENTRY (system search_service) → rule rule_03 → treatment **DELETE**

## Limits and reasons recorded by the run

- none recorded

## Final status and ordered steps

**INCOMPLETE**, 7 steps

| # | phase | system | resource | operation | state | evidence |
|---|---|---|---|---|---|---|
| 1 | FINDING | account_service | account_6345 | REPORT_REMAINING_RECORD | PRESENT | evidence_10 |
| 2 | FINDING | search_service | search_4618 | REPORT_REMAINING_RECORD | PRESENT | evidence_10 |
| 3 | REMEDIATION | account_service | account_6345 | DELETE_RECORD | ABSENT | — |
| 4 | REMEDIATION | search_service | search_4618 | DELETE_RECORD | ABSENT | — |
| 5 | VERIFICATION | account_service | account_6345 | VERIFY_RECORD_ABSENT | ABSENT | — |
| 6 | VERIFICATION | search_service | search_4618 | VERIFY_RECORD_ABSENT | ABSENT | — |
| 7 | VERIFICATION | security_service | audit_record_4520 | VERIFY_RECORD_PRESENT | PRESENT | — |

_Generated by `main.py explain` from `final/decisions.jsonl`; provenance from an offline re-ingest. No model was called._
