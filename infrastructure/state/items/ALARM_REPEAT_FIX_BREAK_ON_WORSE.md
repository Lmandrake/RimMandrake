## Why
T12. No severity or worsening test in the ops_watch repeat path.

Parent: V3_WORKFLOW_AUDIT_EVERY_CLOCK_AND_DOOR. Ruled 2026-11-01 under the owner's word 'Do items 1,2,3 owner items now.' (decisions in design/RimMandrake/rimflow_v3_risk_response_2026-10-29.md section 6, re-measured in rimflow_v3_audit_remeasure_2026-10-31.md). Priority P1: P0 at maximum, P1 behind it, no process-freeze rule (D5(c)).

## Done when
A repeat alarm of the same kind inside the 6 h window is re-raised when its severity rises or its impact metric crosses the rule's stated step; selftest.

Proved by the planted fault on the real path, not by a statement.
