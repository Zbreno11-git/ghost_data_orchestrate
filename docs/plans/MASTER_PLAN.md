> **Frozen record of the plan approved by Breno on 2026-10-24 ~16:50 UTC.** Do not edit.
> Living versions: checkpoint state → `docs/SESSIONS.md`; decisions/discrepancies → `docs/DECISIONS.md`;
> current state → `PROGRESS.md`. If they disagree with this file, they win (and the change is logged in DECISIONS).

# Ghost Data Still Exists — setup + Session plan (software-build format)

## Context

Breno is entering HackerRank Orchestrate Oct 2026, "Ghost Data Still Exists". The goal is a local Python CLI containing a bounded, tool-using deletion-audit agent. For each of 518 requests it must output `COMPLETE` / `INCOMPLETE` / `NOT_APPLICABLE` plus canonically ordered steps, grounded in participant evidence as of `audit_at`.

**Constraints:**
- Gemini spend: USD 5 cumulative, with autonomy up to $4.50.
- The work runs unattended overnight.
- Breno uploads around 05:00 CDT.

This plan was made with the personal **software-build** skill (`/root/.claude/skills/software-build/`, SKILL.md + `referencia/plano-de-sessao.md` + `modelos/*`). The skill's document set is primer, roadmap, progress, diary, error catalog, decisions and status bar. Every session has a checkpoint map, and each checkpoint lists Does / ✅ (command → expected number) / 🐞 Predicted → Debug. Pronto (done) is a ladder of steps, and each session closes with a two-pass review.

## Measured at opening (2026-10-24 16:43 UTC)

| What | How | Result | Consequence |
|---|---|---|---|
| Deadline | user: 2026-10-25 07:00 CDT | **12:00 UTC, ≈19h17m left** | Safety package by 04:00 UTC; freeze by 09:00 UTC |
| Upstream | `gh api …/commits/main` | `0eddbbd` (handoff had `acb3dfc`; AGENTS.md updated today) | Use current contract |
| Dataset | `wc -l` | 518 targets, 32 samples, 94 evidence files, 850 identities, 306 audit rows, 4,011 activities; 0 sample/target id overlap | Matches docs |
| Sample statuses | script | 22 INCOMPLETE, 10 COMPLETE, **0 NOT_APPLICABLE** | Intent classifier only testable on custom cases |
| Non-deletion signal | grep | 10 `CLASSIFY_REQUEST … non-deletion` activities | Targets contain NOT_APPLICABLE |
| Sample citations | script | 75 cite `evidence_*` file_ids, 118 `""`; no activity/audit ids | Prefer file evidence for state proof |
| Ownership grounding | co-occurrence audit (text sources, trace_id-joined) | **82/111** sample resources explicitly linked; 29 not | Ownership modes `strict` vs `scored`, decided by metrics |
| Request-window candidates | script | 3–15 candidate accounts per case; case_24/25/26 share `reported_at` | Timing alone is not unique |
| Admissibility edge | case_11 cites evidence_03 captured == audit_at | `≤` inclusive | Rule: `captured_at <= audit_at` |
| Input order | script | deletion_requests.csv is numeric order, not string order | Sort ambiguity (D5) |
| Gemini key | `models.list` (free) | works; `gemini-3.1-flash-lite`, `gemini-2.5-flash-lite`, `gemini-3.8-flash` available | Pricing page 2026-10-22: $0.25/$1.50, $0.10/$0.40, $0.75/$3.75 per 1M |
| Machine | `python3`, `uv`, `pdftotext` | Py 3.12.3, uv 0.12.10, poppler present, 7.8 GB RAM, 2 CPUs; no pydantic/genai yet | Lean venv |
| GitHub | `gh auth status` | `Zbreno11-git`, scopes incl. repo/workflow; no existing solution repo | Create new repo |
| Formats | inspection | ~8 log formats (key=value, JSON, syslog, bracketed, pipe, cloud `message=`), lookup_key and resource_id on different lines joined by `trace_id`; PDFs extract via text; PNGs are clean UI screens | Deterministic parsers; vision only for 11 PNGs |

