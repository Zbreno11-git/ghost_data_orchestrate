# Mac acceptance runbook (Intel or Apple silicon)

**Written for:** Breno, on his Mac, copy-pasting into Terminal. Each step says what you should see. If a step shows
something else, stop and send me that step's output. The VPS has already passed the same checks; this run proves
the package works on a different machine.

**You need:**
- the three release files from the VPS: `code.zip`, `output.csv`, `SHA256SUMS`;
- the challenge `dataset/` folder (from the official repository; it is not inside code.zip);
- Python 3.11 or newer (`python3 --version`);
- about 5 minutes. Internet is needed only for step 3.

## 0. A clean folder

```bash
mkdir -p ~/ghost-accept && cd ~/ghost-accept
# copy code.zip, output.csv and SHA256SUMS here, e.g. from the VPS:
#   scp root@<vps>:/root/hackthon_1/{code.zip,output.csv} root@<vps>:/root/hackthon_1/docs/release/SHA256SUMS .
ls
```
Expect: `SHA256SUMS  code.zip  output.csv`

## 1. The files are the ones the VPS released

```bash
shasum -a 256 -c SHA256SUMS 2>/dev/null | grep -E '^(code.zip|output.csv):'
```
Expect `code.zip: OK` and `output.csv: OK`. The file also lists log.txt and agent-trace.zip, which you don't need
here; the `grep` hides their "missing" lines. Any `FAILED` line means the copy is not the released file: copy it
again before going on.

## 2. Unpack into an empty folder and add the dataset beside `code/`

```bash
mkdir unpacked && cd unpacked && unzip -q ../code.zip
cp -R /path/to/hackerrank-orchestrate-october26/dataset ./dataset     # adjust the path to your clone
ls
```
Expect: `README.md  code  dataset  runs  state`

## 3. A fresh environment (the only step that needs internet)

```bash
python3 -m venv .venv
.venv/bin/pip install -q -r code/requirements.txt && echo INSTALLED
```
Expect: `INSTALLED`.
- **If the install fails** with SSL or certificate errors (python.org installers): run
  `/Applications/Python\ 3.*/Install\ Certificates.command` once, then retry.
- **If a wheel fails to build:** `.venv/bin/pip install --upgrade pip`, then retry.

## 4. Replay offline: turn Wi-Fi off now

macOS has no per-command network sandbox like Linux `unshare`, so the offline proof is: **Wi-Fi off** (and any
cable unplugged) for steps 4–6.

```bash
unset GEMINI_API_KEY
.venv/bin/python code/main.py run --engine agent --mode replay --agent-scope non_resolved --split targets --out runs/replay
```
Expect the last lines to include `518 rows → runs/replay/output.csv` and an `agent {...}` summary with
`'cost_usd_x1e6': 0`.
- A line mentioning `ReplayMiss`, or a `fallback` count above 0, means a shipped response is missing: send me
  the output.
- `No such file or directory: 'dataset/...'` means step 2's dataset copy is not beside `code/`.

## 5. The replay equals the released answers, and validates

```bash
cmp runs/replay/output.csv ../output.csv && echo IDENTICAL
.venv/bin/python code/main.py validate runs/replay/output.csv
```
Expect: `IDENTICAL`, then `0 violations in runs/replay/output.csv against 518 targets requests`.

## 6. Tests and the evidence viewer

```bash
.venv/bin/python -m pytest code/tests -q 2>&1 | tail -1
.venv/bin/python code/main.py viewer --run runs/replay --out viewer-rebuilt.html
cmp viewer-rebuilt.html code/viewer/viewer.html && echo VIEWER-IDENTICAL
open code/viewer/viewer.html
```
Expect:
- a line `N passed` with no `failed` (N is in `docs/release/RELEASE_RECORD.md`);
- `VIEWER-IDENTICAL`;
- the viewer opens in your browser.

Turn Wi-Fi back on.

## 7. Look at five cases in the viewer (the walkthrough)

Follow `docs/release/WALKTHROUGH.md` (in the repository) with the viewer open. For each case, check that you can
see:
- who the person is;
- which evidence ties each record to them;
- what state each copy was in at the audit cutoff;
- which rule decided the treatment;
- how certain the answer is.

## 8. Report back

Send me, as text:
- the output of steps 1, 4 (last 4 lines), 5 and 6;
- your macOS version and chip (Apple menu → About This Mac);
- your browser and version;
- anything in the viewer that was unclear.

I record these in the release record. The Mac check stays **pending** until your results arrive. If any step
fails, I fix it, rebuild, and you run this again on the new files.
