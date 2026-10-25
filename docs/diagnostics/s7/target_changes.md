# S7 target row changes vs S6, each attributed (runs/s6/final → runs/s7/final)

60 rows changed; status flips: 0; agent contribution 0 rows (`runs/s7/det/targets` → `runs/s7/final`, byte-identical CSV).

| cause | rows |
|---|---|
| A34/A34a: workflow-deduced account no longer asserted | 3 |
| A36: account identified from a pre-audit snapshot; absence cited from an admissible file | 1 |
| A36: retained record read from a pre-audit snapshot envelope (uncited) | 58 |

Each A36 step was traced to its snapshot envelope in the run's `provenance.jsonl` (example: case_432 `legal_hold_438` ← `evidence_40#snap6:0`, a retained order record with `subject_reference user_430`, `retained_until` 2033, snapshot captured before the audit inside the 2026-03-22 bundle).

| case | status | steps added | steps removed | cause |
|---|---|---|---|---|
| case_123 | INCOMPLETE→INCOMPLETE | +VERIFY_RECORD_PRESENT audit_record_5645 | — | A36: retained record read from a pre-audit snapshot envelope (uncited) |
| case_124 | INCOMPLETE→INCOMPLETE | +VERIFY_RECORD_PRESENT audit_record_282 | — | A36: retained record read from a pre-audit snapshot envelope (uncited) |
| case_125 | INCOMPLETE→INCOMPLETE | +VERIFY_RECORD_PRESENT audit_record_023 | — | A36: retained record read from a pre-audit snapshot envelope (uncited) |
| case_128 | INCOMPLETE→INCOMPLETE | +VERIFY_RECORD_PRESENT audit_record_4249 | — | A36: retained record read from a pre-audit snapshot envelope (uncited) |
| case_129 | INCOMPLETE→INCOMPLETE | +VERIFY_RECORD_PRESENT audit_record_5606 | — | A36: retained record read from a pre-audit snapshot envelope (uncited) |
| case_130 | INCOMPLETE→INCOMPLETE | +VERIFY_RECORD_PRESENT audit_record_7634 | — | A36: retained record read from a pre-audit snapshot envelope (uncited) |
| case_131 | INCOMPLETE→INCOMPLETE | +VERIFY_RECORD_PRESENT audit_record_8457 | — | A36: retained record read from a pre-audit snapshot envelope (uncited) |
| case_132 | INCOMPLETE→INCOMPLETE | +VERIFY_RECORD_PRESENT audit_record_1424 | — | A36: retained record read from a pre-audit snapshot envelope (uncited) |
| case_173 | INCOMPLETE→INCOMPLETE | +VERIFY_RECORD_PRESENT audit_record_4126 | — | A36: retained record read from a pre-audit snapshot envelope (uncited) |
| case_174 | INCOMPLETE→INCOMPLETE | +VERIFY_RECORD_PRESENT audit_record_7011 | — | A36: retained record read from a pre-audit snapshot envelope (uncited) |
| case_176 | INCOMPLETE→INCOMPLETE | +VERIFY_RECORD_PRESENT audit_record_1222 | — | A36: retained record read from a pre-audit snapshot envelope (uncited) |
| case_177 | INCOMPLETE→INCOMPLETE | +VERIFY_RECORD_PRESENT audit_record_6729 | — | A36: retained record read from a pre-audit snapshot envelope (uncited) |
| case_179 | INCOMPLETE→INCOMPLETE | +VERIFY_RECORD_PRESENT audit_record_919 | — | A36: retained record read from a pre-audit snapshot envelope (uncited) |
| case_180 | INCOMPLETE→INCOMPLETE | +VERIFY_RECORD_PRESENT audit_record_2207 | — | A36: retained record read from a pre-audit snapshot envelope (uncited) |
| case_181 | INCOMPLETE→INCOMPLETE | +VERIFY_RECORD_PRESENT audit_record_3625 | — | A36: retained record read from a pre-audit snapshot envelope (uncited) |
| case_182 | INCOMPLETE→INCOMPLETE | +VERIFY_RECORD_PRESENT audit_record_8354 | — | A36: retained record read from a pre-audit snapshot envelope (uncited) |
| case_223 | INCOMPLETE→INCOMPLETE | +VERIFY_RECORD_PRESENT audit_record_234 | — | A36: retained record read from a pre-audit snapshot envelope (uncited) |
| case_224 | INCOMPLETE→INCOMPLETE | +VERIFY_RECORD_PRESENT audit_record_6515 | — | A36: retained record read from a pre-audit snapshot envelope (uncited) |
| case_227 | INCOMPLETE→INCOMPLETE | +VERIFY_RECORD_PRESENT audit_record_9043 | — | A36: retained record read from a pre-audit snapshot envelope (uncited) |
| case_228 | INCOMPLETE→INCOMPLETE | +VERIFY_RECORD_PRESENT audit_record_5029 | — | A36: retained record read from a pre-audit snapshot envelope (uncited) |
| case_229 | INCOMPLETE→INCOMPLETE | +VERIFY_RECORD_PRESENT audit_record_4310 | — | A36: retained record read from a pre-audit snapshot envelope (uncited) |
| case_230 | INCOMPLETE→INCOMPLETE | +VERIFY_RECORD_PRESENT audit_record_7027 | — | A36: retained record read from a pre-audit snapshot envelope (uncited) |
| case_232 | INCOMPLETE→INCOMPLETE | +VERIFY_RECORD_PRESENT audit_record_7757 | — | A36: retained record read from a pre-audit snapshot envelope (uncited) |
| case_273 | INCOMPLETE→INCOMPLETE | +VERIFY_RECORD_PRESENT audit_record_3428 | — | A36: retained record read from a pre-audit snapshot envelope (uncited) |
| case_275 | INCOMPLETE→INCOMPLETE | +VERIFY_RECORD_PRESENT audit_record_4188 | — | A36: retained record read from a pre-audit snapshot envelope (uncited) |
| case_278 | INCOMPLETE→INCOMPLETE | +VERIFY_RECORD_PRESENT audit_record_6384 | — | A36: retained record read from a pre-audit snapshot envelope (uncited) |
| case_279 | INCOMPLETE→INCOMPLETE | +VERIFY_RECORD_PRESENT audit_record_5055 | — | A36: retained record read from a pre-audit snapshot envelope (uncited) |
| case_280 | INCOMPLETE→INCOMPLETE | +VERIFY_RECORD_PRESENT audit_record_1518 | — | A36: retained record read from a pre-audit snapshot envelope (uncited) |
| case_281 | INCOMPLETE→INCOMPLETE | +VERIFY_RECORD_PRESENT audit_record_111 | — | A36: retained record read from a pre-audit snapshot envelope (uncited) |
| case_282 | INCOMPLETE→INCOMPLETE | +VERIFY_RECORD_PRESENT audit_record_3198 | — | A36: retained record read from a pre-audit snapshot envelope (uncited) |
| case_325 | INCOMPLETE→INCOMPLETE | +VERIFY_RECORD_PRESENT audit_record_2236 | — | A36: retained record read from a pre-audit snapshot envelope (uncited) |
| case_328 | INCOMPLETE→INCOMPLETE | +VERIFY_RECORD_PRESENT audit_record_5012 | — | A36: retained record read from a pre-audit snapshot envelope (uncited) |
| case_329 | INCOMPLETE→INCOMPLETE | +VERIFY_RECORD_PRESENT audit_record_3525 | — | A36: retained record read from a pre-audit snapshot envelope (uncited) |
| case_330 | INCOMPLETE→INCOMPLETE | +VERIFY_RECORD_PRESENT audit_record_6629 | — | A36: retained record read from a pre-audit snapshot envelope (uncited) |
| case_332 | INCOMPLETE→INCOMPLETE | +VERIFY_RECORD_PRESENT audit_record_8914 | — | A36: retained record read from a pre-audit snapshot envelope (uncited) |
| case_373 | INCOMPLETE→INCOMPLETE | +VERIFY_RECORD_PRESENT audit_record_9163 | — | A36: retained record read from a pre-audit snapshot envelope (uncited) |
| case_376 | INCOMPLETE→INCOMPLETE | +VERIFY_RECORD_PRESENT audit_record_4137 | -VERIFY_RECORD_ABSENT account_5454 | A34/A34a: workflow-deduced account no longer asserted; A36: retained record read from a pre-audit snapshot envelope (uncited) |
| case_377 | INCOMPLETE→INCOMPLETE | +VERIFY_RECORD_PRESENT audit_record_3685 | — | A36: retained record read from a pre-audit snapshot envelope (uncited) |
| case_379 | INCOMPLETE→INCOMPLETE | +VERIFY_RECORD_PRESENT audit_record_8830 | — | A36: retained record read from a pre-audit snapshot envelope (uncited) |
| case_381 | INCOMPLETE→INCOMPLETE | +VERIFY_RECORD_PRESENT audit_record_6833 | — | A36: retained record read from a pre-audit snapshot envelope (uncited) |
| case_382 | INCOMPLETE→INCOMPLETE | +VERIFY_RECORD_PRESENT audit_record_6238 | — | A36: retained record read from a pre-audit snapshot envelope (uncited) |
| case_425 | INCOMPLETE→INCOMPLETE | +VERIFY_RECORD_PRESENT audit_record_4863 | — | A36: retained record read from a pre-audit snapshot envelope (uncited) |
| case_426 | INCOMPLETE→INCOMPLETE | +VERIFY_RECORD_PRESENT audit_record_5472 | — | A36: retained record read from a pre-audit snapshot envelope (uncited) |
| case_428 | INCOMPLETE→INCOMPLETE | +VERIFY_RECORD_PRESENT audit_record_7557 | — | A36: retained record read from a pre-audit snapshot envelope (uncited) |
| case_429 | INCOMPLETE→INCOMPLETE | +VERIFY_RECORD_PRESENT audit_record_9805 | — | A36: retained record read from a pre-audit snapshot envelope (uncited) |
| case_430 | COMPLETE→COMPLETE | +VERIFY_RECORD_ABSENT account_6006 | — | A36: account identified from a pre-audit snapshot; absence cited from an admissible file |
| case_431 | INCOMPLETE→INCOMPLETE | +VERIFY_RECORD_PRESENT audit_record_3236 | — | A36: retained record read from a pre-audit snapshot envelope (uncited) |
| case_432 | INCOMPLETE→INCOMPLETE | +VERIFY_RECORD_PRESENT audit_record_3548, +VERIFY_RECORD_PRESENT legal_hold_438 | — | A36: retained record read from a pre-audit snapshot envelope (uncited) |
| case_523 | INCOMPLETE→INCOMPLETE | +VERIFY_RECORD_PRESENT audit_record_2172 | — | A36: retained record read from a pre-audit snapshot envelope (uncited) |
| case_525 | INCOMPLETE→INCOMPLETE | +VERIFY_RECORD_PRESENT audit_record_3803 | — | A36: retained record read from a pre-audit snapshot envelope (uncited) |
| case_526 | INCOMPLETE→INCOMPLETE | +VERIFY_RECORD_PRESENT audit_record_5792 | — | A36: retained record read from a pre-audit snapshot envelope (uncited) |
| case_527 | INCOMPLETE→INCOMPLETE | +VERIFY_RECORD_PRESENT audit_record_2758 | — | A36: retained record read from a pre-audit snapshot envelope (uncited) |
| case_528 | INCOMPLETE→INCOMPLETE | +VERIFY_RECORD_PRESENT audit_record_2284 | — | A36: retained record read from a pre-audit snapshot envelope (uncited) |
| case_529 | INCOMPLETE→INCOMPLETE | +VERIFY_RECORD_PRESENT audit_record_4542 | — | A36: retained record read from a pre-audit snapshot envelope (uncited) |
| case_531 | INCOMPLETE→INCOMPLETE | +VERIFY_RECORD_PRESENT audit_record_8556 | — | A36: retained record read from a pre-audit snapshot envelope (uncited) |
| case_74 | INCOMPLETE→INCOMPLETE | +VERIFY_RECORD_PRESENT audit_record_7778 | — | A36: retained record read from a pre-audit snapshot envelope (uncited) |
| case_75 | INCOMPLETE→INCOMPLETE | +VERIFY_RECORD_PRESENT audit_record_7491 | — | A36: retained record read from a pre-audit snapshot envelope (uncited) |
| case_76 | INCOMPLETE→INCOMPLETE | +VERIFY_RECORD_PRESENT audit_record_6766 | — | A36: retained record read from a pre-audit snapshot envelope (uncited) |
| case_78 | INCOMPLETE→INCOMPLETE | +VERIFY_RECORD_PRESENT audit_record_6593 | -VERIFY_RECORD_ABSENT account_8754 | A34/A34a: workflow-deduced account no longer asserted; A36: retained record read from a pre-audit snapshot envelope (uncited) |
| case_94 | INCOMPLETE→INCOMPLETE | — | -VERIFY_RECORD_ABSENT account_4037 | A34/A34a: workflow-deduced account no longer asserted |
