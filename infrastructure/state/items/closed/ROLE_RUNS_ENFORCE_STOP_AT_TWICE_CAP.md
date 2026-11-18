## Why
T10. No budget-stop flag in role_launch.py or dispatcher.py; a role run can exceed its allowance.

Parent: V3_WORKFLOW_AUDIT_EVERY_CLOCK_AND_DOOR. Ruled 2026-11-01 under the owner's word 'Do items 1,2,3 owner items now.' (decisions in design/RimMandrake/rimflow_v3_risk_response_2026-10-29.md section 6, re-measured in rimflow_v3_audit_remeasure_2026-10-31.md). Priority P1: P0 at maximum, P1 behind it, no process-freeze rule (D5(c)).

## Done when
Every role launch passes a hard budget stop at 2x its run allowance; docs say allowance; a selftest asserts the flag on each role's command line.

Proved by the planted fault on the real path, not by a statement.
