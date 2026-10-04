# PYRINTH_COVERAGE_GAPS_1

Child of NORTHSTAR_COVERAGE_AUDIT_1. Row `Pyrinth` of `design/RimMandrake/northstar_coverage_audit_2026-10-03.md`.

## spec
The Pyrinth `validation.py` asserts little of what the mod does. Uncovered, per the audit (a Sonnet reader's evidence; re-read the mod first):
glow/heat/meditation of DV_PyrinthLamp/WallLamp/Brazier/Heater (UNMEASURED); DV_MeleeWeapon_PyrinthBlade stats; spark mote effects DV_PyrinthSparkingEffect*; Royalty throne-room patch; whether this pack (vs donor det.epochspyrinth) is the loaded copy

Add a component per uncovered behaviour that asserts it DOES its job (not spawn-and-count), one per settings toggle with an off arm. Static/offline bars first.

## criteria
Each listed behaviour has an asserting component or a stated reason it cannot (UNMEASURED with the missing instrument named); `lint_calls.py` clean for the file.

## progress 2026-10-03 (r34)
- `every_shipped_def_reads_back` wired: all 13 DV_ defs loaded and labelled as this pack says (a donor det.epochspyrinth copy with other labels would read as drift). Still open: lamp/brazier glow/heat/meditation, blade stats, spark motes, throne-room patch.
