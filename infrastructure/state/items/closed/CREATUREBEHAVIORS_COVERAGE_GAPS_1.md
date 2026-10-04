# CREATUREBEHAVIORS_COVERAGE_GAPS_1

Child of NORTHSTAR_COVERAGE_AUDIT_1. Row `CreatureBehaviors` of `design/RimMandrake/northstar_coverage_audit_2026-10-03.md`.

## spec
The CreatureBehaviors `validation.py` asserts little of what the mod does. Uncovered, per the audit (a Sonnet reader's evidence; re-read the mod first):
shared engine of ~50 mechanics, 12+ toggles unasserted live: verminBreeding/RM_MapComponent_VerminPopulation + alert, gnaw, eatCleanable, seekShade, seekMarkedTerrain, sunScald, senseWeb, chewAnchors, frontCreep, aquaticAmbush, parental enrage, drum lure; walk doc owed. Eviction/cap is offline-proven elsewhere (selftest_track_grid.py)

Add a component per uncovered behaviour that asserts it DOES its job (not spawn-and-count), one per settings toggle with an off arm. Static/offline bars first.

## criteria
Each listed behaviour has an asserting component or a stated reason it cannot (UNMEASURED with the missing instrument named); `lint_calls.py` clean for the file.
