# Roadmap — Ghost Data Orchestrate

Each session is a 1–2.5 h package that ends in something verifiable, plus a diary entry. Full checkpoint text
(command → expected number, 🐞 predicted defect) lives in `docs/plans/MASTER_PLAN.md`. This file holds the
**state**, and any change to a checkpoint is noted here with a date and reason.

**Progress: 5 of 8 sessions fully closed** (✅: S0, S1, S2, S3, S4; measured 2026-10-24 21:13 UTC). Partial (🔄) counts as partial.

> **Order notes.** The order follows data dependency, not showcase value. The contract/evaluator (S1) comes before
> ingestion because every later step is measured with it. The deterministic baseline (S3) comes before the agent (S4)
> so that the agent is measured against something. Viewer last (owner).
>
> **2026-10-24 19:46 UTC: S1 + S2 merged (Breno).** One session plan, `docs/plans/session-01-02.md`, still has
> checkpoints C1.1–C1.4 then C2.1–C2.6 in that order. The reason is speed: S0 closed at ~17:25 UTC, but S1 had not
> started by 19:46 UTC, so the schedule had slipped ~1h45.

> **2026-10-24 20:16 UTC: S3 + S4 merged (Breno, A19), executed one at a time.** One plan file,
> `docs/plans/session-03-04.md`; C3.1–C3.5 all close (baseline measured on the samples) before C4.1 starts.

## ▶️ Start the next session here

- Session: **S5 — pilot, full run, reports, safety package** — first step: write `docs/plans/session-05.md`. Then
  C5.1, the pilot on 30 stratified targets with `main.py run --engine agent`, measuring $/case. Also decide
  whether resolved cases skip the agent: the full projection is ≈$1.83 against a $1.75 envelope.
- Read first: `docs/PRIMER.md`, `PROGRESS.md`, `docs/plans/session-03-04.md` (outcomes), DECISIONS A20–A23
- Depends on Breno: before leaving, keep the session running with unattended permissions (Bash/Edit)

Timeline as approved (UTC; CDT = UTC−5): S0 16:50–18:00 · S1 18:00–19:00 · S2 19:00–21:00 · S3 21:00–23:00 ·
S4 23:00–01:30 · S5 01:30–04:00 **safety package** · S6 04:00–07:30 · S7 07:30–09:00 **freeze** ·
S8 optional · upload ≈10:00 · deadline 12:00.

