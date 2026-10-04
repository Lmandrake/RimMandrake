# KEELHOIST_COVERAGE_GAPS_1

Child of NORTHSTAR_COVERAGE_AUDIT_1. Row `KeelHoist` of `design/RimMandrake/northstar_coverage_audit_2026-10-03.md`.

## spec
The KeelHoist `validation.py` asserts little of what the mod does. Uncovered, per the audit (a Sonnet reader's evidence; re-read the mod first):
(1) Zero behavioural proof: hoist transit/cycle timing, cargo lift up/down never run (walk lines only); (2) 9 declared toggles (masterEnabled, requireGravEngine, colonistsMayRide, downedStrangersAndBeasts, openLineMeter, cycleTimeMultiplier, cableRange, restraintHours, tetherLock) none flipped/asserted to do anything; (3) RM_HoistRestraint (beast arrives restrained) and downed-stranger/beast sendability unasserted live; (4) tetherLock only checked as text presence, not that launch is actually refused; (5) RM_HoistFrame/RM_SealedPit site spawn on a map not asserted

Add a component per uncovered behaviour that asserts it DOES its job (not spawn-and-count), one per settings toggle with an off arm. Static/offline bars first.

## criteria
Each listed behaviour has an asserting component or a stated reason it cannot (UNMEASURED with the missing instrument named); `lint_calls.py` clean for the file.
