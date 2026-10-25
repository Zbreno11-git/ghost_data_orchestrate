# Extraction coverage audit (C6.1)

Run `runs/s6/base-samples`; 32 mismatches. Decoders: raw (txt/json/sql/log/csv), pypdf + pdftotext (PDF), cached vision extracts (PNG). Undecodable sources: none.

| case | kind | step | diagnose cause | extraction verdict | sources (lines naming it / observations naming it / tokens on those lines not in any observation; * = cited by the answer) |
|---|---|---|---|---|---|
| case_03 | missing | `VERIFY_RECORD_ANONYMIZED analytics_9406` | identity/resource association | extracted | activity_3852 1/1; *evidence_94 2/1 |
| case_04 | missing | `VERIFY_RECORD_ABSENT account_004` | no supporting fact found | no supporting fact found after documented checks | *evidence_54 0/0 |
| case_04 | missing | `VERIFY_RECORD_ANONYMIZED analytics_901` | identity/resource association | extracted | activity_3463 1/1; *evidence_56 1/1 |
| case_04 | extra | `VERIFY_RECORD_ABSENT account_3865` | identity/resource association | extracted | activity_3443 1/1 |
| case_07 | missing | `VERIFY_RECORD_ABSENT account_007` | identity/resource association | extracted | activity_3590 1/1 |
| case_08 | missing | `VERIFY_RECORD_ABSENT account_008` | identity/resource association | extracted | activity_3554 1/1 |
| case_09 | missing | `VERIFY_RECORD_ABSENT account_3960` | identity/resource association | extracted | activity_3703 1/1; evidence_06 1/1 |
| case_09 | missing | `VERIFY_RECORD_PRESENT audit_record_4902` | temporal state | extracted | evidence_06 1/1 |
| case_10 | missing | `VERIFY_RECORD_ABSENT account_010` | identity/resource association | extracted | activity_3595 1/1 |
| case_18 | missing | `VERIFY_RECORD_ABSENT account_5521` | identity/resource association | extracted | activity_3732 1/1 |
| case_18 | missing | `VERIFY_RECORD_PRESENT audit_record_6645` | no supporting fact found | no supporting fact found after documented checks | — |
| case_20 | missing | `VERIFY_RECORD_ABSENT account_5037` | identity/resource association | extracted | activity_3734 1/1 |
| case_20 | missing | `VERIFY_RECORD_PRESENT audit_record_5569` | no supporting fact found | no supporting fact found after documented checks | — |
| case_21 | missing | `VERIFY_RECORD_ABSENT account_6440` | identity/resource association | extracted | activity_3661 1/1; *evidence_92 1/1 |
| case_21 | missing | `VERIFY_RECORD_ANONYMIZED analytics_5335` | identity/resource association | extracted | activity_3665 1/1; evidence_02 1/1; *evidence_92 1/1 |
| case_22 | missing | `VERIFY_RECORD_ABSENT account_4990` | identity/resource association | extracted | activity_3573 1/1 |
| case_23 | missing | `VERIFY_RECORD_ABSENT account_410` | identity/resource association | extracted | activity_3662 1/1 |
| case_23 | missing | `VERIFY_RECORD_PRESENT audit_record_4128` | temporal state | extracted | evidence_02 1/1 |
| case_24 | missing | `VERIFY_RECORD_PRESENT audit_record_7095` | temporal state | extracted | evidence_02 1/1 |
| case_25 | missing | `VERIFY_RECORD_ABSENT account_3136` | identity/resource association | extracted | activity_3597 1/1; *evidence_92 1/1 |
| case_25 | missing | `VERIFY_RECORD_ANONYMIZED analytics_1895` | identity/resource association | extracted | activity_3602 1/1; evidence_02 1/1; *evidence_92 1/1 |
| case_26 | missing | `VERIFY_RECORD_ABSENT account_5684` | identity/resource association | extracted | activity_3600 1/1; evidence_02 1/1; *evidence_92 1/1 |
| case_26 | missing | `VERIFY_RECORD_ANONYMIZED analytics_4566` | identity/resource association | extracted | activity_3603 1/1; evidence_02 1/1; *evidence_92 1/1 |
| case_27 | missing | `VERIFY_RECORD_ABSENT account_3866` | identity/resource association | extracted | activity_3530 1/1; evidence_02 1/1; *evidence_92 1/1 |
| case_27 | missing | `VERIFY_RECORD_ANONYMIZED analytics_4574` | identity/resource association | extracted | activity_3533 1/1; evidence_02 1/1; *evidence_92 1/1 |
| case_28 | missing | `VERIFY_RECORD_ABSENT account_5482` | identity/resource association | extracted | activity_3529 1/1; *evidence_92 1/1 |
| case_28 | missing | `VERIFY_RECORD_ANONYMIZED analytics_6077` | identity/resource association | extracted | activity_3534 1/1; evidence_02 1/1; *evidence_92 1/1 |
| case_29 | missing | `VERIFY_RECORD_ABSENT account_7012` | identity/resource association | extracted | activity_3532 1/1 |
| case_29 | missing | `VERIFY_RECORD_PRESENT audit_record_3954` | temporal state | extracted | evidence_02 1/1 |
| case_30 | missing | `VERIFY_RECORD_PRESENT audit_record_1707` | temporal state | extracted | evidence_02 1/1 |
| case_31 | missing | `VERIFY_RECORD_ABSENT account_4857` | identity/resource association | extracted | activity_3682 1/1; *evidence_51 0/0 |
| case_32 | missing | `VERIFY_RECORD_ABSENT account_8858` | identity/resource association | extracted | activity_3685 1/1 |

Checks behind "no supporting fact found": the id searched as a whole word in every decoded source (all decoders), in the activity and audit CSVs, and in the extracted store; screenshots additionally need the visual read recorded in session-06.md.
