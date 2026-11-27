# FlowWorks 0.1.0 blind challenge, cycle 5 (judge run judge-1795794888)

## Start time
2026-11-27T15:56:26Z (UTC), before any mod file was opened.

## Changed files to bars
Mechanical: `git diff --name-only a05f0a3b6e origin/main -- <the brief's paths> | grep -v /blind_challenge/` lists 2304 files
[measured], of which 1575 under `version/` (evidence, ledger views), 13 under `pit_melee_reach/`, and the rest in the mod. The
mod's changed files map to bars as below (directory groups; each file named by `record.json` `impl_evidence` adds its row's bar).

| changed files (count) | bars whose inputs they touch |
|---|---|
| `Assemblies` (2: RimMandrakeFlowWorks.dll, RimMandrakeFlowWorks.dll.srchash) | (read per file: see below) |
| `CHANGELOG.md` (1: CHANGELOG.md) | (read per file: see below) |
| `Defs/Canals` (2: FlowWorks_Fluids.xml, FlowWorks_Terrain.xml) | canal_reads_as_dug, inv_liquid_roster, inv_overflow_sheet |
| `Defs/LiquidTypes` (1: RM_LiquidPump.xml) | inv_liquid_net |
| `Defs/Machinery` (1: RM_PipePoles.xml) | inv_liquid_net, inv_looks |
| `Defs/ManyWaters` (2: RM_PitSun.xml, RM_WaterLooks.xml) | inv_looks, pit_reads_as_hole |
| `Defs/Pits` (2: RM_SuspensionBridges.xml, RM_SuspensionStyles.xml) | hung_bridge_spans, inv_bridges |
| `Defs/Sprinklers` (1: RM_Sprinklers.xml) | inv_looks, inv_sprinklers |
| `Defs/Thirst` (1: RM_PipeFaucet.xml) | inv_bottles_thirst, inv_looks |
| `Languages` (1: FlowWorks_Keys.xml) | (read per file: see below) |
| `Source (top level)` (30: RM_DigDiscovery.cs, RM_DrawbridgeMath.cs, RM_FireMath.cs, RM_FlowKernel.cs ...) | inv_fire, inv_flow_level, inv_looks, inv_overflow_sheet, inv_quarry, inv_settings |
| `Source/Debug` (1: RM_GodLiquid.cs) | inv_settings |
| `Source/Hose` (5: CompHoseReel.cs, HoseLayQueue.cs, HoseMath.cs, HoseProbe.cs ...) | hose_reads_as_hose, inv_hoses, one_liquid_network |
| `Source/LiquidTypes` (1: Building_LiquidPump.cs) | inv_liquid_net, one_liquid_network |
| `Source/Machinery` (7: PipeLook.cs, PumpSouthSocket.cs, RM_LineLook.cs, RM_LiquidJoins.cs ...) | inv_liquid_net, inv_looks, no_impossible_plumbing, one_liquid_network |
| `Source/MapControls` (2: RM_FlowTaps.cs, RM_MapControlMath.cs) | inv_map_controls |
| `Source/Pits` (16: Building_PitCover.cs, Building_SpanDeck.cs, RM_DrawbridgeArt.cs, RM_DrawbridgeControl.cs ...) | covered_pit_springs, hung_bridge_spans, inv_bridges, inv_pits, island_bridges_trap_and_fail, pit_reads_as_hole |
| `Source/Sheet` (1: RM_SheetFire.cs) | canal_fire_burns_back, inv_fire, inv_overflow_sheet |
| `Source/Superdeep` (23: RM_ExcavationWalls.cs, RM_FaceMaterial.cs, RM_FlowDoors.cs, RM_Patch_PitLipMelee.cs ...) | drained_hole_is_a_prison, inv_doors, inv_looks, inv_pit_access, inv_pits, inv_prison_no_bed, inv_trench_cover, no_snared_standing, pit_reads_as_hole, trench_gives_cover, ways_in_and_out |
| `Source/Thirst` (2: Building_RM_PipeFaucet.cs, RM_ThirstUtility.cs) | inv_bottles_thirst |
| `Textures` (190: UniversalPipe_Straights.png, RM_LiquidPump.png, RM_LiquidPump.png, RM_LiquidPump.png ...) | inv_looks |
| `Tools` (5: fw_compositor.py, fw_scenes_spikes.py, generate_liquid_suite.py, selftest_fw_modern_fit.py ...) | (read per file: see below) |
| `art_source` (168: bridge_redraw.py, anchor_cable_art.json, frame_geometry.py, basin_ratio.py ...) | inv_looks |
| `model` (5: pitdraw.py, sweep_and_mock.py, underliquid.py, water_mockup.py ...) | (read per file: see below) |
| `northstar` (107: big_pit_scene.py, blind_reader.py, concept_scenes.py, drawbridge_look_stage.py ...) | (live scenes: stage 6) |
| `owed_0_2_0_raider_jump_gear.py` (1: owed_0_2_0_raider_jump_gear.py) | (read per file: see below) |
| `review_map.py` (1: review_map.py) | (read per file: see below) |
| `review_map_coverage.py` (1: review_map_coverage.py) | (read per file: see below) |
| `selftest_flowworks_absolute_deck_descent.py` (1: selftest_flowworks_absolute_deck_descent.py) | (read per file: see below) |
| `selftest_flowworks_deck_strips.py` (1: selftest_flowworks_deck_strips.py) | (read per file: see below) |
| `selftest_flowworks_drawbridge_frame.py` (1: selftest_flowworks_drawbridge_frame.py) | (read per file: see below) |
| `selftest_flowworks_gpt_batch_a.py` (1: selftest_flowworks_gpt_batch_a.py) | (read per file: see below) |
| `selftest_flowworks_humanlike_height.py` (1: selftest_flowworks_humanlike_height.py) | (read per file: see below) |
| `selftest_flowworks_jetty_seams.py` (1: selftest_flowworks_jetty_seams.py) | (read per file: see below) |
| `selftest_flowworks_moat_rim_stabs.py` (1: selftest_flowworks_moat_rim_stabs.py) | (read per file: see below) |
| `selftest_flowworks_no_minified_thingsofdef.py` (1: selftest_flowworks_no_minified_thingsofdef.py) | (read per file: see below) |
| `selftest_flowworks_pawn_own_picture_cut.py` (1: selftest_flowworks_pawn_own_picture_cut.py) | (read per file: see below) |
| `selftest_flowworks_pim_garments_uncut.py` (1: selftest_flowworks_pim_garments_uncut.py) | (read per file: see below) |
| `selftest_flowworks_pit_draw_census.py` (1: selftest_flowworks_pit_draw_census.py) | (read per file: see below) |
| `selftest_flowworks_pit_relative_terrain.py` (1: selftest_flowworks_pit_relative_terrain.py) | (read per file: see below) |
| `selftest_flowworks_rope_bridge.py` (1: selftest_flowworks_rope_bridge.py) | (read per file: see below) |
| `selftest_flowworks_timber_bridge.py` (1: selftest_flowworks_timber_bridge.py) | (read per file: see below) |
| `selftest_flowworks_underliquid_parity.py` (1: selftest_flowworks_underliquid_parity.py) | (read per file: see below) |
| `selftest_flowworks_unset_bridge_look.py` (1: selftest_flowworks_unset_bridge_look.py) | (read per file: see below) |
| `selftest_flowworks_water_mockup.py` (1: selftest_flowworks_water_mockup.py) | (read per file: see below) |
| `selftest_flowworks_water_target.py` (1: selftest_flowworks_water_target.py) | (read per file: see below) |
| `selftest_hose_port.py` (1: selftest_hose_port.py) | (read per file: see below) |
| `selftest_hose_probe_route.py` (1: selftest_hose_probe_route.py) | (read per file: see below) |
| `selftest_pump_draw_conserves.py` (1: selftest_pump_draw_conserves.py) | (read per file: see below) |
| `selftest_pump_south_socket.py` (1: selftest_pump_south_socket.py) | (read per file: see below) |
| `selftest_stage3_owed.py` (1: selftest_stage3_owed.py) | (read per file: see below) |
| `selftest_swim_shore_reach.py` (1: selftest_swim_shore_reach.py) | (read per file: see below) |
| `selftest_tank_art_edges.py` (1: selftest_tank_art_edges.py) | (read per file: see below) |
| `selftest_thermostat_subnotch.py` (1: selftest_thermostat_subnotch.py) | (read per file: see below) |
| `selftest_wrecked_links_draw_in.py` (1: selftest_wrecked_links_draw_in.py) | (read per file: see below) |
| `validation.py` (1: validation.py) | (read per file: see below) |
| `validation_hose.py` (1: validation_hose.py) | (read per file: see below) |

