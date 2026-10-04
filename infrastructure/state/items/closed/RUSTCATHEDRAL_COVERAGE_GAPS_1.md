# RUSTCATHEDRAL_COVERAGE_GAPS_1

Child of NORTHSTAR_COVERAGE_AUDIT_1. Row `RustCathedral` of `design/RimMandrake/northstar_coverage_audit_2026-10-03.md`.

## spec
The RustCathedral `validation.py` asserts little of what the mod does. Uncovered, per the audit (a Sonnet reader's evidence; re-read the mod first):
every behaviour is an explicit UNMEASURED stub: bolt dance/freeze (boltDanceEnabled), watched pricing + kill irritation, eel fishing consequence, deep-drill response replacing infestation, wall tiers laid at mapgen (needs generated RM_RustCathedral map), hum commentary/goodwill drain, roach_eats_filth; hum attitude value ladder never driven; living-bolt shed curiosity

Add a component per uncovered behaviour that asserts it DOES its job (not spawn-and-count), one per settings toggle with an off arm. Static/offline bars first.

## criteria
Each listed behaviour has an asserting component or a stated reason it cannot (UNMEASURED with the missing instrument named); `lint_calls.py` clean for the file.
