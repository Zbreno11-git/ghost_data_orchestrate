# Ghost Data Still Exists — Claude Code implementation handoff

Prepared 2026-10-24. Owner: Breno. This is an implementation specification, not an implemented or tested solution.

## 1. Goal and constraints

Build an AI-powered deletion-audit agent for the HackerRank Orchestrate October 2026 challenge. Optimize competition correctness while keeping internals reusable. Breno reports approximately 20 hours remaining and can participate for only a few hours spread across the day. Claude Code should execute useful work autonomously between check-ins.

Budget: maximum USD 5 of Gemini API spending across development, evaluation, extraction, retries and final runs. Claude Code subscription usage is separate. Keep work local first. No application database, server, deployment, authentication or frontend is required for the scoring engine. An optional local evidence explorer comes after correct engine behavior and packaging.

A CLI is the interface; a bounded, tool-using investigation loop is the agent. Deterministic parsers, evidence constraints and policy validators support its decisions. Do not replace the agent with a collection of case-ID rules, and do not delegate policy authority or CSV serialization to unconstrained model text.

## 2. Authoritative sources and preflight

Read the current checkout's complete AGENTS.md, README.md, problem_statement.md and agent_trace_instructions.md before implementation. The repository is:
https://github.com/interviewstreet/hackerrank-orchestrate-october26

The user-provided challenge page is:
https://www.hackerrank.com/contests/hackerrank-orchestrate-october26/challenges/ghost-data-still-exists

The page was inaccessible from the planning environment. Its extra rules, precise deadline and upload fields have not been verified. Do not invent them or delay implementation waiting for them. Use the user-reported remaining time as a planning estimate, and make the final submission ready early.

The inspected main tree was acb3dfca6e94e4803a26e72c49074a488de93c93. Record the actual checkout SHA; inspect relevant changes if the source has moved.

Preflight checklist:
- Read repo instructions, record authoritative harness/model metadata and start the required append-only log.txt.
- Establish Python environment and pin dependencies after a successful smoke test.
- Verify participant dataset shape and inspect every evidence format.
- Verify GEMINI_API_KEY is set without printing it; make a tiny authentication/model/schema smoke test.
- Check model IDs, function-calling behavior, supported generation settings and token accounting against the installed official SDK.
- Record budget ledger and run IDs before making paid calls.
- Establish a no-network replay mode and test it.
- Preserve original Claude Code session traces from the start.

Use only participant-facing data under dataset/ for predictions. Do not inspect private generators, organizer truth or hidden labels. Public sample_output.csv is for evaluation and interpretation of the published contract, never runtime lookup or a hardcoded predictor.

## 3. Output and policy contract

Input dataset/deletion_requests.csv has 518 target cases. There are 32 public sample requests and answers. Validate actual counts on checkout rather than assuming sample/target overlap.

Output root-level output.csv with exactly:
case_id,deletion_status,steps_json

One unique row for each target case, sorted lexicographically by case_id. Status is COMPLETE, INCOMPLETE or NOT_APPLICABLE. Each step has exactly:
step_no, phase, system_id, resource_id, operation, state, evidence_id

NOT_APPLICABLE: request does not authorize deletion; steps_json is [].
COMPLETE: only evidence-backed verification steps proving compliance at audit_at.
INCOMPLETE: supported findings, complete remediation plan, and required final-state checks. Findings cite valid participant file_id/activity_id/audit_id values. Proposed remediation and all future verification steps use evidence_id="" even for resources already compliant at audit time.

Retained resources and already-clean resources may still need verification in an incomplete case; do not generate checks only for resources that receive remediation. Public samples demonstrate account-absence verification alongside remediation of another remaining copy.

Canonical order is phase, operation rank, system_id, resource_id. Assign consecutive step_no values only after sorting. Operation ranks:

FINDING:
1 REPORT_REMAINING_RECORD -> PRESENT
2 REPORT_EXPOSED_PII -> PRESENT
3 REPORT_ACTIVE_DATA_FLOW -> ACTIVE
4 REPORT_RESTORE_RISK -> ACTIVE

