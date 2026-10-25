# Progress bar — Ghost Data Orchestrate

> **For:** Breno, and anyone who needs the state without reading code. No jargon. **Updated at the end of each
> session, with the date.** Numbers are re-checked at the source when written, never copied from the previous version.

**Last update: 2026-10-25 04:52 UTC.**

`██████████████░░ 7 of 8 sessions closed; the last one (S7) is under way`

## 2026-10-25 04:52 UTC — your Mac check passed; over to you for the final steps

Every check passed on your Mac (macOS 13.7.8, Intel, Python 3.13.5), a different machine, system and Python from
the server: same files, the same answers reproduced byte for byte offline at no cost, 0 errors, 310 tests passed,
and the viewer rebuilt identically. Recorded in `docs/release/mac_acceptance.md`; the closing log entry is written.

**Now: steps 2-7 below** (`/export`, close Claude Code, run the script, copy, upload, tell me). Please don't send
another message in this session before running the script: it checks that every message is in `log.txt`.

## 2026-10-25 04:44 UTC — the final steps are ready and rehearsed; waiting for your Mac result

**What changed:** the end-of-project script (`scripts/finalize_release.sh`) is written, tested, and was run end to
end in a throw-away copy of the project. The rehearsal caught one real flaw, now fixed: a trace with no session in
it would have been accepted. Nothing was uploaded or published.

### Your final steps, in order (after the Mac check)

1. **Send me your Mac results.** I record them in `docs/release/mac_acceptance.md` and write the closing log
   entry. After that, don't send me any more messages: an unlogged message stops the script on purpose.
2. **In this Claude Code session, run `/export`.** Save it under its default name in the project folder, or in
   `~/ghost-exports/`. If your editor has no `/export`, skip this step and use `--no-export` in step 4: the
   session files themselves are the full trace.
3. **Close Claude Code**, so the session file is complete.
4. **In a terminal on the server:**
   ```bash
   cd /root/hackthon_1 && bash scripts/finalize_release.sh      # or: ... finalize_release.sh --no-export
   ```
   It checks everything again, builds `agent-trace.zip`, puts the four files in `~/ghost-release/`, writes the
   checksums and the release record, and pushes them. It ends with "FROZEN" and the list of files. Any problem
   prints "STOP: …" and changes nothing.
5. **Copy the four files to your computer:**
   ```bash
   scp 'root@<vps>:/root/ghost-release/*' ~/ghost-upload/
   ```
6. **Upload them** at https://www.hackerrank.com/contests/hackerrank-orchestrate-october26/challenges/ghost-data-still-exists

   | Slot | File |
   |---|---|
   | code.zip | `code.zip` |
   | output.csv | `output.csv` |
   | chat_transcript | `log.txt` |
   | agent trace | `agent-trace.zip` |
   | AI interview | you (notes: `docs/release/INTERVIEW_CHEAT_SHEET.md` and `WALKTHROUGH.md`) |

7. **Tell me when it is submitted** (in a new session, if you like). Until you say so, it is not submitted.

**If time runs short:** with less than 2 hours to the 12:00 UTC deadline and no finished release, upload the
current `/root/ghost-mac/` files plus `log.txt` (A31). The older safe set is in `/root/ghost-fallback-s5/`.

## 2026-10-25 04:31 UTC — package rebuilt after two small fixes; your Mac check is next

**What changed:**
- **Same answers.** The answers file is unchanged (`0e04ffe2…`); every re-run since 04:01 reproduced it byte for
  byte, all from saved AI responses, at **$0**.
- **Two display defects fixed** (neither touched an answer):
  - a file-reading check could have called an intact run "damaged" if a record held a rare Unicode line break;
  - for 3 cases, after the AI review the viewer stopped showing the "uncertain account" note.
- **The package's front page (`README.md`) is now ours.** It used to be the challenge's starter page, telling a
  reader to "build your solution". The starter text is kept in `docs/`.
- **A safety rule moved into code:** a package that fails its checks can no longer overwrite the last good one.
- **New package `0c4dfef1…`** passed every check again (offline, no key, answers and viewer identical). The
  viewer was re-checked in a browser at desktop and phone width.
- **Spending:** unchanged, $2.27 of $4.50.

