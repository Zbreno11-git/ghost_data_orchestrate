# Plan — Session 0: setup, logging, docs, smoke

## What this session delivers (one verifiable sentence)
A public repo on upstream `0eddbbd` with the skill docs and log.txt, a pinned venv, and a measured Gemini smoke
result recorded in the ledger.

## What it does NOT do (and where it went)
- Any engine code → S1+ (already written in docs/SESSIONS.md: yes)

## Owner answers / technical decisions
See `docs/plans/MASTER_PLAN.md` ("Owner answers") and `docs/DECISIONS.md` (A1–A14, D1–D9).

## Measured at opening (2026-10-24 16:43 UTC)
See the "Measured at opening" table in `docs/plans/MASTER_PLAN.md` (deadline, dataset counts, models, machine).

## Checkpoint map
| C | Closes when | Depends on | State |
|---|---|---|---|
| C0.1 | repo on upstream, .gitignore first | — | ✅ `git log` shows d4a8432 on 0eddbbd; check-ignore → .env, runs/, .venv/ |
| C0.2 | log.txt started | C0.1 | ✅ 6 headers, 6 tool=, 6 model=, 0 secret patterns |
| C0.3 | docs created | C0.1 | ✅ 8 docs + plans/ + handoff/ |
| C0.4 | venv + pins | — | ✅ code/requirements.txt (31 pins) |
| C0.5 | smoke (schema, function call, PNG) | C0.4 | ✅ 4 calls, $0.0005345 |
| C0.6 | public remote pushed | C0.3 | ⬜ |
| C0.7 | memory saved | — | ⬜ |

## Risks / irreversible
- Making the repo public is outward-facing; owner decided. Inspect `git ls-files` before the first push.
- C0.5 costs money (≤ $0.05), recorded in the ledger.