REMEDIATION:
1 DISABLE_DATA_FLOW -> DISABLED
2 BLOCK_RESTORE -> BLOCKED
3 DELETE_RECORD -> ABSENT
4 REDACT_RECORD -> REDACTED
5 ANONYMIZE_RECORD -> ANONYMIZED

VERIFICATION:
1 VERIFY_RECORD_ABSENT -> ABSENT
2 VERIFY_RECORD_PRESENT -> PRESENT
3 VERIFY_RECORD_REDACTED -> REDACTED
4 VERIFY_RECORD_ANONYMIZED -> ANONYMIZED
5 VERIFY_DATA_FLOW_DISABLED -> DISABLED
6 VERIFY_RESTORE_BLOCKED -> BLOCKED

AGENTS.md also describes dependency ordering within remediation. Keep dependency relationships in the internal plan, but preserve the explicit serialized ordering required by problem_statement.md. Inspect public sample behavior and document any unresolved conflict; do not silently invent a new output ordering.

Apply current deletion_rules.csv. In the inspected policy:
- USER_PROFILE, SECONDARY_IDENTIFIER, SEARCH_INDEX_ENTRY, CACHE_ENTRY, USER_EXPORT, MARKETING_PROFILE: DELETE.
- Shared-context SUPPORT_MESSAGE: REDACT.
- Subject-only SUPPORT_ATTACHMENT: DELETE.
- Attributable ANALYTICS_PROFILE and PRODUCT_TELEMETRY: ANONYMIZE.
- EMAIL_DELIVERY_LOG containing email: REDACT.
- SECURITY_AUDIT_LOG within supplied retention and active LEGAL_HOLD_RECORD: RETAIN.
- BACKUP_ARCHIVE whose restore access can be blocked: RETAIN, plus handle unsafe restore access.
- ACCOUNT_TOMBSTONE: REDACT direct identifiers and preserve permitted stable user_id.

Do not extrapolate unspecified retention periods from real law. Evaluate supplied conditions using supplied evidence. A stable user reference may be acceptable in a retained tombstone and still prevent anonymization in analytics. Email hashes remain identifiers where policy forbids them.

## 4. Architecture and stack

Recommended baseline:
- Python 3.11+; standard csv/json/pathlib/hashlib/argparse/asyncio/logging/sqlite3.
- Official google-genai SDK behind one provider adapter.
- Pydantic for typed observations, tool arguments, agent actions and output validation.
- PyMuPDF for PDF text extraction and page rendering; inspect dependency license for later product reuse. A different small PDF adapter is acceptable if installation or licensing is a practical blocker.
- Pillow if needed for image preparation.
- pytest for meaningful contract, identity, temporal, policy and integration tests.
- In-memory dictionaries and sets for exact identifier/resource lookup.
- JSON/JSONL caches and run artifacts on disk; atomic writes and resumability.
- sqlite3 only for isolated inspection of supplied SQL snapshots; no app database.
- No vector database or embeddings in the first implementation. Grounded identifier lookup and full-corpus coverage take precedence.

Avoid orchestration-framework integration work unless a concrete measured need justifies it. Use the official SDK and a small explicit agent state machine. Dependency versions are chosen and pinned during preflight, not guessed in this document.

Suggested modules under code/:
- main.py: stable CLI entry point.
- schemas.py: request, identity, observation, action, plan, output models.
- ingest/: format adapters and manifest inventory.
- evidence.py: immutable evidence store, exact indexes and provenance.
- identity.py: identity history and grounded resource linking.
- temporal.py: cutoff filtering, timelines and conflicts.
- policy.py: supplied-policy evaluation and treatment rules.
- tools.py: typed read-only investigation tools.
- agent.py: bounded plan/tool/observe/check loop.
- model.py: Gemini adapter, validation, retries and usage capture.
- planner.py: canonical findings/remediation/verification compilation.
- validate.py: structural and evidence invariants.
- usage.py: budget reservations and auditable usage ledger.
- evaluation/main.py plus required Markdown reports.
- prompts/: Markdown or source-controlled prompt templates.
- tests/: targeted tests and custom synthetic fixtures.
- viewer.py or a static report generator only after the core gates.

