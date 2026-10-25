## 6. Failures found and improvements made

Each item: what was wrong, how it was found, what changed, and the measured effect. Every fix landed with a test
that failed before it, and a mutation (reverting the fix) that turned that test red. Decision ids refer to the
repository's `docs/DECISIONS.md`.

**Evidence reading**
- **Explicit state results were ignored (A25).**
  - Found by: classifying every non-resolved target case by its earliest failure.
  - Defect: lookups reporting `BLOCKED` / `DISABLED` / `REDACTED`, restore decisions `deny`, and `[REDACTED]`
    message markers fell through to "unknown".
  - Effect: two target cases became resolved, with cited verifications.
- **Screens were read as copies of processes (A25).**
  - Defect: a flow or backup shown on a console was treated as a separate copy whose state could not be read,
    which made the whole verdict unknown.
  - Fix: a screen now never sets a process's state. Health ("Healthy") and configuration ("Continuous") are
    not proof that something is enabled.
- **Table rows were not kept apart (A25, C5.6).**
  - Defect: an exports table listing four owners linked all four exports to one subject, a results table
    linked a look-alike email's row, and the decoy check read every row.
  - Fix: a table row now belongs to one entity, for ownership, state and decoy detection alike.
  - Effect: 7 false links were removed from target cases.
- **Panels of one screen were judged apart (C5.6).**
  - Defect: a single-customer ticket console names the ticket in one panel and the customer's email in another.
  - Effect: one target case gained its cited exposed-PII finding.
- **Two clocks were conflated (A26).**
  - Defect: eligibility and state order used only the artifact's capture time, so findings inside one export
    were ordered by input, and a record observed after the cutoff could be admitted.
  - Fix: both clocks are kept and documented per format, and admissibility needs both to be at or before
    audit_at. Same-instant disagreement is a conflict, not "presence wins".
  - Effect: four target cases changed to COMPLETE, each traced to raw records; none of the 32 samples changed.

**Session 6: audits before fixes (no row changed)**
- **Our diagnostics called a parser blind spot a dataset gap.**
  - Found by: the extraction audit (C6.1).
  - Defect: the evaluator decided "absent from supplied evidence" by a raw-byte search, but the four PDFs are
    compressed, so every identifier in them (10 of 10) is invisible to it.
  - Fix: the search now runs over decoded text (raw text, two PDF decoders, every vision extract), and the
    verdict is "no supporting fact found", with the checks listed. The three items it covers still match
    nothing.
- **Extraction coverage.** Every decoded line of every source that names a resource (7,338 lines) was compared
  with the observations built from it: no record was skipped or partly read. Screenshots implicated in the
  mismatches were also read visually against their extracts.
