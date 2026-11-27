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
(pending)

## Planted
(pending)

## Faults
(pending)

## Fixes
(pending)

## Steward's decisions enacted
(pending)

## Tests edited
(pending)

## Unsettled
(pending)

## Exit
(pending)

## Owed
(pending)
