---
state: proposed
needs: offline
---

# FLOWWORKS_SHOWCASES_BUILD_THREE_FACES_STAGED

Item file restored 2026-11-12 from the ledger (RIMMANDRAKE_RECONCILE_FLOWWORKS_LEDGER_OPEN_WITHOUT_ITEM_FILE); the ledger held the item but its prose file was missing.

## spec

FlowWorks: concept_scenes.py entry points for the showcase and interaction scenes (sc_moat_raid, sc_islands, sc_pit_trap_raid, sc_garden, sc_walk) in design/concepts/FlowWorks/scenes.json

## what is left

- proposed: nothing recorded as owed beyond the title; read `rimflow show FLOWWORKS_SHOWCASES_BUILD_THREE_FACES_STAGED` history before building.

## verify

Prove it where the title says (offline selftest, or the live proof named in the owed criterion); then `rimflow verify FLOWWORKS_SHOWCASES_BUILD_THREE_FACES_STAGED --sha <sha> --level <L> --result pass --config <what ran> --evidence <path>` and `rimflow close`. Check `git log origin/main --grep=FLOWWORKS_SHOWCASES_BUILD_THREE_FACES_STAGED` first: another commit may already do it.
