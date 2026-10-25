# Evaluation report

Generated 2026-10-25 04:14 UTC by `scripts/make_reports.py` from run artifacts; every number below is read from a file.

Final configuration: `main.py run --engine agent --agent-scope non_resolved --ownership strict` (agent model `gemini-3.1-flash-lite`). Run directory `runs/s7/final-r2`.

Three questions are kept apart below, because a row can pass one and fail another: is the output **structurally valid**, is each verdict **supported by evidence**, and how close are the predictions to the **public sample answers**.

## 1. Structural validity (518 target requests)

`main.py validate` on the submitted output: **0 violations**, 518 rows (unique, sorted by case_id, JSON arrays, legal operation/state pairs, canonical order, citations only where required and never after audit_at).

## 2. Evidence support (518 target requests)

| support | rows | meaning |
|---|---|---|
| resolved | 167 | every linked resource is tied to the subject by explicit evidence and has a reconstructed state; account attributed |
| weak | 12 | depends on a workflow-only link, an ownership ambiguity, or a low-confidence intent |
| unresolved | 339 | no attributable account, or a resource whose state the evidence leaves unknown |

Status counts: {"INCOMPLETE": 363, "COMPLETE": 145, "NOT_APPLICABLE": 10}. By support and status: {"resolved/COMPLETE": 52, "resolved/INCOMPLETE": 105, "resolved/NOT_APPLICABLE": 10, "unresolved/COMPLETE": 90, "unresolved/INCOMPLETE": 249, "weak/COMPLETE": 3, "weak/INCOMPLETE": 9}.

Most unresolved rows lack an account: the candidate accounts appear only in deletion-worker activity rows (which carry no run identifier), so no evidence ties one to the subject; the engine reports the case rather than guess. Their other findings remain evidence-backed.

**Heuristic predictions (4 rows)**, by the owner's decisions (A29: screen rules; A34: the nearest-in-time account pick), only for rows that would otherwise have no grounded proposal; each is unresolved and says so in its reasons:

- `case_39` INCOMPLETE: HEURISTIC PREDICTION (A29), not a reconstructed state: data_flow_1121: screen shows status Healthy, mode Continuous sync
- `case_55` INCOMPLETE: HEURISTIC PREDICTION (A29), not a reconstructed state: backup_9287: screen shows the backup retained until 26 Jul 2026
- `case_61` INCOMPLETE: HEURISTIC PREDICTION (A29), not a reconstructed state: object_19: screen lists delivery_confirmation_19.pdf, the name catalog row activity_4007 declares for it
- `case_63` COMPLETE: HEURISTIC PREDICTION (A34), not an attributed account: account_2064 is the nearest anchor to reported_at (752 min); weak

## 3. Public samples (32 cases, full official denominators)

Final configuration on `dataset/sample_deletion_requests.csv` (run `runs/s7/final-r2-samples`):

| metric | value |
|---|---|
| status_accuracy | 1.0000 (32/32) |
| whole_case_exact | 0.4375 (14/32) |
| step_precision | 0.9940 (167/168) |
| step_recall | 0.8653 (167/193) |
| evidence_accuracy_on_matched | 1.0000 (167/167) |
| cited_evidence_recall | 0.8267 (62/75) |
| sequence_accuracy | 0.4375 (14/32) |
| ordered_operations_accuracy | 0.4375 (14/32) |
| step_f1 | 0.9252 |
| field_accuracy.step_no | 1.0000 (168/168) |
| field_accuracy.phase | 1.0000 (168/168) |
| field_accuracy.system_id | 0.7798 (131/168) |
| field_accuracy.resource_id | 0.7738 (130/168) |
| field_accuracy.operation | 0.8333 (140/168) |
| field_accuracy.state | 0.8333 (140/168) |
| field_accuracy.evidence_id | 1.0000 (168/168) |
| aligned / missing / extra steps | 168 / 25 / 0 |

Status confusion (gold → predicted): COMPLETE->COMPLETE: 10, INCOMPLETE->INCOMPLETE: 22

Sequence accuracy counts a case whose full step list matches in order; the grader preserves array order and ignores key order.

### The ceiling of these denominators

The step denominator keeps every answer step, including steps no participant-visible evidence can support (searches recorded in `docs/DECISIONS.md`):

- D10: `audit_record_6645` and `audit_record_5569` (cases 18, 20) appear in no evidence file, table or image extract; a literal byte search of all participant files finds them only in the sample answers.
- D13: `account_004` (case 04) likewise appears only in the sample answers.
- D12: six resources are named only by files captured after their case's audit_at. Under the time policy A36 a snapshot envelope that states its own capture at or before audit_at is read (never cited); measured on this run: named 4 of 6 (audit_record_4128 (case_23), audit_record_7095 (case_24), audit_record_3954 (case_29), audit_record_1707 (case_30)); not named: account_3960 (case_09), audit_record_4902 (case_09).
- Accounts named only by deletion-worker rows cannot be attributed without guessing (see §2); the masked backtest behind A34 is in `docs/diagnostics/s7/legacy_links.md` of the repository.

These are explained beside the score, not removed from it.

