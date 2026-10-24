# Ghost Data Orchestrate — progress in flight

> Working file: describes the **current** session. Updated at every checkpoint. A delivered and answered
> handoff moves to `docs/HANDOFFS.md`, after relocating what lives only here (open decision → SESSIONS,
> lesson → ERRORS, constraint → PRIMER).

## ⏱ Live — S3+S4 in progress (updated at each checkpoint)

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
- ▶️ Next: S4, C4.0 (see the resume block).

## ▶️ RESUME HERE — 2026-10-24 20:57 UTC (15:57 CDT) — S3 closed; S4 next (second half of S3+S4, A19)

**Repository state:** see the check list below. HEAD = the "Close S3" commit, pushed. Background runs: none.
Locks: none.

**State of the world (measured 20:55 UTC):** ledger settled $0.107400, outstanding $0. 141 tests passing.
Deadline 12:00 UTC (≈15 h); no intermediate target (A18).

**Current goal: S4.** A bounded Gemini investigator over the deterministic tools, plus the gateway (budget,
4xx settlement), cache, resume and offline replay, and the benchmark. It is measured against S3's baseline;
spend ≈ $0.30.

**Exact next step:**
1. Read the `integracoes` skill.
2. C4.0: create `code/ghostaudit/llm/gateway.py` + `code/tests/test_gateway.py`.
   - Settlement by error class: `ClientError` 400/401/403/404 → settle $0, `cost_basis="rejected_<code>"`, no
     retry; 429 → $0 + bounded retry; `ServerError` / timeout / unknown → reservation.
   - Use a fake provider that raises the real `google.genai.errors` classes (they carry `.code`).
   - Record A21.

**Baseline to beat (strict, full official denominators):**
- status 32/32; whole-case 11/32;
- steps: precision 161/162, recall 161/193; evidence on matched 161/161; cited recall 61/75.

Scored: whole-case 14/32; steps: precision 168/180, recall 168/193. Custom cases 3/3 exact.

**What the agent should work on (from S3 measurements):**
- **Unattributed accounts.** 338/550 requests have no deduction-forced primary-profile row. In scored mode
  the weak candidate is right 8 of 18 times on the samples.
- **5 target rows with no grounded proposal** (case_39, 46, 53, 55, 61).
- **Screen panels** that carry state but are read as presence only (the backup panel in case_55).
- Weak and unresolved rows are listed in `runs/<id>/unresolved.md`. A20 requires them to be investigated
  before publication.

**Don't forget (measured 2026-10-24):**
- **Remaining ambiguity, for Breno before S5:** the contract needs a status in each of the 518 rows. A row
  still unresolved after the agent carries the grounded proposal's status, flagged and never counted as
  resolved. The 5 rows with no proposal at all need a decision.
- **Replay** must never build a client or read `.env` (A20). `gemini._api_key()` reads `.env`, so the replay
  path must not call it.
- **Gemini:**
  - 3.8-flash rejects MINIMAL, so it runs at LOW;
  - keep `thought_signature` (append the model Content unchanged);
  - every call needs `max_output_tokens`.
- **The workflow assignment is global** (samples + targets in one solve). A run over a subset changes nothing
  for the others, but needs every request file loaded.

**Re-read, in this order:**
1. `AGENTS.md`
2. `docs/PRIMER.md` (the A20 boundary rows)
3. this block
4. `docs/plans/session-03-04.md` §Design — S4 + checkpoints C4.0–C4.6
5. `docs/DECISIONS.md` A6, A7, A10, A20–A22
6. skills `integracoes`, `testes-que-provam`
7. code: `llm/gemini.py`, `llm/ledger.py`, `runner.py`, `planner.py`, `ownership.py`

**Depends on Breno:** keep the session running unattended. Before S5: decide on the 5 rows that have no
grounded proposal.

**Before trusting this block, check:**
- `git status --short` → empty; `git rev-parse HEAD origin/main` → identical; `git log -1 --format=%s` starts
  "Close S3"
- `.venv/bin/python code/main.py status` → settled $0.107400, outstanding $0.000000
- `.venv/bin/python -m pytest code/tests -q` → `141 passed`
- `ls code/ghostaudit/llm` → no `gateway.py` yet

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
