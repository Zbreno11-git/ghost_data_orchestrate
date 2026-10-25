# Ghost Data Orchestrate — agent primer

> Read this first in every session, right after `AGENTS.md` (the upstream contract, which wins on anything
> about output, logging or evidence). It is short on purpose. It carries what is **not** in the code:
> inviolable rules, boundaries in force, and the triggers that reopen them.
>
> Ceiling: narrative of the current and previous session only. When a third closes, the oldest goes to
> `docs/PRIMER_HISTORY.md`. Cut **by type**: a rule that still decides something stays in "Boundaries",
> a lesson moves to `docs/ERRORS.md`, and only narrative moves down.

## What this is

A local Python CLI holding a bounded, tool-using deletion-audit agent for HackerRank Orchestrate Oct 2026,
"Ghost Data Still Exists". For each of the 518 requests in `dataset/deletion_requests.csv` it writes one row of
`output.csv`: `COMPLETE` / `INCOMPLETE` / `NOT_APPLICABLE` plus canonically ordered steps grounded in
participant evidence available at `audit_at`. Owner: Breno. State on 2026-10-25 02:08 UTC: S6 closed (engine frozen; published rows reproduced by replay); S7 next.

## The requirement that breaks ties

> **Competition correctness first.** It is ranked first among Breno's priorities. Then come reusable modules,
> reliable unattended execution, transparent evaluation and spend, and the viewer last.

## Inviolable rules

- **Deadline 2026-10-25 12:00 UTC (07:00 CDT).** The safety package is due at 04:00 UTC and the freeze is at 09:00 UTC. Breno uploads around 10:00 UTC.
  Never let the root `output.csv` be anything but the last fully validated output.
- **Gemini spend ≤ $4.50 cumulative** across the whole project (the $0.50 margin is never spent). Every paid call goes
  through `code/ghostaudit/llm/gateway.py` (reserve → send → settle by error class, A21; cache; replay) and
  `state/usage_ledger.jsonl`; `llm/gemini.py` is the only module that touches the SDK. No call bypasses the ledger.
- **Participant data only.** Never read organizer truth or generators. `dataset/sample_output.csv` is used only by
  the evaluator, never on the prediction path. No hardcoded labels, evidence IDs or case-family shortcuts.
- **Never fabricate a status.** An API error, budget stop or missing evidence is never turned into
  COMPLETE / INCOMPLETE / NOT_APPLICABLE. Unresolved cases are listed in the run's `unresolved.md`.
- **log.txt** is appended for every user turn in AGENTS.md §5 format, with `tool=Claude Code` and
  `model=claude-opus-5-5`. Never rewrite past entries. Never log secrets.