## Owner answers

| Question | Answer | Consequence |
|---|---|---|
| Deadline | 2026-10-25 07:00 CDT | Timeline below (UTC) |
| Weak ownership links | Decide after measuring | `--ownership strict\|scored` flag; choose in S6 on sample metrics, disclose tuning exposure |
| Repo | New **public** `Zbreno11-git/ghost_data_orchestrate` | Public now; secrets, .env, runs/, traces never committed |
| Spend | Full autonomy to $4.50 | Ledger hard-stops at $4.50 cumulative, with $0.50 margin left |
| Upload | Morning ~05:00 CDT | Safety package 04:00 UTC; final freeze 09:00 UTC (04:00 CDT) |
| Doc language | English everywhere | Skill templates translated |
| Custom cases | 3 required; +2 if few sample fixes remain | 3 in S5 gate, +2 in S6 |
| Viewer | Last optional session | S8, only after freeze; never touches frozen artifacts |

## Contract discrepancies (→ docs/DECISIONS.md)

| # | Sources | Resolution |
|---|---|---|
| D1 | handoff SHA `acb3dfc` vs upstream `0eddbbd` | Follow current upstream; record SHA in log/README |
| D2 | Report path: `evaluation/…` (AGENTS §6.8, problem_statement) vs `code/evaluation/…` (README) vs "zip your code/ directory" (site_text) | Reports live in `code/evaluation/`. `code/README.md` is the source and root README.md a pointer. The zip holds `README.md` + `code/`, which satisfies both |
| D3 | `log.txt` = chat_transcript (README/site_text) vs `agent-trace.zip` (trace instructions) | Produce both; agent-trace staged outside the repo, Breno decides on upload |
| D4 | Deadline "not configured" (AGENTS §3) | Owner-supplied 12:00 UTC |
| D5 | "Sort by case_id" with unpadded ids; input file is numeric order | **Lexicographic string sort** (literal `sorted()`; graders key by case_id). Reopen trigger: organizer clarification |
| D6 | Remediation "dependency" prose (AGENTS §6.5) vs canonical sort | Canonical sort (README/problem_statement). S1 ✅ proves samples are canonically sorted 32/32; dependencies kept internal only |
| D7 | Samples lack NOT_APPLICABLE | Intent measured on custom cases plus manual review of classified targets |
| D8 | Handoff model candidates | Confirmed available; final choice by S4 benchmark |

## Architecture decisions (agent's, declared; → docs/DECISIONS.md with reopen triggers)

| Decision | Why | Reopen if |
|---|---|---|
| Repo = `/root/hackthon_1` itself (`git init`, upstream fetched, `main` from `upstream/main`) | Keeps Claude Code traces in `~/.claude/projects/-root-hackthon-1`; AGENTS.md/CLAUDE.md at the cwd root | — |
| Deterministic evidence layer (ingest → observations → indexes → identity → temporal → ownership → policy) feeds an LLM investigator through read-only tools | Grounding and budget: the model cites observation IDs and cannot invent | Agent adds no metric value over deterministic proposal after S6 |
| Native Gemini function calling, with a JSON action envelope as fallback | Handoff requirement; verified in S0 smoke | Smoke shows unreliable calls or missing thought-signature support |
| Model: `gemini-3.1-flash-lite` default, `gemini-3.8-flash` for vision/repair; `2.5-flash-lite` only if benchmark equal | Cost: 518 cases | S4 benchmark |
| Every authorized case gets ≥1 agent decision; clear cases end in 1 call, ambiguous ≤4 tool rounds + ≤2 repairs | Genuine agent at bounded cost | Pilot projects >$1.50/full run |
| Intent: batched LLM classification with a deterministic keyword cross-check; disagreements get a per-case recheck | Multilingual texts; cheap | Custom cases fail |
| PDFs via `pypdf` (pure Python; PyMuPDF is AGPL); PNGs via 1 cached vision call each | Portability/licence; 11 images ≈ cents | pypdf text ≠ pdftotext on the 4 PDFs |
| SQL in in-memory sqlite3 with an authorizer (no ATTACH/extensions) | Safety | A fixture needs a denied statement |
| Admissibility: file `captured_at ≤ audit_at`; activity/audit `event_time ≤ audit_at` | AGENTS §6.6 + case_11 | Sample citation mismatch traced to it |
| Unresolved after the agent: emit the deterministic grounded proposal, flagged in `runs/<id>/unresolved.md`; an API error is never a status | NFR-03 + 518 rows required | — |
| Ledger `state/usage_ledger.jsonl` committed; caches/checkpoints in `runs/` (gitignored) | Budget survives clones | — |
| pydantic only via google-genai's dependency; deps = google-genai, pypdf, pytest | Lean | — |

