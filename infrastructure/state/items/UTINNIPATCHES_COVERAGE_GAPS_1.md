# UTINNIPATCHES_COVERAGE_GAPS_1

Child of NORTHSTAR_COVERAGE_AUDIT_1. Row `UtinniPatches` of `design/RimMandrake/northstar_coverage_audit_2026-10-03.md`.

## spec
The UtinniPatches `validation.py` asserts little of what the mod does. Uncovered, per the audit (a Sonnet reader's evidence; re-read the mod first):
ambientShrineDoctrine guardians swap (UNCOVERED, needs new-map-on-biome verb); geothermalDensityField geyser count (UNCOVERED); holyFlameAct toggle; greatbole shaking/healing/catastrophe thresholds + greatboleCatastropheEnabled; settings-gated patch ops (PatchOperationSettingGate); ~150 flagship defs (factions, scenario, doctrine, precepts, quests, weather) only in walk doc; Infestation planet-wide ban (static check on vanilla baseChance)

Add a component per uncovered behaviour that asserts it DOES its job (not spawn-and-count), one per settings toggle with an off arm. Static/offline bars first.

## criteria
Each listed behaviour has an asserting component or a stated reason it cannot (UNMEASURED with the missing instrument named); `lint_calls.py` clean for the file.
