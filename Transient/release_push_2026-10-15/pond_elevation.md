# POND_ELEVATION_BUILD_LAKES_RUN_DEEP: progress (BENCH builder, 2026-10-15)

Owner by card 2026-10-15: "Deeper ponds (lakes deeper than 4) were held to next week by your card. Today? → Build it today"

## Status: BUILT offline. Source 30661193c0, DLL 5b84c1baf6 (clean export), published. NOT deployed, bridge untouched.

## Steps
- [x] 0 read the item, design §9, POND_BED step 2, and the climb/pocket readers
- [x] 1 kernel: NOT CHANGED, on purpose. Dry beds are not kernel cells (bedGrid, not depthGrid). No dug cell passes
      MaxDepth 4: `FirstCutDepth(12, ...)` is -1. So water height only matters at `RunsIntoBed`, which already compares
      heads. A canal beside a deep bed drains into the pond until its surface reaches the bed floor.
- [x] 2 the 4000-square cap is lifted for inland bodies. Edge-touching or truncated walks keep the old result (an ocean).
      An inland walk past the cap is re-walked up to `drainableLakeMaxCells` (default 40000).
- [x] 3 save/load: `RM_bedDepthRecord` (a map byte grid, LookByteArray), `RM_LiquidBody.levelUnit`, and packed footprints
      (4 bytes a square, deflated) for bodies over 4000 squares. No static tables.
- [x] 4 drawdown: the shallowest bed recedes first, then the old outside-in order. LIFO restore re-wets a square only when
      its whole bed fits. The selftest checks that drain→refill matches step by step.
- [x] 5 readers past 4: HollowDepth/DepthAt/ClimbDepthAt read the bed grid (byte). The pocket grid is gradual (≤1 inside,
      ≤4 anywhere), so "K≥MaxDepth climbs everything" stays true. Sink and wall faces clamp. Step cost past 4 is clamped to
      SUPERDEEP's terrain (before this it was free).
- [x] 6 terrain: `RM_Lakebed_Abyss` at bed ≥ 8. NO NEW ART: it is the deep lakebed texture with a `<color>` tint.
- [x] 7 Mod Settings: deepBedsEnabled (on), deepBedMaxDepth 20, deepBedCellsPerLevel 4, drainableLakeMaxCells 40000.
      With deepBedsEnabled off the model is the old one exactly.
- [x] 8 selftests: DeepBedChecks.cs (10 cases), plus updated pins in PondReturnChecks and ReviewFixChecks
- [x] 9 live proof script: northstar/deep_lake_proof.py and its offline selftest
- [x] 10 build, clean DLL, review marks, commit, push

## Coordinator's riders (same build)
- POND_CAPACITY_FIX_DOUBLING_BED: CLOSED at 5b84c1baf651. Capacity = levelUnit × beds. A limited truncated body's far
  squares bring capacity and stock with them.
- FILLIN_DISPLACE_FIX_DRY_POND_SNUB: CLOSED at 5b84c1baf651. A dry bed is a destination; the walk is bounded by the map.

## Perf (offline, SelfTest host)
39,381-square lake, deepest bed 20: walk 2.6 ms and beds 0.5 ms, both once per lake. Per draining pulse: 0.66 ms scan
plus 7.4 ms for 64 sheds, the worst case. A full lake with nothing dried skips the scan. Nothing runs per tick.

## Live proof command (owed)
Deploy FlowWorks, take the bridge, then run:
`python.exe src/RimMandrake/FlowWorks/northstar/deep_lake_proof.py --fresh-map`
Rows: DL_lake_over_4000_is_limited, DL_drained_reads_gradual_hollow, DL_shallow_dries_first, DL_colonist_free_in_bowl,
DL_colonist_walks_out, DL_refill_restores_exact_shape. Owed: DL_save_reload_bowl_identical.

## Remaining
- The live proof run (above) and the save/reload row.
- Review: still DIRTY (not fully reviewed): RM_MapComponent_Excavation.cs, RimMandrakeFlowWorksMod.cs,
  RM_NorthstarProofs.cs, RM_StockMath.cs, PondReturnChecks.cs, ReviewFixChecks.cs, Program.cs.
- Not mine, seen red during the run: RiverSwitchFlip_riverWorksEnabled/pathfinderAvoidsCurrents (a peer's uncommitted
  Rivers edit) and selftest_review_map (a peer's untracked RM_PitRamp textures).