Keep public samples outside the prediction call path. An evaluator may access them; the predictor must not.

## 5. Evidence ingestion and provenance

Inspected evidence inventory: 94 files, about 2.9 MB total; 24 SQL, 28 JSON, 26 logs, 11 PNG, four PDF, one TXT. Verify the full inventory at runtime.

Extract structured formats deterministically first. Extract PDF text before using vision. Use Gemini vision for screenshots, scanned pages or unresolved layout facts; 15 image/PDF artifacts do not necessarily mean 15 calls or pages. Cache complete extractions once per source content hash.

Each Observation should carry:
- internal observation ID and original file_id/activity_id/audit_id;
- source path and location (page, table/row, JSON pointer or line);
- raw grounded excerpt or extracted fields;
- source origin, physical store/replica, logical system_id and resource_id;
- data category, explicit identifiers, present fields and observed state;
- event_time, observed_at, file captured_at and validity bounds when supplied;
- extraction method/version, cache key and any unresolved extraction issue.

Keep claim versus state observation separate. A SUCCESS event is not the same as observing an absent record. A redaction marker is not enough if prohibited identifiers remain in another field.

Do not infer case membership from filenames, manifest ordering, number patterns or case families. Evidence bundles can contain unrelated people and several timestamps.

Distinguish business content from audit metadata. An evidence wrapper's subject_reference may identify an anonymous business record for the auditor without itself proving that the business record retains that identifier. Inspect the actual business-record fields. Similarly, user_identities.csv is a discovery ledger, not automatically an active profile violation. Determine meaning from source context.

For SQL:
- Load each snapshot into an isolated temporary or in-memory SQLite connection.
- Disable extension loading and prohibit ATTACH, external file access and unexpected statements; permit only necessary fixture schema/data operations.
- Inspect all relevant primary, regional, read, reporting and failover tables.
- Preserve store/replica observations even if logical resource IDs overlap.
- Map final system_id/resource_id using grounded source semantics and public format conventions; do not invent new output IDs for replica names.
- Absence from a filtered or partial table is not proof of deletion. Establish query scope or explicit absence evidence.

For logs, parse distinct concrete formats rather than relying on a single regex. Record unparsed lines/files and investigate extraction coverage gaps.

## 6. Identity and time model

Resolve supplied request email through current and historical records into stable user identity. Collect current and historical email, phone, name, email_hash and grounded resource references, preserving their times and provenance.

Use justified normalization (case-insensitive email comparison where supported by the corpus; punctuation-normalized phones where unambiguous). Preserve original strings. Do not apply provider-specific transformations such as removing dots or plus-tags without evidence. Do not merge people on name/similarity alone.

Avoid speculative hashing conventions. Prefer supplied historical hashes; derive a hash only after verifying the actual normalization/algorithm against supplied evidence.

Discover resources by exact current/historical identifier matches and explicit references. Expand links until no new grounded identifiers/resources emerge. Previously anonymized resources can lose all personal identifiers; recover their identity through historical resource IDs and resource lineage rather than insisting on a current PII match.

Time semantics:
- Use audit_at as the answer cutoff, not reported_at or the newest observation globally.
- Track capture/availability time separately from the business event time.
- Exclude evidence unavailable by cutoff under the repository's current evidence rules. A later export that embeds an older snapshot is not automatically eligible.
- Do not use a later identity update to leak future identifiers into an earlier audit without a permitted historical source.
- Sort per-resource observations using supported observation times and scope, while retaining conflicting evidence.
- A newer workflow claim does not necessarily override a direct state observation.
- Do not declare absence from failed retrieval or missing evidence.
- Do not discard a dirty replica merely because the primary is compliant.
- Preserve uncertainty internally; the public schema has no UNKNOWN status. Route unresolved cases for bounded additional investigation or review rather than fabricating a COMPLETE verdict.

