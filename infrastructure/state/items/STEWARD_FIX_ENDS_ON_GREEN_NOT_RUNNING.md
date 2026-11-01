## Why
T4. testq/steward.py treats RUNNING as the only state that ends an incident; a live lease pauses the claim clock with no cap. D2(c) containment by machine.

Parent: V3_WORKFLOW_AUDIT_EVERY_CLOCK_AND_DOOR. Ruled 2026-11-01 under the owner's word 'Do items 1,2,3 owner items now.' (decisions in design/RimMandrake/rimflow_v3_risk_response_2026-10-29.md section 6, re-measured in rimflow_v3_audit_remeasure_2026-10-31.md). Priority P0: P0 at maximum, P1 behind it, no process-freeze rule (D5(c)).

## Done when
A steward incident closes only on a DONE job with the canary on after the incident's start; the claim pause is capped at 2 h per incident; the impact clock never pauses; selftest RUNNING-then-INVALID keeps it open.

Proved by the planted fault on the real path, not by a statement.
