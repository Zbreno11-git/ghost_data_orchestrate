# Ghost Data — Vision, Specifications and Requirements
Version: 1.0 · Prepared 2026-10-24 · Companion to GHOST_DATA_CLAUDE_HANDOFF.md and GHOST_DATA_BACKEND_GUIDE.md

## 1. Purpose and document roles

Northstar Shop believes it deleted a customer's data, but identifiers survive in secondary systems and a synchronization process can recreate deleted information. The challenge is to audit actual data state rather than repeat the deletion workflow's reported status.

Build an AI-powered deletion-audit agent that answers:
1. Did this person authorize deletion?
2. Which current and historical identifiers belong to this person?
3. Which relevant records and data-recreation paths exist at audit_at?
4. What treatment does the supplied policy require?
5. Is deletion complete, and what evidence or ordered plan supports that answer?

The goal is competition correctness with reusable internals. This version is an offline evidence audit of supplied fictional records; the remediation steps are proposed actions, not actual mutations of live business systems.

Document roles:
- This document: what success means, required behaviors, scope and acceptance checks.
- GHOST_DATA_BACKEND_GUIDE.md: how to implement robustly and avoid common failure modes.
- GHOST_DATA_CLAUDE_HANDOFF.md: initial architecture, model/budget options, roadmap and detailed launch context.
- Current official challenge documents and policy: authoritative output/evaluation contract.

Read current official rules first. Keep a small discrepancy log if sources conflict. Model IDs, costs, inventory and the previously estimated remaining time must be rechecked at execution; they are not permanent requirements.

## 2. User goals, constraints and scope

Owner: Breno. Implementation will be driven by Claude Code, with Breno available intermittently. The initial reported remaining window was about 20 hours; recalculate the real remaining window before assigning sessions. Do not restart a 20-hour clock on every session.

Constraints:
- Up to USD 5 cumulative Gemini API spend across testing, extraction, retries and final runs.
- Local-first Python CLI; no application database required.
- In-memory indexes and file caches; temporary SQLite inspection of supplied SQL is acceptable.
- Both fresh/live inference and cached offline replay.
- Reusable modules, but no general-purpose platform build.
- Optional simple evidence explorer after the engine, tests and submission package work.
- Preserve development transcripts and original traces according to current instructions.
- Final contest submission remains with Breno.

Priority order:
P0: correct, grounded, point-in-time auditing and valid required deliverables.
P1: cost control, replay/resume, targeted evaluation and clear explanations.
P2: a small local viewer if release gates are already met.
Deferred: hosting, live company integrations, actual deletion execution, authentication, multi-tenancy, vector database and elaborate UI.

## 3. What “agent” means here

The agent maintains case state, chooses read-only investigation tools, observes results, follows grounded links, checks coverage and proposes a verdict. It may revisit evidence when contradictions or validation failures appear.

A successful trace can show why the agent inspected an old identifier, why it compared a replica, and why it blocked a restore path in its proposed plan. Clear cases may be short; not every case needs multiple tool calls.

Deterministic code is responsible for evidence eligibility, policy/output invariants and canonical serialization. The model is responsible for grounded language/multimodal interpretation and bounded investigation choices. Neither a free-form chatbot verdict nor case-specific rules meet the intended design.

No particular agent framework or cloud deployment is required by the inspected contract. Tool use is our chosen implementation approach to meet the investigation objective, not an additional official scoring criterion.

## 4. Inputs and evidence boundaries

Only participant-facing dataset/ data is eligible for prediction.

| Input | Purpose |
| --- | --- |
| deletion_requests.csv | Target cases that require output |
| sample_deletion_requests.csv / sample_output.csv | Public examples and evaluation labels |
| user_identities.csv | Current identity discovery |
| user_audit_log.csv | Historical identity changes |
| system_activity.csv | Global activity claims and operational evidence |
| deletion_rules.csv | Required category treatment and conditions |
| evidence_files.csv | Evidence paths, source origins and capture times |
| evidence/ | PDFs, PNGs, logs, JSON, text and SQLite-compatible SQL snapshots |
| dataset/output.csv | Blank format reference, not the final output destination |

Inspected baseline: 518 target cases, 32 public examples and 94 evidence files. Validate these on the actual checkout. Some sources contain unrelated records, decoys, multiple subjects or several timestamps.

Do not infer relevance from source names, sequence numbers or evidence manifest position. Do not access organizer truth, private generators or hidden labels. Do not feed public sample answers into runtime prediction.

## 5. Status semantics and evidence standard

NOT_APPLICABLE:
The request does not authorize deletion. Return [] and do not prescribe deletion or deletion verification. A request for access, correction, export or marketing opt-out is not automatically a deletion request. Mixed requests with an explicit deletion instruction need interpretation; do not reject them merely because another action is also mentioned.

