# Interview cheat sheet — Ghost Data Still Exists

**Written for:** Breno, before the AI interview. One page to re-read; every number lives in
`code/evaluation/evaluation_report.md` and `usage_report.md` (quote from there, not from memory).

## The one-sentence answer

A deterministic evidence engine reconstructs, per physical copy and as of each case's cutoff, what personal data
still exists and what policy requires. A bounded Gemini agent reviews only the cases the engine cannot settle.
The agent may only cite tool-returned evidence, and its decisions are accepted only with a cited chain to the
person. The engine, not the model, writes the steps.

## Architecture (diagram in words)

`dataset/` → **ingest** (94 files → observations with two clocks) → **identity** (current + historical identifiers
at the cutoff) → **CaseView** (the cutoff applied to every read) → **ownership** (explicit links; workflow
deduction only where it held up) → **policy** (state per copy → treatment from deletion_rules.csv) → **planner**
(contract steps, canonical order, support level) → **agent** for weak/unresolved cases (9 read-only tools, lineage
check) → **validator** → `output.csv`. Every paid call goes through the **gateway** (reserve → send → settle,
budget hard stop, response cache, replay).

## What is deterministic, and what the model does

| Deterministic (code) | Model (Gemini 3.1 flash-lite) |
|---|---|
| parsing, identity, cutoff, ownership, per-copy state, policy, step generation, ordering, validation | intent classification (batched, cross-checked with a rule); screenshot reading (once, cached, two models cross-checked) |
| support level per case | investigating weak and unresolved cases with read-only tools, proposing account/addition/exclusion with citations |
| accepting or rejecting the model's proposal (lineage check, account must belong to the account system) | nothing it writes reaches the CSV directly |

Why: an LLM verdict is unauditable and costs money per case. The rules are cheap and testable; the model is used
where reading or searching is needed.

## The ideas worth explaining

- **Two clocks.** `captured_at` (when the artifact was captured) and `observed_at` (the record's own time). A record
  is readable only if both are at or before audit_at. The exception is a snapshot envelope that states its own
  capture time before the audit inside a later export: it is read but never cited (A36, an owner decision on an
  ambiguous contract clause).
- **Per physical copy.** A clean primary never clears a dirty replica. Disagreeing observations at one instant are
  a conflict, not a tie-break.
- **Claims vs state.** Reported statuses and worker "SUCCESS" rows are claims. Only evidence of the record sets
  state.
- **Retention and tombstones.** A RETAIN rule yields VERIFY_RECORD_PRESENT. An account tombstone is redacted to its
  stable user reference, never deleted. One of our custom cases caught the agent nearly deleting one; that was
  fixed.
- **Uncertainty is visible, not hidden.** Each row has a support level (resolved / weak / unresolved). The CSV
  cannot carry it, so `explain`, the viewer and `unresolved.md` do. Rows with no grounded proposal get a flagged
  heuristic prediction (A29, A34), never a silent guess.
- **Accounts from timing.** We measured our own deduction mechanisms with a masked backtest: hide 177 accounts that
  explicit evidence proves, re-run, and score. Only the mechanism that held up is asserted; the rest became
  uncertain candidates. The variants are reported separately and never pooled, with the selection bias stated.

## Evaluation (say it with the denominators)

- **Public samples:** all 32 cases and all 193 steps (full official denominators). Status, whole-case, step P/R/F1,
  citation and sequence accuracy are in the evaluation report.
- **Ceiling:** some answer steps name resources that appear in no participant evidence (D10, D13), or only after
  the cutoff (D12). We report them beside the score, not removed from it.
- **Custom cases:** 5 cases, written by a sub-agent that never saw the engine, its runs or the sample answers.
  Each reuses the official `deletion_rules.csv` unchanged (reused, not invented; pinned in a fixture allowlist).
- **Separate lines:** deterministic gains vs agent contribution are reported apart.
- **Tuning exposure:** the samples were inspected, so they are not held out. No hidden-target accuracy is claimed.

## Costs

The usage report has:
- the final run's calls and tokens per model;
- the full price of the responses behind the output vs what was newly paid in the final run (most were cached
  from earlier runs);
- the cumulative project spend against a $4.50 hard cap enforced by the gateway.

## Limitations (own them)

- Accounts named only in deletion-worker activity rows have no run id, so they stay unattributed unless a
  deduction we measured supports them.
- Anonymized analytics profiles name nobody, so they are not linked.
- The snapshot time policy rests on an interpretation of an ambiguous clause (documented, measured, owner's
  call).
- Heuristic rows are flagged predictions, not reconstructed states.

## One worked case

Open the viewer or `docs/explanations/` (both from the final run); `docs/release/WALKTHROUGH.md` has seven cases
written out. Walk one INCOMPLETE case (`case_105` is the ordinary one):
1. the request text and intent;
2. the person, and the historical email that matched;
3. the record in a replica, with both timestamps;
4. the rule (DELETE / REDACT);
5. the finding cited to its file;
6. remediation and verification with empty evidence (future work);
7. the support level, and why.

Then show one heuristic row, to demonstrate that uncertainty is labelled.

## Process (if asked how you built it)

- Sessions with checkpoints, each closed by tests run, two review passes, and docs (decisions with reopen
  triggers, an error catalog).
- Every claim in the reports is generated from run files.
- Mutation-checked tests: a fixture must reach the behaviour it tests.
- The agent's budget lives in an append-only ledger.
