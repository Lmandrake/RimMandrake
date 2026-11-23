---
state: proposed
needs: offline
---

# HOSE_SCHEDULE_UNIFY_REPLAY_AND_GAME

Item file restored 2026-11-12 from the ledger (RIMMANDRAKE_RECONCILE_FLOWWORKS_LEDGER_OPEN_WITHOUT_ITEM_FILE); the ledger held the item but its prose file was missing.

## spec

Move the hose tick schedule (World/PatchWorld/BuildWorld/CellChanged/MarkDirty, the 250-tick recheck + CorridorHash + CheckReplan, liquid settle) out of RM_MapComponent_Hoses / RM_LiquidNet into a Verse-free class that both the game and FlowWorks/Source/Replay/ReplayTick.cs compile, removing the mirror's drift risk (needed by advisory recommendation #2 anyway)

## what is left

- proposed: nothing recorded as owed beyond the title; read `rimflow show HOSE_SCHEDULE_UNIFY_REPLAY_AND_GAME` history before building.

## verify

Prove it where the title says (offline selftest, or the live proof named in the owed criterion); then `rimflow verify HOSE_SCHEDULE_UNIFY_REPLAY_AND_GAME --sha <sha> --level <L> --result pass --config <what ran> --evidence <path>` and `rimflow close`. Check `git log origin/main --grep=HOSE_SCHEDULE_UNIFY_REPLAY_AND_GAME` first: another commit may already do it.
