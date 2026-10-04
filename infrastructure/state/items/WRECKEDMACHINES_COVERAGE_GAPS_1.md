# WRECKEDMACHINES_COVERAGE_GAPS_1

Child of NORTHSTAR_COVERAGE_AUDIT_1. Row `WreckedMachines` of `design/RimMandrake/northstar_coverage_audit_2026-10-03.md`.

## spec
The WreckedMachines `validation.py` asserts little of what the mod does. Uncovered, per the audit (a Sonnet reader's evidence; re-read the mod first):
STALE HEADER: validation says no settings and `suite.toggles = []`, but Source/WreckedMachinesMod.cs now has 4 settings (allowDonorSmelter, researchCostFactor, materialCostFactor, skipRestorationResearch), none asserted; Repaired tier actually gated by research (research-not-finished -> not buildable); Kludged 3-process vs Repaired 6-process / canOverclock false vs true; replaceTags build-over; Analyse special opportunity

Add a component per uncovered behaviour that asserts it DOES its job (not spawn-and-count), one per settings toggle with an off arm. Static/offline bars first.

## criteria
Each listed behaviour has an asserting component or a stated reason it cannot (UNMEASURED with the missing instrument named); `lint_calls.py` clean for the file.
