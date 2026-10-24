"""Gemini provider: the only module that talks to the SDK. Paid calls go through llm/gateway.py.

The client is built lazily, on the first paid request only, so replay never constructs it or reads a key
(A20). The SDK's own retries are disabled: the gateway retries, and ledgers each attempt.
"""
from __future__ import annotations

import os

from google import genai
from google.genai import types

from ..config import REPO_ROOT, load_config, price_for


def _api_key() -> str:
    key = os.environ.get("GEMINI_API_KEY")
    if not key:
        env = REPO_ROOT / ".env"
        if env.exists():
            for line in env.read_text().splitlines():
                if line.startswith("GEMINI_API_KEY="):
                    key = line.split("=", 1)[1].strip().strip('"').strip("'")
    if not key:
        raise RuntimeError("GEMINI_API_KEY is not set (environment or .env); no paid call was made")
    return key


def usage_cost(usage, model: str, config: dict) -> dict:
    pin, pout = price_for(config, model)
    prompt = (usage.prompt_token_count or 0) + (usage.tool_use_prompt_token_count or 0)
    out = usage.candidates_token_count or 0
    thoughts = usage.thoughts_token_count or 0
    return {
        "input_tokens": prompt,
        "output_tokens": out,
        "thought_tokens": thoughts,
        "cached_tokens": usage.cached_content_token_count or 0,
        "cost_usd": (prompt * pin + (out + thoughts) * pout) / 1_000_000,
    }


class GeminiProvider:
    def __init__(self, timeout_s: float):
        self.timeout_s = timeout_s
        self._client = None

    def send(self, *, model: str, contents, config: types.GenerateContentConfig):
        if self._client is None:
            self._client = genai.Client(api_key=_api_key(), http_options=types.HttpOptions(
                timeout=int(self.timeout_s * 1000), retry_options=types.HttpRetryOptions(attempts=1)))
        return self._client.models.generate_content(model=model, contents=contents, config=config)


class Gemini:
    """Compatibility facade (vision ingestion, smoke script): a live gateway with the default cache."""

    def __init__(self, run_id: str, config: dict | None = None, ledger=None):
        from .gateway import Gateway
        self.gateway = Gateway(run_id=run_id, config=config or load_config(), ledger=ledger, mode="live")

    def generate(self, **kwargs):
        return self.gateway.generate(**kwargs)
