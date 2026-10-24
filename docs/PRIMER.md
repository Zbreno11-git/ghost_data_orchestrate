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
participant evidence available at `audit_at`. Owner: Breno. State on 2026-10-24: setup (S0).

## The requirement that breaks ties

> **Competition correctness first.** It is ranked first among Breno's priorities. Then come reusable modules,
> reliable unattended execution, transparent evaluation and spend, and the viewer last.

## Inviolable rules

- **Deadline 2026-10-25 12:00 UTC (07:00 CDT).** The safety package is due at 04:00 UTC and the freeze is at 09:00 UTC. Breno uploads around 10:00 UTC.
  Never let the root `output.csv` be anything but the last fully validated output.
- **Gemini spend ≤ $4.50 cumulative** across the whole project (the $0.50 margin is never spent). Every paid call goes
  through `code/ghostaudit/llm/gateway.py` and `state/usage_ledger.jsonl`. No call bypasses the ledger.
- **Participant data only.** Never read organizer truth or generators. `dataset/sample_output.csv` is used only by
  the evaluator, never on the prediction path. No hardcoded labels, evidence IDs or case-family shortcuts.
- **Never fabricate a status.** An API error, budget stop or missing evidence is never turned into
  COMPLETE / INCOMPLETE / NOT_APPLICABLE. Unresolved cases are listed in the run's `unresolved.md`.
- **log.txt** is appended for every user turn in AGENTS.md §5 format, with `tool=Claude Code` and
  `model=claude-opus-5-5`. Never rewrite past entries. Never log secrets.
- **Secrets**: `GEMINI_API_KEY` is read from the environment or `.env`, which is gitignored. Never print or log the key.
- **The repo is PUBLIC** (Breno's decision). Check the staged list before every push. Traces and `runs/` never get committed.
- **Fix first.** Don't build on a known defect without the owner's say-so, asked at the time.
- **Nothing is submitted on Breno's behalf.**

## Current session

⚠️ **S0 (2026-10-24): setup.** Repo initialized on upstream `0eddbbd`. Docs created. Next: venv, smoke test, public remote.

## Boundaries and triggers in force

| Boundary | Rule (and what reopens it) |
|---|---|
| Output sort | Rows are in lexicographic `case_id` order (D5). Reopen if organizers clarify. |
| Step order | phase → operation rank → system_id → resource_id, then step_no (D6). Dependencies stay internal. |
| Admissibility | Evidence file `captured_at ≤ audit_at` (inclusive); activity/audit `event_time ≤ audit_at`. Enforced in the tool layer, not only in prompts. |
| Ownership | `--ownership strict|scored`; the choice is made in S6 by measured sample metrics, with tuning exposure disclosed. |
| Agent | The model can only cite observation IDs returned by tools. Policy and serialization are deterministic code. |
| Model fallback | Never silent. A model change is a config change, recorded in DECISIONS. |

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
.venv/bin/python code/main.py status              # ledger total, runs, first open checkpoint
.venv/bin/python code/main.py validate output.csv # output invariants
.venv/bin/python code/evaluation/main.py          # sample + custom metrics → reports
```

## Protocol

- Open: read this file, then `PROGRESS.md`, then run `git status` and `git log -3`, then `main.py status`.
- Long runs go in the background; waiting is not work.
- Close: read the gate output → two review passes with different questions → update DIARY, PROGRESS, SESSIONS and STATUS → commit with the *why* → push.
- On any defect: open `docs/ERRORS.md` first and ask which class this is an instance of.
