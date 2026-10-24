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

---

### 1. Assumed `git reset --mixed upstream/main` would materialize upstream files

**2026-10-24 — S0 C0.1.** Ran `git init` + `fetch` + `reset --mixed upstream/main` in a directory that already held
untracked files. The index matched upstream, but the working tree did not, so `git status` listed every upstream file as
deleted. It was caught right away by reading `git status`, and fixed with `git checkout -- .` (untracked files were
unaffected).

> **`--mixed` moves HEAD and the index, never the working tree. Read `git status` before the next command.**

**The antidote, concrete:** for "adopt upstream into an existing folder", use `reset --mixed` + `checkout -- .`, then
confirm that `git status --short` lists only our untracked files.
