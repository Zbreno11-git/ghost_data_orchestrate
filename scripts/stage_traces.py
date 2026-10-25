"""Stage the agent trace for submission, outside the repository and outside code.zip (S5 C5.13, MASTER_PLAN C7.3).

Follows agent_trace_instructions.md:
- copies this challenge's Claude Code sessions with their folder structure (session JSONL plus its
  `<session>/subagents/` JSONL and meta files) into ~/agent-trace/claude-code/;
- copies the readable `/export` transcripts from an exports folder (default ~/ghost-exports/; Claude Code's
  default `/export` file name in the repository root, `YYYY-MM-DD-*.txt`, is swept there first) into
  ~/agent-trace/claude-code/exports/;
- copies the pre-Claude ChatGPT transcript into ~/agent-trace/chatgpt/, labelled as the text transcription it
  is, not a native trace.

Originals are never modified: redaction (API keys, tokens, private keys, .env values) is applied to the staged
copies only, as string substitutions that keep JSONL lines valid JSON (each line is re-parsed). Memory notes,
settings and credentials are excluded.

The stage folder is generated: it is emptied before staging, so nothing from an earlier staging is shipped.

Usage: python3 -I scripts/stage_traces.py [--dry-run] [--zip] [--exports DIR] [--require-export]
Exit 1 if no session is found, a required export is missing, a staged file still matches a secret pattern, or a
JSONL line stops parsing.
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
# Claude Code names a project folder by its path with every non-alphanumeric character as "-".
PROJECT = Path.home() / ".claude" / "projects" / re.sub(r"[^A-Za-z0-9]", "-", str(ROOT))
STAGE = Path.home() / "agent-trace"
EXPORTS = Path.home() / "ghost-exports"
EXPORT_NAME = re.compile(r"^\d{4}-\d{2}-\d{2}-.*\.txt$")      # Claude Code's default /export file name
PATTERNS = [re.compile(p) for p in (r"AIza[0-9A-Za-z_\-]{30,}", r"gh[opsu]_[0-9A-Za-z]{30,}", r"sk-[A-Za-z0-9]{20,}",
                                    r"-----BEGIN [A-Z ]*PRIVATE KEY-----")]


def env_values() -> list[str]:
    """Values from the uncommitted .env (never printed), so a pasted secret is caught even without a known prefix."""
    env = ROOT / ".env"
    if not env.exists():
        return []
    vals = []
    for line in env.read_text().splitlines():
        if "=" in line and not line.lstrip().startswith("#"):
            v = line.split("=", 1)[1].strip().strip("\"'")
            if len(v) >= 12:
                vals.append(v)
                esc = json.dumps(v)[1:-1]                  # how it appears inside a JSON string
                if esc != v:
                    vals.append(esc)
    return vals


def sweep_exports(exports: Path) -> list[Path]:
    """Moves default-named /export files out of the repository root (public: never committed) into `exports`."""
    moved = []
    for f in sorted(ROOT.glob("*.txt")):
        if EXPORT_NAME.match(f.name):
            exports.mkdir(parents=True, exist_ok=True)
            moved.append(Path(shutil.move(str(f), str(exports / f.name))))
    return moved


def sources(exports: Path | None = None) -> list[tuple[Path, Path]]:
    """(source, staged path) pairs; only this project's session files and their subagent folders, the exports."""
    out = []
    for s in sorted(PROJECT.glob("*.jsonl")):
        out.append((s, STAGE / "claude-code" / s.name))
        sub = PROJECT / s.stem
        if sub.is_dir():
            for f in sorted(p for p in sub.rglob("*") if p.is_file()):
                out.append((f, STAGE / "claude-code" / s.stem / f.relative_to(sub)))
    if exports is not None and exports.is_dir():
        out += [(f, STAGE / "claude-code" / "exports" / f.name) for f in sorted(exports.iterdir()) if f.is_file()]
    gpt = ROOT / "CHAT_GPT_TRANSCRIPT_PRE_CLAUDE.md"
    if gpt.exists():
        out.append((gpt, STAGE / "chatgpt" / gpt.name))
    return out


