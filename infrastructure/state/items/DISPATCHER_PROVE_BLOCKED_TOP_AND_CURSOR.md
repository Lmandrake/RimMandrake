## Why
T15, smaller. Rearm is covered by test_review_w_alarm_rearm; no test named for a blocked top item; the 7 h cursor case was not found.

Parent: V3_WORKFLOW_AUDIT_EVERY_CLOCK_AND_DOOR. Ruled 2026-11-01 under the owner's word 'Do items 1,2,3 owner items now.' (decisions in design/RimMandrake/rimflow_v3_risk_response_2026-10-29.md section 6, re-measured in rimflow_v3_audit_remeasure_2026-10-31.md). Priority P1: P0 at maximum, P1 behind it, no process-freeze rule (D5(c)).

## Done when
Selftests show a blocked top item does not hide a lower offline item from the Dispatcher, and the event cursor survives a 7 h outage without dropping unread events.

Proved by the planted fault on the real path, not by a statement.
