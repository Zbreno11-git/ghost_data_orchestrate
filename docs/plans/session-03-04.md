# S3+S4 merged (A19), executed one at a time — deterministic baseline, then the agent

> The approved overall plan is frozen at `docs/plans/MASTER_PLAN.md` (§S3, §S4). This file plans only the merged
> S3+S4 session. Its first deliverable on disk is `docs/plans/session-03-04.md` (skill format: checkpoint map,
> then Does / ✅ / 🐞 per checkpoint), carrying this content. C3.1–C3.5 all close before C4.1 starts.

## Context

S1+S2 delivered a proven contract/validator/evaluator and one EvidenceStore holding 7,604 provenance-carrying
observations from all 94 files. Nothing decides a case yet.
- **S3** turns the store into a grounded, no-LLM answer for every request: identity → cutoff → ownership →
  policy → planner. It gets measured on the 32 samples, and it also produces a 518-row target output that
  validates. That output is a $0 fallback long before the safety package.
- **S4** puts a bounded, tool-using Gemini investigator on top of it. A single gateway handles budget, cache,
  resume and replay, and the agent is measured against S3's baseline.

**Spend:** S3 $0; S4 ≈ $0.30 (envelope), with the ledger hard stop at $4.50.
**Owner input during the session:** none. The user said to run every checkpoint through C4.6 without asking.

## Opening measurements (2026-10-24 20:24 UTC — the disk agrees with the resume block)

| Check | Result |
|---|---|
| `git status --short` / HEAD = origin/main | empty / both `d900b87` ("Checkpoint before compact (S3+S4 next)…") |
| `main.py status` | settled $0.107400, outstanding $0.000000, 54 rows |
| `pytest code/tests -q` | `78 passed` |
| `code/ghostaudit/` | no `identity.py` (as expected) |

**Probes run during planning** (read-only scratchpad scripts on the samples; tuning exposure is disclosed in the
evaluation report):
- **Explicit identifier links.**
  - Method: an admissible observation whose fields or wrapper contain a normalized identifier of the subject
    (identities plus audit history).
  - Result: **75/111** gold resources, **3 extras** (object_19, account_6523, tombstone_17).
  - What is missed: ~22 accounts, ~8 already-anonymized analytics records (unlinked by construction) and ~7
    audit records.
- **Workflow window.**
  - Method: `deletion_worker` activity rows in [requested_at, reported_at].
  - Result: only 44/111 gold resources, with 539 extras. The rows of each case's workflow cluster
    ~0.75–1.25 h before `reported_at`, interleaved with other cases.
  - Picking the account_service row nearest `reported_at` matches the gold account in 14/32 cases.
  - The worker's `reported_result` tracks the request's `reported_status` (COMPLETE↔SUCCESS,
    NOT_STARTED↔FAILED, PARTIALLY↔PARTIAL).
- **Ceilings**, each a new discrepancy row:
  - 16 gold resources have no evidence other than an activity row;
  - `account_004` appears **only** in sample_output, making it unobservable like D10;
  - 6 gold resources have only post-`audit_at` evidence (`account_3960` and audit records 4902, 4128, 7095,
    3954, 1707). AGENTS §6.2 forbids naming them from that evidence, although `account_3960` is still named by
    its admissible activity row.
- **System id ≠ source container.** `support_002` is observed in `support_replica` but answered as
  `support_platform`; the activity row's `target_system` names the canonical system.
- **Citations.** COMPLETE cases cite the latest admissible comprehensive snapshot (case_28 cites evidence_92;
  the later evidence_02 is ignored).
- **`RESOURCE_RE`** has 14 prefixes but misses `email_delivery_` (368 activity rows), `tombstone_` and
  `object_`, and it carries 3 that never occur. Fix: derive the prefix set from the data.
- **SDK.** `google.genai.errors.ClientError` (4xx) and `ServerError` (5xx) carry `.code`, so S4's settlement
  policy can tell "rejected" from "maybe billed".

## Sample patterns (from the S1+S2 resume block, measured 2026-10-24 20:16 UTC on sample_output.csv)

These are the targets the planner's step-set rules must reproduce; they are measurements on evaluation labels, used to design rules, never read on the prediction path.

