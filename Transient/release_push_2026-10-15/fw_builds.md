# FlowWorks offline builds — release push 2026-10-15 (BENCH builder)

Scope: gap_list.md §2 items marked "build". Each to "built, live proof owed".
Not built here (owner decisions pending): POND_ELEVATION_BUILD_LAKES_RUN_DEEP,
DEEP_DIG_BUILD_DROIDS_TAKE_THE_SHOVEL, any Mod Settings default.

| # | item | state | sha | live proof command |
|---|---|---|---|---|
| 1 | LIQUID_BOTTLE_LOOP_1 (fill job) | built, live proof owed | 5455139557 | `extension_proof.py --live --chains toggle_bottle_loop,toggle_bottle_dirty,bottle_revert` |
| 2 | RIVER_STEAM_ANIMATION_1 (steam predicate) | built, live proof owed | 77003bb595 | `extension_proof.py --live --chains toggle_river_steam` on a Pyrelands river map (on/off) AND on any other map (gate) |
| 3 | LIQUID_FIRE_QUEUE_ORIGIN_1 A1-A3 rows | built, live proof owed | 572f02f625 | `extension_proof.py --live --chains fire_queue_origin` (~4 min) |
| 4 | PIT_POCKET_GRID terrain base cost (RM_PitTrapMath.cs:470) | built, live proof owed | 4e03b77dd5 | `python.exe src/RimMandrake/FlowWorks/northstar/climb_proof.py --origin X,Z` (row CLIMB_step_cost_slow_at_K) |
| 5a | RAID_DETECTOR_REPAIR_FLOOD_NOT_A_RAID | skipped: already built + flood half live PASS (ce40347df6) | - | one governed chain with a real raid (`jawa/fire_raid` dryRun false) to show raid_arrived still fires |
| 5b | DIG_RESET_REPAIR_ROLLED_DEPTH_REMEMBERS | built, live proof owed | 8da362e5a9 | `extension_proof.py --live --chains dig_finds` run TWICE on one map (2nd run must still find) |

## Notes
- 1: the fill job was already FIXED (cf1e75d26) and PASSED live 2026-10-13 (`toggle_bottle_loop` 2/2,
  Transient/night_20261013/tankloop_live.md); gap_list's "never yields a filled bottle" is the 09-25 run. What was
  unbuilt was the drink/dirty/wash rows: `toggle_bottle_dirty` had two `_owed` placeholders. Now three rows
  (bottle_dirty_on, bottle_wash_returns_clean, bottle_dirty_off) via new `RM_NorthstarProofs.ProofBottle`
  (vanilla Thing.Ingested -> the shipped residue doer). bottleDirtyStageEnabled left EXTENSION_TOGGLES_OWED.
  Blood rot (A2 half) stays owner-blocked (no fill source for blood).
- 2: `RM_RiverSteamProof.ProofSteam` (" " reads, "rescan" re-runs the vent scan) over new counters in
  MapComponent_RiverSteam (vents due / ribbons thrown, unsaved). `toggle_river_steam`: river_steam_on/off (needs a
  biome with RiverSteamBiomeExtension) + river_steam_biome_gate (needs one without); the half a map cannot show reads
  UNMEASURED naming the map it needs (new `_unmeasured_if`). riverSteamEnabled left EXTENSION_TOGGLES_OWED. A3 (owner
  look) unchanged.
- 3: new chain `fire_queue_origin` (plot B): fire_torch_advances_pending (A2, slow tar fuse at multiplier 0.05 + a
  real vanilla Fire via `ProofTorch`, twin fuse as control), fire_front_survives_save (A3, Scribe write/read of the
  map's RM_LiquidFire via `ProofFrontRoundTrip`; a full game reload is NOT driven), fire_reach_capped_at_source (A1,
  chemfuel run into a 5x5 tar pond at sourceFireReach 1, `ProofSourceSpread` far=0). Read surfaces ProofCell /
  ProofSourceSpread added. Live risk: tar may flow into the run's mouth before the chemfuel fill (a FAIL there is SITE).
- 4: already wired. RM_Patch_PitStepCost.MaskedStepCost calls RM_PitTrapMath.StepCost whenever RM_CliffMask.On
  (PIT_CLIFF_MASK_BUILD_ASTAR_LEARNS_WALLS, closed 695812d5ec); the :470 "not yet" comment was stale and is corrected.
  What was missing was a script row: ProofClimb "cost:fx,fz;tx,tz;pawnId" prices the walked step through the patched
  PathGrid.CalculatedCostAt for that pawn; climb_proof.py row CLIMB_step_cost_slow_at_K (slow at s=K, 0 along a floor,
  one climb under K), verdict selftested.
- 5a: nothing to build. The detector fix exists (flood letter no longer raid_arrived; offline control
  selftest_detectors.py "a real raid-labelled ThreatSmall still fires"); verify run-1 PASSed live at ce40347df6.
  Only the live real-raid half is owed (its own NEXT note).
- 5b: `RM_DigDiscoveryState.ResetRolled` + ProofResetRect forgets the plot's rolled depths ("RESET ... rolled=n
  left=n"); `_expect_cut_found`'s no-find branch is FAIL again (was UNMEASURED); selftest probe updated.
