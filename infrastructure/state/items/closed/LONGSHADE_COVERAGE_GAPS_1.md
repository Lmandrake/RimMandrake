# LONGSHADE_COVERAGE_GAPS_1

Child of NORTHSTAR_COVERAGE_AUDIT_1. Row `LongShade` of `design/RimMandrake/northstar_coverage_audit_2026-10-03.md`.

## spec
The LongShade `validation.py` asserts little of what the mod does. Uncovered, per the audit (a Sonnet reader's evidence; re-read the mod first):
(1) crawlerRoadEnabled Crawler Road gen step never run; (2) sunGravesEnabled Sun Graves never run; (3) shipfallCommonsEnabled think-tree wildlife gathering unasserted; (4) mirrak false-shade ambush and vorrel seasonal cycle (plant/items/recipe/thought) unasserted; (5) dewfringe rim-only growth effect (component declared, not shown to change spawns); 22 creatures/5 plants only resolve-checked

Add a component per uncovered behaviour that asserts it DOES its job (not spawn-and-count), one per settings toggle with an off arm. Static/offline bars first.

## criteria
Each listed behaviour has an asserting component or a stated reason it cannot (UNMEASURED with the missing instrument named); `lint_calls.py` clean for the file.