- **Account:** 32/32 cases verify the account_service account ABSENT.
  - When the account still exists (3 cases): REPORT_REMAINING_RECORD → DELETE_RECORD → VERIFY_RECORD_ABSENT.
  - Otherwise there is only the verification: cited in COMPLETE cases, `""` in INCOMPLETE ones.
- **Retained audit record:** 24/32 cases have VERIFY_RECORD_PRESENT on a security_service `audit_record_*` (rule_12
  RETAIN). Cases 01, 02, 04–08 and 10 have none.
- **Ops per system** (findings / remediation / verification):

  | System | Findings | Remediation | Verification |
  |---|---|---|---|
  | search | 12 REMAINING | 12 DELETE | 12 ABSENT |
  | analytics | 5 EXPOSED_PII | 5 ANONYMIZE | 12 ANONYMIZED |
  | support | 5 EXPOSED_PII | 5 REDACT | 8 REDACTED |
  | integration | 6 ACTIVE_DATA_FLOW | 6 DISABLE | 9 DISABLED |
  | backup | 3 RESTORE_RISK | 3 BLOCK | 6 BLOCKED |
  | export | 2 REMAINING | 2 DELETE | 2 ABSENT |
  | identity_service `tombstone_*` | 1 EXPOSED_PII | 1 REDACT | 2 REDACTED |

  Exceptions:
  - case_12 analytics_9914: REMAINING → DELETE → ABSENT (likely a marketing/contact profile: `contact_lookup_completed
    email_opt_in`, rule_10 DELETE).
  - Support: 3 cases go REMAINING → DELETE → ABSENT, all subject-only attachments/records (rule_06): case_07 PDF
    `evidence_58`, case_10 `support_replica.log` `evidence_61`, case_13.
- **INCOMPLETE verification set** = account ABSENT + audit PRESENT (if any) + one verification per remediated resource,
  all with `""`.
- **COMPLETE** = verification of every relevant resource, each citing proof:
  - an analytics record that is already anonymized gets VERIFY_RECORD_ANONYMIZED;
  - a connector already disabled gets VERIFY_DATA_FLOW_DISABLED;
  - a backup with `restore_allowed=false` gets VERIFY_RESTORE_BLOCKED;
  - support already redacted gets VERIFY_RECORD_REDACTED.
- **Citations:** 31/32 cases cite exactly one file for all steps (the comprehensive latest admissible snapshot:
  `evidence_92`/`94`/`51`/`54`/`03`/`01`/`05`). case_04 cites two (`evidence_54` account, `evidence_56` analytics report).
  Hypothesis for S3: "latest admissible file that covers the resource's state".
- **Gap:** `evidence.RESOURCE_RE` lacks `tombstone_`, so free-text mentions of tombstones are not indexed (record
  resource_ids still are). Add it in S3.

## Design — S3 (one module per concern, all pure and importable by tests)

Reused:
- `evidence.EvidenceStore` / `normalize_identifier` / `identifiers_in`;
- `ingest.pipeline.ingest_all`, `ingest.csv_tables.load_tables`;
- `contract.OPERATIONS` / `evidence_required`, `serialize.canonical_sort` / `dumps` / `write_output_csv`;
- `validate.validate_row` / `validate_file`, `ingest.manifest.evidence_times`, `evaluation/metrics.evaluate`.

- **`evidence.py` fix (first, C3.1 prerequisite):**
  - `RESOURCE_RE` is built from the resource-id prefixes in `system_activity.resource_id` plus record
    `resource_id`s seen at ingest, so it is derived rather than hand-listed.
  - Test: every prefix in the activity column is matched.
  - The ingest recall gate must stay green (75/75 citations).
- **`identity.py`: `resolve(email, tables, audit_at) → Subject | Ambiguity`.**
  - Builds the fixed point over the identities snapshot plus the audit log (email, phone, email_hash; only
    `event_time ≤ audit_at`).
  - Email matching is case-insensitive; phones match by digits. Matches are **exact normalized** only: no
    fuzzy or prefix matching.
  - If `email_hash == sha256(lower(email))` holds on the snapshot (measured in the test), it derives hashes
    for historical emails.
  - An email that maps to two user_ids is an Ambiguity, which becomes unresolved and never a guess.
  - Each identifier records its role: current vs historical.
