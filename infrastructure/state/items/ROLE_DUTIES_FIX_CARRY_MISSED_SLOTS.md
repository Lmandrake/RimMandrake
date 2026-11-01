## Why
T8. No owed slot key in role_launch.py or the schedule; a slot missed in an outage is silently lost.

Parent: V3_WORKFLOW_AUDIT_EVERY_CLOCK_AND_DOOR. Ruled 2026-11-01 under the owner's word 'Do items 1,2,3 owner items now.' (decisions in design/RimMandrake/rimflow_v3_risk_response_2026-10-29.md section 6, re-measured in rimflow_v3_audit_remeasure_2026-10-31.md). Priority P1: P0 at maximum, P1 behind it, no process-freeze rule (D5(c)).

## Done when
A role slot marked owed that misses its window runs once on the next eligible tick; snapshot slots still drop; an expired run-now or dropped owed slot writes one acknowledged-miss line; selftest with a 3 h outage.

Proved by the planted fault on the real path, not by a statement.
