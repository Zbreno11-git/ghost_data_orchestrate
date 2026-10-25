# S6 accuracy gate

Full official denominators. The 32 public samples have been inspected since S0: they measure regressions, they are not a held-out estimate of hidden-target accuracy. Custom cases were specified independently of the engine (A13).

### samples (`runs/s7/c71t/manifest-samples` → `runs/s7/c71t/snap-samples`)

| metric | baseline | candidate |
|---|---|---|
| status | 32/32 | 28/32 |
| whole-case | 12/32 | 12/32 |
| step precision | 162/163 | 114/119 |
| step recall | 162/193 | 114/193 |
| citation on matched | 162/162 | 112/114 |
| cited-evidence recall | 61/75 | 36/75 |
| sequence | 12/32 | 12/32 |
| step F1 | 0.9101 | 0.7308 |

- Correct steps: kept 112, gained 2, lost 50.
- Incorrect steps: added 4 (4 supported by their cited evidence — a disagreement with the answer, listed apart — and 0 unsupported); removed 0.
- Whole-case gained 0, lost 0. Status flips 4 (INCOMPLETE→COMPLETE 4).
- Support-tier moves: {'resolved→unresolved': 1, 'weak→unresolved': 1}.
  - `case_21` COMPLETE→COMPLETE support unresolved→unresolved: -audit_record_3737:VERIFY_RECORD_PRESENT +account_9155:VERIFY_RECORD_ABSENT
  - `case_23` INCOMPLETE→COMPLETE support unresolved→unresolved: -export_7364:REPORT_REMAINING_RECORD,search_898:REPORT_REMAINING_RECORD,export_7364:DELETE_RECORD,search_898:DELETE_RECORD,export_7364:VERIFY_RECORD_ABSENT,search_898:VERIFY_RECORD_ABSENT +account_410:VERIFY_RECORD_ABSENT
  - `case_24` INCOMPLETE→COMPLETE support resolved→unresolved: -account_5334:REPORT_REMAINING_RECORD,search_5577:REPORT_REMAINING_RECORD,account_5334:DELETE_RECORD,search_5577:DELETE_RECORD,account_5334:VERIFY_RECORD_ABSENT,search_5577:VERIFY_RECORD_ABSENT +∅
  - `case_25` COMPLETE→COMPLETE support unresolved→unresolved: -audit_record_451:VERIFY_RECORD_PRESENT +account_7225:VERIFY_RECORD_ABSENT
  - `case_26` COMPLETE→COMPLETE support unresolved→unresolved: -audit_record_5416:VERIFY_RECORD_PRESENT,support_4715:VERIFY_RECORD_REDACTED,data_flow_6244:VERIFY_DATA_FLOW_DISABLED,backup_3120:VERIFY_RESTORE_BLOCKED +account_5684:VERIFY_RECORD_ABSENT
  - `case_27` COMPLETE→COMPLETE support unresolved→unresolved: -audit_record_3830:VERIFY_RECORD_PRESENT,support_4707:VERIFY_RECORD_REDACTED,data_flow_2295:VERIFY_DATA_FLOW_DISABLED,backup_5970:VERIFY_RESTORE_BLOCKED +account_7012:VERIFY_RECORD_ABSENT
  - `case_28` COMPLETE→COMPLETE support unresolved→unresolved: -audit_record_9265:VERIFY_RECORD_PRESENT,support_2351:VERIFY_RECORD_REDACTED,data_flow_2337:VERIFY_DATA_FLOW_DISABLED,backup_838:VERIFY_RESTORE_BLOCKED +∅
  - `case_29` INCOMPLETE→COMPLETE support unresolved→unresolved: -search_1993:REPORT_REMAINING_RECORD,analytics_5208:REPORT_EXPOSED_PII,support_5281:REPORT_EXPOSED_PII,data_flow_3827:REPORT_ACTIVE_DATA_FLOW,data_flow_3827:DISABLE_DATA_FLOW,search_1993:DELETE_RECORD,support_5281:REDACT_RECORD,analytics_5208:ANONYMIZE_RECORD,search_1993:VERIFY_RECORD_ABSENT,support_5281:VERIFY_RECORD_REDACTED,analytics_5208:VERIFY_RECORD_ANONYMIZED,data_flow_3827:VERIFY_DATA_FLOW_DISABLED +account_3866:VERIFY_RECORD_ABSENT
  - `case_30` INCOMPLETE→COMPLETE support weak→unresolved: -search_9359:REPORT_REMAINING_RECORD,analytics_3697:REPORT_EXPOSED_PII,support_6477:REPORT_EXPOSED_PII,data_flow_8524:REPORT_ACTIVE_DATA_FLOW,data_flow_8524:DISABLE_DATA_FLOW,search_9359:DELETE_RECORD,support_6477:REDACT_RECORD,analytics_3697:ANONYMIZE_RECORD,search_9359:VERIFY_RECORD_ABSENT,support_6477:VERIFY_RECORD_REDACTED,analytics_3697:VERIFY_RECORD_ANONYMIZED,data_flow_8524:VERIFY_DATA_FLOW_DISABLED +∅

### clean_primary_dirty_replica (`runs/s7/c71/all-custom-clean_primary_dirty_replica` → `runs/s7/c71t/snap-custom-clean_primary_dirty_replica`)