## Repository layout (approved proposal)

```
AGENTS.md (upstream) · CLAUDE.md (@AGENTS.md + @docs/PRIMER.md) · README.md (pointer) · PROGRESS.md
log.txt · output.csv · .gitignore · .env.example · .github/workflows/ci.yml (no paid calls)
dataset/ (upstream, read-only)
docs/ PRIMER · SESSIONS · plans/session-NN · DIARY · ERRORS · DECISIONS · STATUS · REQUIREMENTS_MAP · handoff/
code/ main.py · README.md · requirements.txt · config/default.toml · prompts/*.md
      ghostaudit/{contract,validate,serialize,evidence,identity,temporal,ownership,policy,tools,agent,planner,runner}.py
      ghostaudit/ingest/{manifest,csv_tables,sql_snapshot,json_records,logs,pdf_text,images}.py
      ghostaudit/llm/{gateway,gemini,ledger,cache}.py
      evaluation/{main.py,metrics.py,custom_cases/,evaluation_report.md,usage_report.md}
      tests/
scripts/{package_code.py,stage_traces.py} · state/usage_ledger.jsonl · runs/ (ignored)
```

## Timeline (UTC; CDT = UTC−5)

S0 16:50–18:00 · S1 18:00–19:00 · S2 19:00–21:00 · S3 21:00–23:00 · S4 23:00–01:30 · S5 01:30–04:00 (**safety package**) · S6 04:00–07:30 · S7 07:30–09:00 (**freeze**) · S8 optional 09:00–10:00 · Breno uploads ≈10:00 UTC · deadline 12:00 UTC.

**Critical path:** S0→S1→S2→S3→S4→S5 (safety package)→S7. S6 and S8 can be cut. If a session overruns by more than 30 min, S6 scope shrinks first, then the +2 custom cases, then S8. S5 and S7 are never cut.

## Budget envelope (cumulative ledger, hard stop $4.50)

| Stage | Envelope | Basis |
|---|---|---|
| S0 smoke (text + tool call + vision 1 image) | $0.05 | 3 tiny calls |
| S2 vision 11 PNGs (cached by hash) | $0.10 | ~11 calls @ 3.8-flash |
| S4 intent batch + benchmark (10 samples × 2 models) | $0.30 | measured |
| S5 pilot (30 cases) + full run 1 | $1.75 | the pilot must project ≤$1.50 before the full run |
| S6 targeted reruns | $1.00 | invalidated cases only |
| S7 final run (or replay if code unchanged) | $0.80 | |
| Margin | $0.50 | never spent |

---

## Sessions (→ docs/SESSIONS.md; each session gets docs/plans/session-NN.md at open)

Shared closing ritual for every session, per the skill:
1. Read the gates' output, citing the literal lines.
2. Two-pass review with different questions (`referencia/revisao.md`).
3. Update DIARY, PROGRESS (▶️ resume block), SESSIONS and STATUS with today's numbers.
4. Commit with the *why*, then push.
5. Add a log.txt entry per user turn.

