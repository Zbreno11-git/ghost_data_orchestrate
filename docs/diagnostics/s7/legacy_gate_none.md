# S6 accuracy gate

Full official denominators. The 32 public samples have been inspected since S0: they measure regressions, they are not a held-out estimate of hidden-target accuracy. Custom cases were specified independently of the engine (A13).

### samples (`runs/s7/c71/all-samples` → `runs/s7/c71/none-samples`)

| metric | baseline | candidate |
|---|---|---|
| status | 32/32 | 32/32 |
| whole-case | 12/32 | 10/32 |
| step precision | 162/163 | 159/159 |
| step recall | 162/193 | 159/193 |
| citation on matched | 162/162 | 159/159 |
| cited-evidence recall | 61/75 | 59/75 |
| sequence | 12/32 | 10/32 |
| step F1 | 0.9101 | 0.9034 |

- Correct steps: kept 159, gained 0, lost 3.
- Incorrect steps: added 0 (0 supported by their cited evidence — a disagreement with the answer, listed apart — and 0 unsupported); removed 1.
- Whole-case gained 0, lost 2. Status flips 0 (INCOMPLETE→COMPLETE 0).
- Support-tier moves: {'weak→unresolved': 4}.
  - `case_01` COMPLETE→COMPLETE support weak→unresolved: -account_001:VERIFY_RECORD_ABSENT +∅
  - `case_02` COMPLETE→COMPLETE support weak→unresolved: -account_002:VERIFY_RECORD_ABSENT +∅
  - `case_04` COMPLETE→COMPLETE support weak→unresolved: -∅ +∅
  - `case_30` INCOMPLETE→INCOMPLETE support weak→unresolved: -account_4163:VERIFY_RECORD_ABSENT +∅

### clean_primary_dirty_replica (`runs/s7/c71/all-custom-clean_primary_dirty_replica` → `runs/s7/c71/none-custom-clean_primary_dirty_replica`)

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

### historical_email_replica (`runs/s7/c71/all-custom-historical_email_replica` → `runs/s7/c71/none-custom-historical_email_replica`)

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

### post_cutoff_evidence_ignored (`runs/s7/c71/all-custom-post_cutoff_evidence_ignored` → `runs/s7/c71/none-custom-post_cutoff_evidence_ignored`)

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

### success_claim_contradicted (`runs/s7/c71/all-custom-success_claim_contradicted` → `runs/s7/c71/none-custom-success_claim_contradicted`)

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

### tombstone_pair (`runs/s7/c71/all-custom-tombstone_pair` → `runs/s7/c71/none-custom-tombstone_pair`)

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

### Row contribution (`runs/s7/c71/all-targets` → `runs/s7/c71/none-targets`)

- Rows that differ: 19 of 518: case_101, case_161, case_200, case_221, case_234, case_236, case_253, case_260, case_281, case_341, case_373, case_376, case_377, case_401, case_461, case_500, case_63, case_78, case_94
- Support moves: {'weak→unresolved': 18}.

