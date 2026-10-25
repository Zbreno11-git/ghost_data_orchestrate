# Requirements → checkpoints

FR/NFR IDs come from `docs/handoff/GHOST_DATA_VISION_REQUIREMENTS.md` §6 and §10. A requirement counts as met
only when its proving checkpoint is ✅ in `docs/SESSIONS.md`. The proving command is in `docs/plans/MASTER_PLAN.md`.

| ID | Requirement (short) | Proving checkpoint(s) |
|---|---|---|
| FR-01 | Deletion authorization incl. languages/mixed | C4.4 (+ custom NA cases) |
| FR-02 | Current + historical identifiers, no decoy merge | C3.1 |
| FR-03 | Discover copies across systems/formats | C2.1–C2.6 |
| FR-04 | Admissible state at audit_at | C3.2; S5 C5.3b (two clocks, A26: `test_temporal.py`, 5 mutations) and C5.2 (as-of ownership, A24); S7 C7.1T snapshot time policy (A36; readable ≠ citable, `test_temporal.py`) |
| FR-05 | Claims vs observed state | C2.3, C3.4 |
| FR-06 | Replicas preserved | C2.2, C3.4 (state per physical copy, A20) |
| FR-07 | Active data flows | C3.4, C3.5 |
| FR-08 | Restore risks with retention | C3.4, C3.5 |
| FR-09 | Apply deletion_rules.csv | C3.4 |
| FR-10 | Tombstone stable ref vs prohibited ids | C3.4 |
| FR-11 | Wrapper vs business fields | C2.3, C3.4 (exposure reads fields only) |
| FR-12 | Anonymous resources via lineage | C3.1, C3.3; S5 C5.4 agent lineage (A27, `test_agent.py`), A30 subject records name their sources; S7 C7.1 masked backtest, only measured deductions asserted (A34/A34a) |
| FR-13 | Complete finding/remediation/verification sets | C3.5 |
| FR-14 | Eligible evidence citations | C1.3, C3.5 |
| FR-15 | Exact schema + order | C1.1–C1.3 |
| FR-16 | Bounded model/tool loop | C4.3; S5 C5.4 semantic validation of every decision (A27); S6 C6.7 an account must belong to the account system (ERRORS #9) |
| FR-17 | fresh/live/resume/replay | C4.5; S5 C5.5a fingerprinted checkpoints; C5.11 `scripts/package_code.py` (clean unpack, no network, `cmp` identical) |
| FR-18 | Public + custom evaluation | C1.4; S5 C5.9 `code/evaluation/evaluation_report.md`, C5.5 `compare.py`, C5.15 `diagnose.py`; S6 decoded-content search (`corpus.py`), `gate.py` accuracy gate, 5 independent custom cases, `docs/diagnostics/s6/` |
| FR-19 | Usage + cumulative budget | C4.1; S5 C5.10 `code/evaluation/usage_report.md` from the run's `llm_keys.jsonl` + ledger |
| FR-20 | Reproducible artifacts + transcripts | C0.2; S5 C5.11 (hash-verified replay artifacts), C5.12 `log_audit.py`, C5.13 `stage_traces.py`; C7.3 |
| NFR-01 | Traceability | C2.6; S6 C6.2 decision trace + `main.py explain` (no model call), `docs/explanations/`; S7 C7.2 provenance saved and verified with the run, offline viewer (`test_provenance.py`, `test_viewer.py`) |
| NFR-02 | Deterministic compilation | C1.2, C4.5 |
| NFR-03 | Honest uncertainty | C3.5 (unresolved list), A10; S5 `support_of` caps (A24), heuristic rows labelled (A29) |
| NFR-04 | Budget discipline | C4.1 |
| NFR-05 | Interrupted-run recovery | C4.5 |
| NFR-06 | Portable local execution | S5 C5.11 VPS check (passed 2026-10-25 01:12 UTC); S7 C7.4 VPS check on the rebuilt package; Mac acceptance C7.6 pending (Breno, `docs/release/MAC_RUNBOOK.md`) |
| NFR-07 | Input isolation | C3.2, C4.2; S5 C5.2 as-of owner index and solver (A24); S6 C6.5 metamorphic tests (shuffle, duplicate, other person, post-cutoff) |
| NFR-08 | Reusable internals | package layout (S1–S4) |
| NFR-09 | Deadline awareness | timeline in SESSIONS |
| NFR-10 | Maintainable delivery | C5.3, C5.4 |

## Official submission contract → artifact → how it is verified (S7 C7.5)

Sources: `AGENTS.md` §6, `README.md` (starter), `problem_statement.md`, `agent_trace_instructions.md`.

| Requirement | Artifact | Verified by |
|---|---|---|
| 518 rows, exact header, sorted by case_id, valid JSON arrays, consecutive steps, phase order, legal op/state pairs | root `output.csv` | `main.py validate output.csv` → `0 violations … against 518 targets requests` (23 codes, `test_validate.py`) |
| findings cite evidence; COMPLETE verifications cite; future steps `""`; never evidence captured after audit_at | `output.csv` | same validator (FINDING_UNCITED, COMPLETE_VERIFY_UNCITED, FUTURE_STEP_CITED, EVIDENCE_AFTER_AUDIT) |
| participant data only; no labels, ids or case families in code | `code/` | `test_*` grep gate on the prediction path for `sample_output`; DECISIONS D10–D13 |
| runnable from the terminal, reads `dataset/`, writes `output.csv` | `code/main.py`, `code/README.md` §1–4 | `scripts/package_code.py` clean unpack: fresh venv, dataset outside the zip, replay `cmp`-identical |
| setup and run instructions in README | `README.md` (root pointer, D2) + `code/README.md` | C7.6 Mac runbook executes them on a second machine |
| reports at `code/evaluation/evaluation_report.md` and `usage_report.md` (starter README paths; AGENTS' `evaluation/…` wording reconciled by the D2 layout) | inside `code.zip` | `release/checks.py` REQUIRED paths, `test_release.py` |
| evaluation report: status, step/field, sequence accuracy; ≥3 custom cases; failures and improvements | `evaluation_report.md` | generated by `scripts/make_reports.py` from run files; 5 custom cases with expected → observed |
| usage report: providers/models, calls, input/output tokens, totals and averages, per-model and overall cost | `usage_report.md` | generated from the final run's `llm_keys.jsonl` and the ledger |
| no dataset, venv, caches, nested archives, secrets in code.zip | `code.zip` | `release/checks.py` inventory (fixture allowlist pinned by sha256), `test_release.py` |
| chat transcript = root log.txt in AGENTS §5 format | `log.txt` | `scripts/analysis/log_audit.py` (every human message logged literally; tool=/model= present) |
| agent trace ZIP of all sessions, original formats, secrets redacted | `agent-trace.zip` | `scripts/stage_traces.py --zip` (redaction scan, JSONL re-parsed); checksum in `docs/release/SHA256SUMS` |
| AI interview | — | `docs/release/INTERVIEW_CHEAT_SHEET.md` |
