"""C4.0/C4.1/C4.5 (offline part): settlement by error class with the SDK's real error classes, budget refusal,
concurrent reservations, the response cache, and a replay that cannot reach the provider (A20)."""
import socket
import threading
import time
from pathlib import Path

import pytest
from google.genai import errors, types

from conftest import CODE
from ghostaudit.config import load_config
from ghostaudit.llm.gateway import Gateway, ProviderForbidden, ReplayMiss, request_key
from ghostaudit.llm.ledger import BudgetExceeded, Ledger

CFG = load_config()
MODEL = "gemini-3.1-flash-lite"


def _resp(text="ok"):
    return types.GenerateContentResponse(
        candidates=[types.Candidate(content=types.Content(role="model", parts=[types.Part(text=text)]),
                                    finish_reason="STOP")],
        usage_metadata=types.GenerateContentResponseUsageMetadata(prompt_token_count=100, candidates_token_count=20,
                                                                  thoughts_token_count=30))


class FakeProvider:
    """Stateful: replays a script of outcomes and counts what was actually sent."""

    def __init__(self, script):
        self.script, self.sent = list(script), 0

    def send(self, *, model, contents, config):
        self.sent += 1
        out = self.script.pop(0)
        if isinstance(out, Exception):
            raise out
        time.sleep(getattr(self, "delay", 0))
        return out


def _err(cls, code, status):
    return cls(code, {"error": {"code": code, "message": "x", "status": status}})


def _gw(tmp_path, provider, ceiling=4.5, mode="live"):
    led = Ledger(tmp_path / "ledger.jsonl", ceiling)
    return Gateway("t", CFG, led, mode=mode, cache_dir=tmp_path / "cache", provider=provider,
                   sleep=lambda s: None), led


def _call(gw, text="hello", max_out=100):
    return gw.generate(model=MODEL, contents=text, purpose="test", est_input_tokens=1000,
                       config=types.GenerateContentConfig(max_output_tokens=max_out, temperature=0))


def _settles(led):
    return [r for r in led.rows() if r["kind"] == "settle"]


@pytest.mark.parametrize("code", [400, 401, 403, 404])
def test_settle_rejected_request_at_zero_and_never_retry(tmp_path, code):
    p = FakeProvider([_err(errors.ClientError, code, "INVALID_ARGUMENT")])
    gw, led = _gw(tmp_path, p)
    with pytest.raises(errors.ClientError):
        _call(gw)
    s = _settles(led)
    assert p.sent == 1 and len(s) == 1
    assert s[0]["cost_usd"] == 0.0 and s[0]["cost_basis"] == f"rejected_{code}"
    assert led.totals()["committed_usd"] == 0.0


def test_settle_429_at_zero_then_retry(tmp_path):
    p = FakeProvider([_err(errors.ClientError, 429, "RESOURCE_EXHAUSTED"), _resp()])
    gw, led = _gw(tmp_path, p)
    resp, usage = _call(gw)
    s = _settles(led)
    assert p.sent == 2 and [x["cost_basis"] for x in s] == ["rejected_429", "usage_metadata"]
    assert s[0]["cost_usd"] == 0.0 and usage["cost_usd"] > 0


@pytest.mark.parametrize("exc", [_err(errors.ServerError, 503, "UNAVAILABLE"), TimeoutError("read timeout"),
                                 ConnectionResetError("reset")], ids=["503", "timeout", "transport"])
def test_settle_maybe_billed_failures_at_the_reservation_and_retry_finitely(tmp_path, exc):
    p = FakeProvider([exc] * 3)
    gw, led = _gw(tmp_path, p)
    with pytest.raises(type(exc)):
        _call(gw)
    s = _settles(led)
    est = (1000 * 0.25 + 100 * 1.50) / 1_000_000
    assert p.sent == gw.max_attempts == 3
    assert all(x["cost_basis"] == "reservation" and x["cost_usd"] == pytest.approx(est) for x in s)


def test_measured_cost_counts_thinking_tokens_at_the_output_price(tmp_path):
    gw, led = _gw(tmp_path, FakeProvider([_resp()]))
    _, usage = _call(gw)
    assert usage["cost_usd"] == pytest.approx((100 * 0.25 + (20 + 30) * 1.50) / 1_000_000)


def test_over_budget_is_refused_before_anything_is_sent(tmp_path):
    p = FakeProvider([_resp()])
    gw, led = _gw(tmp_path, p, ceiling=0.0001)
    with pytest.raises(BudgetExceeded):
        _call(gw, max_out=10_000)
    assert p.sent == 0 and led.rows() == []