Shared resume procedure:
1. Read `PROGRESS.md` ▶️ RESUME HERE, then `docs/PRIMER.md`.
2. Run `git status` and `git log -3`.
3. Run `python3 code/main.py status`, which prints the ledger total, run checkpoints and the first unchecked C.
4. Continue from the first ⬜ checkpoint.

### S0 — Setup, logging, docs, smoke (FR-17, FR-19, FR-20, NFR-04, NFR-06, NFR-09) · 1h10 · $0.05
**Delivers:** a public repo with upstream provenance, a working venv, log.txt started, skill docs created, and a measured Gemini smoke result in the ledger.
**Not doing:** any engine code (→ S1+).
**Entry:** plan approved. **Blocker for Breno:** before leaving, keep the session running with permissions that allow Bash/Edit unattended (e.g. acceptEdits plus allowlist), or the overnight work stalls on prompts.

| C | Closes when |
|---|---|
| C0.1 | `git init`; upstream remote fetch-only; `main` = `upstream/main` @ 0eddbbd; `.gitignore` committed **before** any `git add` of the docs. ✅ `git log --oneline -1` shows 0eddbbd ancestry; `git check-ignore .env runs/ .venv` → 3 lines |
| C0.2 | log.txt has SESSION START (tool=Claude Code, model=claude-opus-5-5, Time Remaining) plus one entry per planning turn so far. ✅ `grep -c '^## \[' log.txt` ≥ 5; `grep -c '^tool=Claude Code$' log.txt` equals SESSION START count; no `AIza`/`gho_` strings (`grep -cE 'AIza\|gho_' log.txt` → 0) |
| C0.3 | Handoff docs moved to `docs/handoff/`; PRIMER, SESSIONS, PROGRESS, DIARY, ERRORS, DECISIONS (D1–D8 + table above), STATUS, REQUIREMENTS_MAP created from templates. ✅ `ls docs` lists 8 files plus plans/ and handoff/ |
| C0.4 | `uv venv .venv --python 3.12`; install google-genai, pypdf, pytest; pin to `code/requirements.txt`. ✅ `.venv/bin/python -c "import google.genai, pypdf"` exits 0 |
| C0.5 | Smoke via throwaway `code/ghostaudit/llm` minimal gateway: (a) text plus JSON schema, (b) one function-call round trip, (c) one PNG extraction; usage_metadata captured; ledger rows written. ✅ ledger has 3 rows, total < $0.05; record which of (a)–(c) work |
| C0.6 | `gh repo create Zbreno11-git/ghost_data_orchestrate --public`; origin set; first push after inspecting `git status`/staged list. ✅ `gh repo view … --json visibility,url` → PUBLIC; `git ls-files \| grep -E '\.env$\|runs/'` → empty |
| C0.7 | Project memory saved (deadline, budget, repo, owner answers). |

🐞 Predicted: the thought-signature or function-call format differs in the SDK version → read the SDK `types` and switch to the envelope (decision logged). Untracked files collide with upstream paths → none expected (names differ); check `git status` first.

### S1 — Contract core + evaluator (FR-15, FR-18, NFR-02) · 1h · $0
**Delivers:** contract tables, a validator, a canonical serializer and an evaluator, proven against sample_output.
**Entry:** S0 C0.4.

| C | Closes when |
|---|---|
| C1.1 | `contract.py` is the only home of ops, states and ranks. ✅ test: every (phase, op, state) in samples ∈ table (193/193) |
| C1.2 | `serialize.canonical_sort` re-sorts shuffled sample steps back to the identical arrays. ✅ `pytest tests/test_contract.py` → 32/32 identical |
| C1.3 | `validate.py` rejects malformed fixtures, each for the named reason: bad pair, gap in step_no, extra key, NA with steps, COMPLETE with remediation, INCOMPLETE future step with an evidence_id, unknown evidence id, evidence captured after audit_at, duplicate/missing case. ✅ ≥9 rejection tests pass; sample_output validates clean |
| C1.4 | `evaluation/main.py` metrics with defined denominators. **Status accuracy** = correct / 32. **Whole-case exact** = parsed JSON equal (key order ignored). **Step P/R/F1**: a step matches on (phase, system_id, resource_id, operation, state). **Evidence accuracy** = matched steps with an equal evidence_id. **Field accuracy** = per field over aligned steps, with missing/extra counted separately. **Sequence accuracy** = predicted array equals the canonical order of the expected array. **Ordered-ops accuracy** is the same comparison on operation lists only. ✅ evaluating sample_output against itself → all metrics 1.0; against an empty prediction → 0 with correct counts |

