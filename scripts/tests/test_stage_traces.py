"""S7 C7.7: the staged agent trace is complete, redacted and still valid JSONL; the originals are untouched.

Fake project, stage and repo folders (module globals patched), so no real trace or .env is read.
"""
import importlib.util
import json
import zipfile
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("stage_traces", SCRIPTS / "stage_traces.py")
st = importlib.util.module_from_spec(spec)
spec.loader.exec_module(st)

KEY = "AIza" + "Q" * 35
ENV_SECRET = 'pa"ss\\word-1234567'                       # a quote and a backslash: JSON-escaped inside the JSONL


@pytest.fixture
def world(tmp_path, monkeypatch):
    repo, proj, home = tmp_path / "repo", tmp_path / "proj", tmp_path / "home"
    for d in (repo, proj, home):
        d.mkdir()
    (repo / ".env").write_text(f"GEMINI_API_KEY={KEY}\nOTHER_SECRET='{ENV_SECRET}'\n")
    (repo / "CHAT_GPT_TRANSCRIPT_PRE_CLAUDE.md").write_text("# transcription\n")
    lines = [{"type": "user", "text": f"key is {KEY}"},
             {"type": "tool", "text": "env says " + ENV_SECRET},
             {"type": "assistant", "text": "line one line two"}]                 # U+2028 kept raw
    (proj / "s1.jsonl").write_text("".join(json.dumps(l, ensure_ascii=False) + "\n" for l in lines), encoding="utf-8")
    (proj / "s1" / "subagents").mkdir(parents=True)
    (proj / "s1" / "subagents" / "a.jsonl").write_text(json.dumps({"t": "token sk-" + "B" * 24}) + "\n")
    exports = tmp_path / "exports"
    exports.mkdir()
    (exports / "2026-10-25-final.txt").write_text(f"> pasted {KEY}\nhello\n")
    stage = home / "agent-trace"
    monkeypatch.setattr(st, "ROOT", repo)
    monkeypatch.setattr(st, "PROJECT", proj)
    monkeypatch.setattr(st, "STAGE", stage)
    monkeypatch.setattr(st, "EXPORTS", tmp_path / "default-exports")              # never the real ~/ghost-exports
    return repo, proj, stage, exports


def _all_bytes(stage):
    return b"".join(p.read_bytes() for p in stage.rglob("*") if p.is_file())


def test_staged_copies_are_redacted_valid_and_the_originals_untouched(world):
    repo, proj, stage, exports = world
    before = {p: p.read_bytes() for p in list(proj.rglob("*")) + list(exports.rglob("*")) if p.is_file()}
    assert st.main(["--zip", "--exports", str(exports)]) == 0
    staged = _all_bytes(stage)
    assert KEY.encode() not in staged and b"sk-" + b"B" * 24 not in staged
    assert json.dumps(ENV_SECRET)[1:-1].encode() not in staged and ENV_SECRET.encode() not in staged
    for p in stage.rglob("*.jsonl"):
        rows = [json.loads(l) for l in p.read_text(encoding="utf-8").split("\n") if l.strip()]
        assert rows
    s1 = (stage / "claude-code" / "s1.jsonl").read_text(encoding="utf-8")
    assert "line one line two" in s1 and s1.count("[REDACTED]") == 2
    assert (stage / "claude-code" / "s1" / "subagents" / "a.jsonl").exists()
    assert "[REDACTED]" in (stage / "claude-code" / "exports" / "2026-10-25-final.txt").read_text()
    assert (stage / "chatgpt" / "CHAT_GPT_TRANSCRIPT_PRE_CLAUDE.md").exists()
    assert {p: p.read_bytes() for p in before} == before                       # originals unchanged
    with zipfile.ZipFile(stage.parent / "agent-trace.zip") as z:
        names = set(z.namelist())
        assert "agent-trace/README.md" in names and "agent-trace/claude-code/exports/2026-10-25-final.txt" in names
        assert all(KEY.encode() not in z.read(n) for n in names)


def test_a_stale_file_from_an_earlier_staging_is_not_shipped(world):
    repo, proj, stage, exports = world
    (stage / "claude-code").mkdir(parents=True)
    (stage / "claude-code" / "old-session.jsonl").write_text("{}\n")
    assert st.main(["--zip", "--exports", str(exports)]) == 0
    with zipfile.ZipFile(stage.parent / "agent-trace.zip") as z:
        assert not any("old-session" in n for n in z.namelist())


def test_a_required_export_that_is_missing_fails_loudly(world, tmp_path):
    repo, proj, stage, exports = world
    empty = tmp_path / "none"
    empty.mkdir()
    assert st.main(["--zip", "--exports", str(empty), "--require-export"]) == 1
    assert not (stage.parent / "agent-trace.zip").exists()


def test_no_session_is_a_failure_not_an_empty_trace(world, tmp_path, monkeypatch):
    """An export transcript alone is not a trace (found by the finalize rehearsal: the guard counted any file staged
    under claude-code/, so a trace with an export and no session JSONL passed)."""
    repo, proj, stage, exports = world
    monkeypatch.setattr(st, "PROJECT", tmp_path / "empty-proj")
    assert st.main(["--dry-run", "--exports", str(exports)]) == 1               # exports holds a transcript
    assert st.main(["--zip", "--exports", str(exports)]) == 1
    assert not (stage.parent / "agent-trace.zip").exists()