**Coming to you, in order:**
1. **Now: the Mac check**: files in `/root/ghost-mac/` on the server, steps in `MAC_RUNBOOK.md` there.
2. Then the final steps: `/export`, quit, run the finalize script, upload.

## 2026-10-25 04:01 UTC — new answers file built and checked; three steps left

**What changed:**
- **Your two calls are applied.** Timing-picked accounts are now asserted only where the method held up in our
  hide-and-recover test, with the others shown as "uncertain". Snapshots dated before the audit, found inside
  later exports, are read but never cited.
- **Score on the 32 examples:** every status right (32/32); fully right 12 → **14**; steps found 162 → **167 of
  193**; listed steps that are right 167 of 168. No correct step was lost and nothing flipped. The AI reviewer
  changed no answer this time: it only refined certainty labels.
- **The 5 test cases:** all fully right.
- **New answers file and code package are built and pass every release check** on the server. The checks ran
  offline and without the key, and reproduced the answers file byte for byte. They also confirmed no copy of the
  challenge data inside the package.
- **The evidence viewer works** in a browser on desktop and phone width, with no internet.
- **The previous safe version** (from 01:14) is kept aside, untouched, in case anything goes wrong.
- **Spending:** $2.27 of your $4.50 (this session $0.39).

**Coming to you, in order:**
1. The Mac check, with a copy-paste runbook (about 5 minutes).
2. At the very end: `/export` and quit, run one script, then upload. You'll get a checklist.

## 2026-10-25 02:48 UTC — final session started (S7, with the viewer folded in)

**What changed:** you merged the last two sessions into one. It ends with the frozen upload set, after the evidence
viewer, the hardening, your Mac check and the trace collection. Nothing has been uploaded; nothing will be until you
do it yourself.

**Coming to you, in order:**
1. A short table on the 19 "weak" timing-picked accounts: keep them, or turn them into "uncertain candidates" (no
   step in the answers). Measured on both sides before you choose.
2. The Mac check, with a copy-paste runbook.
3. At the very end: `/export`, quit, then the upload checklist.

## 2026-10-25 02:09 UTC — session 6: checked every remaining gap; one real bug found and fixed; answers unchanged

**What changed:**
- **We hunted for missing answers backed by evidence.** For each of the 24 steps we still miss on the examples,
  we followed the evidence to where it stops:
  - 21 point at records that name nobody (anonymized profiles, blank lookups);
  - 3 can be tied to the person only by files captured after the audit date, which the rules forbid.

  So no new link is allowed, and we added none. Guessing from timing would add more wrong steps than right ones;
  we measured it (13 wrong for 5 right) and kept the stricter mode.
- **We checked that nothing was lost while reading the files:** every line that mentions a record was matched to
  what the engine extracted, and the screenshots were checked by eye. Nothing was missed. One of our *checking
  tools* had a blind spot (it could not read compressed PDFs); it is fixed.
- **Two new test cases, written independently, caught a real bug:** the AI reviewer could have marked a
  "deleted-account reference" (which must be kept) as the person's account, which would have planned its deletion.
  That can no longer happen. It never affected the answers file.
- **New:** `main.py explain <case>` explains any answer step by step from the recorded evidence, without calling
  the AI. Examples are in `docs/explanations/`.
- **The answers file did not change** (re-produced byte for byte by the new code, for $0). Score on the 32
  examples is the same: every status right, 12 fully right, 162 of 193 steps found, 162 of 163 listed steps right.
  The 5 test cases are all fully right.

**Spending:** $1.88 of your $4.50 (this session $0.006).

**Needs your decision (no rush; default is to keep):** 19 answers use an account picked by timing and elimination
(labelled "weak"). Your new rule forbids *new* links of that kind; these existed before. Keep them (default) or remove
them?

## 2026-10-25 01:14 UTC — the answer file and the code package are ready to upload (safety package done)

**What changed:**
- **The answers file is ready:** `output.csv` at the root of the project holds all 518 answers.
  - It passes every format rule with 0 problems.
  - 175 answers are fully backed by evidence, 18 partly, and 325 have an open point. Most of those 325 have no
    evidence saying which deleted account was the person's; the rest of each answer is still evidence-backed.
  - 3 answers are informed guesses, as you decided, and are labelled as guesses.
