# Evaluation report

Generated 2026-10-25 02:08 UTC by `scripts/make_reports.py` from run artifacts; every number below is read from a file.

Final configuration: `main.py run --engine agent --agent-scope non_resolved --ownership strict` (agent model `gemini-3.1-flash-lite`). Run directory `runs/s6/final`.

Three questions are kept apart below, because a row can pass one and fail another: is the output **structurally valid**, is each verdict **supported by evidence**, and how close are the predictions to the **public sample answers**.

## 1. Structural validity (518 target requests)

`main.py validate` on the submitted output: **0 violations**, 518 rows (unique, sorted by case_id, JSON arrays, legal operation/state pairs, canonical order, citations only where required and never after audit_at).

## 2. Evidence support (518 target requests)

| support | rows | meaning |
|---|---|---|
| resolved | 175 | every linked resource is tied to the subject by explicit evidence and has a reconstructed state; account attributed |
| weak | 18 | depends on a workflow-only link, an ownership ambiguity, or a low-confidence intent |
| unresolved | 325 | no attributable account, or a resource whose state the evidence leaves unknown |

Status counts: {"INCOMPLETE": 363, "COMPLETE": 145, "NOT_APPLICABLE": 10}. By support and status: {"resolved/COMPLETE": 51, "resolved/INCOMPLETE": 114, "resolved/NOT_APPLICABLE": 10, "unresolved/COMPLETE": 91, "unresolved/INCOMPLETE": 234, "weak/COMPLETE": 3, "weak/INCOMPLETE": 15}.

Most unresolved rows lack an account: the candidate accounts appear only in deletion-worker activity rows (which carry no run identifier), so no evidence ties one to the subject; the engine reports the case rather than guess. Their other findings remain evidence-backed.

**Heuristic predictions (3 rows)**, by the owner's decision (A29), for rows with no grounded proposal; each is unresolved and says so in its reasons:

- `case_39` INCOMPLETE: HEURISTIC PREDICTION (A29), not a reconstructed state: data_flow_1121: screen shows status Healthy, mode Continuous sync
- `case_55` INCOMPLETE: HEURISTIC PREDICTION (A29), not a reconstructed state: backup_9287: screen shows the backup retained until 26 Jul 2026
- `case_61` INCOMPLETE: HEURISTIC PREDICTION (A29), not a reconstructed state: object_19: screen lists delivery_confirmation_19.pdf, the name catalog row activity_4007 declares for it

## 3. Public samples (32 cases, full official denominators)

Final configuration on `dataset/sample_deletion_requests.csv` (run `runs/s6/final-samples`):

| metric | value |
|---|---|
| status_accuracy | 1.0000 (32/32) |
| whole_case_exact | 0.3750 (12/32) |
| step_precision | 0.9939 (162/163) |
| step_recall | 0.8394 (162/193) |
| evidence_accuracy_on_matched | 1.0000 (162/162) |
| cited_evidence_recall | 0.8133 (61/75) |
| sequence_accuracy | 0.3750 (12/32) |
| ordered_operations_accuracy | 0.3750 (12/32) |
| step_f1 | 0.9101 |
| field_accuracy.step_no | 1.0000 (163/163) |
| field_accuracy.phase | 1.0000 (163/163) |
| field_accuracy.system_id | 0.7546 (123/163) |
| field_accuracy.resource_id | 0.7485 (122/163) |
| field_accuracy.operation | 0.8098 (132/163) |
| field_accuracy.state | 0.8098 (132/163) |
| field_accuracy.evidence_id | 1.0000 (163/163) |
| aligned / missing / extra steps | 163 / 30 / 0 |

Status confusion (gold → predicted): COMPLETE->COMPLETE: 10, INCOMPLETE->INCOMPLETE: 22

Sequence accuracy counts a case whose full step list matches in order; the grader preserves array order and ignores key order.

### The ceiling of these denominators

The step denominator keeps every answer step, including steps no participant-visible evidence can support (searches recorded in `docs/DECISIONS.md`):

