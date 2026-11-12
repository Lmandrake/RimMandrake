---
state: built
needs: bridge
---

# RIVER_SCENES_BUILD_WALKTHROUGH_WITH_CAPTIONS

Item file restored 2026-11-12 from the ledger (RIMMANDRAKE_RECONCILE_FLOWWORKS_LEDGER_OPEN_WITHOUT_ITEM_FILE); the ledger held the item but its prose file was missing.

## spec

River scenes the owner can watch: current, ford, weir, wash-off-map, with caption panels like the water scenes

Built at `a54be1db62d6` (origin/main); code is in, what is owed is below.

## what is left

- A2
- A3

## verify

Prove it where the title says (offline selftest, or the live proof named in the owed criterion); then `rimflow verify RIVER_SCENES_BUILD_WALKTHROUGH_WITH_CAPTIONS --sha <sha> --level <L> --result pass --config <what ran> --evidence <path>` and `rimflow close`. Check `git log origin/main --grep=RIVER_SCENES_BUILD_WALKTHROUGH_WITH_CAPTIONS` first: another commit may already do it.
