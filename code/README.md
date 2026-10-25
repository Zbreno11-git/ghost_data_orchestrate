# Ghost Data Still Exists — deletion-audit agent

For each request in `dataset/deletion_requests.csv` this program writes one row of `output.csv`
(`case_id,deletion_status,steps_json`). It decides whether the person asked for deletion, reconstructs every
relevant copy of their data as of `audit_at` from participant evidence only, applies `deletion_rules.csv`,
and emits canonically ordered findings, remediation and verification steps that cite the evidence they rest on.

Reports: [`evaluation/evaluation_report.md`](evaluation/evaluation_report.md) (accuracy, custom cases, failures and
fixes) and [`evaluation/usage_report.md`](evaluation/usage_report.md) (models, calls, tokens, cost of the final run).

## 1. Setup

Python 3.11 or newer (`tomllib`); developed and tested on 3.12. From the directory that holds `README.md` and `code/`:

```bash
python3 -m venv .venv
.venv/bin/pip install -r code/requirements.txt      # needs network once; nothing else does
```

## 2. Place the dataset

Put the challenge `dataset/` folder (the one with `deletion_requests.csv` and `evidence/`) beside `code/`:

```text
README.md
code/
dataset/            ← supplied by the challenge, not included in code.zip
state/vision_cache/ ← shipped: the screenshot extracts the engine reads
runs/cache/llm/     ← shipped: the model responses the final run used
```

## 3. Reproduce the submitted output offline (replay: free, no key, no network)

```bash
.venv/bin/python code/main.py run --engine agent --mode replay --agent-scope non_resolved --split targets --out runs/replay
.venv/bin/python code/main.py validate runs/replay/output.csv          # expect: 0 violations … against 518 targets requests
```

Replay reads only the shipped responses: it never constructs a provider client and never reads a key. A missing
response is a `ReplayMiss` (that case falls back to its deterministic row, and the run says so); it is never a
call. `runs/replay/output.csv` is byte-identical to the submitted `output.csv` (`cmp` prints nothing).

## 4. Fresh paid run (live: needs a key, records spend)

```bash
export GEMINI_API_KEY=...        # or put it in an uncommitted .env; it is never printed or logged
.venv/bin/python code/main.py run --engine agent --mode live --agent-scope non_resolved --split targets --out runs/final
```

Every paid call is reserved, sent and settled in `state/usage_ledger.jsonl` against a hard budget ceiling
(`code/config/default.toml`). Responses already in `runs/cache/llm/` are reused at no cost; a run with a new
cache pays for all of them (see `usage_report.md` for the measured full-price figure). A run with no model at all:
`code/main.py run --split targets --out runs/det` (same evidence engine, rule-based intent).

## 5. Evaluate

```bash
.venv/bin/python code/main.py run --engine agent --mode replay --agent-scope non_resolved --split samples --out runs/samples
.venv/bin/python code/evaluation/main.py --pred runs/samples/output.csv     # vs the 32 public sample answers
.venv/bin/python -m pytest code/tests -q                                    # the test suite (offline)
```

Custom cases: `code/evaluation/custom_cases/README.md`.

## 6. Explain one case (no model call)

```bash
.venv/bin/python code/main.py explain case_105 --run runs/replay
```

It prints the verdict and, separately, how well the evidence supports it; the request and intent; the person and
their current and historical identifiers; the chain from the person to each resource; uncertain candidates and
rejected links; each copy's state with both timestamps; the rule behind each action; and the ordered steps, each
with its basis (direct observation, inference, heuristic prediction, proposed remediation, check to run).
Provenance comes from the run's own `provenance.jsonl`, attached only after its sha256 and run fingerprint are
verified together with `output.csv` and `decisions.jsonl`.

## 7. Evidence viewer (offline HTML)