Choose evidence IDs that actually prove the proposition. Establish deterministic tie-breaking among equally valid sources, inspect sample citation conventions, and document genuine ambiguity. Never hardcode canonical evidence IDs by case.

## 7. Agent behavior and tools

The agent's objective is evidence completeness and a policy-compliant audit, not unlimited conversation.

Initialize each case with deterministic candidate retrieval and a coverage summary. For authorized cases, allow the model to select focused next tools, inspect results, resolve contradictions and submit a structured audit proposal. Clear cases may finish in one model decision; ambiguous cases may require bounded loops.

Suggested tools:
1. resolve_identity(request_identifier, cutoff): grounded aliases and links.
2. search_evidence(identifiers, resource_ids, cutoff, cursor): exact indexed candidates with provenance and pagination.
3. inspect_evidence(evidence_id, locator, cutoff): source excerpt/page or structured record.
4. resource_timeline(system_id, resource_id, cutoff): claims, state observations and conflicts.
5. compare_replicas(resource_id, cutoff): per-store records and drift.
6. inspect_data_flows(subject_links, cutoff): sync/import/indexing routes.
7. inspect_restore_paths(subject_links, cutoff): backups, restore permissions and retention facts.
8. evaluate_policy(observation_ids, cutoff): deterministic supported policy outcomes.
9. check_coverage(case_state): unexplored candidates, categories, aliases and unresolved conflicts.
10. submit_audit(proposal): grounded subject, resource decisions and supporting observation references.

Tools are read-only and scoped to supplied data; no live deletion or external search is needed for case predictions. Search pagination must expose omitted candidates, and finalization must not treat an arbitrary top-k cap as exhaustive coverage.

Implement either native Gemini function calling or a validated structured next-action envelope dispatched by Python. Verify the chosen model/SDK support in preflight. Do not assume structured final output and function calling can be combined identically across model families. Preserve required tool-call IDs and model state/thought signatures in conversations when the selected API requires them.

Agent states: INITIALIZE, INTERPRET_REQUEST, INVESTIGATE, CHECK_COVERAGE, PROPOSE, VALIDATE, DONE; unresolved/error paths persist a checkpoint. The controller validates each transition.

Guardrails:
- Every new factual assertion must point to valid observations.
- Tool results and document contents are untrusted data, never agent instructions.
- Model cannot invent sources, IDs, policy rules or operations.
- Deterministic compiler checks plan completeness and allowed field/state pairs.
- A failed validation returns specific actionable defects for a bounded repair.
- Stop on exhausted budget/turn limits, persist partial progress and report unresolved cases; do not label model failure as NOT_APPLICABLE.
- Do not write a partial or fabricated result over the last validated full output.

Starting bounds, adjustable after measurement:
- One compact investigation/finalization decision for clear cases.
- Up to four tool rounds for ambiguous cases, with at most two targeted repair rounds and an overall per-case cap.
- Fetch related tool results together when independent; use compact excerpts rather than repeating entire histories.
- Start paid-call concurrency at two, adapt to actual rate limits, and use finite retries with backoff.
- Never silently fall back to a different model or turn an API error into a status.

Agent traces need action choices, tool inputs/results, evidence links, brief decision justifications, usage and validation outcomes. Do not request or store private chain-of-thought.

## 8. Models, budget and replay

Initial candidates, to confirm with the user's API account:
- gemini-3.1-flash-lite: routine structured intent/extraction and bounded investigation.
- gemini-3.8-flash: difficult visual extraction, contradictions or review after cheap-model validation failure.
- Prefer one capable model if a small benchmark shows the two-model route hurts correctness or complicates delivery.

