# ENVIRONMENTALHAZARDS_COVERAGE_GAPS_1

Child of NORTHSTAR_COVERAGE_AUDIT_1. Row `EnvironmentalHazards` of `design/RimMandrake/northstar_coverage_audit_2026-10-03.md`.

## spec
The EnvironmentalHazards `validation.py` asserts little of what the mod does. Uncovered, per the audit (a Sonnet reader's evidence; re-read the mod first):
the 12 map_mechanics components are explicit UNMEASURED stubs: gas emitters/gas effects (gasEmittersEnabled), periodic area attack, environmental weather/latent hazard, scaledExplosions death action, water-truce retribution, living boles regrowth, stranding pools/gradient axis, tar coating/glasswalk slip, accelerated rot, sheen scald, venomvine scratch/body-size barrier, worldgen scatterers

Add a component per uncovered behaviour that asserts it DOES its job (not spawn-and-count), one per settings toggle with an off arm. Static/offline bars first.

## criteria
Each listed behaviour has an asserting component or a stated reason it cannot (UNMEASURED with the missing instrument named); `lint_calls.py` clean for the file.
