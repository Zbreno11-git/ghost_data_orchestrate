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

