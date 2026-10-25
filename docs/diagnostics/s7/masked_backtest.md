# Masked-identity backtest of the workflow-account mechanisms (C7.1)

Population: 177 requests whose account is fixed by explicit admissible evidence at their own cutoff (12 samples, 165 targets). The truth mapping exists only in this script.

**Control:** PASSED: no masked request is solved by explicit_account and no truth account stays linked at the explicit tier, in either variant.

## Variant 1: each request masked together with every request competing for its feasible rows

Truth account still feasible after masking: 177/177.

### Solver, by mechanism

| mechanism | correct | incorrect | abstain | n |
|---|---|---|---|---|
| forced_matching | 1 | 1 | 0 | 2 |
| only_feasible_request | 0 | 1 | 0 | 1 |
| only_feasible_row | 4 | 0 | 0 | 4 |
| only_feasible_row (intake row) | 0 | 0 | 1 | 1 |
| unassigned | 0 | 0 | 169 | 169 |

Totals: correct 5, incorrect 2, abstain 170 of 177.

### Nearest-anchor fallback on the solver's abstentions, by candidate count

| candidates | correct | incorrect | abstain | n |
|---|---|---|---|---|
| 1 | 0 | 0 | 1 | 1 |
| 2 | 6 | 2 | 0 | 8 |
| 3 | 11 | 7 | 0 | 18 |
| 4-6 | 24 | 67 | 0 | 91 |
| 7-10 | 5 | 36 | 0 | 41 |
| >10 | 2 | 8 | 1 | 11 |

Fallback totals: correct 48, incorrect 120, no pick 2.

### Solver, by feasible-candidate count

| candidates | correct | incorrect | abstain | n |
|---|---|---|---|---|
| 1 | 4 | 0 | 1 | 5 |
| 2 | 0 | 0 | 8 | 8 |
| 3 | 0 | 0 | 18 | 18 |
| 4-6 | 1 | 0 | 91 | 92 |
| 7-10 | 0 | 2 | 41 | 43 |
| >10 | 0 | 0 | 11 | 11 |

### Solver, by masked cohort size

| masked together | correct | incorrect | abstain | n |
|---|---|---|---|---|
| 1 | 4 | 0 | 12 | 16 |
| 2 | 0 | 1 | 24 | 25 |
| 3 | 1 | 0 | 47 | 48 |
| 4-6 | 0 | 0 | 75 | 75 |
| 7-10 | 0 | 1 | 12 | 13 |

## Variant 2: every connected cohort of overlapping windows masked at once

Cohorts: 3 (sizes [1, 1, 548]).
Truth account still feasible after masking: 177/177.

### Solver, by mechanism

| mechanism | correct | incorrect | abstain | n |
|---|---|---|---|---|
| forced_matching | 0 | 1 | 0 | 1 |
| only_feasible_request | 0 | 1 | 0 | 1 |
| only_feasible_row | 4 | 0 | 0 | 4 |
| only_feasible_row (intake row) | 0 | 0 | 1 | 1 |
| unassigned | 0 | 0 | 170 | 170 |

Totals: correct 4, incorrect 2, abstain 171 of 177.

### Nearest-anchor fallback on the solver's abstentions, by candidate count

| candidates | correct | incorrect | abstain | n |
|---|---|---|---|---|
| 1 | 0 | 0 | 1 | 1 |
| 2 | 6 | 2 | 0 | 8 |
| 3 | 11 | 7 | 0 | 18 |
| 4-6 | 25 | 67 | 0 | 92 |
| 7-10 | 4 | 37 | 0 | 41 |
| >10 | 2 | 8 | 1 | 11 |

Fallback totals: correct 48, incorrect 121, no pick 2.

### Solver, by feasible-candidate count

| candidates | correct | incorrect | abstain | n |
|---|---|---|---|---|
| 1 | 4 | 0 | 1 | 5 |
| 2 | 0 | 0 | 8 | 8 |
| 3 | 0 | 0 | 18 | 18 |
| 4-6 | 0 | 0 | 92 | 92 |
| 7-10 | 0 | 2 | 41 | 43 |
| >10 | 0 | 0 | 11 | 11 |

### Solver, by masked cohort size

| masked together | correct | incorrect | abstain | n |
|---|---|---|---|---|
| 1 | 1 | 0 | 0 | 1 |
| >10 | 3 | 2 | 171 | 176 |

## Reference only (artificially easy, not evidence): one request masked at a time, neighbours visible

Truth account still feasible after masking: 177/177.

### Solver, by mechanism

| mechanism | correct | incorrect | abstain | n |
|---|---|---|---|---|
| forced_matching | 9 | 0 | 0 | 9 |
| only_feasible_request | 1 | 3 | 0 | 4 |
| only_feasible_row | 18 | 0 | 0 | 18 |
| only_feasible_row (intake row) | 0 | 0 | 1 | 1 |
| unassigned | 0 | 0 | 145 | 145 |

Totals: correct 28, incorrect 3, abstain 146 of 177.

### Nearest-anchor fallback on the solver's abstentions, by candidate count

| candidates | correct | incorrect | abstain | n |
|---|---|---|---|---|
| 1 | 0 | 0 | 1 | 1 |
| 2 | 3 | 0 | 0 | 3 |
| 3 | 5 | 4 | 0 | 9 |
| 4-6 | 23 | 63 | 0 | 86 |
| 7-10 | 5 | 32 | 0 | 37 |
| >10 | 2 | 7 | 1 | 10 |

Fallback totals: correct 38, incorrect 106, no pick 2.

### Solver, by feasible-candidate count

| candidates | correct | incorrect | abstain | n |
|---|---|---|---|---|
| 1 | 4 | 0 | 1 | 5 |
| 2 | 5 | 0 | 3 | 8 |
| 3 | 9 | 0 | 9 | 18 |
| 4-6 | 5 | 1 | 86 | 92 |
| 7-10 | 5 | 1 | 37 | 43 |
| >10 | 0 | 1 | 10 | 11 |

### Solver, by masked cohort size

| masked together | correct | incorrect | abstain | n |
|---|---|---|---|---|
| 1 | 28 | 3 | 146 | 177 |

## The legacy links (unmasked), for comparison

| case | mechanism | feasible rows |
|---|---|---|
| case_02 | only_feasible_row | 1 |
| case_101 | only_feasible_row | 1 |
| case_161 | only_feasible_row | 1 |
| case_200 | only_feasible_row | 2 |
| case_221 | only_feasible_row | 1 |
| case_234 | only_feasible_row | 3 |
| case_236 | only_feasible_row | 3 |
| case_253 | only_feasible_row | 5 |
| case_260 | only_feasible_row | 2 |
| case_281 | only_feasible_row | 1 |
| case_30 | only_feasible_row | 4 |
| case_341 | only_feasible_row | 1 |
| case_373 | only_feasible_row | 4 |
| case_376 | only_feasible_request | 5 |
| case_377 | only_feasible_row | 3 |
| case_401 | only_feasible_row | 1 |
| case_461 | only_feasible_row | 1 |
| case_500 | only_feasible_row | 2 |
| case_78 | forced_matching | 7 |
| case_94 | forced_matching | 5 |

## Reading

- Selection bias: these accounts were identifiable, so their windows and neighbours may differ from the genuinely anonymous accounts the legacy links concern. This is supporting evidence about the mechanisms, **not** hidden-target accuracy.
- Only existing mechanisms were run; no cadence, status or guess rule was added.
- The nearest-anchor fallback row is what the strict→scored fallback would pick on the solver's abstentions; the engine uses it only when a row would otherwise have no steps.
