# Diary — Ghost Data Orchestrate

> One entry per session, newest on top. Narrative: what was done, what was decided and **why**, and what was
> learned. State does not live here (see PROGRESS.md).

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
