# PLANETPRESETPRIME_COVERAGE_GAPS_1

Child of NORTHSTAR_COVERAGE_AUDIT_1. Row `PlanetPresetPrime` of `design/RimMandrake/northstar_coverage_audit_2026-10-03.md`.

## spec
The PlanetPresetPrime `validation.py` asserts little of what the mod does. Uncovered, per the audit (a Sonnet reader's evidence; re-read the mod first):
(1) the entire mechanism (Page_CreateWorldParams.Reset postfix priming planetCoverage=1.0 and subdivisions=7, producing 21872 tiles) has no live hook and is unasserted; (2) MLP subcount reflective priming result not read back; (3) no offline static check that the postfix target/field names exist

Add a component per uncovered behaviour that asserts it DOES its job (not spawn-and-count), one per settings toggle with an off arm. Static/offline bars first.

## criteria
Each listed behaviour has an asserting component or a stated reason it cannot (UNMEASURED with the missing instrument named); `lint_calls.py` clean for the file.