🐞 Predicted: the string vs numeric case_id sort leaks into the evaluator → the evaluator joins by id, never by position.

### S2 — Ingestion + evidence store (FR-03, FR-05, FR-06, FR-11, NFR-01, NFR-07) · 2h · ≈$0.10
**Delivers:** every manifest file processed into provenance-carrying Observations with exact indexes, plus a coverage report.
**Not doing:** ownership decisions (→ S3).
**Side task (background):** spawn a subagent that sees only `problem_statement.md`, AGENTS §6 and `deletion_rules.csv` (no engine code). It authors **3 custom cases** in the dataset's schema (a historical email in a replica; a success claim contradicted by a present record; post-cutoff evidence ignored) with expected outputs and written rationale under `code/evaluation/custom_cases/`.

| C | Closes when |
|---|---|
| C2.1 | Manifest plus CSV tables loaded; all 94 paths resolve inside dataset/. ✅ `main.py ingest --report` → 94 files, 0 missing |
| C2.2 | SQL adapter (sandboxed, per-table topology: primary/replica/failover/regional/reporting, `snapshot_scope`). ✅ 24/24 SQL files load; an ATTACH test is denied |
| C2.3 | JSON adapters: export, bundle (business record separated from wrapper `subject_reference`), connectors, export manifest/jobs, analytics report, security ledger. ✅ 28/28 JSON processed; a test asserts wrapper fields are tagged `wrapper` |
| C2.4 | Log adapters for each format, plus the trace_id join (lookup_key ↔ resource_id) and line-level unparsed accounting. ✅ 26/26 logs; unparsed lines reported per file with an explicit count (target 0 non-noise) |
| C2.5 | PDF (pypdf) + TXT adapters; PNG vision extraction once per content hash (structured fields + verbatim panels), cached as success or failure. ✅ 4/4 PDFs, 1/1 TXT, 11/11 PNG extracted; re-run → 0 new paid calls |
| C2.6 | Coverage report: every file processed/partial/failed. ✅ `runs/ingest/coverage.md` shows 94/94 with a status |

🐞 Predicted: a log format variant is missed silently → the unparsed-line counter per file is the gate. Uppercase emails → normalize case for matching and keep the raw value.

### S3 — Identity, time, ownership, policy, planner → deterministic end-to-end (FR-02, FR-04, FR-06–FR-14, NFR-02, NFR-03) · 2h · $0
**Delivers:** a no-LLM proposal for all 32 samples, evaluated. This baseline is what the agent must beat or match.

| C | Closes when |
|---|---|
| C3.1 | Identity fixed point (current + audit history: email/phone/hash/name; case-insensitive email). ✅ case_10 (old Yahoo email) and case_12 resolve historical aliases; a similar-email decoy (case_28) is excluded by test |
| C3.2 | Temporal filter enforced inside the tool layer. ✅ test: an observation captured after audit_at is invisible to every tool |
| C3.3 | Ownership with link strength (explicit / unique-weak / ambiguous) and `--ownership strict\|scored`. ✅ report of the linked fraction on samples, both modes |
| C3.4 | Policy registry from `deletion_rules.csv`; per-resource required treatment and compliance; claim vs state separated. ✅ policy tests: tombstone with stable id only passes, with hash fails; retained security record → PRESENT check |
| C3.5 | Planner compiles typed decisions → steps (including verification for already-clean/retained resources) → validator. ✅ `main.py run --engine deterministic --split samples` validates 32/32 and evaluator metrics are recorded in DIARY (baseline) |

