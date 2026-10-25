# Roadmap — Ghost Data Orchestrate

Each session is a 1–2.5 h package that ends in something verifiable, plus a diary entry. Full checkpoint text
(command → expected number, 🐞 predicted defect) lives in `docs/plans/MASTER_PLAN.md`. This file holds the
**state**, and any change to a checkpoint is noted here with a date and reason.

**Progress: 7 of 8 sessions fully closed; S7 in progress** (✅: S0–S6; 🔄 S7; S8 merged into S7 by Breno, 2026-10-25 02:25 UTC; measured 02:47 UTC). Partial (🔄) counts as partial.

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

- **S7 in progress** (opened 2026-10-25 02:45 UTC; plan `docs/plans/session-07.md`). S7 and S8 were merged by
  Breno (02:25:16 UTC, A35): final integration, evidence viewer, hardening, Mac acceptance and release. Freeze is
  the last checkpoint. **Export and upload only after it (A31).**
- Read first: `docs/PRIMER.md`, `PROGRESS.md`, `docs/plans/session-07.md` (Progress), DECISIONS A31–A35.
- Depends on Breno: the C7.1 legacy-link decision (A34), the Mac acceptance (C7.6), the export and the upload.

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

### ✅ S5 — Pilot, full run, 3 custom cases, reports, SAFETY PACKAGE · spent $1.531410 (session, ledger) · closed 2026-10-25 01:13 UTC, before the 04:00 UTC due time
> **Plan of record: `docs/plans/session-05.md`** (C5.0–C5.15; that file maps each MASTER_PLAN checkpoint in
> brackets). **Changed 2026-10-24 21:34–21:59 UTC (Breno):**
> - accuracy work first: temporal isolation, explicit state, agent lineage, case-by-case comparison and
>   log corrections (C5.0–C5.6, C5.12, C5.13);
> - five amendments (21:45 UTC);
> - **the temporal correctness check is a separate work item, C5.3b (21:59 UTC), closed.**
>
> **Owner decisions (2026-10-25 00:41 UTC):** agent scope non_resolved (A28); flagged heuristic rows (A29).
- [x] C5.1 pilot projection ≤ $1.50 — 30 targets, $0.0035/case, projection $1.22 (non_resolved) [session-05 C5.7]
- [x] C5.2 518 valid rows; unresolved count [C5.8] — `runs/s5/final`: 518 rows, `0 violations`; 175 resolved / 18 weak / 325 unresolved (3 flagged heuristic, A29); root `output.csv` published (sha256 `ee9504d5…`, untracked: public repo)
- [x] C5.3 evaluation_report.md with real metrics [C5.9] — samples 32/32 status, whole 12/32, P 162/163, R 162/193; custom 3/3; comparisons; diagnostics; failures and fixes
- [x] C5.4 usage_report.md from the ledger [C5.10] — final run 1748 responses, 5.16 M tokens, $1.395811 at full price ($0.010792 paid in that run); cumulative $1.870528 + $0.004447 open
- [x] C5.5 package + clean-unpack replay identical, incl. `code/README.md` as source + root `README.md` pointer (D2) [C5.11]. **VPS check passed 2026-10-25 01:12 UTC:** fresh venv, `unshare -rn`, no key, `cmp` identical, 0 violations, scan clean; `code.zip` sha256 `f58aaefe…`. **Added 2026-10-25 (Breno), the VPS check:**
  - unzip into an empty directory, with the dataset supplied outside the zip;
  - a fresh venv from `code/requirements.txt` only;
  - offline replay with the key unset and **network unavailable**;
  - a scan of the unpacked tree for developer paths (`/root/`, the repo path), credentials and caches not
    declared in a MANIFEST;
  - validate the replayed output, then `cmp` it byte for byte with the frozen reference run.
