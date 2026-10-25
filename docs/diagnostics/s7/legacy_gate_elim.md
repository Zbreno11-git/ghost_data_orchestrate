# S6 accuracy gate

Full official denominators. The 32 public samples have been inspected since S0: they measure regressions, they are not a held-out estimate of hidden-target accuracy. Custom cases were specified independently of the engine (A13).

### samples (`runs/s7/c71/all-samples` → `runs/s7/c71/elim-samples`)

| metric | baseline | candidate |
|---|---|---|
| status | 32/32 | 32/32 |
| whole-case | 12/32 | 11/32 |
| step precision | 162/163 | 161/161 |
| step recall | 162/193 | 161/193 |
| citation on matched | 162/162 | 161/161 |
| cited-evidence recall | 61/75 | 60/75 |
| sequence | 12/32 | 11/32 |
| step F1 | 0.9101 | 0.9096 |

- Correct steps: kept 161, gained 0, lost 1.
- Incorrect steps: added 0 (0 supported by their cited evidence — a disagreement with the answer, listed apart — and 0 unsupported); removed 1.
- Whole-case gained 0, lost 1. Status flips 0 (INCOMPLETE→COMPLETE 0).
- Support-tier moves: {'weak→unresolved': 2}.
  - `case_01` COMPLETE→COMPLETE support weak→unresolved: -account_001:VERIFY_RECORD_ABSENT +∅
  - `case_04` COMPLETE→COMPLETE support weak→unresolved: -∅ +∅

### clean_primary_dirty_replica (`runs/s7/c71/all-custom-clean_primary_dirty_replica` → `runs/s7/c71/elim-custom-clean_primary_dirty_replica`)

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

### historical_email_replica (`runs/s7/c71/all-custom-historical_email_replica` → `runs/s7/c71/elim-custom-historical_email_replica`)

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

### post_cutoff_evidence_ignored (`runs/s7/c71/all-custom-post_cutoff_evidence_ignored` → `runs/s7/c71/elim-custom-post_cutoff_evidence_ignored`)

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

### success_claim_contradicted (`runs/s7/c71/all-custom-success_claim_contradicted` → `runs/s7/c71/elim-custom-success_claim_contradicted`)

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

### tombstone_pair (`runs/s7/c71/all-custom-tombstone_pair` → `runs/s7/c71/elim-custom-tombstone_pair`)

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

### Row contribution (`runs/s7/c71/all-targets` → `runs/s7/c71/elim-targets`)

- Rows that differ: 2 of 518: case_376, case_63
- Support moves: {'weak→unresolved': 1}.

