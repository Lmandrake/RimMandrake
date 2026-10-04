# WEBWORK_COVERAGE_GAPS_1

Child of NORTHSTAR_COVERAGE_AUDIT_1. Row `Webwork` of `design/RimMandrake/northstar_coverage_audit_2026-10-03.md`.

## spec
The Webwork `validation.py` asserts little of what the mod does. Uncovered, per the audit (a Sonnet reader's evidence; re-read the mod first):
nest placed at mapgen (nestEnabled); clutch re-lay 20-30 days (eggRelayIntervalMultiplier); emergent spawn on destroy + chance multiplier; sun-scald in sun; loom spit fires; frontCreep actually creeping

Add a component per uncovered behaviour that asserts it DOES its job (not spawn-and-count), one per settings toggle with an off arm. Static/offline bars first.

## criteria
Each listed behaviour has an asserting component or a stated reason it cannot (UNMEASURED with the missing instrument named); `lint_calls.py` clean for the file.
