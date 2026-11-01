## Why
T9. dispatcher.py l.100-105 DEFAULTS and CAP_DEFAULTS (3/30/80/3) are applied with setdefault at l.121, so a missing key silently becomes a number.

Parent: V3_WORKFLOW_AUDIT_EVERY_CLOCK_AND_DOOR. Ruled 2026-11-01 under the owner's word 'Do items 1,2,3 owner items now.' (decisions in design/RimMandrake/rimflow_v3_risk_response_2026-10-29.md section 6, re-measured in rimflow_v3_audit_remeasure_2026-10-31.md). Priority P1: P0 at maximum, P1 behind it, no process-freeze rule (D5(c)).

## Done when
Loading dispatcher_schedule.json with a required key missing refuses (no fallback); the list of required keys lives in one place; selftest.

Proved by the planted fault on the real path, not by a statement.
