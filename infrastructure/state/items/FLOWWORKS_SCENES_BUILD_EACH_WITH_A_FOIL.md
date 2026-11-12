---
state: proposed
needs: offline
---

# FLOWWORKS_SCENES_BUILD_EACH_WITH_A_FOIL

Item file restored 2026-11-12 from the ledger (RIMMANDRAKE_RECONCILE_FLOWWORKS_LEDGER_OPEN_WITHOUT_ITEM_FILE); the ledger held the item but its prose file was missing.

## spec

FlowWorks: concept_scenes.py entry points for the per-leaf acceptance scenes in design/concepts/FlowWorks/scenes.json, each with asserted start, its control and full snapshot restore; reused extensions.py etc. functions get the missing start/control/restore parts

## what is left

- proposed: nothing recorded as owed beyond the title; read `rimflow show FLOWWORKS_SCENES_BUILD_EACH_WITH_A_FOIL` history before building.

## verify

Prove it where the title says (offline selftest, or the live proof named in the owed criterion); then `rimflow verify FLOWWORKS_SCENES_BUILD_EACH_WITH_A_FOIL --sha <sha> --level <L> --result pass --config <what ran> --evidence <path>` and `rimflow close`. Check `git log origin/main --grep=FLOWWORKS_SCENES_BUILD_EACH_WITH_A_FOIL` first: another commit may already do it.