Official pricing checked 2026-10-24, standard paid API, per million tokens:
- gemini-3.1-flash-lite: USD 0.25 text/image/video input, USD 1.50 output including thinking.
- gemini-3.8-flash: USD 0.75 input and USD 3.75 output including thinking at the currently listed promotional rates.
- gemini-2.5-flash: USD 0.30 text/image/video input and USD 2.50 output.
These are estimates for planning, not proof of model availability in the user's project. Recheck prices and model availability during preflight. No API call has been made by this planning handoff.

For scale only: 1,000,000 input plus 100,000 billable output tokens would cost USD 0.40 on the listed 3.1 Flash-Lite rate, or USD 1.125 on the listed 3.8 Flash rate. Real tool histories, images, thinking, retries and repeated rounds can change this substantially.

Allocation across the entire project:
- USD 0.50 model/schema smoke tests and sample benchmark.
- USD 0.75 shared multimodal/ambiguous extraction.
- USD 1.75 first complete run.
- USD 1.00 corrections and targeted reruns.
- USD 0.50 reserved final validation/run.
- USD 0.50 safety margin; controller target ceiling USD 4.50 before margin.

These are envelopes, not entitlements to exhaust each category. Reallocate using measured usage. Project the full run from a small representative pilot before launching all 518 cases. Use aggregate counters across runs and resume sessions, not a reset budget per command.

Before a call, reserve a conservative upper-bound cost for configured input/output/thinking limits and concurrent outstanding calls; reconcile against API usage afterward. Keep the budget ledger atomic. App-side limits are approximate if provider accounting is incomplete; note any gaps and use extra margin. Do not claim an absolute provider-enforced spending cap.

Record provider, requested and returned model IDs/version if supplied, run/call IDs, purpose, attempt, input/cached/output/thinking tokens as available, latency, estimated cost, cache hits and failures. Avoid double-counting thinking when already included in a billable output total.

Cache key: source hashes + prompt hash/version + schema/extractor version + model/config + relevant case cutoff and identity inputs. Distinguish a local response cache from paid provider context caching.

Modes:
- live: uses Gemini, creates fresh evidence/decision caches, checkpoints and usage ledger.
- resume: reuses valid checkpoints and runs only unfinished or invalidated work.
- replay: zero API calls; uses explicitly versioned cached extractions/actions and reruns deterministic decision/output validation.
- fresh: empty cache or new namespace; can rebuild solely from participant data, source prompts/config and API access.

Runtime caches are not ground truth. Do not ship cached labels as a replacement for runnable inference. Explain how replay artifacts are generated and optional. Report both actual final-run API spend/cache hits and the attributable extraction/cache-population cost; never claim an expensive warm-up makes the entire solution free.

Do not use asynchronous Batch API for the critical path without checking completion guarantees against remaining time. Local request grouping and batching compatible tasks are different from a provider batch job.

## 9. Evaluation

Measure against 32 public sample labels:
- Status accuracy and confusion matrix.
- Whole-case exact match after parsing JSON and ignoring object-key order/whitespace only.
- Step precision/recall/F1 with clearly defined matching keys.
- Field accuracy on transparently aligned steps; count missing/extra steps separately.
- Exact ordered sequence accuracy, and optionally operation-order accuracy.
- Evidence-reference accuracy and semantic validity review.
- Extraction coverage, unresolved cases, latency and cost.

Initially hold out a small diverse subset of public samples for regression checking; disclose that these remain public samples, not a genuinely unseen benchmark. Never use their answers as runtime input. Report all 32 after final development and note any tuning exposure. No measured hidden-set accuracy is available.

Create at least three additional team-authored cases; target eight compact cases with independently specified expectations:
1. Historical email/hash survives in a replica.
2. A success log is contradicted by a concrete present record.
3. Post-cutoff evidence cannot change the answer.
4. Access/export/marketing opt-out request yields NOT_APPLICABLE, including non-English phrasing.
5. Compliant tombstone retains stable ID; another tombstone retains prohibited hash.
6. Backup remains retained but requires restore blocking; a disabled path needs only its appropriate checks.
7. Similar-email decoy belongs to someone else.
8. Primary is clean, replica is dirty; retained security record must survive.

