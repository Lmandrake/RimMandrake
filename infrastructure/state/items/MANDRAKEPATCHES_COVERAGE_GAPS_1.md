# MANDRAKEPATCHES_COVERAGE_GAPS_1

Child of NORTHSTAR_COVERAGE_AUDIT_1. Row `MandrakePatches` of `design/RimMandrake/northstar_coverage_audit_2026-10-03.md`.

## spec
The MandrakePatches `validation.py` asserts little of what the mod does. Uncovered, per the audit (a Sonnet reader's evidence; re-read the mod first):
(1) 8 of 9 Patches/*.xml (AnimalDessicatedTexPaths, BTDGravshipQuest grammar, BiomeAnimalDanglingRefs removals, BuzzerApostrophe, DrillTurret_ShootingJob, GrimTerraTexPaths, HeadSetForFA_Revive, ThirdPartySignConfigErrors) have no effect read-back (donor mods absent on minimal list); (2) not even "no red error when donor absent" asserted; (3) texture fixes never checked to load/render against donor

Add a component per uncovered behaviour that asserts it DOES its job (not spawn-and-count), one per settings toggle with an off arm. Static/offline bars first.

## criteria
Each listed behaviour has an asserting component or a stated reason it cannot (UNMEASURED with the missing instrument named); `lint_calls.py` clean for the file.
