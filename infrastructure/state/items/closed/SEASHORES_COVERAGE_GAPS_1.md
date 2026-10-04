# SEASHORES_COVERAGE_GAPS_1

Child of NORTHSTAR_COVERAGE_AUDIT_1. Row `SeaShores` of `design/RimMandrake/northstar_coverage_audit_2026-10-03.md`.

## spec
The SeaShores `validation.py` asserts little of what the mod does. Uncovered, per the audit (a Sonnet reader's evidence; re-read the mod first):
seasCountAsCoast (World.CoastDirectionAt postfix makes land beside a modded sea IsCoastal); generateSeaShores (RM_SeaCoast substituted for vanilla Coast in TryAddMutator); seaCatchTables (rare-catch transpiler on FishingUtility.GetCatchesFor); healFrozenWorldOnLoad count (healed tiles deliberately not asserted); none of the 4 settings flipped

Add a component per uncovered behaviour that asserts it DOES its job (not spawn-and-count), one per settings toggle with an off arm. Static/offline bars first.

## criteria
Each listed behaviour has an asserting component or a stated reason it cannot (UNMEASURED with the missing instrument named); `lint_calls.py` clean for the file.
