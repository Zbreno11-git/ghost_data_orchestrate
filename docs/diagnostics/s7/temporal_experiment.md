# C7.1T: temporal interpretation experiment, measured (2026-10-25 03:15–03:20 UTC)

The interpretation and its assumptions are fixed in `temporal_interpretation.md`. Commit `8c58d55` (03:09Z)
precedes every measurement; the v2 amendment, commit `84f591b` (03:12Z), precedes its own re-measurement. All runs
are deterministic ($0), in `runs/s7/c71t/`. The baseline (`manifest`) is byte-identical to S6 on samples and
targets. This experiment is kept apart from C7.1: the workflow-link configuration is at its default (all
asserted).

## v1 (citation = the copy's latest readable observation): rejected by its own measurement

| samples | manifest | v1 |
|---|---|---|
| status | 32/32 | **28/32** (4 INCOMPLETE→COMPLETE) |
| step P / R | 162/163, 162/193 | 114/119, 114/193 |
| step F1 | 0.9101 | 0.7308 |
| correct steps lost | — | 50 |
| validator violations | 0 | samples 2, targets 12 |

**Why.** A later export's snapshot became the latest observation of a copy and displaced a citable observation
that showed the **same** state. Every such finding then turned unknown. Trace, case_24 account_5334:
- evidence_92's lookup is PRESENT and citable;
- evidence_02's snapshot (captured at audit_at, exported 09-17) is PRESENT and not citable;
- v1 gave "unknown", and the case flipped to COMPLETE.

This is a defect in v1's citation step, not in the interpretation.

## v2 (citation = the latest citable observation of the same copy state)

| samples | manifest | v2 |
|---|---|---|
| status | 32/32 | 32/32 |
| whole-case | 12/32 | **14/32** |
| step precision | 162/163 | 167/168 |
| step recall | 162/193 | 167/193 |
| step F1 | 0.9101 | **0.9252** |
| citation on matched | 162/162 | 167/167 |
| cited-evidence recall | 61/75 | 62/75 |
| sequence | 12/32 | 14/32 |
| correct gained / lost | — | **5 / 0** |
| incorrect added / removed | — | 0 / 0 |
| status flips | — | 0 |
| custom cases (5) | 5/5 | 5/5 |
| validator violations | 0 | **0** (samples and targets) |
| mismatch causes | 24 association, 3 no fact, 5 temporal | 23, 3, 1 |

**Sample steps recovered, each traced to its evidence:**

| case | step | from | cited |
|---|---|---|---|
| case_23, 24, 29, 30 | `VERIFY_RECORD_PRESENT` on retained audit records 4128, 7095, 3954, 1707 | evidence_02 snapshot `security_service`, captured 09-15T12:00 = audit_at, exported 09-17 | `""` (future verification in an INCOMPLETE case) |
| case_26 | `VERIFY_RECORD_ABSENT account_5684` | identity from the evidence_02 snapshot captured 09-09 (customer_reference user_26); absence from an admissible scope | evidence_92 (captured ≤ audit_at) |

**Targets: 59 rows change, 0 status flips, 0 steps removed, 0 violations.**
- 58 INCOMPLETE rows gain one `VERIFY_RECORD_PRESENT` (`""`) on a retained audit record. It is linked only by a
  pre-audit snapshot inside a later snapshot bundle (evidence_07, 12, 17, 22, 26, 31, 35, 40, 49). The record's
  state is known only from that uncitable snapshot, so its assessment is `unknown`: **support moves to unresolved**
  (resolved→unresolved 9, weak→unresolved 5) rather than claiming a proven state.
- 1 COMPLETE row (case_430) gains a cited `VERIFY_RECORD_ABSENT account_6006` (evidence_68, admissible). Its
  identity comes from a pre-audit snapshot, like sample case_26. That row moves unresolved→resolved.
- Every other step is renumbered only.

**A29:** no row is emptied, so there is no interaction.

## What would have to be true for v2 to be right

- The snapshot envelope's `captured_at` is a genuine capture time (assumption 1), so its content existed by
  audit_at.
- §6.2's "information available at or before audit_at" refers to when the information existed, not when the
  auditor could read the export. **The contract does not settle this.**
- Under the other reading, every step v2 adds uses information the auditor could not have had at the audit.

## Cost of promoting it

Code and tests are in place, behind config. The default stays `manifest` until Breno decides. Promotion changes
the briefs of the ≈59 affected target rows that are in the agent's scope. The agent pass is replay plus live on
cache misses: estimate ≤ 70 cases × $0.0035 ≈ $0.25, hard stop $0.40.
