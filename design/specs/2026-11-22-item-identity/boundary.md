# BOUNDARY: the mod that an item names and the stage that a run ran, Design Version 0.1.0

Code: `src/RimMandrake/rimflow/item_identity.py`. Tests: `src/RimMandrake/rimflow/selftest_item_identity.py`. Written
2026-11-22 for `RIMMANDRAKE_GENERALIZE_PIPELINE_REPAIRS_INTO_FEW_PRINCIPLES` (principle 2, one home for a fact). Before
it, three readers (`maturation_now.py`, `rimflow_metrics.py`, `fleet_mods.py`) each had their own rule, and on the
2026-11-22 ledger they named different mods for 1,288 and 2,736 of 9,649 items [measured].

## ACCEPTS

- **an-item-and-a-mod-list.** An item id, the caller's list of mod folder names, and the item's title or nothing.

## DOES NOT SURVIVE

- An item whose id and title name no mod, or name two equally: the answer is None. A run on such an item is placed on
  a mod only by its launch record (`RM_CONTROL_MOD`). A run is never placed by its item's title (a title may only name
  a mod as the example of a pipeline-tool fault), and a run that the ticket lane launched is on no mod.

## PROMISES (each one is owed a test of the same name)

- **one-answer.** `maturation_now`, `rimflow_metrics` and `fleet_mods` ask this module, and so give one answer.
- **id-before-title.** The id decides when it names a mod. Else the title decides. Else the answer is None.
- **a-tie-names-none.** When two mods are named equally well, the answer is None, never a guess.
- **a-run-is-on-its-recorded-stage.** `maturation_now.runs_for_mods` places a run on the stage its launch recorded
  (`RM_CONTROL_STAGE`, written by every pipeline launch since 2026-11-19), and on no other. A run whose launch recorded
  no stage is on no stage: no journal heading and no note text place it. Before this, the page guessed the stage from
  prose, and on the 2026-11-22 records the guess matched the recorded stage for 17 of 91 runs (13 wrong, 22 with extra
  stages, 39 with none) [measured].
- **a-run-is-placed-by-its-record-or-its-id-never-its-title.** `maturation_now.runs_for_mods` puts a run on the mod its
  launch recorded (`RM_CONTROL_MOD`), else the mod its item's id names; a title never places a run, and a run with no
  `RM_CONTROL_STAGE` that the ticket lane launched is on no mod. So the badge of a mod reads a live run only when the run
  is work on that mod (RIMMANDRAKE_FIX_PASSED_MOD_BADGE_HELPER_WAS_TOOL_REPAIR). Tested by case 19 of
  `selftest_maturation_now.py` (`p19_badges`).
- **one-alias-table.** A short name that is not in a mod's own name (`HOSE`, `FW` for FlowWorks) is in `ALIASES` here
  and nowhere else among the readers.
