# RIMPROPERTY_COVERAGE_GAPS_1

Child of NORTHSTAR_COVERAGE_AUDIT_1. Row `RimProperty` of `design/RimMandrake/northstar_coverage_audit_2026-10-03.md`.

## spec
The RimProperty `validation.py` asserts little of what the mod does. Uncovered, per the audit (a Sonnet reader's evidence; re-read the mod first):
salvageClaimFeeEnabled + walkableCommerceEnabled (no component; float-menu only, acknowledged floor gap); perceptionEnabled witness roll/faction-record propagation; claim decay (claimLifetimeMultiplier/suspicionHalfLife, lazy decay on read); pickpocket/hirePlaceless/bribe toggles (no component) ; claim-recording for stolen/purchased/gifted/inherited exceptions

Add a component per uncovered behaviour that asserts it DOES its job (not spawn-and-count), one per settings toggle with an off arm. Static/offline bars first.

## criteria
Each listed behaviour has an asserting component or a stated reason it cannot (UNMEASURED with the missing instrument named); `lint_calls.py` clean for the file.
