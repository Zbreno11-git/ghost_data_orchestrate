# Release record

Written 2026-10-25 05:00 UTC by `scripts/release_record.py`; every value is read from a file.

## Source and configuration

- Source revision (git HEAD when written): `b455ed737cc8302faeddf62d0344f37db6f931b5`
- Final run: `runs/s7/final-r2`: engine agent, model gemini-3.1-flash-lite, agent scope non_resolved, ownership strict, asserted mechanisms ['corroborated_run', 'nearest_anchor', 'only_feasible_row'], time policy snapshot_capture
- Fingerprints: code `2b2749e54e5839f0…`, dataset `37f5c27f8f095d04…`, extraction `2bf0cccbee1901c3…`, config `9dc090e0aef934c7…`, run `b0f0247857e1ed18…`
- Run artifacts (sha256): output.csv `0e04ffe214bb9450…`, decisions.jsonl `7cb6d970cb9a586a…`, provenance.jsonl `ea3e9ab76d27c89b…`
- Replay manifests (sha256): state/vision_cache/MANIFEST.json `35dbcdcc00ac12ff…`, runs/cache/llm/MANIFEST.json `69be9d88f5c84dd8…`

## Results

- Targets: 518 rows; status {"INCOMPLETE": 363, "COMPLETE": 145, "NOT_APPLICABLE": 10}; support {"unresolved": 339, "resolved": 167, "weak": 12}
- Public samples (full denominators): status 32/32, whole-case 14/32, step P 167/168, R 167/193, F1 0.9252, cited recall 62/75, sequence 14/32. Not a hidden-target estimate.

## VPS clean-unpack check

- Inventory problems: none; entries 1927, 2577392 bytes
- Replay: exit 0, network none (unshare -rn), provider client blocked True, output identical True, viewer identical True, validate: 0 violations in /tmp/tmpqclcn8x3/replay/output.csv against 518 targets requests
- Not accepted because: nothing (accepted)

## Mac acceptance

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

## Upload files (release directory)

| file | bytes | sha256 |
|---|---|---|
| code.zip | 2577392 | `0c4dfef137985cf8f712deb1680b3546b94b2a505ca88a6177d99a09790318b2` |
| output.csv | 553327 | `0e04ffe214bb9450b0aed886f4b7ba8c73af62b7ef5552ff6ad55c6e4b8ef06d` |
| log.txt | 137891 | `9cd207dd76e729345ac2736860578805bda05be5467be7e34c98215aba1126f6` |
| agent-trace.zip | 11526235 | `dda7711ee0726712e2b9bad622f707e21bacf6ff0f0c5abff9c736f7daf785fa` |

`SHA256SUMS` sits beside them and in `docs/release/`, outside every archive it hashes. After the freeze, any change to one of these files reopens the affected checks and produces a new record.
