**ACCEPTED on a second machine, 2026-10-25** (results sent by Breno at 2026-10-25T04:50:57Z, session JSONL
3f2c5c59…:12554). The outputs below are copied literally from his terminal; the usernames, hostnames and home
paths in the prompts are left out because this file is published.

- **Machine:** macOS 13.7.8 (build 22H730), Intel `x86_64`, Python 3.13.5 (run from a conda `(base)` shell), git 2.39.2.
  The VPS ran Linux with Python 3.12, so this is a different OS, CPU architecture and Python version.
- **Inputs:**
  - `code.zip` and `output.csv` copied from the VPS `/root/ghost-mac/`;
  - the challenge `dataset/` taken from a fresh clone of this repository at `a614156` (the dataset is tracked
    there), copied beside `code/`;
  - a fresh venv built from `code/requirements.txt`. `cryptography` was built from source; the install
    succeeded.

| Runbook step | Output (literal) | Expected | |
|---|---|---|---|
| 1 checksums | `code.zip: OK` / `output.csv: OK` | 2× OK | ✅ |
| 4 replay (`GEMINI_API_KEY` unset) | `518 rows → runs/replay/output.csv` | same | ✅ |
| | `status {'INCOMPLETE': 363, 'COMPLETE': 145, 'NOT_APPLICABLE': 10}  support {'unresolved': 339, 'resolved': 167, 'weak': 12}` | same | ✅ |
| | `workflow assignment {'explicit_account': 167, 'forced_matching': 2, 'only_feasible_row': 16, 'only_feasible_request': 1}  ambiguous 332` | same | ✅ |
| | `agent {'submitted': 352, 'model_calls': 1749, 'cache_hits': 1749, 'cost_usd_x1e6': 0, 'skipped_resolved': 166}` | same; no `'fallback'` | ✅ |
| 5 output | `IDENTICAL` | `IDENTICAL` | ✅ |
| 5 validate | `0 violations in runs/replay/output.csv against 518 targets requests` | same | ✅ |
| 6 tests | `310 passed in 46.41s` | `310 passed` | ✅ |
| 6 viewer | `wrote viewer-rebuilt.html (4333085 bytes, sha256 def973f60f560953…)`; `VIEWER-IDENTICAL` | `VIEWER-IDENTICAL` | ✅ |
| 6 open | `open code/viewer/viewer.html` ran | the viewer opens | ran; observations not reported |

**Not reported (stated, not assumed):**
- **Network state during steps 4–6.** Wi-Fi off was the runbook's macOS isolation. Independently of that, every
  model call was served from the shipped cache (1749/1749 hits, cost 0), and the VPS check ran the same replay
  with no network at all (`unshare -rn`) and with provider-client construction blocked.
- **Browser, its version, and the step-7 walkthrough observations.** No viewer problem was reported.