- [x] C5.6 committed/pushed; STATUS upload instructions [C5.14]
- [x] **C5.15 (added 2026-10-25, Breno): mismatch diagnostics by earliest responsible stage.** — `code/evaluation/diagnostics.md`: 32 mismatches = 3 absent from evidence, 5 post-audit only, 24 association (S3 baseline 33)
  - **Builds on:** `classify_failures.py` (targets, no answers) and `compare.py` (per-case before/after).
  - **Adds**, evaluator side only (`code/evaluation/diagnose.py`): every sample mismatch (a missing or extra
    step, a wrong field, a status) gets exactly one earliest supported cause:

    | Cause | Meaning |
    |---|---|
    | extraction | the fact is in the files but was not extracted |
    | identity/resource association | |
    | temporal state | |
    | policy/treatment | |
    | citation | |
    | ordering/serialization | |
    | undetermined | the cause cannot be established |

    "Not extracted" (a raw byte search of the files finds the id) is kept apart from "absent from the supplied
    evidence" (it does not, e.g. D10/D13). A parser miss is never reported as a dataset gap.
  - ✅ **Acceptance:**
    - `code/evaluation/diagnostics.md` with counts per cause, one or two representative examples each, and a
      before/after table for this session's fixes (S3 baseline → final);
    - full official denominators (193 steps, 32 cases);
    - the sample answers are read only by this evaluator script; the grep gate on the prediction path stays
      green.

## Block C — Improve and release

### ✅ S6 — Measured improvement · spent $0.005969 (ledger) · closed 2026-10-25 02:08 UTC
Plan `docs/plans/session-06.md`, amended mid-session by Breno (evidence-backed recall at preserved precision;
no links from timing, naming, labels or one-to-one assumptions).
- [x] C6.1 extraction coverage audit (`scripts/analysis/extraction_audit.py`): 0 present-but-missed; evaluator
  defect fixed (raw-byte search blind to compressed PDFs, ERRORS #8, `code/evaluation/corpus.py`)
- [x] C6.2/C6.5 decision trace + `main.py explain` (no model call); examples in `docs/explanations/`
- [x] C6.3 rejected association paths to the break point: 21 anonymous records, 3 lineage only after the cutoff;
  no admissible link → no association rule
- [x] C6.4 no generic fix warranted (whole-dataset line coverage, 7338 lines)
- [x] C6.5 metamorphic robustness tests with controls (shuffle, duplicate, other person, post-cutoff)
- [x] C6.6 ownership mode by a pre-written criterion: strict kept (A33), status compatibility rejected (A32)
- [x] C6.7 +2 independent custom cases; one exposed an engine defect (a linked tombstone accepted as the account →
  DELETE planned; ERRORS #9), fixed
- [x] C6.8 targeted recompute by replay ($0, 1722/1722 cache hits): published rows unchanged; final gate
  `docs/diagnostics/s6/final_gate.md`

### 🔄 S7 — Final integration, evidence viewer, hardening, Mac acceptance, release · ≤$0.20 planned · freeze is the last checkpoint
> **Changed 2026-10-25 02:25 UTC (Breno, A35):** S7 and S8 merged; the viewer is a deliverable; "deploy" =
> documents and the exact HackerRank artifacts; freeze after Mac acceptance and the final trace. Old items mapped
> in `docs/plans/session-07.md` (C7.0) and in the MASTER_PLAN amendment; the old S7 list (C7.1–C7.7 of
> 2026-10-25) is superseded by:
- [x] C7.0 state refresh, session-07.md, roadmap rewrite, MASTER_PLAN amendment
- [x] C7.1 legacy workflow-link comparison (assert vs candidate) + masked-identity cohort backtest (Breno amendment 1) → **Breno decides (A34)**
- [x] C7.1T temporal interpretation experiment (config-gated, separate from C7.1; Breno amendment 2) → results to Breno before promotion
- [ ] C7.2 provenance integrity (saved with the run, fingerprint-checked) + offline evidence viewer [old S8]
- [ ] C7.3 focused review + packaging hardening (explicit validation, exact report paths, truthful isolation, inventory) [old C7.2 part]
- [ ] C7.4 final integration on the approved config; release candidate; clean-unpack VPS check; viewer in a browser [old C7.1, C7.2]
- [ ] C7.5 submission documentation: README entry point, REQUIREMENTS_MAP, reports [old C7.2 docs, C7.4]
- [ ] C7.6 Mac runbook, walkthrough, interview cheat sheet → **Mac acceptance by Breno (PENDING until run on the Mac)** [old C7.5–C7.7]
- [ ] C7.7 final artifacts, trace closure, RELEASE_RECORD, checksums, upload checklist, **freeze** [old C7.3, C7.4]

### ⤴ S8 — merged into S7 (Breno, 2026-10-25 02:25 UTC, A35); the viewer is C7.2