- **`temporal.py`: `CaseView(store, audit_at)`.**
  - It is the only way the engine and the tools read the store. It exposes `by_resource`, `by_identifier`,
    `by_source` and `observations`, minus every observation captured after `audit_at` (inclusive cutoff).
  - Activity and audit rows are filtered on their event time.
- **`ownership.py`: `link(subject, view, requests) → {resource_id: Link(tier, reasons[obs_id…], system_id)}`.**
  - **explicit:** a subject identifier is in the fields or wrapper of an admissible observation, or a
    `LINK_RESOURCE_IDENTITY` catalog row names the subject.
  - **workflow:** the request's deletion-workflow run.
    - Anchors: the worker rows of the explicitly linked resources, plus the account_service "primary
      profile" row.
    - The run is matched to the request on time before `reported_at` and on result consistency with
      `reported_status`.
    - Matching is a **one-to-one assignment over all requests** (samples + targets; both are participant
      files), so a row claimed by one request can't be claimed by another.
    - The run supplies the account id and the already-clean resources that have no subject link.
  - **excluded:** a resource explicitly linked to a *different* subject (the case_28 decoy) is never owned.
  - **Modes:** `strict` = explicit links plus a unique workflow anchor; `scored` = the best candidate (A5,
    decided in S6).
  - The canonical system_id comes from the activity `target_system` or the source's system, never from a
    replica container name.
- **`policy.py`.**
  - `RULES` is loaded from `deletion_rules.csv`; `category(resource, obs)` maps to a data_category with an
    explicit reason (search → SEARCH_INDEX_ENTRY, support message vs subject-only attachment, analytics vs
    marketing/contact profile, export, tombstone, security audit, backup, data flow, account).
  - `state(resource, view)` takes the latest admissible observation of the resource and returns one of
    ABSENT, PRESENT_EXPOSED, PRESENT_CLEAN, REDACTED, ANONYMIZED, ACTIVE, DISABLED, RESTORABLE, BLOCKED or
    UNKNOWN, together with the proving obs_id.
    - Absence is a lookup NOT_FOUND, or a scope that covers the system without the row.
    - **Only `fields` count as exposure (FR-11).** Activity and claims never set a state.
  - `assess(...)` returns compliant, violation (with the finding op) or unknown.
- **`planner.py`.** Typed `ResourceDecision`s become contract steps:
  - **INCOMPLETE** (any violation):
    - findings cite the proving source_id;
    - one remediation per violated resource;
    - verification of the account ABSENT, every retained record PRESENT, and every remediated resource;
    - remediation and verification steps use `""`.
  - **COMPLETE:** a cited verification for every relevant resource.
  - **NOT_APPLICABLE:** `[]`.
  - **Citation rule:** the latest admissible observation proving that resource's state; it is measured in C3.5
    and recorded in DECISIONS.
  - Steps are canonically sorted, and every row goes through `validate_row` before it is emitted. A row that
    fails validation or contains an `unknown` is flagged unresolved (A10).
- **`intent.py` (deterministic half of C4.4).**
  - A multilingual keyword and negative-pattern classifier (access, export, correction, marketing opt-out
    → NA) with a confidence value.
  - S4 adds the LLM half; a disagreement becomes a recheck.
- **`runner.py` + `main.py run --engine deterministic --split samples|targets [--ownership strict|scored]`.**
  - Writes `runs/<run_id>/{output.csv, decisions.jsonl, unresolved.md, summary.json}` atomically.
  - **Never writes the root `output.csv`.** Publishing is an S5/S7 step.

## Design — S4

- **C4.0, first step (carried from S2): the 4xx settlement policy**, after reading the `integracoes` skill.
  - `ClientError` 400/401/403/404 means the request was rejected before generation: settle at $0 with
    `cost_basis="rejected_<code>"`, no retry.
  - 429: settle at $0, then a bounded backoff retry.
  - `ServerError`, timeouts, network errors and anything unknown: settle at the reservation (conservative,
    as today).
  - Tested with a fake provider raising each class. Recorded as A20.
  - The ledger stays append-only: the old $0.0176 row stands and gets explained in the usage report.