## 4. Custom evaluation cases (independently authored)

Written by a subagent that did not see the engine code (A13); each has its own dataset and expected output under `code/evaluation/custom_cases/` (role and provenance: its README.md). Their policy file is the official deletion_rules.csv, reused unchanged.

| case | what it tests | expected → observed status | status | whole-case | step P | step R |
|---|---|---|---|---|---|---|
| clean_primary_dirty_replica | Copy-level state; The audit_at cutoff; Claims are not proof | INCOMPLETE → INCOMPLETE | 1.0000 (1/1) | 1.0000 (1/1) | 1.0000 (3/3) | 1.0000 (3/3) |
| historical_email_replica | Historical identity resolution; Replication drift; Claims are not proof | INCOMPLETE → INCOMPLETE | 1.0000 (1/1) | 1.0000 (1/1) | 1.0000 (3/3) | 1.0000 (3/3) |
| post_cutoff_evidence_ignored | The audit_at cutoff; COMPLETE verifications must cite proof; Records that policy retains; Request in another language | COMPLETE → COMPLETE | 1.0000 (1/1) | 1.0000 (1/1) | 1.0000 (3/3) | 1.0000 (3/3) |
| success_claim_contradicted | An operation result is a claim; Later admissible evidence overrides the claim; Request in another language | INCOMPLETE → INCOMPLETE | 1.0000 (1/1) | 1.0000 (1/1) | 1.0000 (3/3) | 1.0000 (3/3) |
| tombstone_pair | Tombstones are redacted, not deleted; Tombstone pair: one copy is compliant, one is not; The finding is EXPOSED_PII, not REMAINING_RECORD; Claims are not proof; Request in another language | INCOMPLETE → INCOMPLETE | 1.0000 (1/1) | 1.0000 (1/1) | 1.0000 (3/3) | 1.0000 (3/3) |

## 5. Case-by-case comparisons

Each line compares two runs on the same cases against the answers. *Not in the answer but supported* means the added step cites evidence that names the resource; *unsupported* means it does not. A status flip from INCOMPLETE to COMPLETE is listed separately because it can hide a violation.

| comparison | cases | whole-case base → cand | correct steps removed | added: in answer / supported / unsupported | INCOMPLETE→COMPLETE | agent cost paid in that run (replays: $0) |
|---|---|---|---|---|---|---|
| S6 final → S7 final (samples) | 32 | 12 → 14 | 0 | 5 / 0 / 0 | 0 | $0.0000 |
| S7 deterministic → agent (samples) | 32 | 14 → 14 | 0 | 0 / 0 / 0 | 0 | $0.0000 |

On the target split (no answers), engine changes moved rows only where the per-case diffs were traced to raw evidence, and every INCOMPLETE→COMPLETE flip was investigated (`docs/plans/session-05.md`, C5.2–C5.6). Session 6 changed no row: its audits found no evidence-backed link or parsing defect to fix (`docs/plans/session-06.md`). Session 7 changed rows by two owner decisions, each measured deterministically before adoption: A34/A34a (only the account deduction that held up in a masked backtest is asserted) and A36 (the snapshot time policy).

## 5a. Deterministic engine vs agent

The same configuration with no model (`--engine deterministic`, rule-based intent) and with the agent reviewing weak and unresolved proposals:

| | deterministic | agent (final) |
|---|---|---|
| samples status_accuracy | 1.0000 (32/32) | 1.0000 (32/32) |
| samples whole_case_exact | 0.4375 (14/32) | 0.4375 (14/32) |
| samples step_precision | 0.9940 (167/168) | 0.9940 (167/168) |
| samples step_recall | 0.8653 (167/193) | 0.8653 (167/193) |
| samples cited_evidence_recall | 0.8267 (62/75) | 0.8267 (62/75) |
| samples step_f1 | 0.9252 | 0.9252 |
| samples: rows the agent changed | 0 of 32 | support moves none |
| targets: rows the agent changed | 0 of 518 | support moves {'unresolved→resolved': 1, 'weak→resolved': 2} |

## 5b. Mismatch diagnostics by earliest responsible stage

Every sample mismatch of the final run, with one cause each (`code/evaluation/diagnose.py`; the full list with examples is in `code/evaluation/diagnostics.md`). "No supporting fact found" means the id occurs in no decoded source (raw text, PDF text from two decoders, every vision extract, the activity and audit CSVs); it lists the checks made and is not proof that the evidence is absent.

| cause | before | now |
|---|---|---|
| no supporting fact found | 3 | 3 |
| temporal state | 5 | 1 |
| identity/resource association | 24 | 23 |
| **total** | **32** | **27** |

Before = `runs/s6/final-samples` (session 3 baseline); now = `runs/s7/final-r2-samples`.

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


## Tuning exposure

Ownership, citation and screen-reading rules were measured on the 32 public samples, so these scores are optimistic for the hidden targets. No case id, evidence id, label or case family appears in code (a test greps the prediction path for the sample answers file); the 5 custom cases were specified independently of the engine. The samples have been inspected since the first session, so they are not a held-out set. No hidden-target accuracy is claimed.