- **Secrets**: `GEMINI_API_KEY` is read from the environment or `.env`, which is gitignored. Never print or log the key.
- **The repo is PUBLIC** (Breno's decision). Stage **explicit paths only**: never `git add -A`, and review every new `??` file before staging (ERRORS #2). Traces and `runs/` never get committed.
- **Fix first.** Don't build on a known defect without the owner's say-so, asked at the time.
- **Nothing is submitted on Breno's behalf.**

## Current session

✅ **S6 closed 2026-10-25 02:08 UTC (plan `docs/plans/session-06.md`).** Audits first, fixes only where evidence shows a defect.
- Extraction coverage complete; the evaluator's "absent" verdict now searches decoded text (ERRORS #8).
- The 24 sample association misses have no admissible link (21 anonymous records, 3 post-cutoff lineage): no rule added.
- Strict ownership kept by a pre-written criterion (A33); status-compatibility run matching rejected (A32, Breno's rule).
- Engine fix found by an independent custom case: a non-account can never be the account (ERRORS #9).
- Trace + `main.py explain` (no model call); metamorphic tests; 5 custom cases (5/5).
- `runs/s6/final` (replay, $0) reproduces root `output.csv` (sha256 `ee9504d5…`); samples unchanged (12/32, P 162/163, R 162/193).
- **Next:** S7 release freeze (session-07.md); C7.7 Mac check pending.

Previous (S5, 2026-10-25): as-of ownership (A24), explicit state and row-bound screens (A25), two clocks (A26), agent
lineage (A27), scope non_resolved (A28), flagged heuristic rows (A29); final run 518 rows, 0 violations; package
proven from a clean unpack.

## Boundaries and triggers in force

| Boundary | Rule (and what reopens it) |
|---|---|
| Output sort | Rows are in lexicographic `case_id` order (D5). Reopen if organizers clarify. |
| Step order | phase → operation rank → system_id → resource_id, then step_no (D6). Dependencies stay internal. |
| Admissibility | Two clocks (A26): an observation is admissible only if its artifact's `captured_at ≤ audit_at` **and** its own event time (`observed_at`, else capture) `≤ audit_at`, inclusive. An artifact captured later is never admitted by an older timestamp. Enforced in `CaseView`, which every engine and tool read goes through. |
| Ownership | `--ownership strict|scored` (S6 decides by measured metrics). Owner index and one-to-one account assignment are evaluated **as of each case's cutoff** (A24). A table row belongs to one entity, for links, state and decoy checks (A25). |
| New links (Breno, S6) | No new link from timing alone, naming patterns, sample labels or assumed one-to-one assignments; ambiguities stay unresolved; strict mode stays (A33), status-compatibility matching rejected (A32). Pre-S6 workflow-tier accounts (19 target rows, weak) are kept until Breno decides. Reopen: Breno's answer, or a run/trace id in the stream. |
| Agent | The model cites only tool-returned obs_ids, and a decision is accepted only with a **lineage** of cited units to the subject; an exclusion needs evidence (of another owner if the link was explicit) (A27). No case_id in the brief. Policy and serialization are deterministic. Final runs review only weak/unresolved proposals (A28). Checkpoints are reused only with an equal input fingerprint. An account choice must belong to the account system (ERRORS #9); a rejection message is part of the replay cache key. |
| Model fallback | Never silent. A model change is a config change, recorded in DECISIONS. |
| Wrapper vs fields | Lookup keys and ledger `subject_reference` live in `Observation.wrapper`; only `fields` is record content (FR-11). An identifier only in the wrapper never makes a record "exposed". |
| Absence proof | An ABSENT verification may cite a snapshot that covers the system (table or bundle scope) and lacks the row: 4/75 sample citations do exactly that (C2.6). |
| Unobservable | `audit_record_5569/6645` and `account_004` exist only in sample answers (D10, D13): never invent resources to chase recall. |
| Copy-level state | State is reconstructed per physical copy (system/container/topology); a newer clean primary never clears an older dirty replica (A20). |
| Verdict support | A row that validates is not a supported verdict. `planner.support_of` is the only rule: no account/intent or any unknown → unresolved; a workflow link, any ownership ambiguity or low-confidence intent → weak (A20, A24). Rows with no grounded proposal carry flagged **heuristic predictions** and stay unresolved (A29). |
| Intent | An explicit deletion instruction wins over export, correction or marketing words in the same request (A20). |
| Replay | Replay builds no provider client and reads no key (`.env` included); a cache miss is `ReplayMiss`, never a call (A20). |
| Post-audit naming | A resource is never named, linked or cited from evidence captured after `audit_at` (D12), even when the sample answer names it. All engine and tool reads go through `temporal.CaseView`. |

## Where things are

| | |
|---|---|
| `PROGRESS.md` | state now and ▶️ RESUME HERE |
| `docs/SESSIONS.md` | roadmap: sessions, checkpoints, ▶️ start next session |
| `docs/plans/` | `MASTER_PLAN.md` (frozen approved plan) and `session-NN.md` per session |
| `docs/DECISIONS.md` | decisions + contract discrepancies, with reopen triggers |
| `docs/ERRORS.md` | error catalog by class. Open it when you find a defect. |
| `docs/DIARY.md` | one entry per session |
| `docs/STATUS.md` | plain-language progress for Breno |
| `docs/REQUIREMENTS_MAP.md` | FR/NFR → checkpoint → proving command |
| `docs/handoff/` | Breno's original vision/backend/handoff docs and site_text.md |

## Commands

```bash
.venv/bin/python -m pytest code/tests -q          # gates
.venv/bin/python code/main.py status              # ledger total and run dirs
.venv/bin/python code/main.py ingest --report     # 94-file coverage → runs/ingest/coverage.md (PNGs from cache)
.venv/bin/python code/main.py validate output.csv # output invariants
.venv/bin/python code/evaluation/main.py --pred <output.csv>   # metrics vs sample_output (join by case_id)
```

## Protocol

- Open: read this file, then `PROGRESS.md`, then run `git status` and `git log -3`, then `main.py status`.
- Long runs go in the background; waiting is not work.
- Close: read the gate output → two review passes with different questions → update DIARY, PROGRESS, SESSIONS and STATUS → commit with the *why* → push.
- On any defect: open `docs/ERRORS.md` first and ask which class this is an instance of.