COMPLETE:
All relevant copies have the treatment required by supplied policy at audit_at, required retained records remain, and no active process or unsafe restore path can recreate prohibited data. Emit only eligible evidence-backed verification.

INCOMPLETE:
Supported evidence shows remaining policy violations or recreation risks. Emit findings, complete permitted remediation and checks for the required final state. Preserve records required by supplied policy.

Uncertainty:
The public output schema has no UNKNOWN status. Keep uncertainty internal, investigate further and checkpoint unresolved cases. Missing evidence, a tool error or a budget limit is not proof of either compliance or a policy violation. Do not silently manufacture a final status to fill a row.

Evidence must establish ownership, resource state, time and policy relevance. A reported workflow status or SUCCESS activity alone does not prove the resulting state. A citation is valid only if it supports the specific emitted claim/check.

## 6. Functional requirements and acceptance checks

| ID | Requirement | Acceptance evidence |
| --- | --- | --- |
| FR-01 | Determine whether request_text authorizes deletion, including supplied languages and mixed requests | Deletion/non-deletion fixtures; NOT_APPLICABLE always has [] |
| FR-02 | Resolve current and historical identifiers to the correct subject | An old email/hash reaches grounded resources without merging a decoy |
| FR-03 | Discover relevant copies across supplied systems and formats | File inventory, candidate coverage and source-linked resource list |
| FR-04 | Determine admissible state at audit_at | Future evidence cannot change an earlier result; timestamps preserved |
| FR-05 | Separate workflow claims from observed state | A successful delete event contradicted by a present record remains a supported violation |
| FR-06 | Inspect replicas and preserve differences | A clean primary cannot hide a dirty relevant replica |
| FR-07 | Identify active sync/import/indexing paths that can recreate data | Relevant enabled process receives finding, disabling plan and check |
| FR-08 | Identify backup restore risks while respecting retention | Permitted archive remains; unsafe restore access is addressed |
| FR-09 | Apply deletion_rules.csv to each relevant record and condition | Delete/redact/anonymize/retain fixtures have correct outcomes |
| FR-10 | Preserve permitted tombstone references and remove prohibited identifiers | Stable-only tombstone passes; identifying email/hash does not |
| FR-11 | Distinguish audit wrappers from business fields | An anonymous record is not blamed for a subject label present only in wrapper metadata |
| FR-12 | Link anonymous/redacted resources through grounded lineage | Previously identifying resource can be found after identifiers disappear |
| FR-13 | Produce complete finding/remediation/verification sets | Incomplete case also includes relevant clean/retained final-state checks |
| FR-14 | Cite eligible evidence accurately | Every finding and COMPLETE check points to a proving participant ID available by cutoff |
| FR-15 | Enforce exact output schema and order | Validator rejects invalid phases/operations/states, steps, ordering and extra fields |
| FR-16 | Investigate using a bounded model/tool loop | Trace shows grounded tool choice, observations and validated proposal; limits enforced |
| FR-17 | Support fresh, live, resume and offline replay workflows | Fresh setup succeeds; interrupted work resumes; replay makes zero API calls |
| FR-18 | Evaluate on public and participant-created cases | Markdown reports show actual metrics, at least three custom cases and error-driven improvements |
| FR-19 | Account for model usage and cumulative project budget | Usage ledger covers extraction/retries/cache population and final run |
| FR-20 | Produce reproducible competition artifacts and transcripts | Clean unpack/run check, package inventory, log.txt and separately preserved traces |

These are solution requirements. They do not claim every edge case has a unique canonical interpretation; ambiguities must be inspected against the actual supplied sources and official contract.

## 7. Policy requirements

The actual deletion_rules.csv wins if it changes. The inspected policy requires:

| Category/condition | Required treatment |
| --- | --- |
| User profile, secondary identifier, search entry, cache, user export, marketing profile | Delete record |
| Support conversation with shared customer/agent/order context | Redact subject identifiers; preserve required context |
| Attachment belonging only to the subject | Delete attachment |
| Attributable analytics profile or product telemetry | Anonymize |
| Email delivery log containing user email | Redact |
| Security audit log within supplied retention | Retain |
| Legal-hold record under supplied active hold | Retain |
| Backup archive whose restore access can be blocked | Retain and handle restore restriction |
| Deleted-account tombstone needing stable internal reference | Redact direct identifiers; preserve permitted user_id |

Do not invent GDPR retention durations or apply a general “delete every user_id” rule. The supplied category and conditions govern whether a link is permitted.

