# MOVINGDUNES_COVERAGE_GAPS_1

Child of NORTHSTAR_COVERAGE_AUDIT_1. Row `MovingDunes` of `design/RimMandrake/northstar_coverage_audit_2026-10-03.md`.

## spec
The MovingDunes `validation.py` asserts little of what the mod does. Uncovered, per the audit (a Sonnet reader's evidence; re-read the mod first):
(1) slow_* chains all UNMEASURED: transport/banking, influx, burial caches (burialEnabled), plant choke (plantChokeEnabled), wind lock (windLockEnabled), clear yield (clearYieldEnabled/Multiplier); (2) transportRateMultiplier never shown to scale anything; (3) dune_field_report only runs when current map is a dune biome, else UNMEASURED; (4) sand actually moving (cell sand totals change) not asserted

Add a component per uncovered behaviour that asserts it DOES its job (not spawn-and-count), one per settings toggle with an off arm. Static/offline bars first.

## criteria
Each listed behaviour has an asserting component or a stated reason it cannot (UNMEASURED with the missing instrument named); `lint_calls.py` clean for the file.
