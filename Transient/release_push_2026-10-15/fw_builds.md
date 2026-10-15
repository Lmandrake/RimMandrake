# FlowWorks offline builds — release push 2026-10-15 (BENCH builder)

Scope: gap_list.md §2 items marked "build". Each to "built, live proof owed".
Not built here (owner decisions pending): POND_ELEVATION_BUILD_LAKES_RUN_DEEP,
DEEP_DIG_BUILD_DROIDS_TAKE_THE_SHOVEL, any Mod Settings default.

| # | item | state | sha | live proof command |
|---|---|---|---|---|
| 1 | LIQUID_BOTTLE_LOOP_1 (fill job) | built, live proof owed | (this commit) | `extension_proof.py --live --chains toggle_bottle_loop,toggle_bottle_dirty,bottle_revert` |
| 2 | RIVER_STEAM_ANIMATION_1 (steam predicate) | pending | | |
| 3 | LIQUID_FIRE_QUEUE_ORIGIN_1 A1-A3 rows | pending | | |
| 4 | PIT_POCKET_GRID terrain base cost (RM_PitTrapMath.cs:470) | pending | | |
| 5a | RAID_DETECTOR_REPAIR_FLOOD_NOT_A_RAID | pending | | |
| 5b | DIG_RESET_REPAIR_ROLLED_DEPTH_REMEMBERS | pending | | |

## Notes
- 1: the fill job was already FIXED (cf1e75d26) and PASSED live 2026-10-13 (`toggle_bottle_loop` 2/2,
  Transient/night_20261013/tankloop_live.md); gap_list's "never yields a filled bottle" is the 09-25 run. What was
  unbuilt was the drink/dirty/wash rows: `toggle_bottle_dirty` had two `_owed` placeholders. Now three rows
  (bottle_dirty_on, bottle_wash_returns_clean, bottle_dirty_off) via new `RM_NorthstarProofs.ProofBottle`
  (vanilla Thing.Ingested -> the shipped residue doer). bottleDirtyStageEnabled left EXTENSION_TOGGLES_OWED.
  Blood rot (A2 half) stays owner-blocked (no fill source for blood).
