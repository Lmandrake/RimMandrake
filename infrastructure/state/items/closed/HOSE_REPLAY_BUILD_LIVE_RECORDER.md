---
state: proposed
needs: game-up
---

# HOSE_REPLAY_BUILD_LIVE_RECORDER

Item file restored 2026-11-12 from the ledger (RIMMANDRAKE_RECONCILE_FLOWWORKS_LEDGER_OPEN_WITHOUT_ITEM_FILE); the ledger held the item but its prose file was missing.

## spec

Hose replay: record a live RMREPLAY 1 trace (map snapshot + cell/lay/cut/settings/move events) from RM_MapComponent_Hoses in game, so src/RimMandrake/Utils/hose_replay.py run --trace replays a real colony, not only the generated corpus. Touches the FlowWorks DLL: wait until the live-tuning of RM_MapComponent_Hoses.cs is committed

## what is left

- proposed: nothing recorded as owed beyond the title; read `rimflow show HOSE_REPLAY_BUILD_LIVE_RECORDER` history before building.

## verify

Prove it where the title says (offline selftest, or the live proof named in the owed criterion); then `rimflow verify HOSE_REPLAY_BUILD_LIVE_RECORDER --sha <sha> --level <L> --result pass --config <what ran> --evidence <path>` and `rimflow close`. Check `git log origin/main --grep=HOSE_REPLAY_BUILD_LIVE_RECORDER` first: another commit may already do it.
