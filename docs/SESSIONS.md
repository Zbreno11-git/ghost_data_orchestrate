# Roadmap — Ghost Data Orchestrate

Each session is a 1–2.5 h package that ends in something verifiable, plus a diary entry. Full checkpoint text
(command → expected number, 🐞 predicted defect) lives in `docs/plans/MASTER_PLAN.md`. This file holds the
**state**, and any change to a checkpoint is noted here with a date and reason.

**Progress: 0 of 8 sessions fully closed** (✅). Partial (🔄) counts as partial.

> **Order notes.** The order follows data dependency, not showcase value. The contract/evaluator (S1) comes before
> ingestion because every later step is measured with it. The deterministic baseline (S3) comes before the agent (S4)
> so that the agent is measured against something. Viewer last (owner).

## ▶️ Start the next session here

- Session: S0 (in progress) — see `PROGRESS.md` ▶️ RESUME HERE
- Read first: `docs/PRIMER.md`, `PROGRESS.md`
- Depends on Breno: before leaving, keep the session running with unattended permissions (Bash/Edit)

Timeline (UTC; CDT = UTC−5): S0 16:50–18:00 · S1 18:00–19:00 · S2 19:00–21:00 · S3 21:00–23:00 ·
S4 23:00–01:30 · S5 01:30–04:00 **safety package** · S6 04:00–07:30 · S7 07:30–09:00 **freeze** ·
S8 optional · upload ≈10:00 · deadline 12:00.
Cut order if late: S6 scope → +2 custom cases → S8. S5 and S7 are never cut.

---

## Block A — Foundations

### 🔄 S0 — Setup, logging, docs, smoke · $0.05
- [x] C0.1 git init on upstream `0eddbbd`, upstream push disabled, `.gitignore` committed first
- [x] C0.2 log.txt started (SESSION START + planning turns)
- [x] C0.3 docs created (PRIMER, SESSIONS, PROGRESS, DIARY, ERRORS, DECISIONS, STATUS, REQUIREMENTS_MAP)
- [x] C0.4 venv + pinned requirements
- [x] C0.5 Gemini smoke: JSON schema, function call round trip, one PNG; ledger rows — all 3 pass on 3.1-flash-lite, $0.0005345
- [ ] C0.6 public remote created and pushed; no secrets tracked
- [ ] C0.7 project memory saved

### ⬜ S1 — Contract core + evaluator · $0
- [ ] C1.1 contract tables (193/193 sample steps legal)
- [ ] C1.2 canonical sort reproduces 32/32 sample arrays
- [ ] C1.3 validator rejects ≥9 malformed fixtures for the named reason
- [ ] C1.4 evaluator metrics with defined denominators (self = 1.0, empty = 0)

### ⬜ S2 — Ingestion + evidence store · ≈$0.10
- [ ] C2.1 manifest + CSVs, 94/94 paths
- [ ] C2.2 SQL 24/24, ATTACH denied
- [ ] C2.3 JSON 28/28, wrapper fields tagged
- [ ] C2.4 logs 26/26, trace_id join, unparsed count
- [ ] C2.5 PDF 4/4, TXT 1/1, PNG 11/11 (cached, rerun = 0 paid calls)
- [ ] C2.6 coverage report 94/94
- [ ] side: subagent authors 3 custom cases (independent)

## Block B — First end-to-end

### ⬜ S3 — Identity, time, ownership, policy, planner → deterministic baseline · $0
- [ ] C3.1 identity fixed point (historical alias found, decoy excluded)
- [ ] C3.2 cutoff enforced in tool layer
- [ ] C3.3 ownership link strength + strict/scored report
- [ ] C3.4 policy registry tests
- [ ] C3.5 deterministic run validates 32/32; baseline metrics in DIARY

### ⬜ S4 — Agent loop + gateway/ledger/cache/resume/replay · ≈$0.30
- [ ] C4.1 gateway budget refusal + concurrent reservation test
- [ ] C4.2 tools with cutoff + pagination
- [ ] C4.3 one live case: tool choice → submit → canonical output
- [ ] C4.4 intent: 32/32 samples deletion, custom NA phrasings NA
- [ ] C4.5 resume = 0 duplicate paid calls; replay byte-identical with no key
- [ ] C4.6 model benchmark recorded

### ⬜ S5 — Pilot, full run, 3 custom cases, reports, SAFETY PACKAGE · ≈$1.75 · due 04:00 UTC
- [ ] C5.1 pilot projection ≤ $1.50
- [ ] C5.2 518 valid rows; unresolved count
- [ ] C5.3 evaluation_report.md with real metrics
- [ ] C5.4 usage_report.md from the ledger
- [ ] C5.5 package + clean-unpack replay identical
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
