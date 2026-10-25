# Error catalog — Ghost Data Orchestrate

> Errors that **the agent** actually made in this project and can cite. This is not a best-practices list.
> Organized **by class**, with the most frequent class on top. A new occurrence goes into its existing class
> as the "N-th occurrence", noting what is new about it. No incident, no entry.
>
> **When you find a defect, open this file before attacking it:** *which class here is this an instance of?*
> If it matches one, the antidote is already written.
>
> Classes expected for this project's error taxonomy (filled only when an incident happens): extraction, identity,
> temporal, retrieval coverage, resource/category mapping, policy, citation, sequence, serialization, budget/ops.

## Index

| No. | Class | Occurrences | Antidote in one line |
|---|---|---|---|
| 1 | Assumed a git command populated the working tree | 1 | After `reset --mixed`, check `git status` before anything else |
| 2 | Staged with `git add -A` without listing new untracked files | 1 | `git status --short` and review every `??` before staging; stage explicit paths |
| 3 | Wrote over a tracked file without reading it first | 1 | `git ls-files <path>` / Read before any `cat >` to a path in the repo |
| 4 | A test fixture admitted a second explanation (mutation stayed green) | 8 | Build the fixture from the real shape that carries the risk, and order events so only the rule under test can explain the result |
| 5 | Wrote a fact (a data literal, a timestamp) before measuring it | 10 | Measure the fact first (one query, `date -u`, `git log`), then write it; times go in by `$(date)` substitution, never typed |
| 6 | Committed after a gate whose output I had not read | 1 | Chain the commit on the gate's exit code (`pytest -q && git commit`), never after a pipe or `;` |
| 7 | A tool reported success on an empty input | 1 | A tool that can find nothing must say so and exit non-zero; "0 problems" over 0 items is not a pass |
| 8 | A search over encoded bytes was read as a search over content | 1 | Search decoded text (every decoder that applies); "not found" is a list of checks, never proof of absence |
| 9 | A check proved *whose* a value is, never *what* it is | 1 | When a value fills a typed slot (the account, a system, a category), check its type in the slot's terms, not only its provenance |

---

### 1. Assumed `git reset --mixed upstream/main` would materialize upstream files

**2026-10-24 — S0 C0.1.** Ran `git init` + `fetch` + `reset --mixed upstream/main` in a directory that already held
untracked files. The index matched upstream, but the working tree did not, so `git status` listed every upstream file as
deleted. It was caught right away by reading `git status`, and fixed with `git checkout -- .` (untracked files were
unaffected).

> **`--mixed` moves HEAD and the index, never the working tree. Read `git status` before the next command.**

**The antidote, concrete:** for "adopt upstream into an existing folder", use `reset --mixed` + `checkout -- .`, then
confirm that `git status --short` lists only our untracked files.

---

### 2. Staged with `git add -A` without listing new untracked files

**2026-10-24 19:50 UTC — pre-compact checkpoint.** Breno had added `CHAT_GPT_TRANSCRIPT_PRE_CLAUDE.md` (his pre-Claude
ChatGPT planning transcript, 502 lines) to the repo root a few minutes earlier. `git add -A` staged it, and it was
committed and pushed to the **public** repo in `1ac9510`. I noticed it only in the commit's file list. A scan found
0 key or token patterns, 0 emails and 0 phone numbers. The file was not removed: deleting it or rewriting public history
is Breno's call.

> **In a public repo, `git add -A` publishes whatever appeared since the last look. New files are reviewed by name
> before staging.**

**The antidote, concrete:** run `git status --short` right before staging; any `??` line I did not create is read and
asked about first. Stage explicit paths (`git add <paths>`), never `-A`, on this repo.

---

### 3. Wrote over a tracked file without reading it first

**2026-10-24 19:55 UTC — S1 C1.3.** Created `code/main.py` with `cat > code/main.py`, assuming it did not exist. It was
upstream's tracked stub (commit `5d42798`, 0 bytes); `git status` showed ` M code/main.py` and `git show HEAD:code/main.py`
confirmed nothing was lost. Same for `code/evaluation/main.py` (also an empty upstream stub). Harmless this time only
because the stub was empty.

> **A heredoc to a repo path is an overwrite. Check `git ls-files <path>` (or Read it) first.**

**The antidote, concrete:** before writing a new file under `code/`, run `git ls-files <path>`; if it is tracked, Read
it and use Edit.