| metric | baseline | candidate |
|---|---|---|
| status | 1/1 | 1/1 |
| whole-case | 1/1 | 1/1 |
| step precision | 3/3 | 3/3 |
| step recall | 3/3 | 3/3 |
| citation on matched | 3/3 | 3/3 |
| cited-evidence recall | 1/1 | 1/1 |
| sequence | 1/1 | 1/1 |
| step F1 | 1.0000 | 1.0000 |

- Correct steps: kept 3, gained 0, lost 0.
- Incorrect steps: added 0 (0 supported by their cited evidence — a disagreement with the answer, listed apart — and 0 unsupported); removed 0.
- Whole-case gained 0, lost 0. Status flips 0 (INCOMPLETE→COMPLETE 0).
- Support-tier moves: none.

### historical_email_replica (`runs/s7/c71/all-custom-historical_email_replica` → `runs/s7/c71t/snap-custom-historical_email_replica`)

| metric | baseline | candidate |
|---|---|---|
| status | 1/1 | 1/1 |
| whole-case | 1/1 | 1/1 |
| step precision | 3/3 | 3/3 |
| step recall | 3/3 | 3/3 |
| citation on matched | 3/3 | 3/3 |
| cited-evidence recall | 1/1 | 1/1 |
| sequence | 1/1 | 1/1 |
| step F1 | 1.0000 | 1.0000 |

- Correct steps: kept 3, gained 0, lost 0.
- Incorrect steps: added 0 (0 supported by their cited evidence — a disagreement with the answer, listed apart — and 0 unsupported); removed 0.
- Whole-case gained 0, lost 0. Status flips 0 (INCOMPLETE→COMPLETE 0).
- Support-tier moves: none.

### post_cutoff_evidence_ignored (`runs/s7/c71/all-custom-post_cutoff_evidence_ignored` → `runs/s7/c71t/snap-custom-post_cutoff_evidence_ignored`)

| metric | baseline | candidate |
|---|---|---|
| status | 1/1 | 1/1 |
| whole-case | 1/1 | 1/1 |
| step precision | 3/3 | 3/3 |
| step recall | 3/3 | 3/3 |
| citation on matched | 3/3 | 3/3 |
| cited-evidence recall | 3/3 | 3/3 |
| sequence | 1/1 | 1/1 |
| step F1 | 1.0000 | 1.0000 |

- Correct steps: kept 3, gained 0, lost 0.
- Incorrect steps: added 0 (0 supported by their cited evidence — a disagreement with the answer, listed apart — and 0 unsupported); removed 0.
- Whole-case gained 0, lost 0. Status flips 0 (INCOMPLETE→COMPLETE 0).
- Support-tier moves: none.

### success_claim_contradicted (`runs/s7/c71/all-custom-success_claim_contradicted` → `runs/s7/c71t/snap-custom-success_claim_contradicted`)

| metric | baseline | candidate |
|---|---|---|
| status | 1/1 | 1/1 |
| whole-case | 1/1 | 1/1 |
| step precision | 3/3 | 3/3 |
| step recall | 3/3 | 3/3 |
| citation on matched | 3/3 | 3/3 |
| cited-evidence recall | 1/1 | 1/1 |
| sequence | 1/1 | 1/1 |
| step F1 | 1.0000 | 1.0000 |

- Correct steps: kept 3, gained 0, lost 0.
- Incorrect steps: added 0 (0 supported by their cited evidence — a disagreement with the answer, listed apart — and 0 unsupported); removed 0.
- Whole-case gained 0, lost 0. Status flips 0 (INCOMPLETE→COMPLETE 0).
- Support-tier moves: none.

### tombstone_pair (`runs/s7/c71/all-custom-tombstone_pair` → `runs/s7/c71t/snap-custom-tombstone_pair`)

| metric | baseline | candidate |
|---|---|---|
| status | 1/1 | 1/1 |
| whole-case | 1/1 | 1/1 |
| step precision | 3/3 | 3/3 |
| step recall | 3/3 | 3/3 |
| citation on matched | 3/3 | 3/3 |
| cited-evidence recall | 1/1 | 1/1 |
| sequence | 1/1 | 1/1 |
| step F1 | 1.0000 | 1.0000 |

- Correct steps: kept 3, gained 0, lost 0.
- Incorrect steps: added 0 (0 supported by their cited evidence — a disagreement with the answer, listed apart — and 0 unsupported); removed 0.
- Whole-case gained 0, lost 0. Status flips 0 (INCOMPLETE→COMPLETE 0).
- Support-tier moves: none.

### Row contribution (`runs/s7/c71t/manifest-targets` → `runs/s7/c71t/snap-targets`)

- Rows that differ: 86 of 518: case_123, case_124, case_125, case_128, case_129, case_130, case_131, case_132, case_173, case_174, case_176, case_177, case_179, case_180, case_181, case_182, case_223, case_224, case_225, case_226
- Support moves: {'resolved→unresolved': 24, 'weak→unresolved': 5}.

### Mismatch causes (samples)

| cause | baseline | candidate |
|---|---|---|
| citation | 0 | 2 |
| identity/resource association | 24 | 26 |
| no supporting fact found | 3 | 3 |
| temporal state | 5 | 1 |
| temporal state (state) | 0 | 54 |
| undetermined | 0 | 4 |
| **total** | 32 | 90 |
