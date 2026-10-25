# Exploratory measurements (S0, 2026-10-24)

The read-only scripts behind the numbers in `docs/plans/MASTER_PLAN.md` "Measured at opening". They are not part of the
engine and never run on the prediction path. Each one takes the dataset directory as its argument:

```bash
python3 -I scripts/analysis/samples.py dataset     # status/operation/system/citation distributions
python3 -I scripts/analysis/show.py dataset case_01,case_25   # pretty-print sample cases
python3 -I scripts/analysis/linkaudit.py dataset   # 82/111 sample resources with an explicit subject link
python3 -I scripts/analysis/window.py dataset      # 3-15 candidate accounts per request window
```

`linkaudit.py` and `window.py` read `sample_output.csv` **on purpose**: they measure how much ownership is
derivable. They are evaluation-side tools only.

**S6 (2026-10-25), evaluator side, also read `sample_output.csv` on purpose:**

```bash
.venv/bin/python scripts/analysis/extraction_audit.py --run runs/<samples run> --out <md>     # C6.1
```

`extraction_audit.py` compares every decoded line that names a mismatch resource (raw text, two PDF decoders,
vision extracts; `code/evaluation/corpus.py`) with the observations built from that source.

**S7 (2026-10-25), evaluator side:**

```bash
.venv/bin/python scripts/analysis/masked_backtest.py --out <md> --json <json>   # C7.1 masked-identity backtest
```

`masked_backtest.py` hides explicitly proven accounts by cohort and re-runs the existing workflow-account
mechanisms; the truth mapping lives only in the script. It does not read `sample_output.csv`.