Files named in record.json impl_evidence: `CompHoseReel.cs` -> inv_hoses, `Building_LiquidPump.cs` -> inv_liquid_net, `RM_FlowTaps.cs` -> inv_map_controls, `Building_PitCover.cs` -> inv_pits, `Building_SpanDeck.cs` -> inv_bridges, `RM_Drawbridges.cs` -> inv_bridges, `RM_MapComponent_SuspensionBridges.cs` -> inv_bridges, `RM_DigDiscovery.cs` -> inv_quarry, `RM_FireMath.cs` -> inv_fire, `RM_FlowKernel.cs` -> inv_flow_level, `RM_LiquidFire.cs` -> inv_fire, `RM_MapComponent_Excavation.cs` -> inv_flow_level, `RM_SheetMath.cs` -> inv_overflow_sheet, `RM_WaterLooks.cs` -> inv_looks, `RimMandrakeFlowWorksMod.cs` -> inv_settings, `RM_ExcavationWalls.cs` -> inv_looks, `RM_FlowDoors.cs` -> inv_doors, `RM_PitAccess.cs` -> inv_pit_access, `RM_PitDepthDraw.cs` -> inv_pits, `RM_PitLipOcclusion.cs` -> inv_pits, `RM_RaiderTrench.cs` -> inv_pit_access, `RM_Spikes.cs` -> inv_pits, `RM_SuperdeepTrap.cs` -> inv_pits, `Building_RM_PipeFaucet.cs` -> inv_bottles_thirst

