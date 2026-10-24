# Decisions — Ghost Data Orchestrate

> What was decided, why, who decided, and the **written trigger** that reopens it. A decision is not reopened
> unless its trigger fired. Product, money and deadline decisions belong to Breno (the owner).
> Decisions still in force also appear in the "Boundaries" table of `docs/PRIMER.md`.

## Contract discrepancies (official sources vs. planning docs)

Upstream inspected at `0eddbbd` (2026-10-24 15:20Z, "Update AGENTS.md"); the handoff referenced `acb3dfc`.

| # | Sources in conflict | Implication | Resolution | Reopen trigger |
|---|---|---|---|---|
| D1 | handoff SHA `acb3dfc` vs upstream `0eddbbd` | AGENTS.md changed today | Follow current upstream; `git fetch upstream` at each session open and diff the contract files | upstream main moves |
| D2 | Reports at `evaluation/…` (AGENTS §6.8, problem_statement) vs `code/evaluation/…` (README) vs "zip your code/ directory" (site_text.md) | The zip layout could make the reports invisible | Reports live in `code/evaluation/`; `code/README.md` is the source README and root `README.md` points to it; code.zip = `README.md` + `code/`, which satisfies all three readings | organizer clarification |
| D3 | `log.txt` is the chat_transcript (README, site_text) vs `agent-trace.zip` (agent_trace_instructions) | Two different transcript artifacts | Produce both. `agent-trace/` is staged outside the repo; Breno decides whether to upload it | upload form shows/omits a trace slot |
| D4 | AGENTS §3: end time "not configured" | No official deadline in repo | Owner-supplied: **2026-10-25 07:00 CDT = 12:00 UTC** | official update |
| D5 | "Sort rows by case_id", but IDs are unpadded (`case_33`, `case_100`) and the input file is in numeric order | String vs numeric order differ | **Lexicographic string sort** (literal reading; graders join by case_id). The evaluator joins by ID, never by position | organizer clarification |
| D6 | AGENTS §6.5 "disable flows/block restores before changing records; downstream before source" vs README/problem_statement explicit sort | Could imply a dependency order | Canonical operation-rank sort (rank already puts DISABLE/BLOCK first). Dependencies stay internal. S1 must show the 32/32 sample arrays are canonical | a sample array is not canonical |
| D7 | Samples contain 0 NOT_APPLICABLE; activity has 10 `CLASSIFY_REQUEST … non-deletion` events | Intent can't be measured on samples | Measure on custom cases plus manual review of target classifications | — |
| D8 | Handoff model candidates (3.1-flash-lite, 3.8-flash) | Availability unverified | Verified 2026-10-24 via `models.list` and the pricing page (updated 2026-10-22); final pick in the S4 benchmark | benchmark |
| D10 | Samples case_18/case_20 expect future `VERIFY_RECORD_PRESENT` on `audit_record_6645` / `audit_record_5569` vs participant data: neither id appears in any evidence file, CSV or vision extract (grep + store index, 2026-10-24 20:00 UTC) | No grounded engine can name them; sample step recall tops out at 191/193 | Never invent them. Report the ceiling (109/111 resources, 191/193 steps) next to sample metrics in `evaluation_report.md` | a participant source for them is found |
| D11 | AGENTS §6.3 example key order vs sample_output.csv: 24/32 rows use contract order, 8 use alphabetical keys | Byte-identical reproduction of samples is impossible | `dumps()` always writes contract key order; tests assert semantic equality 32/32 and byte equality 24/24 (the grader ignores key order) | — |
| D9 | problem_statement: "Findings and verification steps for COMPLETE cases must cite…" vs AGENTS §6.6: findings always cite; INCOMPLETE future steps use `""` | Ambiguous wording | Findings always cite (samples: 41/41 findings and 34/34 COMPLETE verifications cite a file_id = the 75 non-empty citations; 118 INCOMPLETE remediation/verification steps are `""`); COMPLETE verifications cite; INCOMPLETE remediation/verification use `""` | — |

## Decisions

