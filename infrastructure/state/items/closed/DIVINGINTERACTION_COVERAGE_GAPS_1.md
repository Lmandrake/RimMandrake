# DIVINGINTERACTION_COVERAGE_GAPS_1

Child of NORTHSTAR_COVERAGE_AUDIT_1. Row `DivingInteraction` of `design/RimMandrake/northstar_coverage_audit_2026-10-03.md`.

## spec
The DivingInteraction `validation.py` asserts little of what the mod does. Uncovered, per the audit (a Sonnet reader's evidence; re-read the mod first):
14 settings toggles unasserted as behaviour: greyPoolDefence/Sentinel, greyElderDischarge/Trade, chillFireBan, chillBoilShroud, chillHeatedSuit, chillGardenDefense, thermalFootprints, drownedAurora/auroraSurge; RM_SeaDiveHatch enter/descent (retired, SEA_DIVE_HATCH_RETIRE_1); live floor content/animal count UNMEASURED

Add a component per uncovered behaviour that asserts it DOES its job (not spawn-and-count), one per settings toggle with an off arm. Static/offline bars first.

## criteria
Each listed behaviour has an asserting component or a stated reason it cannot (UNMEASURED with the missing instrument named); `lint_calls.py` clean for the file.