Offline-bar inputs that changed (the lane-1 scope proper, read as diffs of code only, no commit messages):
- `inv_overflow_sheet`: `Source/RM_SheetMath.cs` (+17 lines: `RM_SheetFluidMath.CreepingCatchChance` and
  `CreepingTicksPerNeighbour`, the creeping-fuse fire pace, which also feeds `inv_fire`/`canal_fire_burns_back`),
  `Source/Sheet/RM_SheetFire.cs` (their caller), `Source/RM_FireMath.cs`, `Defs/Canals/FluidDefs/FlowWorks_Fluids.xml`.
- `inv_bottles_thirst`: `Source/Thirst/Building_RM_PipeFaucet.cs` (+18: the faucet's bottle-fill job now holds back once the
  colony's bottle target is met, and counts each filled potable bottle), `Source/Thirst/RM_ThirstUtility.cs` (+5/-1: a
  forbidden terrain drink cell no longer counts against the 40-cell reach budget), `Defs/Thirst/RM_PipeFaucet.xml` (+1 comp).
- `inv_sprinklers`: `Defs/Sprinklers/RM_Sprinklers.xml` (+1 comp, `CompProperties_LineLook`: choose style for the line).
- `inv_converters`, `inv_drilling`: no input changed since `a05f0a3b6e` [measured: `Machinery/RM_ConversionMath.cs`,
  `Machinery/CompLiquidConverter.cs`, `Drilling/*` absent from the list]; read whole once anyway, as the brief starts lane 1
  with all five offline bars.
- Locked files changed: `tree.json`, `sheet.md`, `scenes.json`, `record.json`, `plan.md`, `version/VERSION.json`,
  `version/bars.md`, `version/locked_bars.json` (the 2026-11-23 raid re-pin that `bars.md` describes). Bars on those lines:
  `moat_drains_and_burns`, `trench_gives_cover`, `inv_trench_cover`, `island_bridges_trap_and_fail` (all stage 6).
- `src/RimMandrake/FlowWorks/Source/RM_PumpMath.cs`: one comment line only (no behaviour).


## Lane 1
Command: `python3 design/concepts/FlowWorks/version/blind_challenge/cycle_5/lane1/run_lane1.py` (exit 0). Rows in
`lane1/lane1_rows.jsonl`: **78 rows: 27 PASS, 1 INFO, 0 FAIL, 50 UNSETTLED** [measured]. The 50 UNSETTLED rows are one
`not_kernel` row for each bar that is not offline (every one proves at stage 6 or the walk). No `not_kernel` row names an
offline bar.

