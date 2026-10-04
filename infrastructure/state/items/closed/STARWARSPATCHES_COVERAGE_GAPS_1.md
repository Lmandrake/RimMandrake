# STARWARSPATCHES_COVERAGE_GAPS_1

Child of NORTHSTAR_COVERAGE_AUDIT_1. Row `StarWarsPatches` of `design/RimMandrake/northstar_coverage_audit_2026-10-03.md`.

## spec
The StarWarsPatches `validation.py` asserts little of what the mod does. Uncovered, per the audit (a Sonnet reader's evidence; re-read the mod first):
~23 Patches/*.xml asserted nowhere live (delegated to "def dump"): BodySizeIsReal, EggLayersLayEggs, JawaCombatViability_Tuning, JawaXenotype_Repoint, WeaponTags_Renormalise (tag loss disarms kinds), VanillaFaction_Xenotypes, SWDesertWeather_Attach + SWDesertWeather def, PsychicToForceDisturbance; no static xpath-matches-target check like Shokk has; blast door open/close behaviour

Add a component per uncovered behaviour that asserts it DOES its job (not spawn-and-count), one per settings toggle with an off arm. Static/offline bars first.

## criteria
Each listed behaviour has an asserting component or a stated reason it cannot (UNMEASURED with the missing instrument named); `lint_calls.py` clean for the file.
