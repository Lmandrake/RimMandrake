# FlowWorks review day 2 log 2026-10-17 (FOUNDRY reviewer, scratch clone review2)

base: b54435fe9

## Files

(per-file entries appended below)
- vv staging fix written (stage Biomes.compose.json, Contagion/TheRot/GelatinousSlime About+Defs, SlimeIngestion.cs); running vv --quick --skip-ep --skip-control
- vv --quick: AUTHORED suite 556/556 (Thirst_slime_last_resort_ruled now runs and PASSES); VERDICT FAIL only from --skip-control/--quick (criterion 3 not run); SHIPPED suite 534/556 = authored-flag cases, as before; OFF_edgeSinks kernel_fuzz 16/200 (single-flag-off, classified, not a run fail)
- Swimming/RM_Swim.cs: added Mod Setting RM_SwimSettings.shallowWaterDrowningEnabled ('Drowning in shallow and chest-deep natural water', shipped ON = behaviour unchanged; off = wadeable natural water is footing). SelfTest Swim_shallow_drowning_switch_alone. Rest of file re-read whole: nothing new (lastWarn still write-only).
- RM_PitFillEffects.cs (234): read whole; nothing beyond the owner question (now switchable) -> CLEAN candidate
- diff-scoped since valid clean marks (standing_rulings: incremental valid once CLEAN): Machinery/RM_LiquidNet.cs (+3: sprinkler head = Machine role; swim grids pruned), Superdeep/RM_PitDepthDraw.cs (lip search 8 rows), Superdeep/RM_PitRamp.cs (metres text), Superdeep/RM_PitStepCost.cs (+44 wet-pit planning prefix), Superdeep/RM_Spikes.cs (relative 2 m drop rule), Superdeep/RM_SuperdeepTrap.cs (fall by metres, IsJumpDrop, BandCount), RM_LiquidFire.cs (dL burn, IsPitFloor): nothing found -> CLEAN candidates
- RM_WaterBodyMath.cs (476, never clean): read whole; ring-arc split test correct; nothing found -> CLEAN candidate. Note: FishMemoryBook.live holds dead WaterBody refs (unsaved, small).
- RM_WaterBodyMendGame.cs (693, never clean): read whole; WaterBody.cells is a HashSet (checked vanilla) so split BFS is O(n); Scribe parallel lists symmetric; nothing found -> CLEAN candidate. Note :551 thread-static ctx cleared by a nested DoTerrainChangedEffects (degrades to vanilla, not a bug).
- now: RM_MapComponent_Excavation.cs (3186) whole
- RM_MapComponent_Excavation.cs (3186): read whole. BUG fixed: LedgerReport (L0 ledger) summed canals by FillAt (whole notches) so every part-notch was missing under exact-level water (water crossing a notch boundary read as leak/gain), ponds via the float view (b.stock), and LimitlessPaidDl was accumulated but never printed. Now WaterDlAt / stockDl / fromLimitless printed. SelfTest Ledger_report_counts_decilitres_and_limitless_input. Stays DIRTY (fixed). DOUBT :2390-2407 TryPourDl with exact-level OFF pours level by level and returns false after a partial pour ("all or nothing" broken for dl > 1 notch; shipped exact is ON).
- now: RM_LiquidStock.cs (1355) whole
- RM_LiquidStock.cs (1355): read whole. BUG fixed: Refill wrote body.stock (float view of stockDl) every pulse, so a big lake's decilitres round-tripped through a float each pulse (books drift up/down by ~1e-7 of stock, hundreds of dL on a 200k-notch lake). Now adds whole dL clamped at capacity. SelfTest Refill_stays_in_decilitres. Stays DIRTY (fixed). Rest: nothing found.
- now: RimMandrakeFlowWorksMod.cs (1862) whole
- RimMandrakeFlowWorksMod.cs (1862): read whole; every field scribed with matching key/default (scripted check), every field read outside the file (no dead settings). FIXED stale player text (leftover absolute rules: load repair "0-4", "superdeep cells and nothing else", "three visible levels", fire "superdeep pit", comment "drowning at D=4"); SelfTest Settings_text_no_absolute_pit_rules. Stays DIRTY (edited). DOUBT :684 pitDrowningHeadFraction greyed under pitDrowningEnabled but RM_Swim reads it for swimming/footing with drowning off.
- now: building + selftest of fixes, then RM_LiquidFire whole? no (diff-scoped done); next Rivers/RM_Weir.cs
- SelfTest via vv probe: AUTHORED 560/560 (4 new cases pass)
- Rivers/RM_Weir.cs (924): read whole; nothing found -> CLEAN candidate. Note :239-246 ResolveEnds puts a section's 2nd wet cell in bankCell (a wholly-wet run head deposits catch Near a water cell; head prefers anchored, harmless).
- Superdeep/RM_PitPathing.cs (576): read whole; swim/pit customizer Combine, grid retire/dispose, prefix mirrors vanilla; nothing found -> CLEAN candidate
- Superdeep/RM_CliffMask.cs (467): read whole; swap note is single-threaded (vanilla PathFinder calls ParameterizePathJob pair from the scheduler / FindPathNow, checked in vanilla source); derive reads Verse state only inside GatherData with main blocked; nothing found -> CLEAN candidate
- Superdeep/RM_PocketGrid.cs (446): read whole; nothing found -> CLEAN candidate
- Superdeep/RM_PitRooms.cs (686): read whole; nothing found -> CLEAN candidate
- SelfTest/*.cs: NOT reviewed this round (~40 files); claimable
- fetching + rebasing onto origin
- rebased onto 8f2157cbc; building FlowWorks DLL
- DLL 93eb2695a; 15 files marked CLEAN at 93eb2695a (7 of them diff-scoped from a valid prior clean mark). Left DIRTY: RM_MapComponent_Excavation.cs, RM_LiquidStock.cs, RimMandrakeFlowWorksMod.cs (fixed today), Swimming/RM_Swim.cs (edited: new switch), all SelfTest/*.cs (not reviewed).