- **`llm/gateway.py`** (C4.1) is the only paid path, wrapping `gemini.Gemini`.
  - Reserve → call → settle; finite retries by error class; no silent model fallback (a model is a config
    value).
  - A `BudgetExceeded` refusal means no call and an unresolved case, never a status.
  - **`llm/cache.py`** keys responses on sha256(model, contents, config). The cache lives in gitignored
    `runs/cache/` and stores the raw response, the thought_signature Content and the usage. It is the basis
    for replay.
- **`tools.py`** (C4.2): functions over `CaseView` that return JSON with obs_ids:
  - `resolve_identity`, `search_evidence` (paginated, with an omitted count), `inspect_evidence`;
  - `resource_timeline`, `compare_replicas`, `inspect_flows_restores`;
  - `evaluate_policy`, `check_coverage`, `submit_audit`.
  - A registry gives the declarations to Gemini.
- **`agent.py`** (C4.3), a bounded state machine.
  - Inputs: a brief built from `code/prompts/investigator.md`, the request, the subject, the deterministic
    proposal with obs_ids, and the open questions (ambiguous links, unknown states).
  - Loop: at most 4 tool rounds, then `submit_audit` (per-resource include/exclude/state plus cited obs_ids),
    then deterministic validation. Only obs_ids returned by tools in this session are accepted, and only legal
    decisions.
  - At most 2 repairs. On failure the case gets the deterministic proposal and an unresolved flag.
  - The model Content is appended unchanged (thought_signature).
  - The planner compiles the steps; the model never writes JSON steps.
- **`intent.py` LLM half** (C4.4): batched JSON-schema classification (~20 requests per call) plus the keyword
  cross-check, and a per-case recheck when they disagree.
- **Runner** (C4.5):
  - `--engine agent` writes a per-case checkpoint `runs/<id>/cases/<case_id>.json` atomically, and resume
    skips finished cases.
  - `--mode replay` serves calls from the cache only; a miss is an error, never a call.
- **Benchmark** (C4.6): 10 diverse samples × {3.1-flash-lite, 3.8-flash}, comparing metrics and $/case against
  the S3 baseline. The pick and the A7 trigger outcome are recorded in DECISIONS. If agent == baseline, that is
  written down honestly.

## Checkpoints (command → expected number)

| C | Does | ✅ Closes when | 🐞 Predicted → Debug |
|---|---|---|---|
| C3.0 | derive `RESOURCE_RE` | test: every activity resource prefix (14 measured) matches; `pytest code/tests/test_ingest.py` still green (75/75) | new mentions create duplicate by_resource entries → dedupe per obs |
| C3.1 | identity fixed point | `pytest code/tests/test_identity.py`: case_10 resolves `nadia.ionescu@yahoo.com` → user_10 with current + historical; case_12 old address + hash → user_12; case_28 decoy resource not linked; the sha256 rule holds on N/N snapshot rows (or is not used) | audit rows after audit_at leak → filter on event_time |
| C3.2 | cutoff in the tool layer | test: for every public accessor of `CaseView` (derived by introspection), an observation captured 1 s after audit_at is invisible and one exactly at audit_at is visible; the 6 post-audit-only gold resources measured and recorded (D12) | activity rows filtered on the wrong clock |
| C3.3 | ownership tiers + modes | `main.py run … --report-ownership`: recall/precision vs gold resources on samples, per tier and per mode (baseline explicit 75/111 with 3 extras); the case_28 decoy excluded in both modes | interleaved workflows mis-assign accounts → the one-to-one assignment; report the unresolved rather than guess |
| C3.4 | policy registry + state | `pytest code/tests/test_policy.py`: 15/15 rules mapped (derived from the CSV); tombstone with only subject_reference → compliant, with email_hash → REPORT_EXPOSED_PII; a retained security record → VERIFY_RECORD_PRESENT; wrapper-only email → not exposed; activity SUCCESS + present record → violation | category ambiguity (support message vs attachment; analytics vs marketing) → explicit reason field; unknown never defaults |
| C3.5 | planner + run | `main.py run --engine deterministic --split samples` → 32 rows, `main.py validate … --split samples` → 0 violations; `--split targets` → 518 rows, 0 violations, unresolved count reported; `evaluation/main.py --pred runs/<id>/output.csv` metrics recorded in DIARY as the baseline next to the ceiling (D10 + account_004 + D12); 3 custom cases scored | citation choice differs → measure "latest admissible proving file" and record the rule |
| C4.0 | 4xx settlement | `pytest code/tests/test_gateway.py -k settle`: 400 → $0 `rejected_400`; 429 → $0 + retry; 500/timeout → reservation | the SDK wraps errors differently than read → test with the real class constructor |
| C4.1 | gateway | test: a fake provider over budget is refused before sending; 8 threads reserving concurrently never exceed the ceiling; grep: `generate_content` appears only in `llm/gemini.py` | — |
| C4.2 | tools | `pytest code/tests/test_tools.py`: one test per registered tool (derived from the registry); cutoff enforced in each; pagination omitted counts are correct | — |
| C4.3 | agent live | one sample case live: trace shows ≥1 tool call → submit_audit → a validated canonical row; ledger rows settled | the model paraphrases the proposal → tool-choice stats in the trace |
| C4.4 | intent | 32/32 samples → deletion; ≥3 NA phrasings (incl. non-English) → NOT_APPLICABLE; batch cost in the ledger | — |
| C4.5 | resume + replay | kill mid-run, then resume → 0 duplicate successful calls by request hash; `GEMINI_API_KEY= main.py run --mode replay` → `cmp` byte-identical output.csv | a nondeterministic dict order in the request → sort keys before hashing |
| C4.6 | benchmark | 10 samples × 2 models: metrics and $/case table in DIARY; pick in DECISIONS | — |