Record presence alone is insufficient:
- A support conversation can remain while its subject identifiers must be removed.
- Analytics can remain only when no prohibited attribution survives.
- A hash can still be an identifier.
- A deleted account can have an allowed stable-only tombstone.
- A retained backup can still create an unsafe restore risk.

## 8. Output specification

Final destination: output.csv at repository root.

Exact columns:
case_id,deletion_status,steps_json

One data row for each of the 518 baseline target requests, no duplicates or extras, sorted by case_id. Confirm actual source contract at execution.

Each JSON object has exactly:
step_no, phase, system_id, resource_id, operation, state, evidence_id

Step numbers start at 1 and are consecutive. JSON object key order/whitespace are ignored; array order is significant.

| Phase | Ordered operations and required states |
| --- | --- |
| FINDING | REPORT_REMAINING_RECORD/PRESENT; REPORT_EXPOSED_PII/PRESENT; REPORT_ACTIVE_DATA_FLOW/ACTIVE; REPORT_RESTORE_RISK/ACTIVE |
| REMEDIATION | DISABLE_DATA_FLOW/DISABLED; BLOCK_RESTORE/BLOCKED; DELETE_RECORD/ABSENT; REDACT_RECORD/REDACTED; ANONYMIZE_RECORD/ANONYMIZED |
| VERIFICATION | VERIFY_RECORD_ABSENT/ABSENT; VERIFY_RECORD_PRESENT/PRESENT; VERIFY_RECORD_REDACTED/REDACTED; VERIFY_RECORD_ANONYMIZED/ANONYMIZED; VERIFY_DATA_FLOW_DISABLED/DISABLED; VERIFY_RESTORE_BLOCKED/BLOCKED |

Sort by phase order, operation order listed above, system_id ascending, then resource_id ascending. Assign step_no after sorting. Do not invent new operations or emit explanatory fields inside submission steps.

Citation rules:
- Findings cite valid file_id, activity_id or audit_id values.
- COMPLETE verification cites evidence proving the compliant state.
- INCOMPLETE proposed remediation and future verification use evidence_id="".
- NOT_APPLICABLE has no steps.
- A valid existing evidence ID is not enough: its content, subject, scope and time must support the assertion.

## 9. Behavioral scenarios for acceptance

A. Non-deletion request: the person asks only for a data export. Outcome NOT_APPLICABLE, [].

B. Historical identity: account uses email B, old log/profile uses email A. A grounded historical link makes both relevant. Remaining prohibited data under A is not ignored.

C. False completion: workflow says COMPLETE, but eligible direct evidence shows a profile. Outcome INCOMPLETE with supported finding, delete action and final-state checks.

D. Replica drift: primary is absent/redacted, replica still exposes prohibited data. Do not claim COMPLETE.

E. Retained records: security record qualifies for retention. It remains present and receives the appropriate final-state verification; do not delete it.

F. Tombstone: direct identifiers are removed but stable user_id remains for required references. This can satisfy the tombstone rule. A remaining email_hash can still violate it.

G. Recreation: account is gone but an eligible enabled connector can recreate it. Plan disables the flow before record-changing operation classes in the canonical output.

H. Restore: archive is retained but restoring the subject is still permitted. Plan blocks restoration and verifies it rather than destroying required records.

I. Temporal boundary: a later artifact shows a changed state. It must not alter an earlier audit unless the current official admissibility contract explicitly permits that evidence.

J. Anonymous resource: a resource loses personal fields but is connected through earlier resource lineage. Verify its actual anonymous state without treating only the external audit label as stored PII.

K. Partial failure: model request times out after other cases finished. Completed checkpoints survive; failed case resumes; no fake verdict fills the gap.

L. Retention edge: supplied evidence suggests a mandatory retained record is missing. Do not invent an unsupported restore operation or say COMPLETE; investigate and document the contract limitation.

These scenarios describe expected behavior, not hardcoded case templates for inference.

## 10. Nonfunctional requirements

| ID | Requirement | Acceptance check |
| --- | --- | --- |
| NFR-01 | Evidence traceability | Each decision can be followed to source and locator |
| NFR-02 | Deterministic compilation | Same validated replay inputs produce same ordered steps |
| NFR-03 | Honest uncertainty | Failures/gaps remain visible; no fabricated statuses or accuracy |
| NFR-04 | Budget discipline | Cumulative reservations and actual usage checked before calls |
| NFR-05 | Interrupted-run recovery | Resume avoids duplicate successful model calls |
| NFR-06 | Portable local execution | Documented clean Python setup works on supported machine |
| NFR-07 | Input isolation | Tool scope is participant data; document instructions cannot change agent policy |
| NFR-08 | Reusable internals | Parser, evidence, agent, policy and output concerns remain separable |
| NFR-09 | Deadline awareness | Sessions use remaining time and preserve an upload buffer |
| NFR-10 | Maintainable delivery | README, prompts, actual evaluation and usage details are included |