def test_concurrent_reservations_never_overspend(tmp_path):
    est = (1000 * 0.25 + 1000 * 1.50) / 1_000_000          # per call
    p = FakeProvider([_resp(f"r{i}") for i in range(8)])
    p.delay = 0.05                                           # keep reservations open while others reserve
    gw, led = _gw(tmp_path, p, ceiling=est * 3.5)
    outcomes = []

    def worker(i):
        try:
            _call(gw, text=f"q{i}", max_out=1000)
            outcomes.append("ok")
        except BudgetExceeded:
            outcomes.append("refused")

    threads = [threading.Thread(target=worker, args=(i,)) for i in range(8)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    reserves = [r for r in led.rows() if r["kind"] == "reserve"]
    assert len(outcomes) == 8 and outcomes.count("ok") == len(reserves) <= 3
    assert sum(r["est_usd"] for r in reserves) <= est * 3.5


def test_identical_request_is_served_from_cache_without_a_paid_call(tmp_path):
    p = FakeProvider([_resp("first")])
    gw, led = _gw(tmp_path, p)
    r1, u1 = _call(gw)
    rows = len(led.rows())
    r2, u2 = _call(gw)
    assert p.sent == 1 and len(led.rows()) == rows and u2["cache"] and r2.text == r1.text == "first"
    # both uses are recorded, so a run can list every response behind its output (live, then cached)
    assert [u["cache"] for u in gw.used] == [False, True] and gw.used[0]["request_key"] == gw.used[1]["request_key"]


def test_request_key_is_stable_and_sensitive():
    cfg = types.GenerateContentConfig(max_output_tokens=10, temperature=0)
    assert request_key(MODEL, ["a", {"b": 1, "a": 2}], cfg) == request_key(MODEL, ["a", {"a": 2, "b": 1}], cfg)
    assert request_key(MODEL, "a", cfg) != request_key(MODEL, "b", cfg)
    assert request_key(MODEL, "a", cfg) != request_key("gemini-3.8-flash", "a", cfg)


def test_replay_never_reaches_the_provider_or_the_network(tmp_path, monkeypatch):
    live, led = _gw(tmp_path, FakeProvider([_resp("cached answer")]))
    _call(live, text="seen")
    rows = len(led.rows())

    def boom(*a, **k):
        raise AssertionError("provider or network touched in replay")
    import ghostaudit.llm.gemini as gem
    monkeypatch.setattr(gem, "_api_key", boom)
    monkeypatch.setattr(gem.genai, "Client", boom)
    monkeypatch.setattr(gem, "GeminiProvider", boom)
    monkeypatch.setattr(socket, "socket", boom)
    monkeypatch.setenv("GEMINI_API_KEY", "not-a-real-key")       # present, and still never read
    replay = Gateway("t", CFG, led, mode="replay", cache_dir=tmp_path / "cache")
    resp, usage = _call(replay, text="seen")
    assert resp.text == "cached answer" and usage["cache"]
    with pytest.raises(ReplayMiss):
        _call(replay, text="never seen")
    with pytest.raises(ProviderForbidden):
        replay.provider()
    assert len(led.rows()) == rows and replay.stats["replay_misses"] == 1


def test_only_the_provider_module_calls_the_sdk():
    users = [p for p in (CODE / "ghostaudit").rglob("*.py") if "generate_content(" in p.read_text()]
    assert [p.relative_to(CODE).as_posix() for p in users] == ["ghostaudit/llm/gemini.py"]


# --- S5 C5.11: declared replay artifacts are verified on read; every used response is recorded ---

def test_a_manifest_rejects_a_tampered_or_undeclared_artifact(tmp_path):
    import pytest as _pytest
    from ghostaudit.artifacts import ArtifactMismatch, read_text, write_manifest
    a, b = tmp_path / "x" / "a.json", tmp_path / "x" / "b.json"
    a.parent.mkdir()
    a.write_text('{"v": 1}')
    b.write_text('{"v": 2}')
    assert read_text(tmp_path, a) == '{"v": 1}'                 # no manifest: a working checkout reads as is
    write_manifest(tmp_path, [a])
    assert read_text(tmp_path, a) == '{"v": 1}'
    with _pytest.raises(ArtifactMismatch, match="not declared"):
        read_text(tmp_path, b)
    a.write_text('{"v": 9}')
    with _pytest.raises(ArtifactMismatch, match="sha256"):
        read_text(tmp_path, a)
