"""Audit log.txt against the original Claude Code session records (S5 C5.12). Prints positions, never content.

Human messages are taken from the session JSONL: `user` events whose content is the person's text (not tool
results, skill bodies, compact summaries or command caveats), plus `queued_command` attachments from a human
(messages sent while the agent was working). Each must appear literally (whitespace-normalized, wrapper tags
ignored) in the "User Prompt" field of some log entry. Every entry must carry the AGENTS.md §5 sections and
exactly one non-empty tool= and model= line.

Usage: python3 -I scripts/analysis/log_audit.py [--log log.txt] [--sessions ~/.claude/projects/-root-hackthon-1]
Exit 1 when a human message is unlogged or an entry is malformed.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SECTIONS = ("User Prompt (verbatim, secrets redacted):", "Agent Response Summary:", "Actions:", "Context:")
CORRECTION = ("Recovered Original (verbatim, secrets redacted", "Correction Summary:", "Provenance:", "Context:")
META = ("This session is being continued", "<local-command", "<command-name>", "<command-message>",
        "Base directory for this skill", "<system-reminder>", "[Request interrupted", "<task-notification>")


def norm(text: str) -> str:
    text = re.sub(r"</?pasted_content[^>]*>", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def human_messages(session: Path) -> list[dict]:
    out = []
    # JSONL records end at "\n" only: str.splitlines() also splits at U+2028/U+2029 inside JSON strings (a session
    # that quoted one broke the audit, S7 2026-10-25).
    for n, line in enumerate(session.read_text(encoding="utf-8").split("\n"), 1):
        if not line.strip():
            continue
        e = json.loads(line)
        text = None
        if e.get("type") == "user" and not e.get("isMeta") and not e.get("isCompactSummary"):
            c = (e.get("message") or {}).get("content")
            if isinstance(c, str):
                text = c
            elif isinstance(c, list) and c and all(p.get("type") == "text" for p in c):
                text = "".join(p["text"] for p in c)
        elif e.get("type") == "attachment":
            a = e.get("attachment") or {}
            if a.get("type") == "queued_command" and (a.get("origin") or {}).get("kind") == "human":
                text = "".join(p.get("text", "") for p in a.get("prompt") or [] if isinstance(p, dict))
        if text and text.strip() and not text.lstrip().startswith(META):
            out.append({"line": n, "ts": e.get("timestamp"), "uuid": e.get("uuid"), "text": text})
    return out


def entries(log: Path) -> list[dict]:
    lines = log.read_text(encoding="utf-8").splitlines()
    starts = [i for i, l in enumerate(lines) if l.startswith("## [")]
    out = []
    for k, i in enumerate(starts):
        body = lines[i:starts[k + 1] if k + 1 < len(starts) else len(lines)]
        text = "\n".join(body)
        prompt = ""
        need = CORRECTION if "] CORRECTION to " in lines[i] or "] DISCLOSURE" in lines[i] else SECTIONS
        if need[0] in text and need[1] in text:
            prompt = text.split(need[0], 1)[1].split(need[1], 1)[0]
        prompt_lines = {norm(l) for l in prompt.splitlines() if l.strip()}
        out.append({"line": i + 1, "header": lines[i][:90], "start": "SESSION START" in lines[i],
                    "prompt_lines": prompt_lines,
                    "missing": [s for s in need if s not in text] if "SESSION START" not in lines[i] else [],
                    "tool": [l for l in body if re.fullmatch(r"tool=\S.*", l)],
                    "model": [l for l in body if re.fullmatch(r"model=\S.*", l)], "prompt": norm(prompt)})
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--log", type=Path, default=ROOT / "log.txt")
    ap.add_argument("--sessions", type=Path, default=Path.home() / ".claude" / "projects" / "-root-hackthon-1")
    a = ap.parse_args(argv)
    es = entries(a.log)
    bad = [e for e in es if e["missing"] or len(e["tool"]) != 1 or len(e["model"]) != 1]
    print(f"log entries {len(es)} ({sum(e['start'] for e in es)} SESSION START); malformed {len(bad)}")
    for e in bad:
        print(f"  log.txt:{e['line']} missing={e['missing']} tool={len(e['tool'])} model={len(e['model'])}")
    tools = sorted({t for e in es for t in e["tool"]})
    models = sorted({m for e in es for m in e["model"]})
    print(f"tool values {tools}; model values {models}")
    unlogged = 0
    for s in sorted(a.sessions.glob("*.jsonl")):
        msgs = human_messages(s)
        def logged(m):
            t = norm(m["text"])
            if len(t) < 40:      # a short message must be a whole line of a prompt field, not a substring
                return any(t in e["prompt_lines"] for e in es)
            return any(t[:400] in e["prompt"] for e in es)
        miss = [m for m in msgs if not logged(m)]
        unlogged += len(miss)
        print(f"{s.name}: human messages {len(msgs)}, logged literally {len(msgs) - len(miss)}, not {len(miss)}")
        for m in miss:
            print(f"  not logged literally: JSONL line {m['line']} {m['ts']} uuid {m['uuid']} ({len(m['text'])} chars)")
        subs = sorted((a.sessions / s.stem / "subagents").glob("*.jsonl")) if (a.sessions / s.stem).exists() else []
        print(f"  subagent transcripts: {len(subs)}")
    return 1 if unlogged or bad else 0


if __name__ == "__main__":
    sys.exit(main())