- D10: `audit_record_6645` and `audit_record_5569` (cases 18, 20) appear in no evidence file, table or image extract; a literal byte search of all participant files finds them only in the sample answers.
- D13: `account_004` (case 04) likewise appears only in the sample answers.
- D12: six resources (case 09's `account_3960` and `audit_record_4902`; audit records 4128, 7095, 3954, 1707 in cases 23/24/29/30) are named only by files captured after their case's audit_at; the contract forbids using them, so the engine never names them (account_3960 stays, named by an admissible row).
- Accounts named only by deletion-worker rows cannot be attributed without guessing (see §2).

These are explained beside the score, not removed from it.

## 4. Custom evaluation cases (independently authored)

Written by a subagent that did not see the engine code (A13); each has its own dataset and expected output under `code/evaluation/custom_cases/`.

| case | what it tests | status | whole-case | step P | step R |
|---|---|---|---|---|---|
| historical_email_replica | Historical identity resolution; Replication drift; Claims are not proof | 1.0000 (1/1) | 1.0000 (1/1) | 1.0000 (3/3) | 1.0000 (3/3) |
| post_cutoff_evidence_ignored | The audit_at cutoff; COMPLETE verifications must cite proof; Records that policy retains; Request in another language | 1.0000 (1/1) | 1.0000 (1/1) | 1.0000 (3/3) | 1.0000 (3/3) |
| success_claim_contradicted | An operation result is a claim; Later admissible evidence overrides the claim; Request in another language | 1.0000 (1/1) | 1.0000 (1/1) | 1.0000 (3/3) | 1.0000 (3/3) |
| tombstone_pair | Tombstones are redacted, not deleted; Tombstone pair: one copy is compliant, one is not; The finding is EXPOSED_PII, not REMAINING_RECORD; Claims are not proof; Request in another language | 1.0000 (1/1) | 1.0000 (1/1) | 1.0000 (3/3) | 1.0000 (3/3) |
| clean_primary_dirty_replica | Copy-level state; The audit_at cutoff; Claims are not proof | 1.0000 (1/1) | 1.0000 (1/1) | 1.0000 (3/3) | 1.0000 (3/3) |

## 5. Case-by-case comparisons

Each line compares two runs on the same cases against the answers. *Not in the answer but supported* means the added step cites evidence that names the resource; *unsupported* means it does not. A status flip from INCOMPLETE to COMPLETE is listed separately because it can hide a violation.

| comparison | cases | whole-case base → cand | correct steps removed | added: in answer / supported / unsupported | INCOMPLETE→COMPLETE | agent cost paid in that run (replays: $0) |
|---|---|---|---|---|---|---|
| S3 baseline → S6 final (samples) | 32 | 11 → 12 | 0 | 1 / 0 / 0 | 0 | $0.0000 |
| S5 final → S6 final (samples) | 32 | 12 → 12 | 0 | 0 / 0 / 0 | 0 | $0.0000 |
| S6 deterministic → S6 final with agent (samples) | 32 | 12 → 12 | 0 | 0 / 0 / 0 | 0 | $0.0000 |
| strict → scored ownership, measured, not adopted (samples) | 32 | 12 → 14 | 0 | 5 / 7 / 6 | 0 | $0.0000 |
| deterministic → agent, 10-case bench (pre-A30) | 10 | 2 → 2 | 0 | 0 / 0 / 0 | 0 | $0.0410 |

On the target split (no answers), engine changes moved rows only where the per-case diffs were traced to raw evidence, and every INCOMPLETE→COMPLETE flip was investigated (`docs/plans/session-05.md`, C5.2–C5.6). Session 6 changed no row: its audits found no evidence-backed link or parsing defect to fix (`docs/plans/session-06.md`).

## 5b. Mismatch diagnostics by earliest responsible stage

Every sample mismatch of the final run, with one cause each (`code/evaluation/diagnose.py`; the full list with examples is in `code/evaluation/diagnostics.md`). "No supporting fact found" means the id occurs in no decoded source (raw text, PDF text from two decoders, every vision extract, the activity and audit CSVs); it lists the checks made and is not proof that the evidence is absent.

| cause | before | now |
|---|---|---|
| no supporting fact found | 3 | 3 |
| temporal state | 5 | 5 |
| identity/resource association | 25 | 24 |
| **total** | **33** | **32** |

Before = `runs/s3/samples-strict` (session 3 baseline); now = `runs/s6/final-samples`.

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
- **Three target rows carry flagged heuristic predictions (A29).** The evidence there shows health,
  retention or an alias, not a state.
- **Screen aliases are not used for grounded state.** The same object under its alias would add findings to a
  sample case whose answer omits it.


## Tuning exposure

Ownership, citation and screen-reading rules were measured on the 32 public samples, so these scores are optimistic for the hidden targets. No case id, evidence id, label or case family appears in code (a test greps the prediction path for the sample answers file); the 5 custom cases were specified independently of the engine. The samples have been inspected since the first session, so they are not a held-out set. No hidden-target accuracy is claimed.
