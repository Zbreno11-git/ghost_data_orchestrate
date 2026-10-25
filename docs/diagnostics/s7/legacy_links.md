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

## How reliable the mechanisms are: masked-identity backtest (corrected 2026-10-25 03:38 UTC, after Breno's review)

177 requests whose account is proven by explicit admissible evidence had that evidence hidden, and the existing
mechanisms were re-run. Control passed in every variant: no hidden account stayed reachable by the explicit path.
**The three variants are repeated runs over the same 177 requests, not independent observations. Their counts
must not be added or pooled.** Only the two cohort variants test the mechanisms; the one-at-a-time variant leaves
every neighbour's explicit account visible, which makes elimination artificially easy, and is a reference only.

| mechanism | Variant 1 (strict): request + its competitors masked | Variant 2 (strict): whole connected cohort masked | reference only: one request masked at a time |
|---|---|---|---|
| only_feasible_row | 4 correct / 4, **all four from windows with a single feasible row** | 4 / 4, the same four | 18 / 18 (4 single-row, 14 by elimination) |
| forced_matching | **1 correct, 1 wrong** (n = 2) | **0 correct, 1 wrong** (n = 1) | 9 / 9 |
| only_feasible_request | 0 correct, 1 wrong | 0 correct, 1 wrong | 1 correct, 3 wrong |
| nearest-anchor fallback (on abstentions) | 48 correct, 120 wrong | 48 correct, 121 wrong | 38 correct, 106 wrong |
| solver abstains | 170 / 177 | 171 / 177 | 146 / 177 |

What the strict variants support, and what they do not:
- **Window-unique `only_feasible_row`** (one feasible row in the window): 4 / 4, a small n.
- **Elimination-based `only_feasible_row`** (several rows, the others taken by neighbours' explicit accounts):
  **never exercised by the strict variants** (0 observations); its only support is the reference variant. 9 of
  the 17 legacy `only_feasible_row` links are of this kind (targets case_200, 234, 236, 253, 260, 373, 377, 500;
  samples case_30).
- **`forced_matching`**: 1 of 3 correct across the two strict variants, which overlap. That is small and mixed, and
  no reliability estimate follows from it.
- **`only_feasible_request`** and the **nearest-anchor fallback**: wrong more often than right in every variant.
- **Selection bias:** these accounts were identifiable, and genuinely anonymous accounts may sit in different
  windows and neighbourhoods. This is supporting evidence about the mechanisms, not hidden-target accuracy.

## The two forced-matching rows (case_78, case_94), reviewed

Both accounts are the deletion worker's account_service activity row inside the request's window, a **claim**
row, not a record naming the person. The pair is present in every maximum one-to-one matching of the remaining
rows and requests. It assumes:
1. exactly one worker account row per authorized request (measured globally: 539 rows for 540 requests);
2. the neighbours' explicit assignments are right;
3. no request outside this dataset owns one of these rows.

| | case_78 (user_76) | case_94 (user_92) |
|---|---|---|
| window | 08-16 08:00 → report 08-18 08:00 (+15 min); audit 09-11 | 08-10 06:00 → report 08-13 06:00 (+15 min); audit 09-01 |
| feasible rows | 7: three on 08-16 (one taken by case_105, explicit), four on 08-18 (three taken by case_92, case_77, case_79, explicit) | 5: three on 08-10 (none taken), two on 08-13 (one taken by case_93, explicit) |
| forced pick | account_8754 (`activity_3302`, 08-18 06:45, SUCCESS claim) | account_4037 (`activity_3227`, 08-13 04:55, PARTIAL claim) |
| independently grounded findings (kept either way) | search_8295 REMAINING and support_9652 EXPOSED_PII (evidence_91), with remediation and verification; audit_record_6593 VERIFY_PRESENT | search_7631 REMAINING and support_7691 EXPOSED_PII (evidence_89), with remediation and verification |
| step that rests on the forced pick | `VERIFY_RECORD_ABSENT account_8754`, uncited (a future check) | `VERIFY_RECORD_ABSENT account_4037`, uncited (a future check) |
| with forced_matching off | that one step removed; 7 steps remain; status INCOMPLETE; support unresolved | that one step removed; 6 steps remain; status INCOMPLETE; support weak→unresolved |
| empty-row fallback | not involved (rows keep their findings) | not involved |

Effect of turning `forced_matching` off, deterministic: targets change only these 2 rows; samples are unchanged
(no sample uses it); 0 status flips; 0 cited steps lost. Nothing replaces the removed steps.

## The concrete alternatives

| | A: assert all (current release) | B: assert none | C (approved as A34; A34a then also demoted `forced_matching`): assert only `only_feasible_row` + `forced_matching` (+ `corroborated_run`, unused) |
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
| `only_feasible_row` | The single row in the request's window, after rows that explicit evidence ties to other requests are removed. Strict variants: 4/4, all window-unique; elimination-based picks untested. |
| `forced_matching` | The pair present in every maximum one-to-one matching. Strict variants: 1/2 and 0/1 (small, mixed); depends on the neighbours' assignments. |
| `only_feasible_request` | A row that only this request could still claim. Strict variants: 0/1 and 0/1; reference variant 1/4. |
| nearest-anchor fallback | The closest row to `reported_at`. A ranking, not a deduction. Strict variants: 48 right of 168–169 picks. |

## What the agent adds

Nothing changes here. The agent's account choice needs a cited lineage to the subject (A27), so it cannot
re-assert a workflow-only account; changing the account without one is rejected. All 19 rows are already in its
scope (weak/unresolved). The agent pass runs once, on the chosen configuration, in C7.4.