Inputs: `record.json` inventory rows (the text of the five offline bars), `sheet.md`, `plan.md`, `tree.json`, `bars.md`,
`VERSION.json`, the settings files (defaults and slider ranges, read by regex) and the six kernels: `RM_SheetMath.cs`
(+`RM_Volume.cs`, `RM_FireMath.cs`, `RM_StockMath.cs`), `Machinery/RM_ConversionMath.cs`, `Drilling/RM_DrillSurveyMath.cs`,
`Sprinklers/RM_SprinklerKernel.cs`, `LiquidTypes/RM_ContainerStyleMath.cs`, `Thirst/RM_ThirstMath.cs`.

| bar | rows (kind: cases) | what they show |
|---|---|---|
| inv_overflow_sheet | random ledger 1500 seeds x 120 ops; save/load 400; preview+order 3000; yard level; soak/dry; crop delay sweep 600; crop at the delay; ice; door sealed/slow; switches 64; settings sweep 2592; creeping fire 24 | the ledger closes to the dL after every op; no orphan, negative, over-cap or misplaced cell; save/load continues identical; a yard fills and lies level within 1 dL; it soaks in and dries with every dL disclosed; the crop delay stays wall time over the days slider x the flow-pulse slider, and drowns at exactly the delay, never under a film; ice keeps its dL and thaws only 1 C up; a 0 % door seals |
| inv_converters | rate sweep 1500; idle week 2000; bounds and rotation 25000 | runs at its rate at every multiplier 0.1..5; a week dry bursts at most one tick's income plus one batch; batches bounded; rotation fair; a blocked input never starves the rest; solar only by day |
| inv_bottles_thirst | ruled numbers 8; rate sweep 448; drink gates 431; pick order/reserve/target 35000; container styles 33 | the owner's ruled numbers hold (1.25 d to empty, 3x heat cap, 0.5 per 1.5 L, death 3.34 d after empty); every switch off included |
| inv_drilling | placement + why-not 8208; charges what landed 20000 | refuses a surveyed dry or spent square, allows unsurveyed; one why-not answer, None only when all hold |
| inv_sprinklers | needs a pump 512; pulse cost 11682; valve and wet record 20002 | no pump, no spray; cost never free or short at every litres setting; the valve is a maximal nearest-first prefix within budget and reserve |
| four settings files | initializer = Scribe default, 64 fields | a fresh install and a loaded save start alike |

INFO `L1_INFO_SHEET_MASTER_SWITCH_SHIPS_OFF`: `RM_SheetSettings.sheetOverflowEnabled` ships **false**, so a new game shows none
of `inv_overflow_sheet`'s overspill until the player turns it on. Lane 2 weighs it.

Two of my own test bugs went red on the first run and were fixed before the recorded run (a negative-budget comparison in the
converter bounds row; a declaration line `float a = 4f, b = 2f, c = 1f;` that my settings regex read as one field). Neither
was a mod fault.

Blindness record: this run read its whole brief file at the start, as its launch line ordered, so it saw the sealed
"Steward's decisions" section (design inputs: the raid deferral, the re-pin, no fifth blind cycle by route b, the in-game
recheck) before lane 1. One grep for slider ranges also printed a comment line from
`Source/SelfTest/BlindCycle1Checks.cs` (that the cycle-1 judge found the converter cap dropped part of the rate). That fact
is also in the shipped kernel's own doc comment, `RM_ConversionMath.CapAccrued`. No other sealed file was opened before the
lane-1 commit.


## Lane 2 reruns
`lane2/rerun_offline.py` (generic over the test table; one fix of its own compare during the run: a stock-suite summary
also matches on its count of cases run, because its "N filtered out" grows as the suite grows). `lane2/reruns.jsonl`:
**8 of 8 run deciders PASS and match their records** [measured]: T_SHEET (394 s), PY_FLOWWORKS_SHEET_DROWN_MESSAGE, T_CONVERT
(295 s), T_THIRST (293 s), PY_WATER_NOT_FOOD, PY_NATIVES_DRINK_OWN_WATER, T_DRILL (221 s), T_SPRINKLER (249 s).
T_DIG_TIME_ARITHMETIC is UNRUN as recorded ("specified, not built"; it decides no offline bar).

After the fix (`lane2/reruns_after_fix.jsonl`, at 5d68be6e66): the deciders that `rerun_relation.py` names for
`SheetWaterChecks.cs`: T_SHEET PASS (63 cases, the one new case being the repair), T_TOSS_FLAME_OFFLINE,
T_FETCH_FALLEN_OFFLINE, T_LIQUID_COATING_OFFLINE PASS, T_PIT_LOOK_1114 PASS (875 s). Every other decider keeps its
`reruns.jsonl` row.

