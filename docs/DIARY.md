# Diary — Ghost Data Orchestrate

> One entry per session, newest on top. Narrative: what was done, what was decided and **why**, and what was
> learned. State does not live here (see PROGRESS.md).

## 2026-10-25 — S7 (S7+S8 merged): owner-decided accuracy, provenance and viewer, hardening, two-machine acceptance; $0.39

**Done.** Breno merged S7 and S8 (A35) and amended the plan with six safeguards before any measuring.
- **Two bounded accuracy investigations, decided by Breno on measured alternatives:**
  - legacy workflow accounts, via a masked-identity backtest whose variants are never pooled (A34, A34a);
  - a snapshot time policy whose interpretation was written before measuring; v1 was rejected by its own numbers,
    and v2 adopted (A36).
  - Samples: whole-case 12→14, F1 0.9101→0.9252, 0 correct steps lost, 0 flips.
- **Provenance saved with the run, bound to `output.csv`,** verified before anything is shown. An offline
  single-file viewer shares one representation with `explain`.
- **Packaging hardened.** It checks exact report paths, isolation stated truthfully, a pinned fixture allowlist,
  a token-boundary credential rule, and that a refused build never replaces the release.
- **Final run paid exactly the 82 predicted cases ($0.353).** Every later re-run was free and byte-identical.
- **Mac acceptance passed** on a different OS, CPU and Python.
- **The finalize script was rehearsed end to end** before Breno runs it.

**Decided, and why.** A34/A34a/A36 are owner decisions on presented numbers, each with its selection bias or
contract ambiguity stated. No aggregate score was used to recommend them.

**Learned.**
- ERRORS #10 struck twice in one session: a stage that rebuilds an object drops whatever it does not copy. The
  second fix is a test derived from the dataclass fields, not one more re-applied label.
- A rehearsal finds what unit tests miss: the trace guard counted an export as a session, and the test that
  should have caught it read the real home folder.
- Typed times were wrong three more times; every one was caught by reading the commit or the JSONL.

## 2026-10-25 — S6: audits before fixes; one engine defect found by an independent case; rows unchanged; $0.006

**Done.** Breno strengthened S6 mid-turn: recover evidence-backed missing steps without losing precision, never
link from timing, naming, labels or one-to-one assumptions, and measure everything against a frozen S5 baseline.
- **Extraction audit:** every decoded line naming a resource matches an observation; screenshots read by eye.
  Our evaluator's "absent" verdict was a raw-byte search blind to compressed PDFs (ERRORS #8); fixed.
- **Association paths to the break point:** the 24 sample misses rest on anonymous records (21) or on lineage
  captured after the cutoff (3). The honest conclusion was "no link", so no rule was written.
- **Trace + explain** built early, then used to read the misses; metamorphic tests added (each with a control —
  which caught two hollow first versions).
- **Ownership mode** chosen by a criterion written before measuring: strict stays (A33). A tempting non-timing signal,
  status compatibility, was rejected under Breno's rule (A32).
- **Two independent custom cases**, written blind by a subagent: the deterministic engine passed both on first run;
  the agent failed one by naming a tombstone as the account, which would have planned deleting a kept record. Fixed
  (ERRORS #9); replay then showed that rewording a rejection breaks cached repairs, and the check order was fixed.
- **Final:** replay reproduces the published output byte for byte at $0; gate shows no change on samples, 5/5 custom.

**Decided, and why.** A32 rejected and A33 kept, each with its numbers. The rule: a session that finds nothing
fixable says so with the checks that prove it, instead of shipping a rule the evidence does not support.

**Learned.** Independent cases find what tuned samples cannot (the tombstone defect had no sample). Positive controls
are cheap and catch fixtures that never reach the engine.

## 2026-10-25 — S5: accuracy before spend, owner decisions, final run, reports, proven package, $1.53

**Done.** The six additions Breno sent at the start (plus five amendments, a temporal check and a roadmap
request mid-session) reordered S5: fix what the evidence says before paying the model to look at it.
- **Measured why rows are not resolved.** 342 of 349 non-resolved targets fail on account attribution, which the
  data cannot settle: the activity stream has no run identifier.
- **Fixed what was fixable, each with a red-first test and a mutation:**
  - ownership and the account solver evaluated as of each cutoff (A24; 16 target accounts deduced from later
    information became honestly ambiguous);
  - explicit state results that the engine ignored, and screens treated as copies of processes (A25);
  - table rows that leaked across customers, for links, state and decoys alike;
  - the two clocks (A26; 4 investigated flips to COMPLETE);
  - agent decisions gated by lineage (A27).
- **Built the measuring tools:** compare.py separates "not in the answer" from "unsupported"; diagnose.py gives
  each sample mismatch its earliest cause.
- **Pilot:** the validated agent changed nothing on 40 measured cases. Breno chose to run it on weak and
  unresolved cases only (A28), and to publish three unsettleable rows as flagged heuristic predictions (A29).
- **Final run:** 518 rows, 0 violations; samples 12/32 whole-case (S3: 11/32), with nothing removed. The one gain
  came from the agent's single real find, which A30 then generalized into the engine at $0.
- **Package:** proven from a clean unpack with no network.
- **Log:** corrected by appended records from the session JSONL.

**Decided, and why.** A24–A30, each with its measurement in DECISIONS. The rule behind all of them: a verdict
the evidence does not support is reported as such (weak, unresolved, heuristic), never filled to look complete.

**Learned.**
- An agent that "improves" the score can be taking a shortcut: case_07 → account_007, citing a page that never
  names it. Validating what a citation *establishes* turned the S4 "+1" into 0, and made the real +1 (case_06)
  visible.
- Six timestamps typed from memory in one session made the rule into structure (`$(date)` only; ERRORS #5).
- A commit chained after a failing gate (ERRORS #6) and a tool that passed on an empty input (ERRORS #7) are new
  classes.

**Spent.** $1.531410 this session (ledger $0.339118 → $1.870528; $0.004447 still open from S4), of which the
two full runs were $1.274.

## 2026-10-24 — S4 (second half of S3+S4): gateway, agent, intent, resume/replay, benchmark, $0.237

**Done.**
- **Gateway:** paid calls settle by error class (A21); a budget refusal happens before sending; responses are
  cached; replay can't reach the provider (A20).
- **Agent:** 9 read-only tools and a bounded investigator. It can only pick, exclude or add resources, citing
  evidence a tool returned.
- **Intent:** the LLM half, cross-checked with the rule.
- **Resume:** proven by a real kill (0 duplicate paid calls).
- **Benchmark:** 10 cases × 2 models.
- **Spend:** S4 spent $0.2317 settled (+ $0.0044 open from the deliberate kill). Project: $0.339 settled.

**Decided.** A21 (settlement policy), A23 (flash-lite stays).

**Learned.**
- **The agent is honest but barely moves the score** (+1 exact case of 10 on flash-lite, 0 on 3.8-flash).
  The remaining error is the unattributable deleted account, and the agent rightly refuses to guess it. A
  model can't add evidence that isn't there; S6 decides whether the agent earns its cost (A4 trigger).
- **`pkill -f <pattern>` matched my own shell** (exit 144). Pattern-killing is unsafe when the pattern
  appears in the calling command line; kill by PID instead.
- **`gh run list` printed nothing from this shell** while the API listed every run. CI is checked through
  `gh api …/actions/runs` and the headSha.

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
