# Ghost Data Still Exists — deletion-audit agent

HackerRank Orchestrate, October 2026. For each request in `dataset/deletion_requests.csv` this program writes one
row of `output.csv` (`case_id,deletion_status,steps_json`). It decides whether the person asked for deletion,
reconstructs every relevant copy of their data as of `audit_at` from participant evidence only, applies
`deletion_rules.csv`, and emits the ordered findings, remediation and verification steps with the evidence they
rest on. A deterministic evidence engine writes every step. Gemini classifies request intent (cross-checked by a
rule), read the screenshots once (cached), and, as a bounded tool-using agent, reviews only the cases the engine
cannot settle; its proposals are accepted only with a cited chain to the person.

## Run it

Python 3.11 or newer. From this directory, with the challenge `dataset/` folder placed beside `code/`:

```bash
python3 -m venv .venv
.venv/bin/pip install -r code/requirements.txt      # needs network once; nothing else does
.venv/bin/python code/main.py run --engine agent --mode replay --agent-scope non_resolved --split targets --out runs/replay
.venv/bin/python code/main.py validate runs/replay/output.csv          # expect: 0 violations … against 518 targets requests
```

The replay reproduces the submitted `output.csv` byte for byte from the model responses shipped in
`runs/cache/llm/`, offline, with no key and at no cost. A fresh paid run, evaluation against the public samples,
per-case explanations and the evidence viewer are in [`code/README.md`](code/README.md).

## Where things are

| Path | What |
|---|---|
| [`code/README.md`](code/README.md) | full instructions and how the engine decides |
| [`code/evaluation/evaluation_report.md`](code/evaluation/evaluation_report.md) | accuracy on the public samples, custom cases, failures and fixes |
| [`code/evaluation/usage_report.md`](code/evaluation/usage_report.md) | models, calls, tokens and cost of the final full run |
| `code/viewer/viewer.html` (in code.zip) | offline evidence viewer for every case, built from the final run |
| `code/main.py` | the command-line entry point |

In the repository but not in code.zip: `docs/` (plans, decisions, error catalog, diagnostics, release notes),
`log.txt` (the coding-agent transcript), and the challenge's own files (`AGENTS.md`, `problem_statement.md`, the
starter README in [`docs/STARTER_README.md`](docs/STARTER_README.md)).
