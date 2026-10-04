# STRUCTUREINJECTIONSRUT_COVERAGE_GAPS_1

Child of NORTHSTAR_COVERAGE_AUDIT_1. Row `StructureInjectionsRUT` of `design/RimMandrake/northstar_coverage_audit_2026-10-03.md`.

## spec
The StructureInjectionsRUT `validation.py` asserts little of what the mod does. Uncovered, per the audit (a Sonnet reader's evidence; re-read the mod first):
MapComponent_VaultSleepers (Vault Dungeons); CompIgniteCraterOnDestroy + GameComponent_WarLabCrater/WarLabCraterMutation; warLabCraterEnabled and ashfallCommandCodesEnabled toggles (suite.toggles empty); Seize/command-codes mechanic; natural mapgen path via tile mutator extraGenSteps; PavedTile terrain, Inhabited_Cast

Add a component per uncovered behaviour that asserts it DOES its job (not spawn-and-count), one per settings toggle with an off arm. Static/offline bars first.

## criteria
Each listed behaviour has an asserting component or a stated reason it cannot (UNMEASURED with the missing instrument named); `lint_calls.py` clean for the file.