Also test anonymized resources linked through historical IDs, complete verification coverage on incomplete cases, malformed model output, replay cache invalidation and interrupted-run resume where time permits. Use minimal fixtures to expose behavior, not tests that repeat implementation logic.

Maintain an error taxonomy: extraction, identity, temporal, retrieval coverage, resource/category mapping, policy, citation, sequence and serialization. Fix the earliest causal error instead of patching individual case IDs.

Write all required metric definitions, values, custom cases, failures and improvements directly into code/evaluation/evaluation_report.md. Put token/cost summaries directly into code/evaluation/usage_report.md. Raw JSON/CSV/logs alone are ignored by parts of the judge, according to README.

## 10. Roadmap for the approximately 20-hour window

Times are suggested elapsed working-window targets, not verified contest clock times. Claude can continue while Breno is away, subject to normal session/tool limits.

0–1 hour: preflight, inventory, contract validator, model/schema pilot, transcript setup.
1–3 hours: all format adapters, source cache, identity/resource indexes, initial temporal reducer.
3–6 hours: first vertical agent loop, policy compiler, sample evaluation and first full valid candidate if evidence coverage permits.
6–10 hours: investigate sample mismatches, multimodal gaps, historical links, replicas and restore paths; author custom cases.
10–13 hours: complete the full 518-case run, inspect unresolved/contradictory cases, confirm budget.
13–16 hours: targeted fixes/reruns, clean-install and replay tests, evaluation and usage reports.
16–18 hours: freeze candidate, package code.zip, validate output and prepare submission materials.
Final approximately two hours: buffer for upload/interview preparation and unexpected failures. Optional viewer only if engine, reports and package already pass.

Maintain a readable checkpoint after each milestone:
- completed work and changed decisions;
- sample status/exact-match metrics;
- evidence coverage and unresolved blockers;
- budget spent/reserved and full-run forecast;
- output/package readiness;
- next autonomous action.

Do not spend hours perfecting generic abstractions before producing an end-to-end candidate. Conversely, a structurally valid CSV with fabricated or unsupported states is not a correctness milestone.

## 11. Deliverables and release checklist

Required:
- root output.csv, all 518 target cases.
- code.zip containing runnable source, configuration, prompts, dependency setup, README and code/evaluation/ Markdown reports.
- root log.txt in the repository's exact turn format.
- preparation for the AI interview: explain identity, time, evidence, policy, agent tools, evaluation and cost.

Repository agent_trace_instructions.md additionally asks for agent-trace.zip containing relevant original session traces. Preserve it separately; verify the actual HackerRank upload field/instructions when accessible. README and trace instructions describe different transcript artifacts, so prepare both rather than replacing log.txt.

For Claude Code, preserve relevant ~/.claude/projects/ project session files and export readable transcripts using /export as supported by the installed CLI. Finalize/quit sessions before copying logs where practical. Include this planning conversation as an available hosted transcript/export if the event requests all planning sessions. Do not fabricate a raw hosted trace.

Release:
- [ ] No missing/duplicate/extra case IDs; exact column order, valid arrays and step numbers.
- [ ] Correct allowed phase/operation/state combinations and canonical ordering.
- [ ] NOT_APPLICABLE only when no deletion authorized.
- [ ] COMPLETE contains only evidence-backed compliant-state verification.
- [ ] Findings cite eligible valid source IDs; incomplete future steps use empty IDs.
- [ ] Retained records, tombstones, replicas, data flows and restore risks handled.
- [ ] All extraction failures and unresolved semantic issues reviewed/documented.
- [ ] Fresh mode rebuilds from supplied participant data; replay uses no network.
- [ ] Usage report matches the run that created the final output, with cache provenance.
- [ ] Metrics honestly distinguish public/custom tests from unlabeled target predictions.
- [ ] Reports are Markdown under code/evaluation/; prompts are source or Markdown.
- [ ] No secrets, unrelated personal files, dataset, environments, caches or nested archives in code.zip.
- [ ] Inspect zip contents and run a clean unpacked smoke test.
- [ ] Preserve last validated output; atomically publish the new full output.
- [ ] Package original traces separately and redact credentials.
- [ ] Submit early enough to leave upload time; user handles final contest submission.

