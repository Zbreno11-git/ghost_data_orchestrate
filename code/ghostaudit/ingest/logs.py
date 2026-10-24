"""Log evidence: one tokenizer for every line grammar, then trace grouping.

A lookup key and the resource it resolved to sit on different lines joined by a trace id, so lines are grouped
per (file, trace id) into one Observation. Lookup inputs go to `wrapper`; what the completed read returned goes
to `fields`. Every non-blank line is either parsed or counted as unparsed for the coverage report.
"""
from __future__ import annotations

import json
import re
from collections import Counter, defaultdict

from ..evidence import EvidenceStore, Observation
from ..timeutil import parse_ts
from .coverage import FileCoverage
from .manifest import ManifestEntry

TS = re.compile(r"^(\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d(?:\.\d+)?Z)\s+(.*)$")
KV = re.compile(r'([A-Za-z_][\w.]*)=("(?:[^"\\]|\\.)*"|\S+)')
SYSLOG = re.compile(r"^<\d+>\d+ (\S+) (\S+) (\S+) - - (.*)$")
BRACKET = re.compile(r"^\[(\w+)\] \[([^\]]+)\] \[([^\]]+)\] (\w+): ?(.*)$")
CLOUD = re.compile(r'^requestId=(\S+) level=(\S+) function=(\S+) message="(.*)"$')

LOOKUP_KEYS = {"lookup_key", "match_key", "correlation_key", "subject_key", "subject_ref", "query", "scan_key",
               "owner_key"}
# Per-request plumbing inside a trace; its key-values (e.g. cache result=miss) say nothing about the record.
NOISE_EVENTS = {"connection_acquired", "cache_lookup", "dependency_retry", "dependency_recovered"}
TRANSPORT_KEYS = {"instance", "pod", "region", "attempt", "duration_ms", "wait_ms", "pool", "shard", "cache",
                  "severity", "logger", "level", "seq", "latency_ms", "mode", "cursor", "batch", "source"}


def _unquote(v: str) -> str:
    if len(v) >= 2 and v[0] == v[-1] == '"':
        return v[1:-1].replace('\\"', '"').replace("\\\\", "\\")
    return v


def parse_kv(text: str) -> dict:
    return {k: _unquote(v) for k, v in KV.findall(text)}


def parse_line(line: str) -> tuple[str, dict] | None:
    """→ (grammar, record with ts/service/trace_id/event + key-values), or None if the line is not understood."""
    m = TS.match(line)
    if not m:
        return None
    ts, rest = m.groups()
    if rest.startswith("{"):
        try:
            kv = {k: v if isinstance(v, str) else json.dumps(v) for k, v in json.loads(rest).items()}
        except json.JSONDecodeError:
            return None
        return "json", {"ts": ts, "service": kv.get("service") or kv.get("logger"), "trace_id": kv.get("trace_id"),
                        "event": kv.get("event"), **kv}
    if (s := SYSLOG.match(rest)):
        _, svc, trace, body = s.groups()
        kv = parse_kv(body)
        return "syslog", {"ts": ts, "service": svc, "trace_id": trace, "event": kv.get("event"), **kv}
    if (b := BRACKET.match(rest)):
        level, svc, trace, event, body = b.groups()
        return "bracket", {"ts": ts, "service": svc, "trace_id": trace, "event": event, "level": level,
                           **parse_kv(body)}
    if " | " in rest[:12] or rest.startswith("| "):
        parts = [p.strip() for p in rest.strip("| ").split(" | ")]
        if len(parts) >= 4:
            level, svc, trace, event = parts[:4]
            kv = parse_kv(" ".join(parts[4:]))
            return "pipe", {"ts": ts, "service": svc, "trace_id": trace, "event": event, "level": level, **kv}
        return None
    if (c := CLOUD.match(rest)):
        trace, level, fn, msg = c.groups()
        kv = parse_kv(msg.replace('\\"', '"'))
        return "cloud", {"ts": ts, "service": fn, "trace_id": trace, "event": kv.get("event"), "level": level, **kv}
    kv = parse_kv(rest)
    if not kv:
        return None
    grammar = "record_lookup" if kv.get("event") == "record_lookup" else "kv"
    return grammar, {"ts": ts, "service": kv.get("service"), "trace_id": kv.get("trace_id"), "event": kv.get("event"),
                     **kv}