The budget controller is an application estimate, not a guaranteed provider-enforced cap. Use margin for token accounting gaps and outstanding requests.

## 11. Evaluation and measurable success

No hidden-set accuracy is available during development. Report measured public/custom results separately from unlabeled target predictions.

Report:
- case-level deletion-status accuracy and confusion matrix;
- step-level accuracy or precision/recall with matching rule defined;
- field-level accuracy with missing/extra steps accounted for;
- exact ordered sequence accuracy;
- whole-case exact matches;
- evidence-reference accuracy/validity;
- failures found and improvements made;
- at least three independently authored additional cases;
- token/model/cost totals for the final run and cache provenance.

A target is 100% public sample match and passing independent custom cases, but do not claim this until measured. Do not invent metrics or hardcode sample labels to reach it. If mismatches remain, prioritize their causal fixes and disclose the actual numbers.

Label exposure matters: a held-out subset of public samples is a development aid, not an unseen benchmark. Explain any tuning on public labels.

## 12. Sessions and reachable checkpoints

Use the actual personal software_build skill available in Claude's environment. Read its SKILL.md before creating planning artifacts. This guide does not prescribe or guess its invocation syntax.

Each session must contain:
- a concrete objective and relevant FR/NFR IDs;
- entry dependencies and small bounded scope;
- reachable checkpoints with observable acceptance evidence;
- source files/artifacts and exact validation commands;
- estimated effort and model-cost impact;
- exit criteria, blockers and next-session handoff.

Examples of useful checkpoints:
- A malformed output fixture is rejected for the correct reason.
- Every manifest file has processed/partial/failed coverage status.
- Old-email evidence is retrieved without including a similar-email decoy.
- One case completes model tool selection through canonical output.
- All public samples are evaluated with detailed mismatch categories.
- Full target run has case accounting and measured usage.
- Clean unpacked solution runs and required reports are inside code.zip.

A checkpoint such as “implement backend” is too broad. A checkbox without supporting result is not complete.

Keep sessions resumable for Breno's intermittent availability. Write a short current-state summary, remaining budget, exact next action and any user-only blocker. Reduce optional scope rather than silently dropping requirements.

## 13. Submission acceptance and exclusions

Required deliverables:
1. Runnable code.zip with source, prompts, configuration, README and evaluation reports.
2. Root output.csv.
3. Root log.txt matching current AGENTS.md.
4. AI interview readiness.

Required reports should be under code/evaluation/ per inspected README:
- evaluation_report.md: actual status/step/field/sequence metrics, custom cases, failures and improvements.
- usage_report.md: final-run provider/models, calls, input/output tokens, total/average per request and costs, per-model and overall totals. Explain cached preprocessing costs too.

The repository separately requests agent-trace.zip. Preserve relevant original Claude Code sessions and readable exports; verify current platform upload instructions. Keep this archive outside code.zip.

Exclude dataset/, environments, caches, nested archives and secrets from code.zip. Keep required judge-readable explanations in Markdown/source, not only raw JSON/CSV/logs.

Do not publish competition materials in a public GitHub repo without confirming event rules. Prefer a private user-owned solution repo; preserve upstream attribution and existing local work.

## 14. Decisions to measure during setup

- Which currently accessible Gemini model produces sufficient grounded accuracy at acceptable cost?
- Native function calls or validated action envelopes: which works reliably with the installed SDK?
- Which PDF/image facts require vision after text extraction?
- What exact observation/capture time semantics does current official documentation impose?
- How should multiple equally proving citations be selected deterministically?
- How are physical replicas represented through official output resource/system IDs?
- Are all 32 public examples evaluable from the current participant evidence as expected?
- What upload fields/deadline does the actual HackerRank interface show?

Resolve through inspection, a small representative pilot and recorded decisions. Ask Breno only when information or authorization cannot be obtained independently; keep unrelated work moving.

## 15. Sources and authority

https://github.com/interviewstreet/hackerrank-orchestrate-october26/blob/main/problem_statement.md
https://github.com/interviewstreet/hackerrank-orchestrate-october26/blob/main/README.md
https://github.com/interviewstreet/hackerrank-orchestrate-october26/blob/main/AGENTS.md
https://github.com/interviewstreet/hackerrank-orchestrate-october26/blob/main/agent_trace_instructions.md
https://github.com/interviewstreet/hackerrank-orchestrate-october26/blob/main/dataset/deletion_rules.csv

This is a planning/specification artifact. No engine, test results, GitHub setup or paid-model execution is claimed by this document.

