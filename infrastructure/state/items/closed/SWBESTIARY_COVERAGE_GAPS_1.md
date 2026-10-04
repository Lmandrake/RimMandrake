# SWBESTIARY_COVERAGE_GAPS_1

Child of NORTHSTAR_COVERAGE_AUDIT_1. Row `SWBestiary` of `design/RimMandrake/northstar_coverage_audit_2026-10-03.md`.

## spec
The SWBestiary `validation.py` asserts little of what the mod does. Uncovered, per the audit (a Sonnet reader's evidence; re-read the mod first):
~574 ThingDefs/9 HediffDefs/10 AbilityDefs/11 ThoughtDefs mostly unasserted; toggles never touched: innateAbilitiesEnabled, metalEatingEnabled, moornakGriefEnabled (+moornakReleaseDelayMultiplier), scrapHoardingEnabled, toxinDependenceEnabled; kilnBelly is flip-only (spawn-only, never asserted to DO anything); abilities (Round2/MlieWave) never cast; JawaIkee other effects

Add a component per uncovered behaviour that asserts it DOES its job (not spawn-and-count), one per settings toggle with an off arm. Static/offline bars first.

## criteria
Each listed behaviour has an asserting component or a stated reason it cannot (UNMEASURED with the missing instrument named); `lint_calls.py` clean for the file.
