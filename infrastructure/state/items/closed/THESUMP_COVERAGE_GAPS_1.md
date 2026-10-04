# THESUMP_COVERAGE_GAPS_1

Child of NORTHSTAR_COVERAGE_AUDIT_1. Row `TheSump` of `design/RimMandrake/northstar_coverage_audit_2026-10-03.md`.

## spec
The TheSump `validation.py` asserts little of what the mod does. Uncovered, per the audit (a Sonnet reader's evidence; re-read the mod first):
everything behavioural: Deep Black mere gen step, kethrel shell/molt/property-take, tar vault, biomeRarity, poured tar moat + fuse post ignition, dig-shaft stratum lottery, tar-beast bulge wake, sump-mouse trail, wick-garden crop, permanent dusk lock; biome wiring (BiomeDef held from deploy, so even live density read UNMEASURED); 10 files held by DEPLOY_HOLD

Add a component per uncovered behaviour that asserts it DOES its job (not spawn-and-count), one per settings toggle with an off arm. Static/offline bars first.

## criteria
Each listed behaviour has an asserting component or a stated reason it cannot (UNMEASURED with the missing instrument named); `lint_calls.py` clean for the file.
