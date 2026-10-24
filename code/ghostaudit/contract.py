"""The output contract (AGENTS.md §6.3–6.6, problem_statement.md): the only home of its vocabulary.

Every other module imports these tables; nothing re-lists an operation, a state or a rank.
"""
from __future__ import annotations

PHASES = ("FINDING", "REMEDIATION", "VERIFICATION")
STATUSES = ("COMPLETE", "INCOMPLETE", "NOT_APPLICABLE")
# Key order of the AGENTS.md §6.3 example (24/32 sample rows use it; the grader ignores key order).
STEP_KEY_ORDER = ("step_no", "phase", "system_id", "resource_id", "operation", "state", "evidence_id")
STEP_KEYS = frozenset(STEP_KEY_ORDER)
OUTPUT_HEADER = ("case_id", "deletion_status", "steps_json")

# (operation, phase, state) in the order of the AGENTS.md §6.4 tables. The position in this tuple is the
# operation rank used by the canonical sort ("within each phase, follow the operation order in the table").
_TABLE = (
    ("REPORT_REMAINING_RECORD", "FINDING", "PRESENT"),
    ("REPORT_EXPOSED_PII", "FINDING", "PRESENT"),
    ("REPORT_ACTIVE_DATA_FLOW", "FINDING", "ACTIVE"),
    ("REPORT_RESTORE_RISK", "FINDING", "ACTIVE"),
    ("DISABLE_DATA_FLOW", "REMEDIATION", "DISABLED"),
    ("BLOCK_RESTORE", "REMEDIATION", "BLOCKED"),
    ("DELETE_RECORD", "REMEDIATION", "ABSENT"),
    ("REDACT_RECORD", "REMEDIATION", "REDACTED"),
    ("ANONYMIZE_RECORD", "REMEDIATION", "ANONYMIZED"),
    ("VERIFY_RECORD_ABSENT", "VERIFICATION", "ABSENT"),
    ("VERIFY_RECORD_PRESENT", "VERIFICATION", "PRESENT"),
    ("VERIFY_RECORD_REDACTED", "VERIFICATION", "REDACTED"),
    ("VERIFY_RECORD_ANONYMIZED", "VERIFICATION", "ANONYMIZED"),
    ("VERIFY_DATA_FLOW_DISABLED", "VERIFICATION", "DISABLED"),
    ("VERIFY_RESTORE_BLOCKED", "VERIFICATION", "BLOCKED"),
)
OPERATIONS: dict[str, tuple[str, str, int]] = {op: (phase, state, rank) for rank, (op, phase, state) in enumerate(_TABLE)}
STATES = frozenset(state for _, _, state in _TABLE)


def evidence_required(status: str, phase: str) -> bool:
    """D9: findings always cite; COMPLETE verifications cite; INCOMPLETE remediation/verification are future work ("")."""
    if phase == "FINDING":
        return True
    return status == "COMPLETE" and phase == "VERIFICATION"


def is_legal(phase: str, operation: str, state: str) -> bool:
    entry = OPERATIONS.get(operation)
    return entry is not None and entry[0] == phase and entry[1] == state