---

### 4. A test fixture admitted a second explanation (mutation stayed green)

**2026-10-24 ~20:46 UTC (before commit `1bdcb99`) — S3 C3.4, two occurrences in one checkpoint.**
- The FR-11 test put `lookup_key` in the wrapper. The exposure check never looks at that key name, so the
  mutation "count wrapper fields as exposure" stayed green. The real risk is the ledger's `subject_reference`.
- The "claims never set state" test placed the SUCCESS claim *before* the present record. "Latest wins" alone
  already kept it present, so the mutation "let SUCCESS mark the row absent" was caught only by the sample gate.

Both fixtures were fixed: the wrapper now carries `subject_reference` and `customer_email`, and the claim now
comes *after* the record. Both mutations are now red.

> **A green test is only proof if no other rule could make it green. Run the mutation before trusting the fixture.**

**The antidote, concrete:** take the fixture's keys from the real record that carries the risk, not from a
convenient name. Order the events so that the rule under test is the *only* thing deciding the outcome.

**3rd–5th occurrences, 2026-10-24/25, S5.** Three mutations survived first:
- **C5.3:** the "table row" fixture put the resource in the panel's first row, which the document loop skipped,
  so the row rule was never reached. The skip was removed; it changed 0 rows.
- **C5.5a:** the fingerprint test edited a dataset table but never asserted that the fingerprint moved.
- **C5.6:** the "no merge across rows" fixture took the row path, so the merge code was never exercised.

Each was rebuilt so that only the rule under test decides, and each mutation is now red. What is new: two of the
three were *unreached* code, not weak asserts.

**6th–8th occurrences, 2026-10-25, S6.**
- **C6.2:** the "trace missing" test asserted that "not recorded in the trace" appeared *anywhere*, and other
  lines print it too, so two mutations stayed green. The asserts are now line by line.
- **C6.5:** a robustness fixture was an unknown JSON shape. Ingest marked it failed in coverage, but the
  test never looked, so "no contamination" was trivially true.
- **C6.5:** another fixture put the shared name in a lookup field that the adapter drops.

Positive controls caught both C6.5 fixtures: the same input, changed so it *must* alter the answer. What is new:
every metamorphic test now carries a control, and the harness asserts that no input failed to ingest.

---

### 5. Wrote a fact (a data literal, a timestamp) before measuring it

**2026-10-24 ~20:26 UTC (before commit `cc3c490`) — S3 C3.0.** I asserted that free-text mentions of `email_delivery_*`, `tombstone_*` and
`object_*` would be indexed once the prefixes were derived, carrying the claim over from the resume block's
"gap" note. A measurement then showed 0 such mentions in the data: those ids occur only as a record's own
`resource_id`. The test was replaced with a synthetic check of the mechanism, and the fact (0 mentions) went
into the commit message.

> **A note in our own docs is a past hypothesis, not a measurement. Measure before pinning a literal.**

**The antidote, concrete:** for every literal in a test, write the one-line query that produced it, and run it
before writing the assert.

**2nd and 3rd occurrences, 2026-10-24, S3+S4: timestamps.** Twice I wrote times into the docs by estimating
instead of reading the clock.
- At C3.4 I wrote "~21:30" and "~20:45" when the commits were at 20:48 and 20:28. The S3 close caught it.
- At the S4 close I wrote "21:18–21:22 UTC" into PRIMER, SESSIONS, STATUS, PROGRESS and A23 when the clock
  read 21:15 and the close commit is at 21:13. The pre-compact check caught it.

All stamps were corrected to commit-backed times. What is new: a timestamp is a measurement too.

> **Never type a time from memory: `date -u` or `git log --date=format-local:%H:%MZ` first.**

**4th–9th occurrences, 2026-10-24/25, S5: timestamps again, six times in one session.**
- **Plan mode:** "21:5x" for an answer that came at 21:41:52, and "21:34–21:50" for an opening that ended at 21:44.
- **Progress notes:** "C5.0 ✅ 21:47Z" (commit at 21:45:41) and "C5.5 ✅ 22:20Z", typed in the same command that
  printed 22:16:31.
- **Code:** a docstring said "measured 22:05 UTC" at 22:02.
- **Decisions:** A28/A29 were dated "~22:28 UTC" when the owner's answer arrived at 00:41:32 the next day. The
  wait for the answer took two hours, and I assumed none had passed.

