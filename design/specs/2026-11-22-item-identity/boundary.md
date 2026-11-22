# BOUNDARY: the mod that an item names, Design Version 0.1.0

Code: `src/RimMandrake/rimflow/item_identity.py`. Tests: `src/RimMandrake/rimflow/selftest_item_identity.py`. Written
2026-11-22 for `RIMMANDRAKE_GENERALIZE_PIPELINE_REPAIRS_INTO_FEW_PRINCIPLES` (principle 2, one home for a fact). Before
it, three readers (`maturation_now.py`, `rimflow_metrics.py`, `fleet_mods.py`) each had their own rule, and on the
2026-11-22 ledger they named different mods for 1,288 and 2,736 of 9,649 items [measured].

## ACCEPTS

- **an-item-and-a-mod-list.** An item id, the caller's list of mod folder names, and the item's title or nothing.

## DOES NOT SURVIVE

- An item whose id and title name no mod, or name two equally: the answer is None. A run on such an item is placed on
  a mod only by its launch record (`RM_CONTROL_MOD`).

## PROMISES (each one is owed a test of the same name)

- **one-answer.** `maturation_now`, `rimflow_metrics` and `fleet_mods` ask this module, and so give one answer.
- **id-before-title.** The id decides when it names a mod. Else the title decides. Else the answer is None.
- **a-tie-names-none.** When two mods are named equally well, the answer is None, never a guess.
- **one-alias-table.** A short name that is not in a mod's own name (`HOSE`, `FW` for FlowWorks) is in `ALIASES` here
  and nowhere else among the readers.