## Planted
`lane2/planted_faults.json` (29 faults), `lane2/plant_faults.py` (WINBUILD_ROOT
`/mnt/d/ClaudeWork/rimmandrake/scratch/flowworks_blind_c5_mut/`; restores on SIGTERM, SIGINT, SIGHUP; a catch is a new failing
row only), `lane2/planted_results.jsonl` (baseline first, from this cycle's unplanted reruns and lane 1; last row
`{"tree_clean_after": true}`). **22 of 29 caught** [measured].

| group | planted | caught | missed |
|---|---|---|---|
| sheet kernel (`RM_SheetMath.cs`: ledger, crop timer, film tier; and its changed lines, creeping fire) | 5 | 5 | 0 |
| sheet callers (`RM_MapComponent_Sheet.cs` crop kill; changed `RM_SheetFire.cs` x2) | 3 | 0 | 3 |
| converter (kernel x2, caller x1) | 3 | 3 | 0 |
| thirst and containers (kernel x3, reserve caller, changed faucet x2, changed thirst reach x2) | 8 | 8 | 0 |
| faucet def (changed `RM_PipeFaucet.xml` x2) | 2 | 0 | 2 |
| drilling (kernel x2, place worker) | 3 | 3 | 0 |
| sprinklers (kernel x2, caller x1) | 3 | 3 | 0 |
| sprinkler def (changed `RM_Sprinklers.xml` x2) | 2 | 0 | 2 |

Lane 1 caught every kernel plant it can see (17 of 17 kernel and changed-kernel-line plants). The misses:
`PF_SHEET_CALLER_CROP_NEVER_KILLED` is the Problem below (an offline bar's claim). The two tar-fire caller plants and the four
line-style def plants touch no offline bar's claim (`inv_fire`, `canal_fire_burns_back` and `inv_looks` prove at stage 6).
"Two per changed file" was read as two per changed file of the offline bars' inputs (2304 files changed, most of them
ledger, evidence and art).

## Faults
`lane2/faults.json`: **1 Problem (FIXED), 4 Polish (NOTED_FOR_CONDUCTOR)**.

- **Problem** `RIMMANDRAKE_PIN_SHEET_CALLER_KILLS_THE_DROWNED_CROP` (inv_overflow_sheet, against the check, `miss_of: 4`):
  with `plant.Kill()` deleted from the sheet caller, T_SHEET and PY_FLOWWORKS_SHEET_DROWN_MESSAGE stayed green [measured],
  as `polish.md` line 116 had predicted from source. FIXED at 5d68be6e66.
- Polish `RIMMANDRAKE_NOTE_FLOWWORKS_OVERSPILL_SHIPS_SWITCHED_OFF` (against mod): `sheetOverflowEnabled` ships false. It
  is already on `polish.md` under this name, to flip at his walk's sign-off (his D7 card). No new line.
- Polish `RIMMANDRAKE_RECORD_TAR_SHEET_FIRE_UNSEEN_OFFLINE` (against scene, stage 6): no offline decider of the sheet
  sees the tar sheet's creeping catch in `RM_SheetFire.cs` (changed since cycle 4). Stage 6's `sc_canal_fire` should
  stage a tar sheet, not only a channel.
- Polish `RIMMANDRAKE_RECORD_LINE_STYLE_COMP_UNCHECKED_ON_TWO_DEFS` (against check, stage 6): no test reads the new
  `CompProperties_LineLook` on the sprinkler head and the faucet. A misspelt class would fail the def load at L1.
- Polish `RIMMANDRAKE_CORRECT_CROP_TOOLTIP_TWO_CM_IS_THREE` (against mod, `miss_of: 4`): the crop-drown tooltip says "at
  least 2 cm". The kernel counts water rising from dry only from 3 cm (hysteresis 3 cm up, 2 cm down); lane 1 measured that
  2.5 cm poured on dry ground never stands.

Callers read and found sound (no fault): the creeping-fire caller passes a constant 60-tick check (the kernel's NaN at a
0-tick check cannot arise); the faucet's bottle-stock hold and its fill count; the thirst search's forbidden-cell change;
the converter's capped and clipped budget and rotation; the drill's tick order against `WhyNot`; the sprinkler's pump and
drinking-reserve gates.

