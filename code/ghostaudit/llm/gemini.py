"""Gemini adapter: the only place that sends paid requests (S0 minimal version; S4 adds cache/retries).

Each call reserves an upper-bound cost in the ledger, sends one request, and settles
the measured cost from usage_metadata. Output price covers candidate + thinking tokens.
"""
from __future__ import annotations

import os
import time
from pathlib import Path

from google import genai
from google.genai import types

from ..config import REPO_ROOT, load_config, price_for
from .ledger import Ledger


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


class Gemini:
    def __init__(self, run_id: str, config: dict | None = None, ledger: Ledger | None = None):
        self.config = config or load_config()
        self.ledger = ledger or Ledger(REPO_ROOT / self.config["budget"]["ledger_path"],
                                       self.config["budget"]["ceiling_usd"])
        self.run_id = run_id
        self.client = genai.Client(api_key=_api_key())

    def generate(self, *, model: str, contents, config: types.GenerateContentConfig, purpose: str,
                 est_input_tokens: int, case_id: str | None = None):
        if not config.max_output_tokens:
            raise ValueError("max_output_tokens is required so the reservation is a true upper bound")
        pin, pout = price_for(self.config, model)
        est = (est_input_tokens * pin + config.max_output_tokens * pout) / 1_000_000
        res_id = self.ledger.reserve(est_usd=est, model=model, purpose=purpose, run_id=self.run_id, case_id=case_id)
        t0 = time.monotonic()
        try:
            resp = self.client.models.generate_content(model=model, contents=contents, config=config)
        except Exception as exc:
            # The request may have been billed; settle at the reserved estimate (conservative).
            self.ledger.settle(res_id, status="error", cost_usd=est, error=type(exc).__name__,
                               latency_ms=int((time.monotonic() - t0) * 1000), cost_basis="reservation")
            raise
        measured = usage_cost(resp.usage_metadata, model, self.config)
        self.ledger.settle(res_id, status="ok", latency_ms=int((time.monotonic() - t0) * 1000),
                           model_version=getattr(resp, "model_version", None), cost_basis="usage_metadata",
                           **measured)
        return resp, measured