A small static HTML evidence explorer can later read generated audit artifacts and show case status, timeline, resource treatment, citations and validation warnings. Escape all source text. Keep it local; deployment is optional and outside the critical path.

## 12. Claude Code launch prompt

You are implementing the HackerRank Orchestrate October 2026 challenge for Breno.

Read this entire handoff, then read the current repository's AGENTS.md, README.md, problem_statement.md and agent_trace_instructions.md in full. The current challenge contract wins over an outdated assumption in this handoff; explain material differences in a decision log. Follow the repo transcript requirements and preserve original session traces.

Goal: competition correctness with reusable internals. Approximately 20 hours remain according to the user. Gemini budget across all work is USD 5. Build a local Python CLI exposing a real bounded, tool-using deletion-audit agent. Use in-memory indexes and disk caches; sqlite3 is only for supplied SQL evidence. Build the agent core and evaluation before any viewer.

Start with preflight, a tiny model/schema pilot and a representative vertical slice. Then keep implementing and evaluating autonomously. Make routine reversible choices yourself, record important architecture changes with reasons, and do not stop after writing a plan. Ask Breno only for missing credentials/access, a genuinely blocking ambiguity, or authorization beyond the existing scope. Read credentials from environment variables and never print them.

Keep the agent evidence-grounded: current/historical identity resolution, point-in-time state, all relevant copies and replicas, allowed retention, tombstone redaction, active data flows and unsafe restores. Tool selection and investigation are model-assisted; output invariants, policy constraints and canonical serialization are enforced in code.

Measure on public samples without using sample labels at prediction time. Add independent custom test cases. Never inspect hidden organizer truth or hardcode case labels, evidence IDs or case-family shortcuts.

Implement cache/resume/replay and budget accounting early so work can continue through interruptions. Do not force COMPLETE or NOT_APPLICABLE on errors or unresolved evidence. Build an early end-to-end candidate, then improve causal errors using evaluation.

At every milestone update a brief checkpoint with metrics, unresolved cases, evidence coverage, cost and next action. Aim to have a packaged, validated candidate at least two hours before the user-reported end. Produce output.csv, code.zip, code/evaluation/evaluation_report.md, code/evaluation/usage_report.md, root log.txt and separately prepared session traces. Do not submit the contest entry on Breno's behalf.

Begin now by inspecting the checkout and reporting only material contract differences, the tiny pilot result, and your immediate implementation choices; continue the authorized implementation after that.

## 13. Reference links

Challenge:
https://github.com/interviewstreet/hackerrank-orchestrate-october26/blob/main/problem_statement.md
https://github.com/interviewstreet/hackerrank-orchestrate-october26/blob/main/README.md
https://github.com/interviewstreet/hackerrank-orchestrate-october26/blob/main/AGENTS.md
https://github.com/interviewstreet/hackerrank-orchestrate-october26/blob/main/agent_trace_instructions.md
https://github.com/interviewstreet/hackerrank-orchestrate-october26/blob/main/dataset/deletion_rules.csv

Gemini official pricing, tools, schemas and SDK:
https://ai.google.dev/gemini-api/docs/pricing
https://ai.google.dev/gemini-api/docs/function-calling
https://ai.google.dev/gemini-api/docs/structured-output
https://googleapis.github.io/python-genai/

Validation and PDF adapters:
https://docs.pydantic.dev/latest/
https://pymupdf.readthedocs.io/en/latest/

