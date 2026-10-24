# Ghost Data Orchestrate — progress in flight

> Working file: describes the **current** session. Updated at every checkpoint. A delivered and answered
> handoff moves to `docs/HANDOFFS.md`, after relocating what lives only here (open decision → SESSIONS,
> lesson → ERRORS, constraint → PRIMER).

## ▶️ RESUME HERE — 2026-10-24 ~17:25 UTC (S0 closed; S1 next)

**State:** tree clean after the S0-close commit · `main` == `origin/main` · on GitHub: yes (public) ·
background runs: none · locks: none

**Exact next step:** open S1 (write `docs/plans/session-01.md` first): write `code/ghostaudit/contract.py` + `code/tests/test_contract.py`;
expect `pytest code/tests/test_contract.py` → 193/193 sample steps legal, 32/32 canonical arrays reproduced.

**Plan checkpoints (S0):**
| C | Closes when | State |
|---|---|---|
| C0.1 | repo on upstream, .gitignore first | ✅ |
| C0.2 | log.txt started | ✅ |
| C0.3 | docs created | ✅ |
| C0.4 | venv + pins | ✅ |
| C0.5 | Gemini smoke | ✅ $0.0005345, 4 calls |
| C0.6 | public remote pushed | ✅ 54a7673 |
| C0.7 | memory saved | ✅ |

**Don't forget (only here):**
- The `thought_signature` comes back on function-call parts (gemini-3.1-flash-lite). The agent loop must append the model's
  full `Content` to history unchanged, as `scripts/smoke_gemini.py` does.
- `thinking_level="MINIMAL"` gave 0 thought tokens in all 4 smoke calls, so the cost is input + candidates only.
- Vision on flash-lite read the account console exactly (1,101 input tokens per image ≈ $0.0004). 11 PNGs ≈ $0.005.

**Depends on Breno:** keep the session running with unattended permissions before leaving.

## Proofs this session

| Proof | Command | Result (literal) | When |
|---|---|---|---|
| upstream base | `git log --oneline -2` | `d4a8432 Add .gitignore…` / `0eddbbd Update AGENTS.md` | 16:52Z |
| ignores | `git check-ignore .env runs/ .venv/` | `.env` `runs/` `.venv/` | 16:52Z |
| log format | `grep -c '^## \[' log.txt`; tool=/model= counts; secret grep | 6 / 6 / 6 / 0 | 16:52Z |
| deps | import check | genai 2.33.0, pypdf 6.21.2, pydantic 2.14.1, pytest 9.1.1 | 17:05Z |
| remote | `gh repo view … --json visibility` ; `git rev-parse HEAD origin/main` | `PUBLIC` ; both `54a7673…` | 17:20Z |
| smoke | `.venv/bin/python scripts/smoke_gemini.py` | a: `{"authorizes_deletion": true, "language": "es"}`; b: call `lookup_resource(account_3136)`, thought_signature true; c: `user_11`/`account_5762` exact; settled $0.0005345 | 17:10Z |