All were corrected to clock- or JSONL-backed times before or right after their commit. What is new: the rule
alone failed six times, so it became structure. Progress notes now take times only from `$(date -u +%H:%MZ)`
in an unquoted heredoc, and decisions take the event time from the session JSONL.


---

### 6. Committed after a gate whose output I had not read

**2026-10-24 22:09 UTC — commit `5fbb4c2` (S5 C5.4).** One command ran the agent tests, printed `1 failed,
14 passed`, and then committed. A `sed` had put `import json` inside the module docstring. The next commit
(`0d93699`) fixed it. The failure was visible in the output that preceded the commit in the same command.

> **A gate whose exit code does not stop the commit is decoration.**

**The antidote, concrete:** `pytest -q && git commit …`, with no `| tail` in between (a pipe returns tail's
status), or `set -o pipefail`.

---

### 7. A tool reported success on an empty input

**2026-10-24, between commits `c3cc0fc` (22:23 UTC) and `092d700` (22:27 UTC) — `scripts/stage_traces.py` first dry run (S5 C5.13).** It printed `1 files; 0
redactions …; problems: none` and exited 0. It had derived the session folder as `-root-hackthon_1`, but Claude
Code writes `-root-hackthon-1`, so not one session was found. Only reading the file list showed the trace was
empty. The folder is now derived the way Claude Code does it (every non-alphanumeric character becomes "-"),
and finding no session exits 1.

> **"No problems" over zero items is not a pass (falha-ruidosa: the empty result that looks healthy).**

**10th occurrence, 2026-10-25 01:35 UTC, S6 opening.** The approved plan dated the C6.1 pre-measurement "01:33–01:40
UTC"; the first log write read the clock at 01:35:06Z, so the end was an estimate. session-06.md carries only
clock-bounded times ("before 01:35:06Z").

---

### 8. A search over encoded bytes was read as a search over content

**2026-10-25, found at S6 C6.1 (defect from S5 C5.15, `code/evaluation/diagnose.py`).** The cause "absent from
supplied evidence" was decided by a raw-byte regex over every participant file. All four PDFs are
FlateDecode-compressed: 10 of the 10 resource and user ids in them are invisible to that search (measured with
pypdf vs the bytes). support_001 occurs in no other source, so a miss on it would have been published as a
dataset gap. S5's `diagnostics.md` and the evaluation report used the phrase for 3 items; the decoded search
still finds none of those 3, but the S5 claim was unproven when written.

Fixed: `code/evaluation/corpus.py` decodes every source (raw text, pypdf and pdftotext, all vision extracts, the
activity and audit CSVs) and the cause is now "no supporting fact found" (or "undetermined" when a source cannot
be decoded), with the checks listed. `test_diagnose.py` is red against the raw-byte version (mutation: PDFs read
as bytes).

> **A search answers for the representation it searched. "Not in the bytes" is not "not in the document".**

---

### 9. A check proved *whose* a value is, never *what* it is

**2026-10-25, found at S6 C6.7 by the independent custom case `tombstone_pair` (defect since S4/S5, `agent.py`).**
The agent submitted the subject's tombstone as the person's *account*. The lineage check (A27) passed: the record
does carry the subject's identifier. But `apply_submission` then wrote it into the account slot with the system
forced to `account_service`, so policy read it as a USER_PROFILE and planned **DELETE** for a record the rules
require to be kept and redacted (rule_15). Support also rose from unresolved to resolved.

No sample exercised it: in the samples, every agent account pick was an `account_*` resource.

Fixed: an account choice must be a resource whose own records belong to the account system
(`canonical_system`, the same function the deterministic path uses). `apply_submission` no longer forces the
system. Test red first, with a close positive (an account_service record with the same lineage is accepted);
mutation red.

**Second-order effect, caught by replay.** The first version put the new check *before* the existing candidacy
check. Three cases (case_147/208/406), in which the S5 model had submitted a user id as the account, were then
rejected with a different message. A different message makes a different repair request, so replay raised
ReplayMiss, and the three cases fell back to their deterministic rows: same rows, no money spent. With the
candidacy check first, the old wording and its cached repairs hold. A rejection message is part of the
cache key.

> **Provenance answers "whose"; a typed slot also needs "what". Check both where the value enters the slot.**