`code/viewer/viewer.html` in code.zip is built from the final run. Open it in any browser (no server, no network).
To rebuild it from a run: `.venv/bin/python code/main.py viewer --run runs/replay --out viewer.html`. It shows the
same representation as `explain`, with search and filters by status and support, and heuristic predictions
labelled. It embeds no path or time, so a rebuild from a replay of the final run is byte-identical; build details
go to `viewer.html.meta.json` beside it.

## What a run writes

A run writes into its own directory, never over the root `output.csv`:
- `output.csv`;
- `decisions.jsonl`: per case, every resource with tier, category, rule, treatment, verdict, copies and proof,
  plus a `trace` (intent and source, identifiers, account deduction, uncertain candidates, exclusions,
  ambiguities, heuristic flag);
- `provenance.jsonl`: every referenced observation (source file, locator, both clocks, bounded excerpt);
- `summary.json`: configuration, counts, fingerprints (code, dataset, extraction, config) and the sha256 of the
  three files above;
- `unresolved.md`, `llm_keys.jsonl` (the responses used), `cases/` (checkpoints reused only with equal inputs).

## How it decides

1. **Ingest** (`ghostaudit/ingest/`). All 94 evidence files become `Observation`s with provenance and two clocks:
   `captured_at` (the artifact's capture) and `observed_at` (the record's own time). Screenshots are read once by
   a vision model, cross-checked by a second, and cached in `state/vision_cache/`.
2. **Identity** (`identity.py`). The subject's current and historical identifiers as of `audit_at`. Matching is
   exact and normalized; an identifier held by two people is an ambiguity, never a guess.
3. **Cutoff** (`temporal.py`). Every read goes through `CaseView`. An observation is readable only if its artifact
   was captured, and its event happened, at or before `audit_at`. One exception, by configuration
   (`[time] historical_snapshots = "snapshot_capture"`): a snapshot envelope that states its own capture time at or
   before `audit_at` may be read even inside an export captured later; it is **never cited** (a citation must be an
   evidence item captured by `audit_at`). Later assertions with old timestamps never qualify.
4. **Ownership** (`ownership.py`). A resource is linked when an admissible unit (a record, one table row, a
   single-subject page) names it with a subject identifier. The deletion workflow's account rows are assigned
   one-to-one by deduction; only the deduction that holds up in a masked backtest (`only_feasible_row`) is
   asserted, as a labelled workflow inference. Weaker deductions stay visible as uncertain candidates with no
   step. A nearest-in-time pick is used only to fill a row that would otherwise be empty, flagged as a heuristic
   prediction.
5. **Policy** (`policy.py`). State per physical copy (primary, replicas, documents) from the latest observation by
   event time; a clean primary never clears a dirty replica; disagreeing observations at one instant are a
   conflict; activity rows and reported statuses are claims and never set a state.
6. **Plan** (`planner.py`). Each verdict becomes contract steps (findings cite their proof; remediation and later
   verification use `""`), in canonical order, then validated. Each row gets a support level (`resolved`, `weak`,
   `unresolved`) that never claims more than the evidence; the CSV cannot carry it, so `explain`, the viewer and
   `unresolved.md` do.
7. **Agent** (`agent.py`, `tools.py`, `prompts/investigator.md`). A bounded Gemini investigator reviews the weak
   and unresolved proposals with 9 read-only, cutoff-bound tools. It can cite only observations a tool returned,
   and a decision (account, addition, exclusion) is accepted only with a cited chain to the subject. The engine,
   not the model, recompiles the steps.
8. **Gateway** (`llm/gateway.py`). Reserve → send → settle by error class, against a hard budget; responses cached
   by request content; replay never builds a client.

## Replay artifacts and release checks

`state/vision_cache/` and `runs/cache/llm/` each ship a `MANIFEST.json` of sha256s, verified by the runtime on every
read (`ghostaudit/artifacts.py`). `code/release/checks.py` defines what code.zip may hold (no dataset copy outside
a pinned fixture allowlist, no nested archive, no environment or credential file) and when a clean-unpack replay
is accepted (validator exit 0 with "0 violations", byte-identical output and viewer, clean scan, no network, no
provider client).