**Re-timed 2026-10-24 19:46 UTC (proposed by the agent, awaiting Breno's confirmation):** S1+S2 19:50–22:50 ·
S3 22:50–00:50 · S4 00:50–03:20 · S5 03:20–05:30 **safety package (00:30 CDT)** · S6 05:30–07:30 (shrunk) ·
S7 07:30–09:00 **freeze unchanged** · upload ≈10:00 · deadline 12:00.
Cut order if late: S6 scope → +2 custom cases → S8. S5 and S7 are never cut.

**2026-10-24 20:15 UTC: S1+S2 closed at ~20:15**, ≈2h35 ahead of the re-timed plan and ≈45 min ahead of the original
(S2 was due 21:00). Proposal: run S3 now and keep the original 04:00 UTC safety-package target as the goal, with the
re-timed 05:30 UTC as the fallback. **Breno, 20:20 UTC (A18): no fixed time target for now — keep working.**

---

## Block A — Foundations

### ✅ S0 — Setup, logging, docs, smoke · spent $0.0005345
- [x] C0.1 git init on upstream `0eddbbd`, upstream push disabled, `.gitignore` committed first
- [x] C0.2 log.txt started (SESSION START + planning turns)
- [x] C0.3 docs created (PRIMER, SESSIONS, PROGRESS, DIARY, ERRORS, DECISIONS, STATUS, REQUIREMENTS_MAP)
- [x] C0.4 venv + pinned requirements
- [x] C0.5 Gemini smoke: JSON schema, function call round trip, one PNG; ledger rows — all 3 pass on 3.1-flash-lite, $0.0005345
- [x] C0.6 public remote created and pushed; no secrets tracked — https://github.com/Zbreno11-git/ghost_data_orchestrate @ 54a7673
- [x] C0.7 project memory saved

### ✅ S1 — Contract core + evaluator · $0 (merged with S2) · `ac17988`, `600715a`
- [x] C1.1 contract tables (193/193 sample steps legal)
- [x] C1.2 canonical sort reproduces 32/32 sample arrays — *changed 2026-10-24: byte-identical serialization is impossible (D11); 32/32 semantic + 24/24 byte*
- [x] C1.3 validator: 23 codes, each with a fixture rejected for exactly that code (incl. DUPLICATE_STEP added in review); sample_output 0 violations
- [x] C1.4 evaluator: self = 1.0 on every metric (32/193/75), empty = 0, join by case_id

### ✅ S2 — Ingestion + evidence store · spent $0.1069 · `c729b3f`
- [x] C2.1 manifest + CSVs, 94/94 paths (traversal guard), tables 518/32/850/306/4011/15
- [x] C2.2 SQL 24/24, ATTACH and non-foreign_keys PRAGMAs denied
- [x] C2.3 JSON 28/28 (4 shapes), wrapper fields tagged
- [x] C2.4 logs 26/26, 7 grammars, trace join, 0 unparsed lines
- [x] C2.5 PDF 4/4 (pypdf = pdftotext identifiers), TXT 1/1, PNG 11/11 dual-read agree; rerun = 0 paid calls
- [x] C2.6 coverage 94/94 processed; 75/75 citations grounded (71 mention + 4 scope) — *changed 2026-10-24: 111/111 resources is unreachable; 108 indexed + account_004 absence-by-scope + 2 unobservable (D10)*
- [x] side: 3 custom cases (independent subagent), each validates 0 and ingests cleanly

## Block B — First end-to-end

### ✅ S3 — Identity, time, ownership, policy, planner → deterministic baseline · $0 · `cc3c490`…S3 close
> **Changed 2026-10-24 ~20:29 UTC (Breno, A20):** six safeguards added to the acceptance criteria (see `docs/plans/session-03-04.md`).
- [x] C3.0 resource-id prefixes derived from the data (added at planning: the S2 pattern was hand-written)
- [x] C3.1 identity fixed point: 550/550 request emails → one user; decoy excluded (mutation red)
- [x] C3.2 cutoff in CaseView, accessors derived by introspection; suspected gaps re-checked against raw files
- [x] C3.3 ownership tiers: explicit + deduction-only workflow; ties never forced; strict 78/111, scored 86/111
- [x] C3.4 policy per physical copy: 41/41 findings + 34/34 COMPLETE verifications incl. citation
- [x] C3.5 deterministic run: samples 32 rows, 0 violations; baseline in DIARY; targets 518 rows (5 without a grounded proposal, listed)

### ✅ S4 — Agent loop + gateway/ledger/cache/resume/replay · spent $0.2317 (+$0.0044 open) · `8a0683c`…S4 close
- [x] C4.0 4xx settlement by error class (A21), with the SDK's real error classes
- [x] C4.1 gateway: budget refusal before sending; 8 concurrent threads never overspend; SDK confined to `gemini.py`
- [x] C4.2 9 tools, cutoff in each (derived from the registry), pagination with omitted counts
- [x] C4.3 live case_28: 4 tool calls → submit → valid row ($0.0041)
- [x] C4.4 intent: samples 32/32, fixtures 14/14 (5 languages), targets rule = LLM 518/518
- [x] C4.5 real kill + resume: 0 duplicate paid calls; offline replay byte-identical (10 cases)
- [x] C4.6 benchmark 10 × 2 models: flash-lite kept (A23); the agent ≈ the baseline

### ⬜ S5 — Pilot, full run, 3 custom cases, reports, SAFETY PACKAGE · ≈$1.75 · due 04:00 UTC
- [ ] C5.1 pilot projection ≤ $1.50
- [ ] C5.2 518 valid rows; unresolved count
- [ ] C5.3 evaluation_report.md with real metrics
- [ ] C5.4 usage_report.md from the ledger
- [ ] C5.5 package + clean-unpack replay identical (incl. `code/README.md` as source + root `README.md` pointer, D2) — *added 2026-10-24 at S0 close: README pointer had no checkpoint home*
- [ ] C5.6 committed/pushed; STATUS upload instructions

## Block C — Improve and release

### ⬜ S6 — Measured improvement · ≈$1.00
- [ ] C6.1 mismatch table by error class
- [ ] C6.2 each fix: failing-then-passing test (+ ERRORS.md when ours)
- [ ] C6.3 ownership mode chosen by metrics
- [ ] C6.4 targeted rerun only of invalidated cases
- [ ] +2 custom cases if few sample fixes remain

### ⬜ S7 — Release freeze · ≤$0.80 · freeze 09:00 UTC
- [ ] C7.1 final run or replay; validator; atomic output.csv
- [ ] C7.2 reports regenerated; README verified from clean unpack
- [ ] C7.3 traces staged outside repo; redaction scan 0 hits
- [ ] C7.4 STATUS upload checklist

### ⬜ S8 — Optional static evidence viewer · $0
> **Written trigger:** starts only if S7 is frozen with ≥ 2 h to the deadline; must not modify frozen artifacts.
