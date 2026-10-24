# Progress bar — Ghost Data Orchestrate

> **For:** Breno, and anyone who needs the state without reading code. No jargon. **Updated at the end of each
> session, with the date.** Numbers are re-checked at the source when written, never copied from the previous version.

**Last update: 2026-10-24 20:15 UTC.**

`██████░░░░░░░░░░ 3 of 8 sessions closed`

## 2026-10-24 — The project folder now tracks the official challenge files

**What changed:**
- Your folder `/root/hackthon_1` is now a Git project built on the official challenge files.
- Your three planning documents moved to `docs/handoff/`.
- The plan you approved is saved in `docs/plans/MASTER_PLAN.md`.

**How we know:** Git shows the official last change (`0eddbbd`) under our first commit, and your API key file is excluded
from Git.

**Also done:**
- The public GitHub repo is live: https://github.com/Zbreno11-git/ghost_data_orchestrate
- The Python environment is set up.
- The first paid Gemini test passed, costing $0.0005 of the $4.50 you allowed. The model read a customer screenshot correctly and used a tool the way the agent will need to.

**Missing:**
- **From you:** before you leave, keep this Claude Code session running with permissions that allow it to work unattended.
- **From us:** next is the output checker and scorer (session 1), then reading all 94 evidence files (session 2).

## 2026-10-24 20:15 UTC — the answer checker, the scorer and the evidence reader are done; we are ahead again

**What changed:**
- **Checker:** the program checks any answer file against every rule of the challenge format. The official example
  answers pass with 0 problems.
- **Scorer:** it scores answers against the examples. The examples score 100% against themselves, and an empty file
  scores 0.
- **Evidence reader:** all 94 evidence files (databases, logs, documents, screenshots) are read into one searchable
  store, with 0 files skipped and 0 unreadable lines.
- **Screenshots:** each one is read by two different Gemini models, and both agree on every one.
- **Test cases:** three test cases of our own exist. A helper agent wrote them without seeing our code.

**How we know:** 78 automatic tests pass, and each important rule was deliberately broken once to confirm a test catches it.

**Spending:** $0.11 of your $4.50 so far ($0.107 cumulative).

**Worth knowing:** two of the example answers mention records that appear nowhere in the files we are given. No honest
program can find them, so a perfect score on the examples is impossible. We will say so in the report, not invent them.

**Needs your OK:** we finished about 2.5 h earlier than the re-timed plan. Proposal: aim again for the original **~23:00 CDT**
safety package, keeping 00:30 CDT as the fallback.

## 2026-10-24 19:50 UTC — we are about 1h45 behind, and sessions 1 and 2 now run together (your call)

**What changed:** nothing new is built yet since session 0. The next work block merges session 1 (output checker + scorer)
with session 2 (reading all 94 evidence files) to win back time.

**Needs your OK:** the safety package moves from ~23:00 CDT to **~00:30 CDT**. The final freeze stays at 04:00 CDT
because the improvement session gets shorter.

## Timeline you can hold us to (your time, CDT; as approved, before the re-time above)
- ~23:00 tonight: a complete, validated **safety package** (output.csv + code.zip + log.txt) is ready to upload.
- ~04:00 tomorrow: final package frozen. You upload around 05:00; the deadline is 07:00.