Pipeline defect found and fixed (not a FlowWorks fault): `RIMMANDRAKE_RESTORE_RED_SEEN_TREE_WHEN_A_TIMEOUT_KILLS_IT`.
A `timeout`-killed `maturation.py red-seen` left its planted fault (`plant.Kill()` deleted) in this clone's tree, because
Python skips `finally` on a default SIGTERM. I found it at the next `red-seen` ("patch does not apply") and reversed it by
hand with `git apply -R` before anything else ran. The fix is in `judge_certificate.red_seen`: while the fault is planted,
SIGTERM and SIGHUP raise SystemExit, so the restore runs. The test is `selftest_red_seen.py`
`t_killed_run_restores_the_tree`: red on the parent (restored False, 19/21), green on the fix (21/21). Published at
79815237e7.

## Fixes
`lane2/fixes.jsonl`: one check repair, no mod fix.

- `RIMMANDRAKE_PIN_SHEET_CALLER_KILLS_THE_DROWNED_CROP`: new case `SheetCropKill_the_caller_kills_each_drowning_crop` in
  `Source/SelfTest/SheetWaterChecks.cs` (under T_SHEET's `Sheet*` glob). Shown at the fix sha 5d68be6e66: **red** rc 1 on the
  plant (`plant_faults.py --run-planted PF_SHEET_CALLER_CROP_NEVER_KILLED -- <T_SHEET>`: "FAIL SheetCropKill... the crop
  the kernel drowns is killed (plant.Kill) before it is counted", 62/63), and **green** rc 0 on the real build (63/63).
  `maturation.py red-seen FlowWorks T_SHEET` recorded RED SEEN. The first version (30dbdfc2b9) read the file through
  `Src()`, which flattens whitespace, so it failed on the real build. That version was never counted; 5d68be6e66 reads the
  raw file. A check repair owes no fresh reader.

## Steward's decisions enacted
None. This run acted on none of the four (the raid deferral and re-pin, route b's "no fifth blind cycle", and the
in-game recheck are design inputs for other stages; nothing in this cycle's offline scope turned on them). So no
OWNER.jsonl event was written.

## Tests edited
`tests_edited.json`: `src/RimMandrake/FlowWorks/Source/SelfTest/SheetWaterChecks.cs` (blob 590f39b2ae ->
5aa3bd4de2; one case added, no assertion removed or weakened; commits 30dbdfc2b9, 5d68be6e66). Also
`src/RimMandrake/rimflow/selftest_red_seen.py` (pipeline, not a FlowWorks decider; 79815237e7).

## Unsettled
- 50 lane-1 `not_kernel` rows (every non-offline bar): settled by their stage-6 scenes.
- Planted misses outside the offline bars: the tar-sheet creeping catch (`inv_fire`, `canal_fire_burns_back`) and the
  line-style comp on two defs (`inv_looks`). T_FIRE and PY_FLOWWORKS_FUEL_MOAT were not run on the tar plants.
- `code_review_status.py check` on `SheetWaterChecks.cs` did not finish inside 120 s: UNMEASURED.
- judge-verify listed 53 findings claimed fixed. I ruled on the five on the offline bars I judged (verified at 5d68be6e66,
  each by reading the fixed code and by the decider reruns). The other 48 (stage-6 bars or none, plus
  `FLOWWORKS_HOTPATH_MEASURE_EVERY_FRAME`, of which I checked only the feed-mesh cache) are not ruled: their claims rest on
  live rows or suites outside this offline stage, and a ruling without that check would be false.

## Exit
offline_bars: {inv_overflow_sheet: green, inv_converters: green, inv_bottles_thirst: green, inv_drilling: green, inv_sprinklers: green}
problems_open: 0
exit_met: true

## Owed
- The fresh reader of the pipeline fix 79815237e7 (`judge_certificate.py`), filed with `fresh_reader.py file --fix`.
- The four Polish rows go to the Conductor for the Polish-list call.
- The 48 unruled judge-verify claims: for the stage-6 visit or the steward.
- `maturation.py certificate FlowWorks --run` (this run, 1333 s: 6 tests rerun, 116 kept) refuses 1 of 53 bars:
  `inv_settings`, red_seen owed by PY_VALIDATION_V2_OFFLINE, whose `northstar/validation_v2.py` another run changed; not this
  cycle's edit and not an offline bar of this exit. The stamps of the six rerun tests are in `version/test_table.json`
  (`runs_today` only).
