"""ISO-8601 UTC timestamps as aware datetimes. A missing or malformed time is an error, never 'now'."""
from __future__ import annotations

from datetime import datetime, timezone


def parse_ts(value: str) -> datetime:
    v = value.strip()
    if v.endswith("Z"):
        v = v[:-1] + "+00:00"
    dt = datetime.fromisoformat(v)
    if dt.tzinfo is None:
        raise ValueError(f"timestamp without timezone: {value!r}")
    return dt.astimezone(timezone.utc)
