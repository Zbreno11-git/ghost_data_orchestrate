# C7.1T: temporal interpretation, written before measuring sample gains (2026-10-25 03:09 UTC, commit 8c58d55)

Breno's amendment 2 asks whether we treat an artifact's export time and the creation time of a historical snapshot
inside it too uniformly. This file fixes the interpretation and its assumptions **before** any sample or target
gain is measured; the measurement follows in `temporal_experiment.md`. The commit that adds this file precedes the
measurement commit.

## The official time contract (re-read)

- AGENTS §6.2: "Use only information available at or before `audit_at` when deciding the case. Evidence created
  later must not change the answer for that case."
- AGENTS §6.6: "Never cite organizer-only truth or an evidence item captured after the case's `audit_at`."
- AGENTS §6.1: `evidence_files.csv` maps each file to "its path, source origin, and capture time".
- problem_statement: "Determine the resource state at `audit_at` using the available evidence."

## Where the contract is clear, and where it is not

- **Citations: clear.** An evidence item, i.e. a manifest file_id, captured after audit_at is never cited.
  Both policies keep this, and the validator enforces it (`EVIDENCE_AFTER_AUDIT`).
- **Reasoning: ambiguous.** Consider a file captured after the audit that holds a snapshot envelope explicitly
  captured before it. Under §6.2, is that snapshot "information available at or before audit_at", or "evidence
  created later"? The snapshot's content existed at its capture, but the auditor could only read it in the later
  export. The contract does not say which time governs. **We state this as unresolved; the experiment measures,
  and Breno decides.**

## The three cases the amendment names

| Case | Example in the supplied formats | Baseline (`manifest`, A26) | Variant (`snapshot_capture`) |
|---|---|---|---|
| (a) historical snapshot explicitly captured before the audit, inside a later export | a snapshot bundle's `snapshots[i].captured_at`, or a collection capture's `captured_at`, earlier than the file's manifest capture | not read | **read** for identity, ownership and state; **never cited** |
| (b) later assertion describing an earlier event | a lookup ledger's `recorded_at`; a service export's per-record `observed_at`; a log line's `ts`; a SQL row's own time column, all inside a file captured later | not read | **not read** (an old timestamp alone never proves the information existed before the audit) |
| (c) observation without a reliable internal time | screens, PDF free text | its capture time | unchanged |

Rules of the variant:
- Only an envelope whose explicit capture time is ≤ its own export's capture time qualifies. A snapshot dated
  after its export is contradictory and stays out.
- There is no global manifest bypass: everything outside case (a) keeps the A26 rule.
- One semantics everywhere: the policy is set once on the evidence store, and every `CaseView`, and therefore
  identity, ownership, state reconstruction, agent tools and proof selection, reads it.
- **Citable ≠ readable.** A state known only from such a snapshot cannot be cited, so it becomes `unknown`,
  never a finding cited from a forbidden file.

## Assumptions, stated

1. A snapshot envelope's `captured_at` is the snapshot system's own record of when it captured the data, not an
   annotation added at export. The field name and the bundle's `exported_at` beside it suggest this. It is an
   assumption, not something the contract states.
2. Log lines, lookup `recorded_at` and per-record `observed_at` describe events, but the artifact we can read is
   the later export. They are type (b) and are not admitted. (One could argue logs are append-only and so
   contemporaneous; we do not take that step without a contract basis.)
3. Ownership derived from such a snapshot is explicit-tier evidence (it names the subject). It is labelled with its
   source, so the decision trail shows the snapshot came from a later export.

## Survey of the supplied formats (dataset-wide, before measuring)

- Snapshot-dated observations: 483, i.e. 118 scope envelopes and 365 records.
- 11 files hold snapshots older than their export (407 observations). The lag ranges from 0.12 to 8.00 days,
  median 2.00.
- Other observations with an internal time earlier than their file's capture: log 981, SQL 220, JSON 411. All are
  type (b) or same-file rows and are **not** read early by the variant.

## Disclosure

Before writing this, an evaluator-side look at the public answers showed two things:
- 0 of their 75 citations point to a file captured after the case's audit_at;
- the resources the answers name only from later exports (D12) sit in snapshot envelopes dated at or before the
  audit (4 retained audit records captured exactly at audit_at; account_5684 captured 09-09), except
  account_3866, which is dated after.

That observation motivated scoping the variant to envelope capture times. It does not tune the variant to any
case: the rule contains no id, family or label. The samples are not a held-out set for this experiment.

## Amendment v2 (written after the v1 measurement, before re-measuring; 2026-10-25 03:10 UTC)

**What v1 got wrong.** v1 (commit 8c58d55) cited the copy's *latest* readable observation. When a later export's
snapshot became the latest observation of a copy, it displaced a citable observation that shows the **same** state.
The row then lost a cited finding it already had. Trace, case_24 account_5334: evidence_92's profile lookup is
PRESENT and citable; evidence_02's snapshot (captured at audit_at, exported 09-17) is PRESENT and not citable; v1
gave "unknown".

**v2 rule (generic: no id, family or label).** A copy's state is still its latest readable observation. Its
citation is the latest **citable** observation of that copy showing the **same state**. If no citable
observation shows that state, the copy keeps the uncitable reference and the assessment is `unknown`, as in v1.
Under `manifest` every readable observation is citable, so the baseline is unchanged. v1 and v2 results are both
reported.
