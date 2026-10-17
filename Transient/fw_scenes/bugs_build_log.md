# FlowWorks live-bug fixes — FOUNDRY offline build log (2026-10-17)

Items: PUMP_CANAL_FEED_FIX_ONE_NOTCH_ONLY, HOSE_LEFTOVER_FIX_NO_VANISHING_LITRES, CANAL_FILLIN_FIX_SHEET_WATER_DESTROYED.
Source: `Transient/fw_scenes/live_day2_report.md` findings 1-3. No bridge, no game.

## Stage 0 — orientation
- DONE. Base origin/main cdc59f211 (+a00177add). Root causes read from source:
  - PUMP: every whole-level writer asks `RoomNotches(i)` (whole notches of room in ONE square). Once a canal holds a
    sheet (1,000 L over 6 squares = 1,667 dL each in a 1-notch canal) no square has a whole notch of room, so
    `CanPourLevel` is false everywhere, `RM_LiquidSpill.Outlet` answers Blocked and the world-to-world move (whole level,
    `TryTakeLevel`/`TryPourLevel`) never runs again. Same wall for pour-mode, Dump drains, Flow taps, Level Holder.
  - HOSE: `PlaceHeld` pours whole levels only (refused, same wall), then `Spill`: the outflow square is canal water, so
    `ReturnToPond` skips it (dug) and no filth lies on water: `Unplaced`, WarningOnce, 973 L gone.
  - FILL-IN: `FillIn` destroyed `partGrid` on a fill to the surface ("the part has no level to travel as") and
    `Displace` moved whole levels only.

## Stage 1 — pump into canal (root cause, fix)
- DONE (source). New Verse-free `Source/RM_LevelPour.cs`: `Spread` (BFS from the square, cardinal N E S W, nearest first,
  each square up to its dL room; pond squares collected, never conducted) + `KeptOnFillIn`. Excavation: `PlanPour`,
  `PourRoomDl`, `TryPourDl` (all or nothing, spreads over the canal the square joins, cap 1,024 squares),
  `ReturnRoomDl`/`TryReturnDl` (pond in dL); `CanPourLevel`/`TryPourLevel` use them under exact-level water (whole-notch
  path unchanged when off). Stock: `SupplyDl`, `TryDebitDl`, `CreditDl`. Pump world-to-world moves
  `min(level, source dL, outlet room dL)`; outlet candidacy = any dL room. Exact-level off: whole levels only, as before.

## Stage 2 — hose leftover accounted
- DONE (source). `PlaceHeld`: into the water it lands in, in dL (canal spread / pond), then `Spill`. `Spill`: over water or
  a wall -> that water, then the nearest canal/pond of its kind within 6.9 squares (`PlaceNearby`); on dry ground filth as
  ruled; the share no filth records -> nearby water; truly nowhere -> `ReportLiquidLost` (counted with the overflow,
  player message in litres, `LostUnits`). Conserving default; owner question noted on the item.

## Stage 3 — fill-in displaces a sheet
- DONE (source). `FillIn` keeps `min(water, newD notches)`, displaces the rest in dL (all of it to the surface / a bed);
  `Displace(dl)` = `RM_LevelPour.Spread` (phase 1 canal squares) then ponds in dL (`CreditDl`); `ReportOverflow` in
  litres. Mod DLL compiles (winbuild).

## Stage 4 — tests (SelfTest, oracle differential, vv_shipped_matrix, run_selftests)
- SelfTest 521/521 (+7 `LevelPour_*`: spread order + the whole-notch stall as a can-fail; S3 pump fills 6,000 L to the
  brim; S5.G redrawn: 4,000 L level over six squares at 0.333 m, pond dry; hose 973.4 L onto a sheet lands; S5.C sheet
  filled in, 0 destroyed; S5.D exactly 1,000 L; production call sites). 8 source-pattern checks re-pointed to the dL code.
- Oracle differential: new mode `exactops` (plain scenes + 1-4 pours of up to 2 notches / fill-ins between pulses; kernel
  side `LevelOps` over the production `RM_LevelPour`, Python side `level_water.spread/pour/fill_in`): 3000/3000 agree.
  Coverage over the 3000: 3,776 pours (380 partly placed), 3,567 fill-ins (641 of a part-notch sheet), 172 overflows.
  Harness fix found by it: a square filled in to the surface leaves the pulse's seeds (production removes it from
  excavatedCells; the kernel given an undug seed diverged, seed 1707).
- Full differential 3000/3000 in depth, surface, levelset, shipped, pond, exact, exactpond, exactops.
- vv_shipped_matrix --skip-ep: SHIPPED kernel_fuzz 0/10000, fills_from_limitless 0/10000, surface_random 0/1000, seq_* 0,
  hose 0/2798, trail 0/1500; control 194/2000 vs 0/2000. VERDICT FAIL only on AUTHORED `Thirst_slime_last_resort_ruled`
  (known, BENCH). OFF_edgeSinksEnabled kernel_fuzz 142/2000 (known). No LevelPour_* red in the SHIPPED suite; under
  OFF_levelExactEnabled 3 LevelPour_* go red with the Exact_* cases (they need exact-level water by design).
- run_selftests --only (12 FlowWorks tests): 12/12 after re-pointing call_sites P7 (displacement's palette claim) to the
  dL code. selftest_hose_port and selftest_extensions were PASS here (red at the a54be1db6 baseline).
- After rebase on origin (P12 0e59ee10c..8dac8740b): SelfTest 529/529 on the merged tree, DLL rebuilt there.

## Stage 5 — publish
- Source b5459caa0, DLL e40b3d972: PUBLISHED from scratch clone /home/mandrake/rm/scratch/FOUNDRY/bugs. Item notes filed.
- Defaults (veto-able): pump fills a canal to the brim (a pump lifts), not to its source's level; hose leftover goes
  to water first (landing square, then nearest canal/pond within 6.9 squares), filth only on dry ground after that,
  announced loss only when nothing takes it (owner question on the item: is filth an allowed destination?).
- Not mine, left: RIVER_SWEEP_FIX_COLONISTS_RETURN_AS_NPCS. HARNESS: water_scenes_walk still reads whole notches (S3/S5/S6
  rows); scene doc rows S5.a/S5.c/S5.G ("never a 5th cell") are whole-notch pictures, obsolete under P3.
- Moved to scratch clone /home/mandrake/rm/scratch/FOUNDRY/bugs (another builder's uncommitted lake-floor WIP shares RM_LiquidStock/Excavation in the FOUNDRY clone); my hunks removed from that clone, its DLL rebuilt on its own tree.
