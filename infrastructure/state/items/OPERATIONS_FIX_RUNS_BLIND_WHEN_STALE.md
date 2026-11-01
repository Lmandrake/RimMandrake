## Why
T5. role_launch.py gate 2 refuses every role on a stale reading, Operations included, so the role that reads the watch cannot start when the watch is stale.

Parent: V3_WORKFLOW_AUDIT_EVERY_CLOCK_AND_DOOR. Ruled 2026-11-01 under the owner's word 'Do items 1,2,3 owner items now.' (decisions in design/RimMandrake/rimflow_v3_risk_response_2026-10-29.md section 6, re-measured in rimflow_v3_audit_remeasure_2026-10-31.md). Priority P0: P0 at maximum, P1 behind it, no process-freeze rule (D5(c)).

## Done when
With a stale or unreadable status.json, role_launch starts Operations in degraded mode (reading marked UNMEASURED, brief: diagnose the watch first) and still refuses the other roles; selftest.

Proved by the planted fault on the real path, not by a statement.
