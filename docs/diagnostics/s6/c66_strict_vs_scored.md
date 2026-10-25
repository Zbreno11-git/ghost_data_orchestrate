# S6 accuracy gate

Full official denominators. The 32 public samples have been inspected since S0: they measure regressions, they are not a held-out estimate of hidden-target accuracy. Custom cases were specified independently of the engine (A13).

### samples (`runs/s6/c66strict-samples` → `runs/s6/scored-samples`)

| metric | baseline | candidate |
|---|---|---|
| status | 32/32 | 32/32 |
| whole-case | 12/32 | 14/32 |
| step precision | 162/163 | 167/181 |
| step recall | 162/193 | 167/193 |
| citation on matched | 162/162 | 167/167 |
| cited-evidence recall | 61/75 | 62/75 |
| sequence | 12/32 | 14/32 |
| step F1 | 0.9101 | 0.8930 |

- Correct steps: kept 162, gained 5, lost 0.
- Incorrect steps: added 13 (7 supported by their cited evidence — a disagreement with the answer, listed apart — and 6 unsupported); removed 0.
- Whole-case gained 3, lost 1. Status flips 0 (INCOMPLETE→COMPLETE 0).
- Support-tier moves: {'resolved→weak': 3, 'unresolved→weak': 14, 'resolved→unresolved': 1}.
  - `case_07` INCOMPLETE→INCOMPLETE support unresolved→unresolved: -∅ +account_007:VERIFY_RECORD_ABSENT
  - `case_08` INCOMPLETE→INCOMPLETE support unresolved→weak: -∅ +account_008:VERIFY_RECORD_ABSENT
  - `case_09` INCOMPLETE→INCOMPLETE support unresolved→weak: -∅ +account_565:VERIFY_RECORD_ABSENT
  - `case_10` INCOMPLETE→INCOMPLETE support unresolved→weak: -∅ +account_010:VERIFY_RECORD_ABSENT
  - `case_18` INCOMPLETE→INCOMPLETE support unresolved→weak: -∅ +account_5193:VERIFY_RECORD_ABSENT
  - `case_19` INCOMPLETE→INCOMPLETE support resolved→weak: -∅ +analytics_3264:REPORT_EXPOSED_PII,analytics_3264:ANONYMIZE_RECORD,analytics_3264:VERIFY_RECORD_ANONYMIZED
  - `case_20` INCOMPLETE→INCOMPLETE support unresolved→weak: -∅ +account_9335:VERIFY_RECORD_ABSENT
  - `case_21` COMPLETE→COMPLETE support unresolved→weak: -∅ +account_9155:VERIFY_RECORD_ABSENT
  - `case_22` INCOMPLETE→INCOMPLETE support unresolved→weak: -∅ +account_902:VERIFY_RECORD_ABSENT
  - `case_23` INCOMPLETE→INCOMPLETE support unresolved→weak: -∅ +account_410:VERIFY_RECORD_ABSENT
  - `case_25` COMPLETE→COMPLETE support unresolved→weak: -∅ +account_7225:VERIFY_RECORD_ABSENT
  - `case_26` COMPLETE→COMPLETE support unresolved→weak: -∅ +account_5684:VERIFY_RECORD_ABSENT
  - `case_27` COMPLETE→COMPLETE support unresolved→weak: -∅ +account_7012:VERIFY_RECORD_ABSENT
  - `case_29` INCOMPLETE→INCOMPLETE support unresolved→weak: -∅ +account_3866:VERIFY_RECORD_ABSENT
  - `case_31` COMPLETE→COMPLETE support unresolved→weak: -∅ +account_8858:VERIFY_RECORD_ABSENT
  - `case_32` INCOMPLETE→INCOMPLETE support unresolved→weak: -∅ +account_1810:VERIFY_RECORD_ABSENT

### historical_email_replica (`runs/s6/c66strict-custom-historical_email_replica` → `runs/s6/scored-custom-historical_email_replica`)

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

### post_cutoff_evidence_ignored (`runs/s6/c66strict-custom-post_cutoff_evidence_ignored` → `runs/s6/scored-custom-post_cutoff_evidence_ignored`)

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

### success_claim_contradicted (`runs/s6/c66strict-custom-success_claim_contradicted` → `runs/s6/scored-custom-success_claim_contradicted`)

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

### Deterministic vs agent (`runs/s6/c66strict-targets` → `runs/s6/scored-targets`)

- Rows changed by the agent: 331 of 518: case_100, case_102, case_103, case_104, case_106, case_107, case_108, case_109, case_110, case_111, case_112, case_114, case_116, case_117, case_118, case_119, case_120, case_122, case_123, case_124
- Support moves: {'unresolved→weak': 309, 'resolved→weak': 71}.

### Mismatch causes (samples)

| cause | baseline | candidate |
|---|---|---|
| identity/resource association | 24 | 32 |
| no supporting fact found | 3 | 3 |
| temporal state | 5 | 5 |
| **total** | 32 | 40 |