- **The code package `code.zip` is ready.** We unpacked it in an empty folder on this server, installed only what
  it lists, cut off the network, and re-ran it. It reproduced the answers file exactly, without the API key.
- **The two required reports are inside the package:** the evaluation report and the usage report.
- **Score on the 32 example answers:**
  - every deletion status is right;
  - 12 examples are fully right (11 before this session);
  - 162 of the 193 expected steps are found, and 162 of the 163 steps we list are right.
- **The AI investigator** now has to prove every decision with a chain of evidence. Its one earlier "win" turned out
  to be a lucky guess; the one real find is now applied to every case.
- **The chat log (`log.txt`)** was checked against the original session records. Two old entries were corrected by
  adding records at the end; nothing was erased.

**Spending:** $1.87 of your $4.50 (this session $1.53).

**To upload — at the very end, after all sessions (your call, 01:21 UTC)** (at https://www.hackerrank.com/contests/hackerrank-orchestrate-october26/challenges/ghost-data-still-exists):
1. `/root/hackthon_1/output.csv`
2. `/root/hackthon_1/code.zip`
3. `/root/hackthon_1/log.txt` as the chat transcript
4. Optional: `agent-trace.zip`. Before we build it, run `/export` in this Claude Code session, save the export
   into `~/agent-trace/claude-code/`, and quit the session.

**Needs your decision:** `output.csv` and `code.zip` are **not** in the public GitHub repo, so other teams cannot
copy them. Say so if you want them there.

**Next:** session 6 (fix the largest remaining cause the examples show; a command that explains any one case), then
session 7 (release record, a Mac runbook, an interview cheat sheet). The Mac check stays "pending" until it is run
on your Mac.

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

## 2026-10-24 20:56 UTC — the program now answers every request on its own, without AI, and says how sure it is

**What changed:**
- The program goes from a request to an answer by itself: it finds the person (including old email addresses),
  ignores evidence dated after the audit, finds the person's records, and applies the deletion rules.
- **On the 32 examples:** every deletion status is right (32/32), and when it lists a step it's right in 161
  of 162 cases. It still misses about 1 step in 6, mostly accounts that were already deleted and that no
  evidence ties back to the person.
- **On the 518 real requests:** it writes 518 answers and labels each one:
  - 169 "solid";
  - 34 "plausible, weak link";
  - 315 "unresolved", most of them only because the deleted account can't be identified from the evidence.
  5 answers can't be built at all yet; it says so instead of guessing.
- Your six safeguards are now rules with tests.

**How we know:** 141 automatic tests pass. The three test cases written by a helper agent are reproduced exactly.

**Spent:** $0 this session ($0.107 total of $4.50).

**Missing:**
- **From you:** nothing new. At some point before publishing, a decision on the 5 answers that have no evidence
  to stand on.
- **From us:** next, the AI investigator (session 4), measured against this baseline.

## 2026-10-24 21:13 UTC — the AI investigator works, costs a third of a cent per request, and doesn't guess

**What changed:**
- **Every paid call goes through one gate.** It books each call before sending it, stops at your $4.50
  limit, and doesn't charge for requests Google rejects outright.
- **Answers are cached**, so a re-run or a re-check costs nothing and needs no key.
- **The AI investigator** (Gemini 3.1 Flash-Lite) reviews each case using read-only tools. It can only point
  at evidence it actually saw; the program still writes the answer.
- **It reads intent too.** On all 518 requests it agrees with our rules: 508 ask for deletion and 10 don't.

**How we know:**
- **Stop and resume:** we stopped a run halfway and restarted it, and no paid call was repeated. Re-running
  offline gives byte-identical output.
- **On 10 test cases:** the investigator improves on the plain program only slightly (one more fully right
  case). The bigger model wasn't better and costs 4× more, so we keep the cheap one.
- **Why the gain is small:** the remaining misses are accounts that were deleted, where no evidence names
  their owner. The investigator correctly refuses to guess.

**Spent:** $0.237 this session; $0.339 total of $4.50.

**Missing:**
- **From you:** before publishing, a decision on the 5 answers that have no evidence to stand on.
- **From us:** next, a pilot on 30 real requests, then the full run, the reports and the upload package
  (session 5).
