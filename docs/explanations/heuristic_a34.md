# case_63: COMPLETE

## Verdict and certainty (kept apart)

- Best-effort status: **COMPLETE**
- Evidential support: **unresolved**
- **HEURISTIC PREDICTION**: part of this row is not a reconstructed state; see the limits below
- Run integrity: verified (output.csv, decisions.jsonl and provenance.jsonl match their recorded sha256 and each other; run fingerprint b0f0247857e1)

## Request

- Requested 2026-09-14T04:20:00Z; the workflow claimed **NOT_STARTED** at 2026-09-15T22:20:00Z (a claim, never proof)
- Cutoff (audit_at): 2026-09-17T09:20:00+00:00; request email: `kwame-mensah@proton.me`
- Intent: authorizes deletion = True, confidence high, source llm batch cross-checked with the rule; reason: rule and LLM agree (en)

## Person

- `user_09`; the request email is a **current** identifier

| type | value | role at the cutoff | source |
|---|---|---|---|
| email | `kwame-mensah@proton.me` | current | user_identities |
| email_hash | `e7ce7f1fd5cd4e5873576243ee7a0ca8599c51d0e9f2197f6184efc514e5bd2a` | current | derived:sha256 |
| name | `Kwame Mensah` | current | user_identities |
| phone | `+233 24 456 1267` | current | user_identities |
| user_id | `user_09` | current | user_identities |

## Ownership: the chain from the person to each resource

- Account `account_2064`: tier **workflow**, deduced by nearest anchor to reported_at (752 min); weak; evidence `activity_3849#row`
- `account_2064` (account_service): tier **workflow**
  - linked by `activity_3849#row` — csv activity in `activity_3849`, system account_service, captured 2026-09-15T09:47:50+00:00, observed 2026-09-15T09:47:50+00:00, basis observed
- `marketing_001` (marketing_platform): tier **explicit**
  - linked by `activity_4008#row` — csv activity in `activity_4008`, system marketing_platform, captured 2026-09-16T07:27:01+00:00, observed 2026-09-16T07:27:01+00:00, basis observed

### Rejected links and open questions

- no exclusions recorded
- ambiguity: primary profile is a weak candidate among ['account_2064', 'account_6523', 'account_7566']

## Each copy and its state at the cutoff

- `account_2064`: verdict **compliant** (8 copies compliant); proof `evidence_51#snap0` — json scope in `evidence/records/customer_data_snapshot_bundle_20260915.json`, system account_service, captured 2026-09-15T12:00:00+00:00, observed 2026-09-15T12:00:00+00:00, basis observed (snapshot envelope: observed = its own capture time)
  - account_service/failover_replica: **ABSENT** from scope; `evidence_54#table:customer_profiles_failover_replica` — sql scope in `evidence/databases/customer_accounts_failover_replica_20260902.sql`, system account_service, captured 2026-09-02T23:00:00+00:00, observed 2026-09-02T23:00:00+00:00, basis observed
  - account_service/inventory: **ABSENT** from scope; `evidence_93#table:customer_profiles` — sql scope in `evidence/databases/customer_data_inventory_20260916.sql`, system account_service, captured 2026-09-16T08:37:39+00:00, observed none stated, basis captured
  - account_service/primary: **ABSENT** from scope; `evidence_51#snap0` — json scope in `evidence/records/customer_data_snapshot_bundle_20260915.json`, system account_service, captured 2026-09-15T12:00:00+00:00, observed 2026-09-15T12:00:00+00:00, basis observed (snapshot envelope: observed = its own capture time)
  - account_service/read_replica: **ABSENT** from scope; `evidence_10#table:customer_data_read_replica` — sql scope in `evidence/databases/customer_data_read_replica_20260827.sql`, system ?, captured 2026-08-27T12:00:00+00:00, observed 2026-08-27T12:00:00+00:00, basis observed
  - account_service/regional_replica:ap_south: **ABSENT** from scope; `evidence_29#table:customer_data_replica_ap_south` — sql scope in `evidence/databases/customer_data_regional_replicas_20260519.sql`, system ?, captured 2026-05-19T06:00:00+00:00, observed 2026-05-19T06:00:00+00:00, basis observed
  - account_service/regional_replica:eu_west: **ABSENT** from scope; `evidence_33#table:customer_data_replica_eu_west` — sql scope in `evidence/databases/customer_data_regional_replicas_20260424.sql`, system ?, captured 2026-04-24T08:00:00+00:00, observed 2026-04-24T08:00:00+00:00, basis observed
  - account_service/reporting_replica: **ABSENT** from scope; `evidence_43#table:customer_data_reporting_replica` — sql scope in `evidence/databases/customer_data_reporting_replica_20260305.sql`, system ?, captured 2026-03-05T12:00:00+00:00, observed 2026-03-05T12:00:00+00:00, basis observed
  - account_service/scope: **ABSENT** from scope; `evidence_93#scope:account_service` — sql scope in `evidence/databases/customer_data_inventory_20260916.sql`, system account_service, captured 2026-09-16T08:37:39+00:00, observed 2026-09-16T08:37:39+00:00, basis observed
- `marketing_001`: verdict **unknown** (no admissible evidence of its state); proof not recorded in the trace

## Policy behind each action

- `account_2064`: category USER_PROFILE (system account_service) → rule rule_01 → treatment **DELETE**
- `marketing_001`: category MARKETING_PROFILE (system marketing_platform) → rule rule_10 → treatment **DELETE**

## Limits and reasons recorded by the run

- HEURISTIC PREDICTION (A34), not an attributed account: account_2064 is the nearest anchor to reported_at (752 min); weak
- agent: I confirmed marketing_001 is linked to the user's email and ID. No evidence confirms account_2064 belongs to the user, so I left the account as null.
- weak links used: account_2064
- primary profile is a weak candidate among ['account_2064', 'account_6523', 'account_7566']
- marketing_001: state unknown, cannot be verified (no admissible evidence of its state)

## Final status and ordered steps

**COMPLETE**, 1 steps

| # | phase | system | resource | operation | state | evidence | basis |
|---|---|---|---|---|---|---|---|
| 1 | VERIFICATION | account_service | account_2064 | VERIFY_RECORD_ABSENT | ABSENT | evidence_51 | heuristic prediction |

_Generated by `main.py explain` from `final-r2/decisions.jsonl` and its saved provenance. No model was called._
