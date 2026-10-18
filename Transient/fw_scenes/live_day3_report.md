# FlowWorks live day 3 — FOUNDRY, 2026-10-18

Bridge taken by FOUNDRY 2026-10-18T00:53Z (last foreign call 00:36:49Z, driver lock FREE).

## 1. Fetch, DLL check, deploy, relaunch
- Ran from scratch clone `/home/mandrake/rm/scratch/FOUNDRY/live3` at origin/main 7f4d872d0. Latest FlowWorks DLL on
  origin = 71aaadd97 (review day 3, on 646a91a38; includes P13 247ce987c and the shallow-drowning switch 93eb2695a).
- Deployed was 05fabdc5 (BENCH's thirst DLL); repo 6df49ba0; `dll_source_stamp.py check`: MATCH. Game closed 00:56Z,
  Saves backed up whole to `C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Saves_backup_FOUNDRY_20261018T0100Z`,
  `deploy_custom_mods.py --mod FlowWorks --apply`: 2 files (DLL, srchash), VERIFIED; deployed sha = repo sha, srchash identical.
- BENCH's 22-mod walk list saved as `infrastructure/state/modlists/ModsConfig_BENCH_walk22_before_fw11_2026-10-18.xml`;
  live list set to the 11-mod flowworks list (harmony, core + 5 DLC, rimbridgeserver, flowworks, gimmesomeslack,
  simplecamerasetting). companion_profile.json expiresUtc 02:00Z -> 2026-10-18T14:00:00Z (only that field).
- Launched via Steam 00:57Z, bridge up 00:58Z (~70 s). Player.log clean: FlowWorks Harmony patched 78, missing 0; hose
  essential patches all present; no exception at load.

## 2. validation_v2 + river extension chain
- `validation_v2.py --live` (calm saved site), stdout `Transient/fw_scenes/live/day3/validation_v2_stdout.txt`, result
  `src/RimMandrake/FlowWorks/northstar/validation_v2_result_20261017T180214.json`:
  **32 PASS / 24 FAIL / 5 UNMEASURED vs the 61/0/0 baseline (20261011T151120, mod hash 76c06af4 -> e98755c7).**
  `--compare`: 11 of 21 zero-tick rows differ. This is the first validation_v2 run since P3..P13; nothing below is
  diagnosed to a root cause yet. Grouped by what they share:
  - **Pond capacity (P11 shore shelf?)**: S3_classification: painted 1-cell pond W2 cap 1.0 (want 2), W2R 4 cells cap 4
    (want 8) = 1 level a square, not ShallowBedLevels 2. Consistent with P11's 0.5 m shore shelf on every lake's outer
    ring (a small painted pond is all ring). If so the script's expectation is stale (HARNESS), and it cascades:
    E3b_recession_shipped, E3_budget_exhaustion, E3n_budget_off_supplies, E6_rain ("pulse-0 vector != oracle state"),
    G_every_cell_vs_oracle, E2_rerun_determinism.
  - **Flow/scheduler**: E2_channels_fill_every_direction (west never full: None), E5_sink_drains, E5n_sinks_off,
    E5_sinks_back_on (+6.62 vs oracle +7), E4_engine_off ("OFF for 0 ticks"), E1c_cadence_real_scheduler (nextPulseTick
    advances [0, 60]), E4_engine_on_scheduled, E6n_rain_toggle_off. Not classified.
  - **Pits (P7 relative rules?)**: P1_width_matrix (every small pit "held False want True"), P4_ladder_frees,
    P4f_ladder_frees_forced, P5n_own_faction_carveout, X2/X3 (sink 0 -> 0, drawDz 0), X4 (colonist on D=4 drawn 0 down).
    Under P7 a D=4 (2 m) pit is judged against body height, so "held" rows may be stale expectations; but drawDz 0 on a
    D=4 square is a draw-depth regression unless P7 removed the sink. Not classified.
  - X6_two_fluids_distinct, X10_canal_fire (2 cells still alight at the end): not classified.
  - UNMEASURED: E7a/E7b/E8 (jobs never started: curJob None for 2280 ticks), P4b (HARNESS), E9 (log cap).
- River extension chain: **NOT RUN (SITE)**. `extension_proof.py --live --site river` loads the clean saved river site,
  which was saved on a list with RSW creatures: on the 11-mod list it logged "Could not load reference to ...
  Corpse_RSW_*" then `Root level exception in Update(): NullReferenceException at Verse.MapDrawer.WholeMapChanged`
  every frame (belt_watchdog WEDGED). Killed and relaunched. `river_site.py` (the found-a-river path) then tried 20 river
  tiles on the quicktest world: every one `fast=0` (all size 1.00/0.74 rivers; day 2 found its fast lane only on a
  size-1.89 river), "no river tile with a current"; the second try reused the same world (0 tried).

## 3. water_scenes_walk S1..S6 + level-surface bar
DLL 6df49ba0 (71aaadd97), 11-mod list, `go S<n> --fresh-map`, shipped settings bar the scene file's exceptions.
Stdout `Transient/fw_scenes/live/day3/run_S<n>_stdout.txt`; screenshots and logs `Transient/fw_scenes/live/S*`.
(The first S1 attempt CRASHED on a game stuck in MapInitializing after river_site's 20 generated maps; relaunched, rerun.)

**Totals: 32 MATCHES, 6 DIFFERS, 1 UNMEASURED (S3.e, not staged), 3 OPEN RULINGS (S3.Q1, S4.Q1, S6.Q1). Every level row
(.lvl, 8 of them) MATCHES: worst gap 0.0001 m.**

| scene | rows |
|---|---|
| S1 | a, b, c, d MATCH |
| S2 | lvl, a, b, c, d, lvl.end MATCH (day 2's S2.d harness DIFFER is gone) |
| S3 | **a, b MATCH (pump fix: all 6 canal squares 10,000 dL = 6,000 L to the brim, first at pulse 8)**, d, lvl MATCH; **c DIFFERS**; e UNMEASURED |
| S4 | a, b, e, c, d MATCH |
| S5 | lvl.A, lvl.E, lvl.F, lvl.G, d, e, f, g MATCH; **a, b, c, h, i DIFFER** |
| S6 | lvl.run1, a, b, c, lvl.run2 MATCH (reload equal to the dL; run 2 = run 1 at pulse 30) |

**S3.c DIFFERS = MOD (hose leftover lost, announced):** pond lost 69,750 dL, canal gained 60,000, hoses 0. Player.log:
`a spill of RM_Liquid_FreshWater at (55, 0, 32) found no filth cell and no water within 6.9 squares; 9750 units were
lost (announced)` plus `conservation exception: 1.0 fill level(s) overflowed ... destroyed`. The pump keeps lifting
(pump.moved 7) after the canal is brim-full; the 7th level sits in the hose, and when the hose drains the full canal
has no room and the source pond is further than 6.9 squares, so 975 L leave the world. Better than day 2 (announced,
counted), but the S3 doc wants canal + hoses = pond loss. Fix candidate: a pump stops when its outlet has no dL room,
or the leftover returns to the body it was drawn from.

**S5 a, b, c, h DIFFER = the ponds are not 2 m deep any more (P11 floors form on water painted mid-game).** The walk
paints WaterDeep ponds after map creation; they get a lake floor with the 0.5 m shore shelf. ProofReadout over pond A
(3x3, scene says 2 m, 36,000 L): 8 ring squares `Hole 0.5 m`, centre `Hole 1.5 m`, stocked 110,000 dL (11,000 L).
1-square ponds B, F, G: 10,000 dL (0.5 m). Day 2 (pre-P11) read `Hole 2 m` on all 9. The level logic itself holds: pond
and canal share one surface (-0.263 m), S5.i conserves to the dL (end 6 x 1,620 dL = 0.333 m level, the redrawn level
row's numbers) and S5.e/f/g match. S5.i reads DIFFERS only because the pond held 10,000 dL, not 40,000. The same
cause explains validation_v2 S3_classification (W2 cap 1, W2R cap 4) and the oracle-out-of-sync rows. Owner/spec
question: should a lake floor form on water painted or created mid-game? Either the floor waits for map creation /
first load only, or the scene and validation staging must set the shelf off.

Level-surface bar (`ProofLevelSurface("-")`, whole S6 map): 6 bodies, worst 0.0001 m. PASS.
`Transient/fw_scenes/live/day3/level_surface_S6.txt`.

## 4. Live proofs (P12, P7, P5, pump/hose/fill-in, river sweep, P13)
New script `src/RimMandrake/FlowWorks/northstar/depth_rebuild_proofs.py` (sections swim, drown, p7, p5; one plot each,
prepare_site, every touched setting restored and read back). Results: `Transient/fw_scenes/live/day3/proofs_swim.json`,
`proofs_drown_p7_p5.json`, `proofs_p5.json` (+ `_stdout.txt`); hand trace `armour_midlake_trace.txt`.

**P12 swimming (DEEP_WATER_BUILD_SWIM_OR_SINK), natural lake = painted WaterDeep 9x4 (readout `Hole 2 m · Water 2.00 m`):**
- PASS colonist reaches the lake middle: `SWIM class=Swimmer deepCell=True pathCost=60 headUp=True water=2.00`, exhaustion rising.
- PASS climbs out the far side (end = target, 1,203 ticks).
- PASS warned before going under: message at 3,000 ticks, verbatim "Grill is tiring in deep water: about 29 minutes of
  swimming left before going under." (The marine-armour staging used wrong defNames on the first runs; armour was worn
  by hand afterwards: `load=0.41 enduranceH=0.70 costX=2.27`.)
- PASS drafted and held mid-lake goes under and drowns: exhaustion 1.000, headUp False, RM_PitDrowning 0.26 -> 0.52 ->
  0.77 per 750 ticks, pawn dead by ~2,750 ticks after (about one game hour, the spec's number). On the lake's EDGE row the
  same exhausted swimmer never drowned in 6,000 ticks (exit in reach, rule V2).
- PASS land animal walks around: tame muffalo sampled every 60 ticks, 0 samples in the lake, arrived round it.
- PASS mechanoid refused: Militor `class=None` (sinks), drafted order to the middle CanReach false.
- PASS prisoner in a flooded sheer pit (3.5 m hole, 2 m water): swims (headUp True, exhaustion 0.31 after 1,500 ticks),
  `CLIMB held=True trapped=True`, still in the pit, alive.
- PASS swim master off/on mid-game (same pawn in the lake): on pathCost 60 deepCell True -> off 10000 False -> on 60 True
  (field write + RM_SwimWater.Reapply, which is what WriteSettings calls).
- **FAIL = MOD: a dug, brim-full 3 m reservoir is not swimmable.** 9x5 dug 6 notches, filled (`Hole 3 m · Water 3.00 m`):
  order to the middle CanReach false; a pawn standing in dug water reads `deepCell=False pathCost=300`. P12's scope says
  lakes, dug canals and pits. In a dug PIT a pawn does swim (exhaustion rises), but the path grid never opens dug water.
- Instrument note: ProofDrown prints `water=0.00` on natural water even while RM_PitDrowning rises (it reads dug water only).

**Shallow-water drowning (RM_SwimSettings.shallowWaterDrowningEnabled), for the owner's ruling.** A colonist downed
(no bleeding) on painted WaterShallow (readout `Hole 1 m · Water 1.00 m`), 2,500 ticks (1 game hour):
- ON (shipped): RM_PitDrowning +0.0867 per 250 ticks (0.087, 0.173 ... 0.840 at 2,500): dead at about 2,900 ticks
  (~1.15 game hours) if nobody rescues them.
- OFF: no drowning hediff at all in 2,500 ticks; the pawn lies there alive.

**P7 relative pit rules (PIT_RULES_REWIRE_RELATIVE_NOT_ABSOLUTE L2):**
- PASS 7 m fall: forced landing (ProofForcedFlyer) 2 m pit fall=4.9, 7 m pit fall=17.0, ratio 3.47 (V3 wants 3.5:
  2 m + 50% a metre past it), alive.
- PASS prisoner held in a sheer 1.5 m pocket: `CLIMB held=True trapped=True`; `ROOM pitRoom=True proper=True`
  (prison=False: no bed/prison designation staged); stays in for 1,200 ticks.
- PASS shooting across a 2 m trench: attack_target_probe picks the hostile across it.
- PASS shooting between two 7 m pits (7 m of ground in the line): no target picked.

**P5 deeper digs (PIT_DEPTH_WIDEN_TWO_METRES_TO_EIGHT):** the 4/7/7/4 square by the drive tool (not the designator: one
square to 8 m is ~3.3 digger-days), filled: 12 ring squares `Hole 4 m · Water 4.00 m (8,000 L)`, 4 core squares
`Hole 7 m (ledge 4 m) · Water 7.00 m (14,000 L)` = **152,000 L, one body, gap 0.0000 m. PASS.**

**Pump / hose / fill-in fixes (from section 3):** pump into a canal PASS (S3.b: 6,000 L to the brim, was stuck at 1,000 L);
fill-in of a sheet PASS (S5.e "destroys nothing", S5.f exactly 1,000 L for the middle cell); hose leftover: now announced,
but 975 L still leave the world when the canal is full (S3.c, a remaining MOD finding).

**River sweep identity (RIVER_SWEEP_FIX_COLONISTS_RETURN_AS_NPCS):** river map found by `river_site.py --allow-no-fast`
(new opt-in: the quicktest world held no river with a fast lane; R3 needs edge current only), tile 830.
- `river_scenes_walk.py go R3`: R3.a, R3.b, **R3.c MATCH (day 2 DIFFERED)**: 3 colonists swept, all 3 back with the same
  ThingID and faction PlayerColony. R3.d UNMEASURED (letters not read). `Transient/fw_scenes/live/day3/rivers_R3_stdout.txt`.
- New `sweep_identity_proof.py` (`sweep_identity.json`): colonist PASS (same ThingID, PlayerColony, back on the map);
  tame muffalo (downed so the current can take it; standing it walks out) PASS, same ThingID, PlayerColony, back on the map.
  **Prisoner FAIL = MOD:** gone from the map within 250 ticks of standing in edge water, never entered the swept book (book
  counted 2 for 3 gone), and after `ProofSwept return` it is still off the map (same ThingID, faction, still Prisoner,
  no position). A prisoner the river takes is lost.

**P13 fish / reeds (FISH_ROLL_MEND_PONDS_BORN_BARREN):** `proofs_p13.json`.
- Reeds through a drain/refill (drive tool, not a pump): 6 of 6 alive after 600 dry ticks, after refill, and 25 h later.
  **Not evidence for the grace mechanism:** the CONTROL run (6 reeds left dry 25 h, past the 24 h grace) also kept 6 of 6,
  so on a dug canal reeds never die when it dries at all. Recorded as a note, not a verify.
- Fish rows (roll as a pond grows, dry-and-refill keeps fish/zone, split pond): **UNMEASURED**. The bridge cannot read
  vanilla WaterBody fish types or fishing zones (owed: a ProofWaterBody static surface in RM_WaterBodyMendGame.cs).

## 5. Lake floor look (flat + mountainous)
New `src/RimMandrake/FlowWorks/northstar/lake_floor_stage.py`: founds a map on a lake tile, local noon (clock jump), each
lake photographed full and drawn down to 35% (ProofSetBodyFraction), captioned panels with the measured floor.
**Look here: `D:\Luke\dev\RimMandrake\Transient\fw_scenes\lake_floors\live\index.html`** (26 panels under `annotated\`).
Keeper save: `RM_fw_lake_floors_flat_hills_mountain_20261018.rws` (all three maps).
- Flat (tile 2120, BorealForest, LakeWithIsland): 5 lakes (710/430/125/24/14 squares), every floor 0.5 m (shelf) or 1 m.
- Hills (tile 6281, LargeHills, Lake): 6 lakes (889..94 squares), every floor 0.5 or 1 m.
- Mountainous (tile 24575, TemperateForest, Chasm+Caves+Lake): a 14,974-square lake, floors 0.5..10 m (6.5-8.5 m: 2,000
  squares; first generation of the same tile read 13.5 m deepest), 62.9 million L; plus one 14-square pond at 1 m.
- **Finding (spec question):** every Player.log "lake floors" line on flat and hill maps today says "(1 m deepest)". Vanilla
  lakes there are WaterShallow only, so P11 has no deep water to give a floor: the offline preview's "flat mean deepest
  2.6 m / hills 4.3 m" does not happen live. Only vanilla deep water (the chasm lake) gets the deep floor. And drawn down
  to 35% the deep lake still shows 14,174 of 14,974 squares as their original water (800 mud on the shelf): the floor
  is barely visible from above at that level.

## 6. raid_trench re-stage
`raid_trench_proof.py --fresh-map --direct` (6 PirateYttakin, LordJob_AssaultColony, storyteller off, 15,000 ticks):
`Transient/fw_scenes/live/day3/raid_trench_direct.json`.
- RAID_island_sealed PASS (person-band east lip 0xCB, derived).
- **RAID_outcome STALL_FAR** (day 2: LEFT + SHOT_ACROSS, all colonists downed): the 6 raiders never moved (late move 0.0
  per raider per sample), never came within 15 squares, no colonist downed. A FleshbeastAssault lord (Entities, 2) also
  sat on the map. So under the new rules the raid did not even approach; whether the island is now unreachable to the
  raid lord (no target, so it stalls) is not measured.
- MASKSWAP_no_wall_crossing UNMEASURED again (0 raiders within 15 squares; 60 churn rebuilds, no error).

## Bugs found (MOD unless marked)
1. `SWIM_DUG_RESERVOIR_NOT_SWIMMABLE`: brim-full dug water (3 m) has `deepCell=False pathCost=300`, CanReach false; only
   natural deep water opens for swimmers.
2. `SWEEP_PRISONER_LOST_OFF_MAP`: a prisoner taken by an edge current is never booked and never returned.
3. `HOSE_LEFTOVER_LOST_WHEN_CANAL_FULL`: pump keeps lifting into a full canal; the hose leftover (975 L in S3) leaves the
   world, announced. S3.c.
4. `P11_FLOOR_ON_PAINTED_PONDS` (spec question): water painted or created mid-game gets a P11 floor with the 0.5 m shelf,
   so the scenes' and validation_v2's "2 m" ponds hold a third of their water. Explains S5.a/b/c/h/i and several v2 rows.
5. `LAKE_FLOORS_SHALLOW_LAKES_STAY_ONE_METRE` (spec question): live flat/hill lakes are WaterShallow and keep 1 m floors.
6. `VALIDATION_V2_REBASE_ON_P3_P13`: 24 FAIL / 5 UNMEASURED, not yet sorted into MOD vs stale expectation (section 2);
   the flow-scheduler rows (E4_engine_off "OFF for 0 ticks", E1c cadence) and X2-X4 (pawn drawn 0 m down in a D=4 pit)
   look most like real regressions.
7. HARNESS/instrument: ProofDrown prints water=0.00 on natural water while drowning runs; P13 has no fish read surface;
   the saved river site cannot load on the 11-mod list (RSW corpses, then MapDrawer NRE every frame).
8. P13 reeds do not die on a dried dug canal even past grace (control), so the grace path was not exercised.

## Not run / claimable
- The river extension chain (`extension_proof.py --site river`): blocked by the saved river site (item 7); it could run on
  the `--allow-no-fast` site with `--current-map`, but its fast-lane rows would read UNMEASURED.
- P13 fish rows (needs the read surface); P5 "dig to 8 m by the designator" (3.3 digger-days; drive tool used instead);
  S3.e round trip.

## Bridge
Released 02:17Z. Game left RUNNING on the 11-mod flowworks list (hills lake map current), storyteller re-enabled.
BENCH's 22-mod walk list NOT restored (saved at `infrastructure/state/modlists/ModsConfig_BENCH_walk22_before_fw11_2026-10-18.xml`).
companion_profile.json expiresUtc now 2026-10-18T14:00:00Z.
