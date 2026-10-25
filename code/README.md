# Ghost Data Still Exists — deletion-audit agent

For each request in `dataset/deletion_requests.csv` this program writes one row of `output.csv`
(`case_id,deletion_status,steps_json`). It decides whether the person asked for deletion, reconstructs every
relevant copy of their data as of `audit_at` from participant evidence only, applies `deletion_rules.csv`,
and emits canonically ordered findings, remediation and verification steps that cite the evidence they rest on.

## Setup

Python 3.12, from the repository root:

```bash
python3 -m venv .venv
.venv/bin/pip install -r code/requirements.txt
export GEMINI_API_KEY=...        # only for live model calls; replay and the deterministic engine need none
```

The key is read from the environment, or from an uncommitted `.env`. It is never printed or logged.

## Run

```bash
# the submitted configuration: deterministic evidence engine + Gemini intent pass + agent on weak/unresolved
.venv/bin/python code/main.py run --engine agent --mode live --agent-scope non_resolved --split targets --out runs/final

# offline, no key, from the shipped responses (byte-identical output; a missing response is an error, never a call)
.venv/bin/python code/main.py run --engine agent --mode replay --agent-scope non_resolved --split targets --out runs/replay

# no model at all (same evidence engine, rule-based intent)
.venv/bin/python code/main.py run --split targets --out runs/det

.venv/bin/python code/main.py validate runs/final/output.csv               # contract invariants, 518 rows
.venv/bin/python code/evaluation/main.py --pred runs/s/output.csv          # metrics vs the public samples
.venv/bin/python -m pytest code/tests -q                                    # the test suite
```

A run writes into its own directory, never over the root `output.csv`:
- `output.csv`;
- `decisions.jsonl`: per case, every resource with its tier, category, treatment, verdict, copies and proof;
- `unresolved.md`;
- `summary.json`;
- `llm_keys.jsonl`: every model response used;
- `cases/` checkpoints, so a killed run resumes without repeating paid calls.

The submitted `output.csv` is copied from a run only after it validates.

## How it decides

1. **Ingest** (`ghostaudit/ingest/`). All 94 evidence files (SQL snapshots, JSON, logs, PDFs, screenshots,
   text) become `Observation`s with provenance and two clocks:
   - `captured_at`: the artifact's capture time;
   - `observed_at`: the record's own time.

   Screenshots are read once by a vision model and cached in `state/vision_cache/`, cross-checked by a
   second model.
2. **Identity** (`identity.py`). The subject's identifiers as of `audit_at`: current and historical emails,
   phones and hashes. Matching is exact and normalized; an address held by two people is an ambiguity, never
   a guess.
3. **Cutoff** (`temporal.py`). Every read goes through `CaseView`: an observation is admissible only if its
   artifact was captured, and its event happened, at or before `audit_at`.
4. **Ownership** (`ownership.py`).
   - A resource is linked when an admissible unit names it together with a subject identifier. A unit is a
     record, one table row, or a single-subject page.
   - Workflow timing only produces candidates.
   - The primary account is assigned one-to-one across all requests, by deduction from what existed at each
     case's cutoff.
5. **Policy** (`policy.py`).
   - State is reconstructed per physical copy (primary, replicas, documents) from the latest observation by
     event time. A clean primary never clears a dirty replica.
   - Disagreeing observations at the same instant are a conflict, not a tie-break.
   - Activity rows and reported statuses are claims and never set a state.
6. **Plan** (`planner.py`).
   - Each verdict becomes contract steps: findings cite their proof; remediation and later verification use
     `""`.
   - Canonical order, then validation.
   - Each row gets a support level (`resolved`, `weak`, `unresolved`) that never claims more than the
     evidence.
7. **Agent** (`agent.py`, `tools.py`, `prompts/investigator.md`).
   - A bounded Gemini investigator reviews weak and unresolved proposals with 9 read-only, cutoff-bound
     tools.
   - It can only cite observations a tool returned. Each decision (account, addition, exclusion) is accepted
     only if the cited evidence chains the resource to the subject.
   - The engine, not the model, recompiles the steps.
8. **Gateway** (`llm/gateway.py`).
   - Every paid call is reserved, sent and settled in `state/usage_ledger.jsonl`, by error class, against a
     hard budget.
   - Responses are cached by request content; replay never builds a client.

Rows the evidence cannot settle are flagged rather than filled: `unresolved.md` lists them. Three target rows
carry heuristic predictions by the owner's decision (A29 in the repository's `docs/DECISIONS.md`), each
labelled as such.

## Evaluation and usage

- `evaluation/evaluation_report.md` covers:
  - status, step, field and sequence accuracy on the 32 public samples, with full denominators;
  - three independently written custom cases;
  - case-by-case comparisons (`evaluation/compare.py`);
  - failures found and fixed.
- `evaluation/usage_report.md` gives providers, models, calls, tokens and cost for the run that produced the
  submitted `output.csv`.

## Replay artifacts in `code.zip`

`state/vision_cache/` and `runs/cache/llm/` each ship a `MANIFEST.json` of sha256s, which the runtime verifies
on every read (`ghostaudit/artifacts.py`). The LLM directory holds exactly the responses the final run used. To
reproduce `output.csv` offline:
1. unpack `code.zip`;
2. place the challenge `dataset/` beside `code/`;
3. install `code/requirements.txt`;
4. run the replay command above.