**Mutation proofs (testes-que-provam §3)**, each run once, restored, then `git diff` checked empty:
1. prefix email match in identity → the decoy test goes red;
2. drop the CaseView filter → C3.2 goes red;
3. count wrapper identifiers as exposure → the FR-11 policy test goes red;
4. let activity SUCCESS set the state → the contradicted-claim test goes red;
5. settle 5xx at $0 → the C4.0 test goes red.

## Execution order

1. Append the log.txt entry for this turn. Write `docs/plans/session-03-04.md`.
2. Record D12 (post-audit-only resources), D13 (account_004 unobservable) and the planned A20 placeholder; add
   a PRIMER boundary for "naming from post-audit evidence is forbidden".
3. C3.0 → C3.5, committing after each closed checkpoint (explicit paths only).
4. **Close S3** with the ritual:
   - read the gates literally;
   - two review passes with different questions;
   - update DIARY (baseline), PROGRESS, SESSIONS, STATUS and REQUIREMENTS_MAP;
   - commit with the *why*, push, and check CI by headSha.
5. Read the `integracoes` skill. Then C4.0 → C4.6 (paid steps C4.3, C4.4, C4.6 are ledgered; check
   `main.py status` before and after each).
6. **Close S4** with the same ritual, plus the benchmark decision in DECISIONS.

## Verification (end of S3, then end of S4)

```bash
.venv/bin/python -m pytest code/tests -q                                       # all green, 0 skipped
.venv/bin/python code/main.py run --engine deterministic --split samples        # 32 rows → runs/<id>/
.venv/bin/python code/main.py validate runs/<id>/output.csv --split samples     # 0 violations
.venv/bin/python code/main.py run --engine deterministic --split targets        # 518 rows, unresolved count
.venv/bin/python code/evaluation/main.py --pred runs/<id>/output.csv            # baseline metrics
GEMINI_API_KEY= .venv/bin/python code/main.py run --engine agent --mode replay --split samples   # byte-identical
.venv/bin/python code/main.py status                                           # ledger ≤ $0.41 cumulative
git status --short; git rev-parse HEAD origin/main                             # clean; equal
```

## Risks

- **Overfitting to 32 samples.** Ownership and citation rules are measured on the samples, and the exposure is
  disclosed. No case ids, evidence ids or labels appear in code; the sample_output grep test stays.
- **Workflow attribution is the weakest link.** The one-to-one assignment can mis-assign under concurrency, so
  it is reported per tier and the ambiguous rows go to the agent (S4) and to unresolved.md, never guessed.
- **Spend.** It is confined to C4.3, C4.4 and C4.6, all through the gateway with the $4.50 hard stop. If S4
  overruns, S3's validated 518-row deterministic output remains the fallback.
- **Public repo.** Stage explicit paths only. `runs/` (cache, traces) stays gitignored.