def redact(text: str, secrets: list[str]) -> tuple[str, int]:
    n = 0
    for v in secrets:
        n += text.count(v)
        text = text.replace(v, "[REDACTED]")
    for p in PATTERNS:
        text, k = p.subn("[REDACTED]", text)
        n += k
    return text, n


README = """# agent-trace — Ghost Data Still Exists (HackerRank Orchestrate, October 2026)

- `claude-code/`: the original Claude Code session JSONL for this challenge, with its `subagents/` folder
  (structure preserved; secrets redacted in these copies only). Readable `/export` transcripts are saved here too.
- `chatgpt/CHAT_GPT_TRANSCRIPT_PRE_CLAUDE.md`: a **text transcription** of the planning conversation held in
  ChatGPT before Claude Code, as its own header says; it is not a native platform export or a raw agent trace.
  Later ChatGPT reviews are added here only if exported from the hosted product, and labelled the same way.
- The challenge's `chat_transcript` slot takes the repository's `log.txt`, which is not part of this archive.
"""


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--zip", action="store_true")
    ap.add_argument("--exports", type=Path, default=EXPORTS, help="folder holding the /export transcripts")
    ap.add_argument("--require-export", action="store_true", help="fail when no /export transcript is found")
    a = ap.parse_args(argv)
    secrets = env_values()
    if not a.dry_run:
        for f in sweep_exports(a.exports):
            print(f"moved {f.name} from the repository root to {a.exports}")
    pairs = sources(a.exports)
    n_exports = sum("exports" in dst.parts for _, dst in pairs)
    if a.require_export and not n_exports:
        print(f"no /export transcript in {a.exports}: run /export in the session first (or drop --require-export)")
        return 1
    if not any(dst.parts[-2:-1] == ("claude-code",) or "claude-code" in dst.parts for _, dst in pairs):
        print(f"no Claude Code session found under {PROJECT}: nothing staged")   # an empty trace is a failure
        return 1
    if not a.dry_run and STAGE.exists():
        shutil.rmtree(STAGE)                               # generated: nothing from an earlier staging survives
    hits_total, bad = 0, []
    for src, dst in pairs:
        text = src.read_text(encoding="utf-8", errors="replace")
        red, hits = redact(text, secrets)
        hits_total += hits
        if src.suffix == ".jsonl":
            for i, line in enumerate(red.split("\n"), 1):     # not splitlines(): U+2028 can sit inside a string
                if line.strip():
                    try:
                        json.loads(line)
                    except json.JSONDecodeError:
                        bad.append(f"{dst.name}:{i}")
                        break
        print(f"{'would stage' if a.dry_run else 'staged'} {src} → {dst} ({src.stat().st_size} B, {hits} redactions)")
        if not a.dry_run:
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.write_text(red, encoding="utf-8")
    if not a.dry_run:
        (STAGE / "README.md").write_text(README)
        left = [p for p in STAGE.rglob("*") if p.is_file() and any(
            pat.search(p.read_text(errors="replace")) for pat in PATTERNS)]
        bad += [f"secret pattern still in {p}" for p in left]
    print(f"{len(pairs)} files ({n_exports} /export transcripts); {hits_total} redactions in staged copies; "
          f"problems: {bad or 'none'}")
    if a.zip and not a.dry_run and not bad:
        out = STAGE.parent / "agent-trace.zip"
        with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
            for p in sorted(STAGE.rglob("*")):
                if p.is_file():
                    z.write(p, Path("agent-trace") / p.relative_to(STAGE))
        with zipfile.ZipFile(out) as z:
            names = z.namelist()
        print(f"wrote {out}: {len(names)} entries; first {names[:3]}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