- **Rejected association paths, to the break point.** Of the 24 sample steps whose resource is not linked:
  - 21 rest on records that carry no identifier or reference at all (anonymized analytics profiles, profile
    lookups);
  - 3 are linked to the person only by evidence captured after the cutoff.
  
  No admissible chain exists, so no link rule was added. A tempting non-timing signal (workflow status vs the
  run's result) was rejected: a link would still come from a time window plus a one-to-one assumption.
- **Ownership mode by a criterion fixed beforehand.** Strict stays: the scored mode would gain 2 whole cases
  but add 13 wrong account steps, so step F1 falls from 0.910 to 0.893.
- **Robustness tests with controls.** End-to-end metamorphic tests cover input order, duplicated evidence,
  another person with the same name, and post-cutoff files. Each has a positive control, which caught two
  first versions whose fixtures the engine never read.

**Temporal isolation and support labels (A24)**
- **Ownership used information after a case's cutoff.**
  - Defect: an owner index built with a far-future cutoff, and a one-to-one account assignment solved once
    for all requests, let later requests' rows and links decide earlier cases.
  - Fix: both are now solved as of each case's audit_at.
  - Effect: 16 target accounts deduced from later information became honestly ambiguous; sample scores
    unchanged.
- **A valid row was not a supported verdict.**
  - Defect: ownership ambiguities and unknown retained records never lowered the support label.
  - Fix: one rule now decides the label: any ambiguity is at most weak, any unknown is unresolved.

**Agent (A27, A23, A28)**
- **Citations were checked for existence, not meaning.**
  - Defect: a seen observation that merely mentioned a resource could add it, pick an account, or (with no
    evidence at all) exclude a violation.
  - Fix: decisions now need a lineage, a chain of cited admissible units from the resource to the subject's
    identifiers. Exclusions need evidence, and evidence of another owner if the link was explicit.
  - Offline re-validation of the earlier benchmark rejected one decision. It matched the sample answer, but
    the page it cited never names the account, and the account id mirrors the case number: a shortcut, not
    evidence. The case id was removed from the model's brief.
- **Measured value of the agent.**
  - Once validated, the agent changed 0 rows out of 40 measured cases (10 samples, 30 stratified targets), at
    about $0.0035 per case.
  - It runs on weak and unresolved proposals only (A28, the owner's decision).
  - The earlier "+1 case" was the unsupported pick above.
- **Stale checkpoints.**
  - Defect: resumed runs matched saved cases by id only.
  - Fix: a fingerprint of code, prompts, config, model, dataset and request row now gates reuse.

**Session 7**
- **Timing-deduced accounts asserted as steps (A34, A34a).**
  - Finding: 19 target rows carried an account deduced only from timing and one-to-one matching. The CSV cannot
    say "weak", so each was an asserted step.
  - Measured: a masked-identity backtest. 177 explicitly proven accounts were hidden by cohort and the existing
    mechanisms re-run. In the strict variants:
    - `only_feasible_request` was wrong 1 of 1 times;
    - `forced_matching` was right 1 of 2 and 0 of 1;
    - the nearest-in-time fallback was right 48 of 168 times;
    - window-unique `only_feasible_row` was right 4 of 4.
  - Fix (owner's decision): only `only_feasible_row` is asserted, labelled a workflow inference. The weaker
    picks became uncertain candidates with no step, and the nearest-in-time pick only fills a row that would
    otherwise be empty, flagged a heuristic prediction.
- **A first temporal variant that lost cited findings (A36, v1).**
  - Defect: reading pre-audit snapshot envelopes inside later exports let an uncitable observation displace a
    citable one of the same state. Sample F1 fell to 0.73, with 4 status flips.
  - Fix (v2): cite the latest citable observation of the same copy state. Its measurement: +5 correct sample
    steps, 0 lost, 0 flips.
- **Explanations that could describe a different version.**
  - Defect: `explain` re-ingested today's dataset to describe an older run, and nothing tied the explanation to
    the submitted CSV.
  - Fix: provenance is saved with each run. `explain` and the viewer attach it only after `output.csv`,
    `decisions.jsonl` and `provenance.jsonl` match their recorded sha256 and each other.
- **A package check weaker than it read.**
  - Defects:
    - acceptance followed byte equality, not explicit validation;
    - the reports were counted by suffix;
    - a dead proxy was called isolation;
    - there was no rule against copies of dataset files.
  - Fix: `code/release/checks.py`, with one test per rule. The fixture allowlist pins the custom cases' reused
    policy file by path and sha256.

**Earlier sessions**
- **Copy-level state (A20, A22).**
  - Defect: a later partial capture erased a directly observed record.
  - Fix: scope absence now proves only deletion targets, and never overrides a direct observation.
- **Policy measured in isolation from ownership.**
  - 41/41 sample findings and 34/34 COMPLETE verifications match on verdict, operation and citation.
- **Settlement by error class (A21).** A rejected request is booked at $0, a server failure at its reservation.

**Not fixed, and why**
- **Accounts and anonymized records named only in deletion-worker rows** stay unattributed. The activity
  stream has no run identifier, the records name no one, and timing or position is not evidence. Session 6
  checked each one to its break point.
- **Four target rows carry flagged heuristic predictions**: three under A29 (the evidence shows health, retention or
  an alias, not a state) and one under A34 (the nearest-in-time account pick for a row that would otherwise be empty).
- **Screen aliases are not used for grounded state.** The same object under its alias would add findings to a
  sample case whose answer omits it.
