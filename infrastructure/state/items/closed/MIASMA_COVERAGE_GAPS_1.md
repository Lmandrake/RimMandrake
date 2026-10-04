# MIASMA_COVERAGE_GAPS_1

Child of NORTHSTAR_COVERAGE_AUDIT_1. Row `Miasma` of `design/RimMandrake/northstar_coverage_audit_2026-10-03.md`.

## spec
The Miasma `validation.py` asserts little of what the mod does. Uncovered, per the audit (a Sonnet reader's evidence; re-read the mod first):
(1) switches_gate_mechanics (plantPredationEnabled, pollinationGateEnabled, strandedDeformationEnabled/Chance) UNMEASURED; (2) decay cells power/rot (decayCellsEnabled) UNMEASURED; (3) youngCall cry, ambush frog hunt, swarm composter (Karrobel), flotsam yard, attar recipe/glaze UNMEASURED (defs-count only described, not asserted); (4) salt-crust repaint and four juvenile stranding on free tier; (5) wardenSuccessionEnabled, selfTameChancePerCheck, biomeRarityFactor round-trip only

Add a component per uncovered behaviour that asserts it DOES its job (not spawn-and-count), one per settings toggle with an off arm. Static/offline bars first.

## criteria
Each listed behaviour has an asserting component or a stated reason it cannot (UNMEASURED with the missing instrument named); `lint_calls.py` clean for the file.
