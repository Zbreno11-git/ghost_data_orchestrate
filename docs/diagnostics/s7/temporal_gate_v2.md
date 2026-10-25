# S6 accuracy gate

Full official denominators. The 32 public samples have been inspected since S0: they measure regressions, they are not a held-out estimate of hidden-target accuracy. Custom cases were specified independently of the engine (A13).

### samples (`runs/s7/c71t/manifest2-samples` → `runs/s7/c71t/snap2-samples`)

| metric | baseline | candidate |
|---|---|---|
| status | 32/32 | 32/32 |
| whole-case | 12/32 | 14/32 |
| step precision | 162/163 | 167/168 |
| step recall | 162/193 | 167/193 |
| citation on matched | 162/162 | 167/167 |
| cited-evidence recall | 61/75 | 62/75 |
| sequence | 12/32 | 14/32 |
| step F1 | 0.9101 | 0.9252 |

- Correct steps: kept 162, gained 5, lost 0.
- Incorrect steps: added 0 (0 supported by their cited evidence — a disagreement with the answer, listed apart — and 0 unsupported); removed 0.
- Whole-case gained 2, lost 0. Status flips 0 (INCOMPLETE→COMPLETE 0).
- Support-tier moves: {'resolved→unresolved': 1, 'unresolved→resolved': 1, 'weak→unresolved': 1}.
  - `case_23` INCOMPLETE→INCOMPLETE support unresolved→unresolved: -∅ +audit_record_4128:VERIFY_RECORD_PRESENT
  - `case_24` INCOMPLETE→INCOMPLETE support resolved→unresolved: -∅ +audit_record_7095:VERIFY_RECORD_PRESENT
  - `case_26` COMPLETE→COMPLETE support unresolved→resolved: -∅ +account_5684:VERIFY_RECORD_ABSENT
  - `case_29` INCOMPLETE→INCOMPLETE support unresolved→unresolved: -∅ +audit_record_3954:VERIFY_RECORD_PRESENT
  - `case_30` INCOMPLETE→INCOMPLETE support weak→unresolved: -∅ +audit_record_1707:VERIFY_RECORD_PRESENT

### clean_primary_dirty_replica (`runs/s7/c71/all-custom-clean_primary_dirty_replica` → `runs/s7/c71t/snap2-custom-clean_primary_dirty_replica`)

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

### historical_email_replica (`runs/s7/c71/all-custom-historical_email_replica` → `runs/s7/c71t/snap2-custom-historical_email_replica`)

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

### post_cutoff_evidence_ignored (`runs/s7/c71/all-custom-post_cutoff_evidence_ignored` → `runs/s7/c71t/snap2-custom-post_cutoff_evidence_ignored`)

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

### success_claim_contradicted (`runs/s7/c71/all-custom-success_claim_contradicted` → `runs/s7/c71t/snap2-custom-success_claim_contradicted`)

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

### tombstone_pair (`runs/s7/c71/all-custom-tombstone_pair` → `runs/s7/c71t/snap2-custom-tombstone_pair`)

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

### Row contribution (`runs/s7/c71t/manifest2-targets` → `runs/s7/c71t/snap2-targets`)

- Rows that differ: 59 of 518: case_123, case_124, case_125, case_128, case_129, case_130, case_131, case_132, case_173, case_174, case_176, case_177, case_179, case_180, case_181, case_182, case_223, case_224, case_227, case_228
- Support moves: {'resolved→unresolved': 9, 'weak→unresolved': 5, 'unresolved→resolved': 1}.

### Mismatch causes (samples)

| cause | baseline | candidate |
|---|---|---|
| identity/resource association | 24 | 23 |
| no supporting fact found | 3 | 3 |
| temporal state | 5 | 1 |
| **total** | 32 | 27 |