🐞 Predicted: citation choice differs (which file proves the state) → measure "latest admissible proving file" against samples and record the rule in DECISIONS.

### S4 — Agent loop + gateway, ledger, cache, resume, replay (FR-01, FR-16, FR-17, FR-19, NFR-04, NFR-05) · 2h30 · ≈$0.30
**Delivers:** a tool-using investigator over the deterministic tools; paid calls are ledgered, cached and resumable; replay runs with zero network.

| C | Closes when |
|---|---|
| C4.1 | Gateway: the only paid path, with reservation before each call and reconciliation after, finite retries, no silent model fallback, hard stop at $4.50. ✅ test: a fake provider exceeding budget is refused; concurrent reservations don't overspend |
| C4.2 | Tools exposed (resolve_identity, search_evidence with pagination and omitted counts, inspect_evidence, resource_timeline, compare_replicas, inspect_flows_restores, evaluate_policy, check_coverage, submit_audit). ✅ unit tests per tool; cutoff enforced |
| C4.3 | Agent state machine with validation-repair loop. ✅ one sample case runs live: trace shows ≥1 tool choice → submit → canonical output |
| C4.4 | Intent classifier (batched, multilingual) plus a keyword cross-check. ✅ 32/32 samples deletion=true; the 3 custom NA phrasings (incl. non-English) → NOT_APPLICABLE |
| C4.5 | Resume + replay. ✅ kill mid-run then resume → ledger shows 0 duplicate successful calls; `--mode replay` with network disabled (`GEMINI_API_KEY=` unset) reproduces byte-identical output.csv |
| C4.6 | Model benchmark: 10 diverse samples × {3.1-flash-lite, 3.8-flash}; pick by metrics/$ and record in DECISIONS. |

🐞 Predicted: the model paraphrases the deterministic proposal without investigating → tool-choice stats in the trace; if agent == baseline everywhere, record it honestly in DECISIONS.

### S5 — Pilot, full run, 3 custom cases, reports, SAFETY PACKAGE (FR-18–FR-20, NFR-09, NFR-10) · 2h30 · ≈$1.75
**Delivers:** by **04:00 UTC (23:00 CDT)**, an uploadable `output.csv` + `code.zip` + `log.txt` that passed every release check.

| C | Closes when |
|---|---|
| C5.1 | Pilot on 30 stratified target cases; projected full cost written. ✅ projection ≤ $1.50, otherwise shrink context/turns before C5.2 |
| C5.2 | Full 518 run. ✅ validator: 518 rows, unique, sorted, all JSON valid; unresolved count reported |
| C5.3 | Samples (all 32) and the 3 custom cases evaluated. ✅ metrics written into `evaluation_report.md` (status/step/field/sequence/evidence, confusion matrix, tuning exposure note) |
| C5.4 | `usage_report.md` generated from the ledger rows of this run (providers, models, calls, in/out tokens, totals/averages per request, cost per model + overall, cache provenance, cumulative project spend). |
| C5.5 | `scripts/package_code.py`: zip inventory (no dataset/.env/venv/caches/nested archives), clean unpack into a temp dir, then `replay` produces an identical output. ✅ script exits 0; `unzip -l` reviewed |
| C5.6 | Safety artifacts committed and pushed; STATUS tells Breno what to upload if later work regresses. |

### S6 — Measured improvement (FR-02, FR-05–FR-14 as failures dictate) · 3h30 · ≈$1.00
**Delivers:** fixes for causal error classes (taxonomy: extraction, identity, temporal, retrieval coverage, mapping, policy, citation, sequence, serialization), each verified on samples/custom cases without regression; ownership-mode decision; +2 custom cases (tombstone pair, clean primary/dirty replica) if few sample fixes remain.

