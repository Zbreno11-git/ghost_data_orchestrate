# case_100: INCOMPLETE

## Verdict and certainty (kept apart)

- Best-effort status: **INCOMPLETE**
- Evidential support: **unresolved**
- Run integrity: verified (output.csv, decisions.jsonl and provenance.jsonl match their recorded sha256 and each other; run fingerprint 30c7f4dd5065)

## Request

- Requested 2026-08-04T06:00:00Z; the workflow claimed **COMPLETE** at 2026-08-07T06:00:00Z (a claim, never proof)
- Cutoff (audit_at): 2026-09-01T06:00:00+00:00; request email: `nasser.mariam88@gmail.com`
- Intent: authorizes deletion = True, confidence high, source llm batch cross-checked with the rule; reason: rule and LLM agree (en)

## Person

- `user_98`; the request email is a **historical** identifier

| type | value | role at the cutoff | source |
|---|---|---|---|
| email | `nasser.mariam@gmail.com` | current | user_identities |
| email_hash | `f4e9abcb5082caba70103ebee3257753e7cbb75302913ab60b2af432c607eded` | current | derived:sha256 |
| name | `Mariam Nasser` | current | user_identities |
| phone | `+971 54 770 5148` | current | user_identities |
| user_id | `user_98` | current | user_identities |
| email | `nasser.mariam88@gmail.com` | historical | audit_256 |
| email_hash | `1fb889a86885d20c89078754af088be580a899073865e6991b42ce60333dcad4` | historical | audit_257 |

## Ownership: the chain from the person to each resource

- Account: **none attributed**; candidates left by the deduction: ['account_7637', 'account_6805', 'account_7927', 'account_1034', 'account_9511']
- `search_018` (search_service): tier **explicit**
  - linked by `evidence_89#search_service/index_queries:0:search_018:hit0` — json record in `evidence/records/service_resource_export_20260901_053316.json`, system search_service, captured 2026-09-01T05:33:16+00:00, observed 2026-09-01T04:45:42+00:00, basis observed
- `support_1630` (support_platform): tier **explicit**
  - linked by `evidence_89#support_platform/tickets:0:support_1630` — json record in `evidence/records/service_resource_export_20260901_053316.json`, system support_platform, captured 2026-09-01T05:33:16+00:00, observed 2026-09-01T04:10:02+00:00, basis observed

### Rejected links and open questions

- no exclusions recorded
- ambiguity: primary profile unassigned; candidates ['account_7637', 'account_6805', 'account_7927', 'account_1034', 'account_9511']

## Each copy and its state at the cutoff

- `search_018`: verdict **violation** (1/7 copies violate DELETE); proof `evidence_89#search_service/index_queries:0:search_018:hit0` — json record in `evidence/records/service_resource_export_20260901_053316.json`, system search_service, captured 2026-09-01T05:33:16+00:00, observed 2026-09-01T04:45:42+00:00, basis observed
  - search_service/inventory: **ABSENT** from scope; `evidence_87#table:customer_search_documents` — sql scope in `evidence/databases/customer_data_inventory_20260817.sql`, system search_service, captured 2026-08-17T09:42:50+00:00, observed none stated, basis captured
  - search_service/primary: **PRESENT** from direct; `evidence_89#search_service/index_queries:0:search_018:hit0` — json record in `evidence/records/service_resource_export_20260901_053316.json`, system search_service, captured 2026-09-01T05:33:16+00:00, observed 2026-09-01T04:45:42+00:00, basis observed
  - search_service/read_replica: **ABSENT** from scope; `evidence_10#table:customer_data_read_replica` — sql scope in `evidence/databases/customer_data_read_replica_20260827.sql`, system ?, captured 2026-08-27T12:00:00+00:00, observed 2026-08-27T12:00:00+00:00, basis observed
  - search_service/regional_replica:ap_south: **ABSENT** from scope; `evidence_29#table:customer_data_replica_ap_south` — sql scope in `evidence/databases/customer_data_regional_replicas_20260519.sql`, system ?, captured 2026-05-19T06:00:00+00:00, observed 2026-05-19T06:00:00+00:00, basis observed
  - search_service/regional_replica:eu_west: **ABSENT** from scope; `evidence_29#table:customer_data_replica_eu_west` — sql scope in `evidence/databases/customer_data_regional_replicas_20260519.sql`, system ?, captured 2026-05-19T06:00:00+00:00, observed 2026-05-19T06:00:00+00:00, basis observed
  - search_service/reporting_replica: **ABSENT** from scope; `evidence_43#table:customer_data_reporting_replica` — sql scope in `evidence/databases/customer_data_reporting_replica_20260305.sql`, system ?, captured 2026-03-05T12:00:00+00:00, observed 2026-03-05T12:00:00+00:00, basis observed
  - search_service/scope: **ABSENT** from scope; `evidence_87#scope:search_service` — sql scope in `evidence/databases/customer_data_inventory_20260817.sql`, system search_service, captured 2026-08-17T09:42:50+00:00, observed 2026-08-17T09:42:50+00:00, basis observed
- `support_1630`: verdict **violation** (1/1 copies violate REDACT); proof `evidence_89#support_platform/tickets:0:support_1630` — json record in `evidence/records/service_resource_export_20260901_053316.json`, system support_platform, captured 2026-09-01T05:33:16+00:00, observed 2026-09-01T04:10:02+00:00, basis observed
  - support_platform/primary: **PRESENT_EXPOSED** from direct; `evidence_89#support_platform/tickets:0:support_1630` — json record in `evidence/records/service_resource_export_20260901_053316.json`, system support_platform, captured 2026-09-01T05:33:16+00:00, observed 2026-09-01T04:10:02+00:00, basis observed

## Policy behind each action

- `search_018`: category SEARCH_INDEX_ENTRY (system search_service) → rule rule_03 → treatment **DELETE**
- `support_1630`: category SUPPORT_MESSAGE (workflow action type ['REDACT'] (claimed result ignored)) → rule rule_05 → treatment **REDACT**

## Limits and reasons recorded by the run

- agent: I reviewed the audit logs and confirmed user_98 is associated with both the current and historical emails. However, none of the account candidates are linked to user_98 by evidence, so I am leaving th
- primary profile unassigned; candidates ['account_7637', 'account_6805', 'account_7927', 'account_1034', 'account_9511']
- no account resource attributed

## Final status and ordered steps

**INCOMPLETE**, 6 steps

| # | phase | system | resource | operation | state | evidence | basis |
|---|---|---|---|---|---|---|---|
| 1 | FINDING | search_service | search_018 | REPORT_REMAINING_RECORD | PRESENT | evidence_89 | direct observation |
| 2 | FINDING | support_platform | support_1630 | REPORT_EXPOSED_PII | PRESENT | evidence_89 | direct observation |
| 3 | REMEDIATION | search_service | search_018 | DELETE_RECORD | ABSENT | — | proposed remediation (not executed) |
| 4 | REMEDIATION | support_platform | support_1630 | REDACT_RECORD | REDACTED | — | proposed remediation (not executed) |
| 5 | VERIFICATION | search_service | search_018 | VERIFY_RECORD_ABSENT | ABSENT | — | check to run after remediation |
| 6 | VERIFICATION | support_platform | support_1630 | VERIFY_RECORD_REDACTED | REDACTED | — | check to run after remediation |

_Generated by `main.py explain` from `final-r2/decisions.jsonl` and its saved provenance. No model was called._
