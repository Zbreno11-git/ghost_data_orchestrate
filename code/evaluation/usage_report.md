# Usage report

Generated 2026-10-25 03:57 UTC by `scripts/make_reports.py` from `runs/s7/final-r2/llm_keys.jsonl` (every model response the final run used) and `state/usage_ledger.jsonl` (every paid call of the project).

## Final full-dataset run (the one that produced output.csv)

Provider: Google Gemini API. Requests: 518. Responses are counted once each; *live* ones were paid in this run, the others were served from the response cache, paid by the earlier run named under provenance (identical request content).

| model | purpose | calls | live | input tokens | output tokens (incl. thinking) | cost (USD) |
|---|---|---|---|---|---|---|
| gemini-3.1-flash-lite | agent | 1749 | 0 | 5,281,025 | 61,236 | 1.412100 |
| gemini-3.1-flash-lite | intent-batch | 26 | 0 | 30,061 | 28,103 | 0.049669 |
| **all** | | **1775** | 0 | **5,311,086** | **89,339** | **1.461769** |

The cost column is what the responses behind this output cost when they were generated (the full price of the run); of it, $0.000000 was paid in this run and the rest earlier (provenance below).

Per request (518): 3.43 calls, 10,426 tokens, $0.002822. Total tokens 5,400,425.

Agent scope `non_resolved`: 166 resolved proposals were published without a model call; 352 reviews submitted, 0 fell back to the deterministic proposal. Intent is one batched classification pass over all requests, cross-checked against the deterministic rule.

Provenance of cached responses (run that paid for them): `20261025T004200Z-agent-live-targets-strict` 1249, `20261025T034529Z-agent-live-targets-strict` 409, `20261024T222156Z-agent-live-targets-strict` 78, `c4.4-intent-targets` 26, `20261025T010756Z-agent-live-targets-strict` 13

Screenshot extraction (one-time, cached in `state/vision_cache/` and shipped with the code) is part of ingestion, not of this run; it is in the cumulative table below.

## Cumulative project spend (all runs, from the ledger)

| purpose | model | settled calls | cost (USD) |
|---|---|---|---|
| agent | gemini-3.1-flash-lite | 2413 | 1.925388 |
| agent | gemini-3.8-flash | 64 | 0.177595 |
| intent-batch | gemini-3.1-flash-lite | 39 | 0.060259 |
| smoke-json | gemini-3.1-flash-lite | 1 | 0.000041 |
| smoke-tool-1 | gemini-3.1-flash-lite | 1 | 0.000054 |
| smoke-tool-2 | gemini-3.1-flash-lite | 1 | 0.000054 |
| smoke-vision | gemini-3.1-flash-lite | 1 | 0.000385 |
| vision-extract | gemini-3.1-flash-lite | 11 | 0.027120 |
| vision-extract | gemini-3.8-flash | 12 | 0.079747 |
| **settled total** | | 2543 | **2.270643** |

Open reservations: 2, $0.004997, counted against the budget because they may have been billed: agent in run `20261024T210748Z-agent-live-samples-strict`; intent-batch in run `20261025T033340Z-agent-live-samples-strict` (in-flight calls of a run killed on purpose to prove resume, and a release-check control that stopped before sending). A ClientError (HTTP 4xx, code not recorded) on vision-extract was booked at its reservation, $0.017610, before rejected requests were settled at $0 (A21); the append-only ledger keeps it. Budget ceiling $4.50 (hard stop in the gateway). No key or credential appears in this report.
