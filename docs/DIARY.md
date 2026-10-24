# Diary — Ghost Data Orchestrate

> One entry per session, newest on top. Narrative: what was done, what was decided and **why**, and what was
> learned. State does not live here (see PROGRESS.md).

## 2026-10-24 — S3 (first half of the merged S3+S4): deterministic baseline, honest support levels, $0

**Done.** identity → cutoff → ownership → policy → planner → runner, all pure and tested (141 tests).
- **Baseline on the 32 samples (strict, full official denominators):**
  - status 32/32; whole-case 11/32;
  - steps: precision 161/162, recall 161/193; evidence on matched 161/161.
- **Scored mode:** whole-case 14/32; recall 168/193 at precision 168/180.
- **Custom cases:** 3/3 exact.
- **Targets:** 518 rows: 169 resolved, 34 weak, 315 unresolved. 5 rows have no grounded proposal and stay
  invalid.

**Decided.**
- **A20 (Breno), six safeguards:** workflow links are candidates; state per copy; resolved/weak/unresolved;
  provisional ceiling; mixed intent; offline replay.
- **A22 (agent): policy evidence rules.**
- **D12/D13:** post-audit-only and unobservable ids, re-checked against raw files by tests.

**Learned.**
- **Ownership of deleted accounts is the evidence limit, not a code gap.** There are 549 anchor rows for 550
  requests, so one-to-one holds. But deduction only fixes 212 requests: the windows span 1–3 days with ~10
  concurrent runs, and a fitted lag window forces just 69 more while leaving 13 targets with no candidate. Most
  unresolved cases are exactly this.
- **Policy is not the bottleneck.** Isolated from ownership, it reproduces 41/41 findings and 34/34 COMPLETE
  verifications with their citations.
- **Two of my fixtures let mutations survive (ERRORS #4).** Both were fixed and re-proven red.

## 2026-10-24 — S1+S2 (merged): contract and evaluator proven, every evidence file readable, $0.107

**Done.**
- **Contract core:** `contract.py` is the one home of ops, states and ranks. Measured: 193/193 sample steps legal, and the
  canonical sort reproduces 32/32 arrays (D6 holds).
- **Validator:** 23 violation codes, each with a fixture that fails for exactly that reason. sample_output: 0 violations.
- **Evaluator:** explicit denominators, joined by case_id. Self = 1.0, empty = 0.
- **Ingestion:** all 94 files → 7,604 Observations, 0 unparsed lines:
  - SQL runs in an authorizer sandbox;
  - JSON is dispatched by shape;
  - logs go through one tokenizer for 7 grammars plus a trace join;
  - PDFs via pypdf, at parity with pdftotext;
  - PNGs get a dual-model read.
- **Custom cases:** 3, from an independent subagent (sees only problem statement, contract and rules).

**Decided.**
- A16 (Breno): the ChatGPT transcript stays.
- A17 (agent): vision cache committed, with a cross-check read.
- D10: two sample resources are unobservable.
- D11: samples mix JSON key orders.
- A case-3 naming fix.

**Learned.**
- Absence in the samples is proven by *scope* (a snapshot covering the system without the row), not by mention. 4 of 75
  citations work that way, and S3's planner must cite like that.
- Recall against samples has a hard ceiling of 109/111 resources (D10). Chasing the last two would mean fabricating.
- The first cross-check counted only emails/ids, so two "agreeing" screens had 0–1 tokens. Widening it to references
  and file names gave 5 and 9 tokens, still in agreement. A check that compares empty sets is not a check.
- gemini-3.8-flash rejects MINIMAL thinking. The failed call was ledgered at its reservation.
- Error class 3: I overwrote an (empty) upstream stub without reading it.

**Next.** S3: the deterministic baseline on the samples.

## 2026-10-24 — S0: repo public on upstream, docs in place, Gemini proven for $0.0005

**Done.**
- Read the full upstream contract at `0eddbbd` and measured the dataset with scripts:
  - 518 targets, 32 samples with 0 NOT_APPLICABLE, 94 evidence files;
  - 82/111 sample resources explicitly linked to their subject in text sources;
  - 3–15 candidate accounts per request window.
- Two rounds of owner questions.
- Plan approved: `docs/plans/MASTER_PLAN.md`.
- Repo initialized on upstream with `.gitignore` first; `log.txt` started.

**Decided.**
- Breno decided: deadline 2026-10-25 07:00 CDT; public repo; spend autonomy to $4.50; ownership mode decided by
  metrics; English docs; 3(+2) custom cases; viewer last.
- Agent decided: lexicographic case_id sort (D5), deterministic evidence layer + tool-using investigator (A4).
- All decisions and triggers are in `docs/DECISIONS.md`.

**Found.** Some sample answers name resources (e.g. case_25 `account_3136`) whose owner is not stated next to any subject
identifier in participant text. This is the main correctness risk, and it is why A5 exists.

**Smoke (C0.5).** On `gemini-3.1-flash-lite` with `thinking_level=MINIMAL`:
- JSON schema: Spanish request → `authorizes_deletion: true`;
- function call `lookup_resource(account_3136)` with `thought_signature` present, then a final answer after the function response;
- PNG extraction exact.

Cost: 4 calls, 0 thought tokens, $0.0005345 (ledger: 8 rows).

**Found (ours).** `git reset --mixed` doesn't touch the working tree → ERRORS.md class 1.

**Not verified.** HackerRank page (login wall), so the upload form fields are unknown. Gemini rate limits are untested at concurrency > 1.

**Next.** S1: contract.py + validator + evaluator.
