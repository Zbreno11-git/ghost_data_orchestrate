# Custom evaluation cases

Five small, self-contained datasets written for this project, used as an evaluation gate next to the 32 public
samples. Each folder holds:
- `dataset/`: the inputs, in the challenge's file formats;
- `expected_output.csv`: the answer, written before the engine was run on the case;
- `RATIONALE.md`: the readable specification (scenario, inputs, what it tests, the expected answer and why).

**These are not the supplied challenge dataset.** They were authored independently by a sub-agent that saw only
`problem_statement.md`, AGENTS §6 and `deletion_rules.csv`: never the public sample answers, the engine or its
runs (DECISIONS A13). All people and domains are fictional.

**Provenance, stated accurately.** The scenarios, people, records and expected answers were authored for these
cases. The policy file `dataset/deletion_rules.csv` in each case is the official policy, copied unchanged so that
each case applies the real rules. That content was reused, not independently invented. These five files are the
only bytes in `code/` identical to a supplied dataset file, and each is listed, with its sha256, in
`FIXTURE_ALLOWLIST.json` and `FIXTURE_ALLOWLIST.md`. The package check rejects any other copy (`code/release/checks.py`).

| case | folder | expected | what it tests |
|---|---|---|---|
| custom_01 | `historical_email_replica` | INCOMPLETE, 3 steps | identity through a historical email; a dirty failover replica behind a clean primary |
| custom_02 | `success_claim_contradicted` | INCOMPLETE, 3 steps | a SUCCESS operation result contradicted by later admissible evidence; a German request |
| custom_03 | `post_cutoff_evidence_ignored` | COMPLETE, 3 steps | evidence captured after audit_at is ignored; COMPLETE verifications cite proof |
| custom_04 | `tombstone_pair` | INCOMPLETE, 3 steps | an account tombstone redacted, not deleted; one compliant copy and one exposing copy |
| custom_05 | `clean_primary_dirty_replica` | INCOMPLETE, 3 steps | an older dirty replica is not cleared by a newer clean primary; a post-cutoff clean replica as a trap |

Observed results (status, steps, citations) are reported in `../evaluation_report.md`.

Run one case: `python code/main.py run --split targets --dataset code/evaluation/custom_cases/<folder>/dataset --out runs/<name>`,
then `python code/evaluation/main.py --pred runs/<name>/output.csv --gold code/evaluation/custom_cases/<folder>/expected_output.csv`.
