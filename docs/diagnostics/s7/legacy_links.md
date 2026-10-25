# C7.1: legacy workflow-account links, measured (2026-10-25 ~03:00 UTC)

Everything below is deterministic ($0), from `runs/s7/c71/*`, on the S7 code. The default configuration (all
mechanisms asserted) reproduces `runs/s6/c66strict-*` byte for byte, so the comparison starts from the published
release. Full gate reports: `legacy_gate_none.md`, `legacy_gate_elim.md`; backtest: `masked_backtest.md`.

## What the legacy links are (reconciled against the final agent run `runs/s6/final`)

| | targets | samples |
|---|---|---|
| rows whose published steps use a workflow-tier account | 19 | 4 |
| by `only_feasible_row` | 15 | 2 (case_02, case_30) |
| by `forced_matching` | 2 (case_78, case_94) | 0 |
| by `only_feasible_request` | 1 (case_376) | 0 |
| by the strict→scored **nearest-anchor fallback** | 1 (case_63, 752 min) | 2 (case_01 0 min, case_04 1447 min) |
| changed by the agent (`account_source`) | 0 | 0 |
| A29 heuristic rows among them | 0 | 0 |
| sample answer agrees | — | 3 of 4 (case_04's account_3865 is the extra) |

Each such account contributes exactly one asserted step (`VERIFY_RECORD_ABSENT` or a finding with its remediation
and verification). **The CSV schema has no confidence field: in the submission, a "weak" account is an asserted
step like any other.**

## How reliable the mechanisms are: masked-identity backtest

177 requests whose account is proven by explicit admissible evidence had that evidence hidden, cohort by cohort,
and the existing mechanisms were re-run. Control passed: no hidden account remained reachable by the explicit path.

| mechanism | cohort-masked (competitors together) | one at a time (artificially easy, reference only) |
|---|---|---|
| only_feasible_row | **4 / 4 correct** | 18 / 18 |
| forced_matching | 1 correct, 1 wrong | 9 / 9 |
| only_feasible_request | 0 correct, 1 wrong | 1 correct, 3 wrong |
| nearest-anchor fallback (on abstentions) | **48 correct, 120 wrong** | 38 correct, 106 wrong |
| solver abstains | 170 of 177 | 146 of 177 |

Reading:
- The solver mostly **abstains**, and that is its honest behaviour.
- When it does assert by `only_feasible_row`, it was right every time measured (22/22 across both variants).
- `forced_matching` was right 10 of 11.
- `only_feasible_request` was right 1 of 5.
- The nearest-anchor fallback was right ≈29% of the time.
- **Selection bias:** these accounts were identifiable, and the genuinely anonymous accounts may sit in different
  windows. This is supporting evidence about the mechanisms, not hidden-target accuracy.

## The concrete alternatives

| | A: assert all (current release) | B: assert none | C: assert only `only_feasible_row` + `forced_matching` (+ `corroborated_run`, unused) |
|---|---|---|---|
| sample status | 32/32 | 32/32 | 32/32 |
| sample whole-case | 12/32 | 10/32 | 11/32 |
| sample step P | 162/163 | 159/159 | 161/161 |
| sample step R | 162/193 | 159/193 | 161/193 |
| sample step F1 | 0.9101 | 0.9034 | 0.9096 |
| cited-evidence recall | 61/75 | 59/75 | 60/75 |
| sequence | 12/32 | 10/32 | 11/32 |
| correct / incorrect sample steps removed | — | 3 / 1 | 1 / 1 |
| target rows changed | — | 19 | 2 (case_376, case_63) |
| target status flips | — | 0 | 0 |
| target support moves | — | weak→unresolved 18 | weak→unresolved 1 |
| **structurally invalid rows** (validator) | 0 | samples 3, **targets 1** | samples 2, **targets 1** |

**The A29 interaction, shown explicitly:**
- Under B and C, case_63 (targets) and case_01 / case_04 (samples, plus case_02 under B) lose their only step.
- The A29 heuristic path runs and finds no screen rule that applies, so they become `DECIDED_EMPTY`: an empty
  COMPLETE, which the validator rejects.
- We do not invent a replacement finding to make them valid.
- Keeping these rows valid needs the nearest-anchor pick, whose measured accuracy is ≈29%, or an empty COMPLETE
  that the contract does not support.

## Evidence quality

All of the legacy links come from **timing windows plus the one-to-one assignment**. One worker account row per
authorized request was measured (539 rows for 540 requests, 2026-10-24). None comes from a record naming the
person. Breno's S6 rule forbids *new* links of this kind; these predate it.

| mechanism | basis |
|---|---|
| `only_feasible_row` | The single row in the request's window, after rows that explicit evidence ties to other requests are removed. Most consistent in the backtest. |
| `forced_matching` | The pair present in every maximum one-to-one matching. Consistent unless a neighbour's account is itself unknown. |
| `only_feasible_request` | A row that only this request could still claim. In the backtest it failed 4 of 5 times. |
| nearest-anchor fallback | The closest row to `reported_at`. A ranking, not a deduction. Wrong about 7 times in 10 in the backtest. |

## What the agent adds

Nothing changes here. The agent's account choice needs a cited lineage to the subject (A27), so it cannot
re-assert a workflow-only account; changing the account without one is rejected. All 19 rows are already in its
scope (weak/unresolved). The agent pass runs once, on the chosen configuration, in C7.4.
