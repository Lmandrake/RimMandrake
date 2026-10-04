# RAIDREDESIGNER_COVERAGE_GAPS_1

Child of NORTHSTAR_COVERAGE_AUDIT_1. Row `RaidRedesigner` of `design/RimMandrake/northstar_coverage_audit_2026-10-03.md`.

## spec
The RaidRedesigner `validation.py` asserts little of what the mod does. Uncovered, per the audit (a Sonnet reader's evidence; re-read the mod first):
GameComponent_OldFriends actually recording an Encounter for any of the hooks (flee, captain leave, prisoner escape/release, kidnap, caravan robbed, NAMED_HUNTER); 24-living-entry cap/notability pruning (RosterPruning); world-pawn KeepForever pinning effect; maxLivingEntries/grudgeNotabilityMultiplier tuning; scribe round-trip of roster

Add a component per uncovered behaviour that asserts it DOES its job (not spawn-and-count), one per settings toggle with an off arm. Static/offline bars first.

## criteria
Each listed behaviour has an asserting component or a stated reason it cannot (UNMEASURED with the missing instrument named); `lint_calls.py` clean for the file.
