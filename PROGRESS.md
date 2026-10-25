# Ghost Data Orchestrate — progress in flight

> Working file: describes the **current** session. Updated at every checkpoint. A delivered and answered
> handoff moves to `docs/HANDOFFS.md`, after relocating what lives only here (open decision → SESSIONS,
> lesson → ERRORS, constraint → PRIMER).

## ⏱ Live — S5 closed 2026-10-25 01:14 UTC

The checkpoint log, with every number and its time, is in `docs/plans/session-05.md` ("Progress"). This file
only points to it, so each fact has one source.

- **What S5 did:**
  - accuracy fixes before spend: A24, as-of ownership; A25, explicit state and row-bound screens; A26, two
    clocks; A27, agent lineage; A30, subject records link their sources;
  - the case-by-case harness (`compare.py`) and the diagnostics (`diagnose.py`);
  - the pilot;
  - Breno's decisions: A28, agent scope non_resolved; A29, flagged heuristic rows;
  - the final run, the reports, the package with the VPS check, the log corrections, the trace stager and the
    release kit.
- **Published locally, not committed (the repo is public):**
  - root `output.csv` = `runs/s5/final/output.csv` (sha256 `ee9504d517fb…`);
  - `code.zip` (sha256 `f58aaefe3c17…`).

## ▶️ RESUME HERE — 2026-10-25 01:14 UTC — S5 closed; S6 next

**Repository state:** HEAD = the "Close S5" commit, pushed. Background runs: none. Locks: none. Untracked on
purpose: `output.csv` (and `code.zip`, gitignored).

**State of the world (measured at the close):**
- **Ledger:** settled $1.870528, outstanding $0.004447 (the C4.5 kill), ceiling $4.50.
- **Tests:** 225 passing.
- **Log:** `log_audit.py` reports 19/19 human messages logged literally.
- **Deadline:** 12:00 UTC.

**Exact next step:** write `docs/plans/session-06.md` from `docs/SESSIONS.md` (S6: C6.1–C6.5). Start from
`code/evaluation/diagnostics.md`: 24 association mismatches, mostly accounts named only by worker rows (not
fixable without guessing) and ~6 anonymized analytics records. Look for a lineage the engine can see. Any fix
needs:
- a failing test first, and a mutation;
- `compare.py` showing no unexplained regression;
- a targeted re-run (fingerprints make it exact).

Then C6.5: `main.py explain <case>` from `decisions.jsonl` only.

**After every engine change:**
1. Re-run the final configuration:
   `main.py run --engine agent --mode live --agent-scope non_resolved --split targets --out runs/s6/final`.
   Cache hits make it cheap.
2. `validate`.
3. `scripts/make_reports.py` (arguments as in the S5 close; see `session-05.md` C5.9).
4. `scripts/package_code.py --run runs/s6/final` (must exit 0).
5. Re-publish root `output.csv` atomically only if all of these pass.