| # | Decision | Why (measured number if any) | Who, when | Alternative refused, why | Reopen trigger |
|---|---|---|---|---|---|
| A1 | Repo = `/root/hackthon_1` itself (`git init`, `main` from `upstream/main`, upstream push disabled) | Keeps Claude Code traces in `~/.claude/projects/-root-hackthon-1`; AGENTS.md at the cwd root keeps logging automatic | agent, 2026-10-24 | Subdirectory clone: AGENTS.md would not load from the session cwd | — |
| A2 | Public repo `Zbreno11-git/ghost_data_orchestrate` | Owner request (free Actions) | **Breno**, 2026-10-24 | Private until deadline (recommended): refused by owner. The exposure risk was stated and accepted | — |
| A3 | Spend autonomy up to $4.50 cumulative; hard stop in the gateway | Owner answer | **Breno**, 2026-10-24 | Gated/ask-per-stage | ledger ≥ $4.50 |
| A4 | Deterministic evidence layer + LLM investigator over read-only tools; the model cites observation IDs only | 82/111 sample resources are explicitly linked, so the deterministic part does most of the work and the agent resolves the rest within budget | agent, 2026-10-24 | Free-form LLM verdict (ungrounded); pure rules (not an agent, case-family risk) | agent adds nothing over the baseline after S6 |
| A5 | Ownership mode flag `strict` (explicit or unique-weak links only) vs `scored` (best candidate) | 29/111 sample resources lack an explicit co-occurring link; request windows hold 3–15 candidates | **Breno**: decide by metrics (S6) | — | S6 measurement |
| A6 | Native Gemini function calling; JSON action envelope as fallback | Handoff requirement | agent | — | S0 smoke result |
| A7 | Default model `gemini-3.1-flash-lite` ($0.25/$1.50); `gemini-3.8-flash` ($0.75/$3.75) for vision and repair | Cost over 518 cases | agent | `gemini-4-argon` ($2/$10): too expensive for the budget | S4 benchmark |
| A8 | PDFs via `pypdf` (pure Python); PNGs via one cached vision call each | Portable on the judge's machine; PyMuPDF is AGPL; poppler is not guaranteed | agent | PyMuPDF; pdftotext subprocess | pypdf text loses facts versus pdftotext |
| A9 | SQL via in-memory sqlite3 with an authorizer that denies ATTACH/extensions | Safety | agent | Regex parsing of INSERTs (fragile) | a fixture needs a denied statement |
| A10 | Unresolved cases emit the deterministic grounded proposal and are flagged in `runs/<id>/unresolved.md`; an API error is never a status | 518 rows are required and uncertainty stays visible | agent | Default to INCOMPLETE/NOT_APPLICABLE (fabrication) | — |
| A11 | Ledger committed at `state/usage_ledger.jsonl`; caches and checkpoints in gitignored `runs/` | The budget must survive clones and resumes; caches are not ground truth | agent | Ledger in runs/ (lost on clean clone) | — |
| A12 | Docs in English, using software-build structure | Judge and interviewer read English | **Breno** | Portuguese | — |
| A13 | 3 custom cases as a gate, +2 if few sample fixes remain; authored by a subagent that doesn't see engine code | Independent expectations | **Breno** | 8 cases up front | — |
| A14 | Viewer kept as the last optional session (S8) | — | **Breno** | Cut | — |
| A15 | S1 and S2 run as one merged session (one plan file, checkpoints unchanged) | ~1h45 behind schedule at 19:46 UTC | **Breno**, 2026-10-24 19:46 UTC | Separate sessions | — |
| A16 | `CHAT_GPT_TRANSCRIPT_PRE_CLAUDE.md` stays in the repo | It will be organized into the full chat-transcript delivery at the end | **Breno**, 2026-10-24 19:52 UTC | Move to `~/agent-trace/` | final packaging (S7) |
| A17 | PNG vision extracts cached in `state/vision_cache/` and **committed**; each PNG read by `gemini-3.8-flash` and cross-checked by `gemini-3.1-flash-lite` (a disagreement marks the file partial) | A clean clone, CI and the judge's replay need no key; the dual read turns a silent misread into a visible one, for ≈$0.05 | agent, 2026-10-24 | Cache in gitignored `runs/` (every clean clone re-pays and replay needs a key) | organizers forbid derived caches, or the two models disagree on more than 2/11 images |
| A18 | No fixed time target for now: keep working session by session; the 12:00 UTC deadline is the only hard limit | Owner instruction after S1+S2 closed early | **Breno**, 2026-10-24 20:20 UTC | Re-aim at the 04:00 UTC safety package (proposed by the agent) | Breno sets a target, or <4 h remain without a safety package |
| A19 | S3 and S4 run as one merged session (one plan file `docs/plans/session-03-04.md`), executed one at a time: S3 checkpoints close before S4 starts | Momentum after S1+S2 closed early; S4 measures the agent against S3's baseline, so the order cannot flip | **Breno**, 2026-10-24 20:16 UTC | Separate sessions | — |

## A good trigger

Measurable, with who measures it, and never "when there's time".
