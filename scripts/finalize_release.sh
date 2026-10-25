#!/usr/bin/env bash
# Final release, amendment 6 steps 3-5 (S7 C7.7): stage and zip the traces, assemble and verify the four upload
# files, write the checksums and the release record, commit and push them. Nothing is uploaded: Breno does that.
#
# Run it only AFTER: the Mac acceptance is recorded (docs/release/mac_acceptance.md), the closing turn is in
# log.txt, the session's /export transcript is saved, and Claude Code is closed (the JSONL is then complete).
#
#   bash scripts/finalize_release.sh               # requires an /export transcript (~/ghost-exports/ or the repo root)
#   bash scripts/finalize_release.sh --no-export   # when /export is not available: the session JSONL is the trace
#
# Every check stops the script with "STOP: ..." and a non-zero exit; nothing is committed after a failed check.
set -euo pipefail
cd "$(dirname "$0")/.."

PY=.venv/bin/python
RUN=runs/s7/final-r2
SAMPLES=runs/s7/final-r2-samples
REPORT=runs/s7/package_report.json
MAC_SET="$HOME/ghost-mac"
REL="$HOME/ghost-release"
EXPORT_FLAG=--require-export
[ "${1:-}" = "--no-export" ] && EXPORT_FLAG=""

step() { printf '\n== %s\n' "$*"; }
stop() { printf 'STOP: %s\n' "$*" >&2; exit 1; }
sha() { sha256sum "$1" | cut -d' ' -f1; }

step "0. preconditions"
[ -z "$(git status --porcelain)" ] || stop "uncommitted changes: commit them first (git status)"
git fetch -q origin
[ "$(git rev-parse HEAD)" = "$(git rev-parse origin/main)" ] || stop "HEAD is not origin/main: push or pull first"
[ -s docs/release/mac_acceptance.md ] || stop "docs/release/mac_acceptance.md missing: the Mac acceptance is not recorded"
if pgrep -x claude >/dev/null; then echo "warning: a 'claude' process is running; its session file may still grow"; fi
$PY -m pytest code/tests scripts/tests -q || stop "tests failed"
cmp -s output.csv "$RUN/output.csv" || stop "root output.csv is not $RUN/output.csv"
$PY code/main.py validate output.csv | tail -1
$PY code/main.py validate output.csv >/dev/null || stop "output.csv does not validate"
accepted=$($PY -c "import json; c=json.load(open('$REPORT'))['check']; print(c['sha256']['code.zip'] if c['not_accepted_because']==[] else 'REFUSED')")
[ "$(sha code.zip)" = "$accepted" ] || stop "code.zip is not the archive the package check accepted ($REPORT)"
(cd "$MAC_SET" && sha256sum -c --quiet SHA256SUMS) || stop "$MAC_SET does not match its SHA256SUMS"
[ "$(sha code.zip)" = "$(sha "$MAC_SET/code.zip")" ] || stop "code.zip differs from the one the Mac accepted"
[ "$(sha output.csv)" = "$(sha "$MAC_SET/output.csv")" ] || stop "output.csv differs from the one the Mac accepted"
$PY scripts/analysis/log_audit.py || stop "log.txt audit failed (an unlogged message, or a malformed entry)"

step "1. stage, redact and zip the traces"
$PY -I scripts/stage_traces.py --zip $EXPORT_FLAG || stop "trace staging failed"

step "2. assemble the release folder ($REL)"
rm -rf "$REL"
mkdir -p "$REL"
cp code.zip output.csv log.txt "$REL/"
cp "$HOME/agent-trace.zip" "$REL/"

step "3. verify the four files"
unzip -tq "$REL/code.zip" || stop "code.zip is not a valid archive"
unzip -tq "$REL/agent-trace.zip" || stop "agent-trace.zip is not a valid archive"
for z in code.zip agent-trace.zip; do
  if unzip -Z1 "$REL/$z" | grep -Ei '\.(zip|tar|gz|tgz|7z|rar|bz2|xz)$'; then stop "$z holds a nested archive"; fi
done
$PY code/main.py validate "$REL/output.csv" >/dev/null || stop "release output.csv does not validate"
cmp -s "$REL/log.txt" log.txt || stop "release log.txt differs from the repository's"

step "4. checksums and release record"
$PY scripts/release_record.py --run "$RUN" --samples "$SAMPLES" --package-report "$REPORT" \
  --release-dir "$REL" --mac docs/release/mac_acceptance.md || stop "release record refused"
(cd "$REL" && sha256sum -c SHA256SUMS) || stop "checksums do not verify"
cmp -s "$REL/SHA256SUMS" docs/release/SHA256SUMS || stop "the two SHA256SUMS copies differ"

step "5. commit and push the record (the four files themselves are never committed)"
git add docs/release/SHA256SUMS docs/release/RELEASE_RECORD.md
git commit -q -m "S7 C7.7: release record and checksums (freeze)" \
  -m "Written by scripts/finalize_release.sh from the files in ~/ghost-release." \
  -m "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
git push -q origin main
echo "pushed $(git rev-parse --short HEAD)"

step "FROZEN. Upload exactly these files from $REL:"
cat "$REL/SHA256SUMS"
cat <<'EOF'

  code.zip         -> code.zip slot
  output.csv       -> output.csv slot
  log.txt          -> chat_transcript slot
  agent-trace.zip  -> agent trace (ZIP)
  then the AI interview.

  Submission page: https://www.hackerrank.com/contests/hackerrank-orchestrate-october26/challenges/ghost-data-still-exists
EOF
