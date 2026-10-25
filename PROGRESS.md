# Ghost Data Orchestrate — progress in flight

> Working file: describes the **current** session. Updated at every checkpoint. A delivered and answered
> handoff moves to `docs/HANDOFFS.md`, after relocating what lives only here (open decision → SESSIONS,
> lesson → ERRORS, constraint → PRIMER).

## ⏱ Live — S7 in progress (opened 2026-10-25 02:45 UTC; measured 03:40 UTC)

Plan and checkpoint log: `docs/plans/session-07.md` (Amendments + "Progress"). S7 = S7+S8 merged by Breno (A35).

| C | State | Evidence |
|---|---|---|
| C7.0 roadmap rewrite | ✅ 02:49Z | `439baea`, `c908cf9` (Breno's six amendments recorded) |
| C7.1 legacy workflow links | ✅ decided: **A34** (03:18:25Z) | `docs/diagnostics/s7/legacy_links.md` (backtest summary corrected 03:38Z: variants never pooled) |
| C7.1 follow-up: forced_matching | ⏳ **Breno's answer pending** (case_78/case_94 review in legacy_links.md) | config unchanged until he answers |
| C7.1T time policy | ✅ decided: **A36** snapshot_capture v2 | `temporal_interpretation.md` (written first, `8c58d55`), `temporal_experiment.md` |
| C7.2 provenance + viewer | ✅ 03:33Z; run binding to output.csv ✅ 03:39Z | `f21a996`, `8d83eb2`, `d6f75a2`; browser check: chromium 156, 1280/390 px |
| C7.3 packaging hardening | ✅ code + tests 03:36Z (`d84ae0c`); dry run on `runs/s7/det/targets` accepted | the release-candidate run is C7.4 |
| C7.4 integration + release candidate | next | |
| C7.5 docs (README, REQUIREMENTS_MAP, reports) | pending | |
| C7.6 Mac handoff + **Mac acceptance (Breno)** | pending | |
| C7.7 final artifacts, traces, checksums, freeze | pending | finalization order fixed by Breno (amendment 6) |

## ▶️ RESUME HERE — 2026-10-25 03:40 UTC — S7 between C7.3 and C7.4

**Settled; do not reopen** (DECISIONS):
- A34: assert only `only_feasible_row` and `forced_matching` (plus `corroborated_run`); `only_feasible_request` is an
  uncertain candidate; the nearest-anchor pick only fills an otherwise empty row, flagged HEURISTIC PREDICTION.
- A36: time policy `snapshot_capture` v2. Envelope-dated pre-audit snapshots are read and never cited.
- A35: viewer is a deliverable; freeze is last.

**Open, waiting for Breno:**
- whether `forced_matching` stays asserted (recommendation in the chat and in `legacy_links.md`). If he says
  demote, set `asserted_mechanisms = ["corroborated_run", "only_feasible_row", "nearest_anchor"]` in
  `code/config/default.toml`. Measured: targets case_78 and case_94 each lose one uncited future
  `VERIFY_RECORD_ABSENT`; samples unchanged.

**Current configuration** (`code/config/default.toml`): strict ownership (A33); `asserted_mechanisms` = corroborated_run,
only_feasible_row, forced_matching, nearest_anchor; `historical_snapshots = "snapshot_capture"`; agent scope
`non_resolved` (A28) via `--agent-scope`; model gemini-3.1-flash-lite.

**Measured combined result, deterministic** (`runs/s7/det`, 03:21Z; agent not yet run on this config):
- samples: status 32/32, whole-case 14/32, P 167/168, R 167/193, F1 0.9252, 0 violations (S6: 12/32, F1 0.9101);
- custom 5/5;
- targets: 0 violations, 59 rows differ from S6, 0 status flips;
- HEURISTIC PREDICTION rows: targets 4 (case_39/55/61 under A29, case_63 under A34).

The deterministic gains are separate from any agent contribution, which C7.4 measures.

**Packages:**
- **Fallback, untouched:** root `output.csv` sha256 `ee9504d5…8c4c` (= S5/S6 published rows) and `code.zip`
  `f58aaefe…` (S5 build). They stay as they are until C7.4 publishes a validated replacement.
- **Eventual release:** rebuilt in C7.4 from `runs/s7/final` with `scripts/package_code.py` (hardened), then frozen in
  C7.7.

**Next concrete action (C7.4):**
```
.venv/bin/python code/main.py run --engine agent --mode live --agent-scope non_resolved --split targets --out runs/s7/final
```
- Cache hits are free; only changed briefs pay. Estimate ≤ $0.35; hard stop $0.50 for C7.4.
- Then run the same for `--split samples` (`runs/s7/final-samples`) and the 5 custom cases, then validate and
  run `gate.py` vs S6.
- Then `package_code.py --run runs/s7/final` (fresh venv) → exit 0, publish root `output.csv` atomically, and
  regenerate `docs/explanations/`.

**Ledger:** settled $1.876497, outstanding $0.004997 (03:40Z). $0.00055 of that is a reservation left open by the C7.3
live-mode probe control; it was never sent.

**Tests:** `297 passed` (03:39Z). HEAD `d6f75a2`, pushed.

**Re-read, in order:**
1. AGENTS.md
2. docs/PRIMER.md
3. this block
4. docs/plans/session-07.md (Amendments, Progress)
5. DECISIONS A31–A36
6. docs/diagnostics/s7/legacy_links.md and temporal_experiment.md
7. ERRORS #4–#9

**Check before trusting:**
- `git status --short` and `git log -1`;
- `main.py status`;
- `pytest -q` → 297;
- `sha256sum output.csv` → `ee9504d5…`.

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
