## Why
T6. The phone push exists since 3645471658 (src/RimMandrake/Utils/pulse/phone_push.py, Todoist due-now task, one send per incident, red only). deadman_check.py does not call it.

Parent: V3_WORKFLOW_AUDIT_EVERY_CLOCK_AND_DOOR. Ruled 2026-11-01 under the owner's word 'Do items 1,2,3 owner items now.' (decisions in design/RimMandrake/rimflow_v3_risk_response_2026-10-29.md section 6, re-measured in rimflow_v3_audit_remeasure_2026-10-31.md). Priority P0: P0 at maximum, P1 behind it, no process-freeze rule (D5(c)).

## Done when
A dead-man finding (Dispatcher, ops_watch or timer stale) reaches the owner's phone through phone_push with no AI in the path, as well as the ledger; selftest asserts the line; one live drill by stopping ops_watch for its limit. Note INCIDENT_LEDGER_BUILD_TOLD_ACKED_RECOVERED says phone push stays off: that sentence is stale since the owner turned it on (2026-11-01); fix it there too.

Proved by the planted fault on the real path, not by a statement.