HEADER_KEYS = {"ts", "service", "trace_id", "event"}


def _classify(fields: dict) -> str | None:
    """Result of a completed read, from what the read itself reported (never from the workflow's claim)."""
    rows, status, result = fields.get("rows"), fields.get("http_status"), fields.get("result")
    total = fields.get("total_hits")
    if rows == "0" or status == "404" or result == "miss" or total == "0":
        return "NOT_FOUND"
    if (rows and rows != "0") or status == "200" or result == "hit" or (total and total != "0"):
        return "FOUND"
    return None


def ingest_log(entry: ManifestEntry, store: EvidenceStore, cov: FileCoverage) -> None:
    lines = entry.path.read_text(encoding="utf-8").splitlines()
    grammars = Counter()
    groups: dict[str, list[tuple[int, dict]]] = defaultdict(list)
    n = 0
    cov.adapter = "logs"
    for i, line in enumerate(lines, start=1):
        if not line.strip():
            continue
        cov.lines += 1
        parsed = parse_line(line)
        if parsed is None:
            cov.unparsed += 1
            if cov.unparsed <= 3:
                cov.notes.append(f"unparsed line {i}: {line[:120]}")
            continue
        grammar, rec = parsed
        grammars[grammar] += 1
        if grammar == "record_lookup":
            kv = {k: v for k, v in rec.items() if k not in HEADER_KEYS | TRANSPORT_KEYS}
            store.add(Observation(
                obs_id=f"{entry.file_id}#line:{i}", source_id=entry.file_id, source_kind="log", kind="lookup",
                captured_at=entry.captured_at, observed_at=parse_ts(rec["ts"]), system_id=kv.get("system"),
                resource_id=kv.get("resource_id"), record_type=kv.get("record_type"), result=kv.get("result"),
                container=rec.get("service"), wrapper={"subject_reference": kv.get("subject_reference"),
                                                       "recorded_by": rec.get("service")},
                locator=f"line:{i}"))
            n += 1
        elif rec.get("trace_id"):
            groups[rec["trace_id"]].append((i, rec))
        elif rec.get("resource_id"):
            groups[f"line:{i}"].append((i, rec))  # a resource line outside any trace keeps its own observation
    for trace, recs in groups.items():
        resources = [r["resource_id"] for _, r in recs if r.get("resource_id")]
        if not resources:
            continue  # collector / resolver chatter: parsed, but carries no resource
        wrapper, fields, events = {}, {}, []
        payload_events = []
        for _, r in recs:
            ev = r.get("event") or ""
            events.append(ev)
            for k, v in r.items():
                if k in HEADER_KEYS or k in TRANSPORT_KEYS:
                    continue
                if k in LOOKUP_KEYS:
                    wrapper[k] = v
                elif ev not in NOISE_EVENTS and not ev.endswith("_started"):
                    fields[k] = v
            if ev not in NOISE_EVENTS and not ev.endswith("_started"):
                payload_events.append(r)
        last = payload_events[-1] if payload_events else recs[-1][1]
        result = _classify(fields)
        has_payload = bool(set(fields) - {"resource_id"})
        services = sorted({r["service"] for _, r in recs if r.get("service")})
        fields["events"] = ",".join(events)
        if len(set(resources)) > 1:
            fields["resource_ids"] = ",".join(dict.fromkeys(resources))
        store.add(Observation(
            obs_id=f"{entry.file_id}#{trace if trace.startswith('line:') else 'trace:' + trace}", source_id=entry.file_id, source_kind="log",
            kind="record" if result == "FOUND" or (result is None and has_payload) else "lookup",
            captured_at=entry.captured_at,
            observed_at=parse_ts(last["ts"]), system_id=services[0] if services else None, resource_id=resources[0],
            result=result, container=",".join(services), fields=fields,
            wrapper={**wrapper, "trace_lines": f"{recs[0][0]}-{recs[-1][0]}"}, locator=trace if trace.startswith("line:") else f"trace:{trace}"))
        n += 1
    cov.observations = n
    cov.notes.insert(0, "grammars=" + ",".join(f"{g}:{c}" for g, c in sorted(grammars.items())))
    cov.status = "partial" if cov.unparsed else "processed"