| C | Closes when |
|---|---|
| C6.1 | Mismatch table by error class from S5. ✅ every mismatch has a class |
| C6.2 | Each fix: a test that fails before and passes after, plus ERRORS.md entry if it was our error. |
| C6.3 | Ownership mode chosen (metrics both modes, tuning exposure disclosed). |
| C6.4 | Targeted rerun of invalidated cases only. ✅ ledger shows only those cases called |

### S7 — Release freeze (FR-17, FR-20, NFR-06, NFR-10) · 1h30 · ≤$0.80 · freeze **09:00 UTC (04:00 CDT)**
**Delivers:** the final upload set plus staged traces.

| C | Closes when |
|---|---|
| C7.1 | Final run (or replay if the engine is unchanged since the last full run); the validator passes; output.csv published atomically. |
| C7.2 | Reports regenerated from the final run; README run/setup instructions verified from a clean unpack. |
| C7.3 | `scripts/stage_traces.py` copies this project's `~/.claude/projects/-root-hackthon-1/*.jsonl` into `~/agent-trace/claude-code/` (outside the repo), redaction-scanned (`AIza`, `gho_`, `.env`). ✅ scan → 0 hits |
| C7.4 | STATUS "upload checklist": the 3 HackerRank files + optional agent-trace.zip, with paths. Breno must `/export` and quit the session before the final trace copy. |

### S8 — Optional static evidence viewer · ≤1h · $0
Only if S7 is frozen with ≥2h to the deadline. It reads the run traces and writes one escaped static HTML file; it must not modify output.csv, code.zip or the reports.

---

## Requirements → checkpoint map (→ docs/REQUIREMENTS_MAP.md)
FR-01 C4.4 · FR-02 C3.1 · FR-03 C2.1–C2.6 · FR-04 C3.2 · FR-05 C2.3/C3.4 · FR-06 C2.2/C3.4 · FR-07/08 C3.4–C3.5 · FR-09/10 C3.4 · FR-11 C2.3 · FR-12 C3.1/C3.3 · FR-13 C3.5 · FR-14 C1.3/C3.5 · FR-15 C1.1–C1.3 · FR-16 C4.3 · FR-17 C4.5/C5.5 · FR-18 C1.4/C5.3 · FR-19 C4.1/C5.4 · FR-20 C0.2/C5.5/C7.3 · NFR-01 C2.6 · NFR-02 C1.2/C4.5 · NFR-03 C3.5 · NFR-04 C4.1 · NFR-05 C4.5 · NFR-06 C5.5 · NFR-07 C3.2/C4.2 · NFR-08 layout · NFR-09 timeline · NFR-10 C5.3–C5.4.

## End-to-end verification
1. `python3 code/main.py run --mode fresh` produces a 518-row output.csv.
2. `python3 code/main.py validate output.csv` reports 0 violations.
3. `python3 code/evaluation/main.py` updates the reports with real numbers.
4. `python3 scripts/package_code.py` builds code.zip, then replays it from a clean unpack with identical output.
5. `python3 code/main.py status` shows the cumulative ledger ≤ $4.50.

## Risks / irreversible
- Public repo: the solution and log.txt are visible to competitors (owner accepted). Check the staged list before every push; `.env` is ignored before the first add.
- Paid calls are protected by the ledger hard stop; the full run only goes ahead after the pilot projection.
- The upload is Breno's action; nothing gets submitted on his behalf.

## First implementation checkpoint
**S0 C0.1:** in `/root/hackthon_1`:
1. Write `.gitignore` (`.env`, `.venv/`, `runs/`, `__pycache__/`, `*.zip`, `agent-trace/`).
2. Run `git init -b main`, `git remote add upstream https://github.com/interviewstreet/hackerrank-orchestrate-october26.git`, `git fetch upstream`, `git reset --mixed upstream/main`.
3. Confirm with `git status` that only our files are untracked and `.env` is ignored.

**Resume after an interruption:** read `PROGRESS.md` ▶️ RESUME HERE.
