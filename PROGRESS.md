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

## ▶️ RESUME HERE — 2026-10-25 01:22 UTC — before a compact; S5 closed; S6 next

**Repository state:** HEAD = the "Checkpoint before compact (S6" commit, pushed; the tree is clean. Root
`output.csv` is gitignored on purpose (A31), and `code.zip` is gitignored (`*.zip`). Background runs: none.
Locks: none held. `state/usage_ledger.lock` is the ledger's persistent, gitignored lock file, not a held lock.

**State of the world (measured 2026-10-25 01:22 UTC):**
- **Ledger:** settled $1.870528, outstanding $0.004447 (the S4 C4.5 kill), ceiling $4.50, $2.63 of headroom.
- **Tests:** `225 passed`. CI green on `a61b4a8` ("Close S5", 01:16:19Z).
- **Published locally** (A31: not uploaded, not committed):
  - `output.csv` (sha256 `ee9504d517fb36f0af3c361bba833bf8129a5ae4a8a78d4efce448925b398c4c`) = `runs/s5/final/output.csv`;
  - `code.zip` (sha256 `f58aaefe3c174a9ea1919aeb62f5fd07089f6d57d0913d27b9618a512c56ecff`).
- **Deadline** 12:00 UTC (≈10.6 h at 2026-10-25 01:22 UTC). MASTER_PLAN: freeze 09:00 UTC; Breno uploads ≈10:00 UTC.

**Current goal: S6 — measured improvement** (`docs/SESSIONS.md` § S6: C6.1–C6.5). Owner instruction
(A31, 01:21:40 UTC): finish all the sessions and solve the full problem first. The export and upload come only at
the very end.

**Exact next step:**
1. Write `docs/plans/session-06.md` (skill format: checkpoint map, then Does / ✅ / 🐞 per checkpoint) from
   SESSIONS § S6.
2. C6.1 starts from `code/evaluation/diagnostics.md`. 32 sample mismatches:
   - 24 identity/resource association: 17 account steps (16 missing accounts named only by deletion-worker rows,
     plus 1 extra, account_3865 in case_04) and 7 missing anonymized analytics records (counted from the file at
     01:23Z);
   - 5 post-audit only (D12);
   - 3 absent from the supplied evidence (D10/D13).

   Measure for each association miss whether *any* admissible observation names the resource together with
   something already tied to the subject (an account id, an order, a ticket, a hash), using
   `diagnose.py`'s World plus the store.
3. Fix only a generic lineage the evidence shows. Each fix needs:
   - a failing test first, and a mutation red;
   - `compare.py` with no unexplained regression;
   - `diagnose.py` before/after.
4. C6.3: choose the ownership mode by metrics. Strict vs scored are both measurable now with `compare.py`.
5. C6.5: `main.py explain <case> --run <dir> [--md]` from `decisions.jsonl` + provenance, with no LLM call.
   Examples: COMPLETE, INCOMPLETE, NOT_APPLICABLE, unresolved, heuristic.
6. Then S7 (`SESSIONS` § S7: C7.1–C7.7): release record, replay vs paid instructions, Mac runbook, interview
   cheat sheet. The Mac check (C7.7) stays pending until it is run on the Mac.

**Re-publication recipe after any engine change** (all from the repo root, with `.venv/bin/python`):
1. `code/main.py run --engine agent --mode live --agent-scope non_resolved --split targets --out runs/s6/final`
   (cache hits make it cheap; a changed brief pays about $0.0035).
2. `code/main.py validate runs/s6/final/output.csv` → `0 violations`.
3. Samples and custom cases, same flags, into `runs/s6/final-samples` and
   `runs/s6/final-custom-<name>` (`--dataset code/evaluation/custom_cases/<name>/dataset --split targets`).
4. `code/evaluation/diagnose.py --run runs/s6/final-samples --before runs/s3/samples-strict`.
5. `scripts/make_reports.py --final runs/s6/final --samples runs/s6/final-samples --custom runs/s6/final-custom-* --compare "<base>:<cand>:<label>" …`
6. `scripts/package_code.py --run runs/s6/final` (must exit 0).
7. Atomic copy to root `output.csv`.

**S5 numbers to beat (2026-10-25 01:08Z):**
- samples: status 32/32, whole-case 12/32, steps P 162/163, R 162/193, cited recall 61/75;
- custom: 3/3;
- targets: 175 resolved / 18 weak / 325 unresolved, 0 violations.

**Don't forget:**
- Times only through `$(date)` or the JSONL (ERRORS #5, 9 occurrences).
- `pytest -q && git commit`, never after a pipe (ERRORS #6).
- An empty result is a failure (ERRORS #7).
- `.venv/bin/python` for every script (the system python has no deps).
- Kill by PID.
- CI through `gh api repos/Zbreno11-git/ghost_data_orchestrate/actions/runs?head_sha=<sha>`.
- Never commit `output.csv` or `code.zip` (public repo, A31).
- The prediction path never reads `sample_output.csv` (grep gate). Evaluator scripts may.
- Agent decisions need a lineage (A27). Heuristic rows stay labelled and unresolved (A29).

**Depends on Breno:**
- at the very end only (A31): `/export` this session into `~/agent-trace/claude-code/` and quit, then
  `stage_traces.py --zip`, then the upload;
- the Mac check (C7.7), run on his Mac;
- whether `output.csv`/`code.zip` should ever be committed (default: no).

**Re-read, in this order:**
1. `AGENTS.md`
2. `docs/PRIMER.md`
3. this block
4. `docs/SESSIONS.md` § S6 and § S7
5. `docs/plans/MASTER_PLAN.md` § S6, § S7
6. `docs/plans/session-05.md` (Progress, Release kit, Amendments 2)
7. `docs/DECISIONS.md` A24–A31
8. `code/evaluation/diagnostics.md`
9. `docs/ERRORS.md` #4–#7
10. skills `software-build`, `testes-que-provam`, `falha-ruidosa`

**Before trusting this block, check:**
- `git status --short` → empty; `git rev-parse HEAD origin/main` → equal; the subject starts
  "Checkpoint before compact (S6"; CI green on that SHA;
- `.venv/bin/python code/main.py status` → settled $1.870528, outstanding $0.004447;
- `.venv/bin/python -m pytest code/tests -q` → `225 passed`;
- `sha256sum output.csv` → `ee9504d5…8c4c` (above); `ls docs/plans/session-06.md` → not there yet.

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