**Don't forget:**
- Times are typed only through `$(date)` (ERRORS #5, 9 occurrences).
- Chain the commit on the gate: `pytest -q && git commit`, never after a pipe (ERRORS #6).
- Run the scripts with `.venv/bin/python`; the system python has no deps.
- Kill by PID.
- `gh api …/actions/runs?head_sha=` for CI.
- Never commit `output.csv` or `code.zip` without Breno's OK (public repo).

**Depends on Breno:**
- whether `output.csv`/`code.zip` should ever be committed (default: no);
- `/export` of this session, then quit it, before the final trace copy;
- the upload;
- running the Mac check (S7 C7.7).

**Re-read, in this order:**
1. `AGENTS.md`
2. `docs/PRIMER.md`
3. this block
4. `docs/SESSIONS.md` (S6, S7)
5. `docs/plans/session-05.md` (Release kit; Progress)
6. `docs/DECISIONS.md` A24–A30
7. `code/evaluation/diagnostics.md`
8. skills `software-build`, `testes-que-provam`

**Before trusting this block, check:**
- `git status --short` → only `?? output.csv`;
- `git rev-parse HEAD origin/main` → equal; CI on that SHA green;
- `main.py status` → settled $1.870528;
- `pytest code/tests -q` → `225 passed`;
- `sha256sum output.csv` → `ee9504d517fb36f0af3c361bba833bf8129a5ae4a8a78d4efce448925b398c4c`.

## Proofs from S5

| Proof | Command | Result (literal) | When |
|---|---|---|---|
| suite | `pytest code/tests -q` | `225 passed` | 01:12Z |
| final run | `main.py run --engine agent --mode live --agent-scope non_resolved --split targets --out runs/s5/final` + validate | `518 rows`; `0 violations`; support 175/18/325 | 01:08Z (file mtime) |
| samples | `evaluation/main.py --pred runs/s5/final-samples2/output.csv` | status 32/32, whole 12/32, P 162/163, R 162/193 | 01:08Z (run mtime) |
| package | `scripts/package_code.py --run runs/s5/final` | `"identical": true`, `"network": "none (unshare -rn)"`, scan empty, 0 violations | 01:12Z |
| log | `scripts/analysis/log_audit.py` | `human messages 19, logged literally 19, not 0` | 01:12Z |
| traces | `scripts/stage_traces.py --dry-run` | `8 files; 0 redactions …; problems: none` | 2026-10-24, between commits c3cc0fc (22:23Z) and 092d700 (22:27Z) |


## Earlier — S3+S4 closed 2026-10-24 21:13 UTC (`79f33e4`); log of its checkpoints

- Plan: `docs/plans/session-03-04.md`, with Breno's six safeguards integrated after approval (A20: weak workflow
  links, copy-level state, resolved/weak/unresolved, provisional ceiling, mixed intent, offline replay). The 4xx
  policy is A21.
- ✅ C3.0 `cc3c490`: resource-id prefixes derived from the activity stream (14, equal to the record prefixes).
  The old hand-written gap changed no index.
- ✅ C3.1: `identity.py`, with identities rolled back to audit_at. Matching is exact normalized only, a shared
  address is an Ambiguity, names are weak, and the derived sha256 holds 850/850. 550/550 request emails resolve
  to exactly one user (32 samples + 518 targets). Mutation (prefix match) → decoy test red.
- ✅ C3.2: `temporal.CaseView` with an inclusive cutoff, and its accessors derived by introspection (8). Both
  mutations turn it red: no filter (2 fail) and an exclusive cutoff (1 fail). Suspected gaps re-checked by a
  literal byte search over 102 dataset files plus 22 vision extracts, pinned by 2 tests: D10/D13 have 0 hits;
  the D12 ids appear only in files captured after their audits.
- ✅ C3.3: `ownership.py`.
  - **One-to-one is measured, not assumed:** 539 worker primary-profile rows (all distinct accounts) + 10
    intake CLASSIFY_REQUEST rows = 549 anchors for 550 requests. The missing one is case_04 (D13).
  - **Assignment is deduction only:** explicit account (176), only feasible row (27), forced in every maximum
    matching (6), only feasible request (2), corroborated run (1). That makes 212/550 assigned; 338 stay
    ambiguous, because the windows span 1–3 days with ~10 concurrent runs.
  - **Text co-occurrence links only inside a unit that names this subject alone.** A multi-customer screen
    splits into rows; it had tied user_14's data_flow_1121 to case_15.
  - **Samples (full 111):**
    - strict: 78 found, 2 extras (object_19, tombstone_17, both the subject's own), accounts 13/32;
    - scored: 86 found, 16 extras, accounts 21/32. The weak ranked account is right 8 of 18 times, so it is
      never counted as resolved.
  - Tests: interleaved, repeated person, a tie in both modes, tiers and reasons preserved. The forcing
    mutation turns 3 tests red.
- ✅ C3.4: `policy.py`.
  - **Category:** taken from content and rules first; the worker's *action type* is a tie-break only (it
    matches the sample treatment family for 85/85 resources). A disagreement is unknown, and
    SECONDARY_IDENTIFIER is declared unmapped (no source).
  - **State per physical copy** (system × topology), plus business documents as copies. Scope absence applies
    to DELETE targets only, and never overrides a direct observation (a later bundle can be partial).
  - **Citation:** direct evidence over scope inference, the primary copy over other copies, then the latest.
  - **Samples, isolated from ownership:** 41/41 findings and 34/34 COMPLETE verifications, verdict + op +
    citation. The 7 unknowns are exactly the D10/D12 ids.
  - **Mutations:** per-copy (M6), wrapper (M3) and claims (M4) all go red, the last two after strengthening
    the fixtures (ERRORS #4).
- ✅ C3.5: `intent.py` (508 deletion + 10 NA on the targets; mixed-intent tests in 5 languages; mutation red),
  `planner.py` (resolved / weak / unresolved), `runner.py`, `main.py run`. Baseline in DIARY. **S3 closed.**
- ✅ C4.0 + C4.1: `llm/gateway.py`.
  - Settlement by error class (A21), checked with the SDK's real `ClientError`/`ServerError`: 400/401/403/404
    → $0, not retried; 429 → $0 + retry; 5xx/timeout/transport → reservation + finite retry.
  - Budget refusal before sending, and 8 concurrent threads never overspend.
  - A response cache keyed by request hash.
  - Replay builds no provider and reads no key (the test patches `genai.Client`, `_api_key` and `socket` to
    fail, with the env key set); a miss is `ReplayMiss` with the ledger unchanged.
  - `gemini.py` is now a lazy provider (90 s timeout, SDK retries off); `generate_content` appears only there.
  - Mutations M5 (5xx at $0) and M8 (replay fall-through) both go red. 156 tests passing.
- ✅ C4.2: `tools.py`, 9 read-only tools over the CaseView.
  - Declarations are derived from the registry; each result carries obs_ids, and the session's `seen` set is
    what the agent may cite. Activity rows are labelled as claims.
  - Search is exact-value, paginated with an omitted count.
  - 16 tests: cutoff in every tool (derived from the registry), pagination, look-alikes, bad arguments.
    Mutation (bypass the view) goes red. 172 tests passing.
- ✅ C4.3: `agent.py` + `code/prompts/investigator.md` + `main.py run --engine agent --mode live|replay
  --cases`.
  - The model can only choose the account, exclude, or add (each citing obs_ids a tool returned); the engine
    recompiles. 4 offline loop tests cover submit, repair, exhausted repairs and a provider error.
  - **Live case_28** (flash-lite): 4 tool calls → submit_audit → a valid row. 5 calls, $0.004143, all
    settled. The agent left the account null ("none of the candidate accounts could be definitively linked"):
    honest, unresolved.
  - Replay without a key: byte-identical, 5 cache hits, ledger unchanged.
- ✅ C4.4: `intent.classify_all`: batches of 20 on flash-lite, cross-checked with the rule; a disagreement
  gets a 3.8-flash recheck, and a remaining disagreement is low confidence (weak).
  - **Live:** 32/32 samples are deletion; 14/14 hand-written fixtures (7 mixed-intent, 7 non-deletion, 5
    languages) correct; $0.0045.
  - **Targets:** 518/518 rule = LLM (508 deletion, 10 NA, all high), $0.0497, cached for the full run.
- ✅ C4.5: a real kill after 4/10 cases + resume → 0 duplicate paid calls (79 keyed); offline replay
  byte-identical; offline resume test + mutation.
- ✅ C4.6: benchmark 10 × 2 models → flash-lite kept (A23); the agent ≈ the baseline. **S4 closed.**
- ▶️ Next: S5 (see the resume block).

## Proofs from S4

| Proof | Command | Result (literal) | When |
|---|---|---|---|
| gateway | `pytest code/tests/test_gateway.py -q` | `15 passed`; mutations M5, M8 red | 21:00Z |
| live agent | `main.py run --engine agent --mode live --cases case_28` | `submitted 1, model_calls 5, cost_usd_x1e6 4143` | 21:04Z |
| intent | `scripts/intent_check.py`; targets batch | `samples deletion 32/32; fixtures right 14/14`; targets `(True,'high'): 508, (False,'high'): 10` | 21:06Z |
| resume | kill after 4 cases, then rerun the same `--out` | `resumed 4, submitted 6`; `duplicates: 0` over 79 keyed calls | ≤21:13Z |
| replay | `env -u GEMINI_API_KEY main.py run --engine agent --mode replay …` + `cmp` | `cache_hits 49`, `replay byte-identical (10 cases)` | ≤21:13Z |
| benchmark | 10 cases × {lite, flash} | see A23 | ≤21:13Z |
| suite | `pytest code/tests -q` | `177 passed` | 21:13Z |

## Proofs from S3

| Proof | Command | Result (literal) | When |
|---|---|---|---|
| suite | `pytest code/tests -q` | `141 passed` | 20:55Z |
| samples run | `main.py run --split samples --out runs/s3/samples-strict` + `main.py validate … --split samples` | `32 rows`; `0 violations … against 32 samples requests` | 20:52Z |
| baseline | `evaluation/main.py --pred runs/s3/samples-strict/output.csv` | status `32/32`, step P `161/162`, R `161/193`, evidence `161/161`, whole `11/32` | 20:52Z |
| targets run | `main.py run --split targets` + validate | `518 rows`; support resolved 169 / weak 34 / unresolved 315; `5 violations` (DECIDED_EMPTY, listed) | 20:53Z |
| custom | engine on 3 custom datasets | whole-case `1/1` each | 20:54Z |
| mutations | prefix email / no cutoff / exclusive cutoff / forcing / per-copy / wrapper / claims / intent precedence | each red, then restored (`cmp`) | 20:31–20:51Z |

## Proofs from S1+S2

| Proof | Command | Result (literal) | When |
|---|---|---|---|
| contract | `pytest code/tests/test_contract.py -q` | `8 passed` (193/193 legal, 32/32 canonical) | 19:56Z |
| validator | `main.py validate dataset/sample_output.csv --split samples` | `0 violations in dataset/sample_output.csv against 32 samples requests` | 19:55Z |
| evaluator | `evaluation/main.py --pred dataset/sample_output.csv` | every metric `1.0000` (32/32, 193/193, 75/75) | 19:57Z |
| ingest | `main.py ingest --allow-paid --report` | `94 files, 7604 observations, 94 processed, 0 partial, 0 failed` | 20:03Z |
| cache rerun | `main.py ingest` then `main.py status` | ledger rows 54 → 54 | 20:05Z |
| suite | `pytest code/tests -q` | `78 passed` | 20:12Z |
| mutations | rank swap / exclusive cutoff / no ATTACH deny / wrapper→fields | each 1+ test red, then restored green | 19:56–20:08Z |

## Proofs from S0

| Proof | Command | Result (literal) | When |
|---|---|---|---|
| upstream base | `git log --oneline -2` | `d4a8432 Add .gitignore…` / `0eddbbd Update AGENTS.md` | 16:52Z |
| ignores | `git check-ignore .env runs/ .venv/` | `.env` `runs/` `.venv/` | 16:52Z |
| log format | header / tool= / model= / secret counts | 6 / 6 / 6 / 0 | 16:52Z |
| deps | import check | genai 2.33.0, pypdf 6.21.2, pydantic 2.14.1, pytest 9.1.1 | 17:05Z |
| remote | `gh repo view … --json visibility`; `git rev-parse HEAD origin/main` | `PUBLIC`; both equal | 17:20Z |
| smoke | `.venv/bin/python scripts/smoke_gemini.py` | a: `{"authorizes_deletion": true, "language": "es"}`; b: `lookup_resource(account_3136)`, thought_signature true; c: `user_11`/`account_5762` exact; settled $0.0005345 | 17:10Z |
| link audit | `python3 -I scripts/analysis/linkaudit.py dataset` | `sample resources 111 with explicit co-occurring subject link 82` | 19:46Z |
