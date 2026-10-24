"""Cumulative, append-only usage ledger shared by every run and session.

Every paid call reserves a conservative upper bound *before* it is sent and settles
the measured cost afterwards. An open reservation (crash, timeout) keeps counting
toward the total until it is explicitly released, because the provider may have
billed it. The ceiling therefore holds across processes, resumes and clones.
"""
from __future__ import annotations

import fcntl
import json
import os
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path


class BudgetExceeded(RuntimeError):
    pass


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


class Ledger:
    def __init__(self, path: Path, ceiling_usd: float):
        self.path = Path(path)
        self.ceiling_usd = ceiling_usd
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._lock_path = self.path.with_suffix(".lock")

    @contextmanager
    def _locked(self):
        with open(self._lock_path, "a") as lock:
            fcntl.flock(lock, fcntl.LOCK_EX)
            try:
                yield
            finally:
                fcntl.flock(lock, fcntl.LOCK_UN)

    def rows(self) -> list[dict]:
        if not self.path.exists():
            return []
        with open(self.path, encoding="utf-8") as fh:
            return [json.loads(line) for line in fh if line.strip()]

    def _append(self, row: dict) -> None:
        with open(self.path, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(row, sort_keys=True) + "\n")
            fh.flush()
            os.fsync(fh.fileno())

    @staticmethod
    def summarize(rows: list[dict]) -> dict:
        """settled = measured spend; outstanding = reservations not yet settled or released."""
        reserved, closed, settled = {}, set(), 0.0
        for r in rows:
            if r["kind"] == "reserve":
                reserved[r["res_id"]] = r["est_usd"]
            elif r["kind"] == "settle":
                closed.add(r["res_id"])
                settled += r["cost_usd"]
            elif r["kind"] == "release":
                closed.add(r["res_id"])
        outstanding = sum(v for k, v in reserved.items() if k not in closed)
        return {"settled_usd": settled, "outstanding_usd": outstanding, "committed_usd": settled + outstanding}

    def totals(self) -> dict:
        return self.summarize(self.rows())

    def reserve(self, *, est_usd: float, model: str, purpose: str, run_id: str, case_id: str | None = None) -> str:
        with self._locked():
            committed = self.summarize(self.rows())["committed_usd"]
            if committed + est_usd > self.ceiling_usd:
                raise BudgetExceeded(
                    f"reservation ${est_usd:.4f} would raise committed ${committed:.4f} above ceiling ${self.ceiling_usd:.2f}"
                )
            res_id = uuid.uuid4().hex
            self._append({"kind": "reserve", "ts": _now(), "res_id": res_id, "est_usd": est_usd, "model": model,
                          "purpose": purpose, "run_id": run_id, "case_id": case_id})
            return res_id

    def settle(self, res_id: str, **fields) -> None:
        """fields must include cost_usd and status ('ok' or 'error'); token counts as available."""
        with self._locked():
            self._append({"kind": "settle", "ts": _now(), "res_id": res_id, **fields})

    def release(self, res_id: str, reason: str) -> None:
        """Only for a reservation proven never sent (e.g. failed before the HTTP request)."""
        with self._locked():
            self._append({"kind": "release", "ts": _now(), "res_id": res_id, "reason": reason})
