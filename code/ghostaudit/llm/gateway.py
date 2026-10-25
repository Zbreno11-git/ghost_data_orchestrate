"""The only paid path: reserve → send → settle, by error class, with a response cache for resume and replay.

Settlement policy (A21, from the S2 incident where one 400 was booked at its $0.0176 reservation):
- ClientError 400/401/403/404: the provider rejected the request before generating → settle $0, never retried.
- ClientError 429: rate limited, not processed → settle $0, retried after a backoff.
- ServerError (5xx), timeouts, transport and unknown errors: the request may have been billed → settle at the
  reservation (conservative), retried after a backoff.
Each attempt is its own reservation, so the $4.50 ceiling holds across retries, processes and resumes.

Replay (A20): the gateway serves cached responses only. It never builds the provider, so no key is read (the
provider reads `.env` too). A cache miss raises ReplayMiss, which the caller turns into an unresolved case.
"""
from __future__ import annotations

import hashlib
import json
import os
import tempfile
import time
from pathlib import Path

from google.genai import errors, types

from ..config import REPO_ROOT, load_config, price_for
from .ledger import Ledger

REJECTED = {400, 401, 403, 404}
RATE_LIMITED = 429


class ReplayMiss(RuntimeError):
    """Replay found no cached response for a request; nothing was sent."""


class ProviderForbidden(RuntimeError):
    """A provider was requested in replay mode."""


def _jsonable(x):
    if hasattr(x, "model_dump"):
        return _jsonable(x.model_dump(mode="json", exclude_none=True))
    if isinstance(x, bytes):
        return {"sha256": hashlib.sha256(x).hexdigest()}
    if isinstance(x, dict):
        return {str(k): _jsonable(v) for k, v in sorted(x.items())}
    if isinstance(x, (list, tuple)):
        return [_jsonable(v) for v in x]
    return x


def request_key(model: str, contents, config) -> str:
    """Stable hash of everything that determines the response (sorted keys, bytes by digest)."""
    blob = json.dumps({"model": model, "contents": _jsonable(contents), "config": _jsonable(config)},
                      sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(blob.encode()).hexdigest()


def classify_error(exc: Exception) -> tuple[str, bool]:
    """(cost basis, retryable). The basis decides what the ledger books for the attempt."""
    if isinstance(exc, errors.ClientError):
        if exc.code in REJECTED:
            return f"rejected_{exc.code}", False
        if exc.code == RATE_LIMITED:
            return "rejected_429", True
        return "reservation", False        # other 4xx: ours, not retried, may have been processed
    return "reservation", True             # 5xx, timeouts, transport, unknown


class Gateway:
    def __init__(self, run_id: str, config: dict | None = None, ledger: Ledger | None = None, mode: str = "live",
                 cache_dir: Path | None = None, provider=None, sleep=time.sleep):
        if mode not in ("live", "replay"):
            raise ValueError(f"unknown gateway mode {mode!r}")
        self.config = config or load_config()
        g = self.config.get("gateway", {})
        self.mode = mode
        self.run_id = run_id
        self.ledger = ledger or Ledger(REPO_ROOT / self.config["budget"]["ledger_path"],
                                       self.config["budget"]["ceiling_usd"])
        self.cache_dir = Path(cache_dir or REPO_ROOT / g.get("cache_dir", "runs/cache/llm"))
        self.max_attempts = int(g.get("max_attempts", 3))
        self.backoff_s = float(g.get("backoff_s", 2.0))
        self.timeout_s = float(g.get("timeout_s", 90))
        self._provider = provider
        self._sleep = sleep
        self.stats = {"cache_hits": 0, "paid_calls": 0, "failed_attempts": 0, "replay_misses": 0}
        self.used: list[dict] = []      # every response this run used, live or cached (usage report, package)

    # --- provider: built only on a live cache miss -------------------------------------------------
    def provider(self):
        if self.mode == "replay":
            raise ProviderForbidden("replay mode never contacts the provider")
        if self._provider is None:
            from .gemini import GeminiProvider
            self._provider = GeminiProvider(self.timeout_s)
        return self._provider

    # --- cache --------------------------------------------------------------------------------------
    def _cache_path(self, key: str) -> Path:
        return self.cache_dir / f"{key[:2]}/{key}.json"

    def cached(self, key: str) -> dict | None:
        from ..artifacts import read_text
        p = self._cache_path(key)
        return json.loads(read_text(self.cache_dir, p)) if p.exists() else None

    def _store(self, key: str, record: dict) -> None:
        p = self._cache_path(key)
        p.parent.mkdir(parents=True, exist_ok=True)
        fd, tmp = tempfile.mkstemp(dir=p.parent, suffix=".tmp")
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            json.dump(record, fh, ensure_ascii=False, sort_keys=True)
        os.replace(tmp, p)

    # --- the call -----------------------------------------------------------------------------------
    def generate(self, *, model: str, contents, config: types.GenerateContentConfig, purpose: str,
                 est_input_tokens: int, case_id: str | None = None):
        """(response, usage). usage['cache'] is True when no paid call was made."""
        key = request_key(model, contents, config)
        hit = self.cached(key)
        if hit is not None:
            self.stats["cache_hits"] += 1
            self.used.append({"request_key": key, "purpose": purpose, "model": model, "case_id": case_id,
                              "cache": True, "usage": hit["usage"]})
            resp = types.GenerateContentResponse.model_validate(hit["response"])
            return resp, {**hit["usage"], "cost_usd": 0.0, "cache": True, "request_key": key}
        if self.mode == "replay":
            self.stats["replay_misses"] += 1
            raise ReplayMiss(f"no cached response for {purpose} ({case_id or '-'}), request {key[:12]}")
        if not config.max_output_tokens:
            raise ValueError("max_output_tokens is required so the reservation is a true upper bound")
        pin, pout = price_for(self.config, model)
        est = (est_input_tokens * pin + config.max_output_tokens * pout) / 1_000_000
        from .gemini import usage_cost

        delay = self.backoff_s
        for attempt in range(1, self.max_attempts + 1):
            res_id = self.ledger.reserve(est_usd=est, model=model, purpose=purpose, run_id=self.run_id,
                                         case_id=case_id)
            t0 = time.monotonic()
            try:
                resp = self.provider().send(model=model, contents=contents, config=config)
            except Exception as exc:  # classified, booked, then retried or re-raised: never swallowed
                basis, retryable = classify_error(exc)
                self.ledger.settle(res_id, status="error", cost_usd=0.0 if basis.startswith("rejected") else est,
                                   error=type(exc).__name__, code=getattr(exc, "code", None), attempt=attempt,
                                   latency_ms=int((time.monotonic() - t0) * 1000), cost_basis=basis)
                self.stats["failed_attempts"] += 1
                if not retryable or attempt == self.max_attempts:
                    raise
                self._sleep(delay)
                delay *= 2
                continue
            measured = usage_cost(resp.usage_metadata, model, self.config)
            self.ledger.settle(res_id, status="ok", latency_ms=int((time.monotonic() - t0) * 1000),
                               model_version=getattr(resp, "model_version", None), cost_basis="usage_metadata",
                               attempt=attempt, request_key=key, **measured)
            self.stats["paid_calls"] += 1
            self.used.append({"request_key": key, "purpose": purpose, "model": model, "case_id": case_id,
                              "cache": False, "usage": measured})
            self._store(key, {"model": model, "purpose": purpose, "case_id": case_id, "usage": measured,
                              "response": resp.model_dump(mode="json", exclude_none=True)})
            return resp, {**measured, "cache": False, "request_key": key}
        raise AssertionError("unreachable: the loop returns or raises")
