# FlowWorks 0.1.0: test-and-stage table

Generated 2026-11-23T23:23:42-08:00 from `test_table.json` (the record; this is its read view). Stages: 2 preflight, 4-5 blind offline, 6 in-game, 8 his walk. A bar passes when every deciding test passes. Columns match Explosive Knockback's table.

## Counts (measured)

- bars: 55
- with at least one test runnable today (an offline test that ran, or an in-game scene whose entry exists): 55
- with every deciding test runnable today: 55
- with an offline deciding test, all green today: 53
- with an offline deciding test that exists (built), green or red: 53
- with no offline deciding test at all: 2
- decided offline only (no game needed): 5
- in-game scenes: 29, entry exists 29, absent 0
- offline tests: 122 built (ran today: 121 PASS, 1 red), 1 specified for Stage 3

## Bars

| bar | from | proves at | decides | supports | runnable today | offline green |
|---|---|---|---|---|---|---|
| `inv_dig_depth` | record | 6 | T_DIG, PY_FLOWWORKS_REVIEW1022_EXCAVATION, T_WALL_FACES, PY_FLOWWORKS_FLAT_SHADOW, sc_dig_and_read | T_DIG_TIME_ARITHMETIC, T_CALL_SITES_OFFLINE, T_GPT_B_FIXES_OFFLINE | all | yes |
| `inv_flow_level` | record | 6 | T_LEVEL, PY_FLOWWORKS_KERNEL_ORACLE, PY_FLOWWORKS_ONE_WATER_NUMBER, PY_FLOWWORKS_FLOOD_HOUR_CADENCE, sc_fill_front, sc_one_surface | T_LEVEL_WATER_OFFLINE, T_GPT_BATCH_A_FIXES_OFFLINE, T_SWALE_STATIC_OFFLINE | all | yes |
| `inv_stock` | record | 6 | T_STOCK, PY_FLOWWORKS_POND_OUTLET_FRACTIONAL, PY_PUMP_DRAW_CONSERVES, sc_source_pays | T_CONSERVATION_ROUNDTRIP_OFFLINE, T_POND_CAPACITY_RULE_OFFLINE, T_POND_FILM_OFFLINE | all | yes |
| `inv_overflow_sheet` | record | 4-5 | T_SHEET, PY_FLOWWORKS_SHEET_DROWN_MESSAGE | sc_garden, T_FROZEN_HANDOVER_OFFLINE, T_GPT_BATCH_A_FIXES_OFFLINE, T_REVIEW1022_SHEET_OFFLINE, T_SPREADING_FUEL_IRRIGATION_OFFLINE, T_SHEET_KERNEL_OFFLINE | all | yes |
| `inv_liquid_roster` | record | 6 | T_ROSTER, PY_LIQUID_DEFS_HAZARDS, PY_WATER_TERRAINS_NAME_LIQUID, PY_LAVA_ROW, PY_FLOWWORKS_HOT_WET_TERRAIN, sc_fill_tiers | T_GPT_C_FIXES_OFFLINE, T_SALT_BREAK_POTABLE_OFFLINE | all | yes |
| `inv_fire` | record | 6 | T_FIRE, PY_FLOWWORKS_FUEL_MOAT, sc_canal_fire | T_CALL_SITES_OFFLINE, T_REVIEW1022_SHEET_OFFLINE, T_SPREADING_FUEL_IRRIGATION_OFFLINE | all | yes |
| `inv_slime` | record | 6 | T_SLIME, sc_slime | - | all | yes |
| `inv_pits` | record | 6 | T_PIT_DRAW, PY_FLOWWORKS_PIT_DRAW_CENSUS, PY_FLOWWORKS_PIT_FLOOR_GROUND, PY_FLOWWORKS_REVIEW1022_SUPERDEEP, T_PIT_COVER, PY_FLOWWORKS_COVER_BREAKS, PY_SPIKE_FLOAT32_PARITY, sc_pit_reads, sc_covered_pit | T_PIT_LOOK_1114, PIT_LOOK_1114_LIVE, T_GPT_B_FIXES_OFFLINE | all | yes |
| `inv_pit_access` | record | 6 | T_PIT_ACCESS, PY_FLOWWORKS_DRAFTED_MOVE_PIT, PY_FLOWWORKS_PIT_TRAVEL_TAGS, sc_ways_out | T_PIT_LOOK_1114, PIT_LOOK_1114_LIVE, T_FETCH_FALLEN_OFFLINE | all | yes |
| `inv_doors` | record | 6 | T_DOORS, PY_FW_GATE_LIFT, sc_sluice | - | all | yes |
| `inv_bridges` | record | 6 | T_BRIDGES, PY_FLOWWORKS_DRAWBRIDGE_POSE, PY_FLOWWORKS_SUSPENSION_LINKED, sc_hung_bridge | T_MODERN_BRIDGE_ART_OFFLINE, T_BELT_FIXES_H_OFFLINE, T_DRAWBRIDGE_ART_OFFLINE, T_HEAVY_TRUSS_LABELS_OFFLINE | all | yes |
| `inv_trench_cover` | record | 6 | T_TRENCH, sc_trench_cover_pawns | T_TRENCH_COVER_CSHARP_OFFLINE | all | yes |
| `inv_swim` | record | 6 | T_SWIM, PY_SWIM_SHORE_REACH, sc_pawn_height | T_JAWA_SHALLOWS_OFFLINE | all | yes |
| `inv_hoses` | record | 6 | T_HOSE, PY_HOSE_OFFLINE, PY_HOSE_PORTS, PY_HOSE_LAY_SETTLE, PY_HOSE_FITTINGS, sc_hose_look | sc_garden, T_FREEZE_BIG_MAP_OFFLINE, T_HOSE_PIPE_SADDLE_OFFLINE, T_HOSE_PORT_OFFLINE, T_PUMP_STATION_PORTS_COMPILED_OFFLINE | all | yes |
| `inv_liquid_net` | record | 6 | T_NET, PY_PUMP_STATION_PORTS, PY_FLOWWORKS_TANK_DRINK_RECHECK, PY_PIPE_SEAT, sc_one_network | sc_garden, T_CALL_SITES_OFFLINE, T_REVIEW1022_LIQUIDNET_OFFLINE, T_FREEZE_BIG_MAP_OFFLINE, T_THERMOSTAT_SUBNOTCH_OFFLINE | all | yes |
| `inv_converters` | record | 4-5 | T_CONVERT | sc_garden | all | yes |
| `inv_bottles_thirst` | record | 4-5 | T_THIRST, PY_WATER_NOT_FOOD, PY_NATIVES_DRINK_OWN_WATER | sc_garden | all | yes |
| `inv_drilling` | record | 4-5 | T_DRILL | sc_garden | all | yes |
| `inv_sprinklers` | record | 4-5 | T_SPRINKLER | sc_garden | all | yes |
| `inv_rivers` | record | 6 | T_RIVER, PY_FLOWWORKS_RIVERS, PY_FLOWWORKS_RIVER_COLORS, PY_WEIR_INSTALLED, sc_river | T_GPT_B_FIXES_OFFLINE | all | yes |
| `inv_map_controls` | record | 6 | T_MAP_CONTROLS, sc_source_pays | - | all | yes |
| `inv_quarry` | record | 6 | T_QUARRY, sc_dig_finds | - | all | yes |
| `inv_settings` | record | 6 | T_SETTINGS_SWEEP_OFFLINE, PY_SETTINGS_REGISTRY, PY_SETTINGS_SEARCH, PY_FLOWWORKS_NORTHSTAR, PY_VALIDATION_V2_OFFLINE, sc_walk | T_BELT_FIXES_H_OFFLINE, T_SWALE_STATIC_OFFLINE | all | yes |
| `inv_looks` | record | 6 | T_UNDERLIQUID, PY_FLOWWORKS_UNDERLIQUID_PARITY, PY_LIQUID_LOOK_TUNE, PY_FLOWWORKS_TANK_SHADOW, T_STYLES, PY_FW_OFFLINE_ART, PY_LIQUID_LOOKS, PY_FLOWWORKS_PIPE_POLE_ART, T_WALL_FACES, PY_FLOWWORKS_FLAT_SHADOW, LOOK_BLIND_READER | OL_OWNER_LOOK_READS, sc_fill_tiers, LOOK_STAGE8, T_PIT_LOOK_1114, PIT_LOOK_1114_LIVE, T_MODERN_FIT_OFFLINE, T_PIPE_ATLAS_CELL_OFFLINE, T_PLAYER_TRUTHS_ART_OFFLINE, T_WEIR_LOOKS_OFFLINE, T_WEIR_MATERIAL_OFFLINE, T_WEIR_SPILL_OFFLINE, T_MODERN_BRIDGE_ART_OFFLINE, T_SUSPENSION_REDESIGN_ART_OFFLINE, T_DRAWBRIDGE_ART_OFFLINE, T_GPT_C_FIXES_OFFLINE, T_LOOKS_ROUND_OFFLINE, T_SUSPENSION_ART_OFFLINE, T_HEAVY_TRUSS_LABELS_OFFLINE, T_PIPE_GIRTH_OFFLINE, T_TANK_ART_EDGES_OFFLINE, T_WRECKED_LINKS_OFFLINE | all | yes |
| `inv_prison_no_bed` | record | 6 | T_PRISON, T_PRISON_CARE_OFFLINE, sc_hole_prison | T_HOLE_PRISON_OFFLINE | all | yes |
| `inv_toss_flame` | record | 6 | T_TOSS_FLAME_OFFLINE, sc_toss_flame | - | all | yes |
| `canal_reads_as_dug` | tree | 6 | T_DIG, PY_FLOWWORKS_REVIEW1022_EXCAVATION, T_WALL_FACES, PY_FLOWWORKS_FLAT_SHADOW, sc_dig_and_read, LOOK_BLIND_READER | sc_dig_finds, T_DIG_TIME_ARITHMETIC, T_LOOKS_ROUND_OFFLINE | all | yes |
| `fill_flows_along_canal` | tree | 6 | T_LEVEL, PY_FLOWWORKS_KERNEL_ORACLE, PY_FLOWWORKS_ONE_WATER_NUMBER, PY_FLOWWORKS_FLOOD_HOUR_CADENCE, sc_fill_front | LOOK_STAGE8 | all | yes |
| `fill_level_legible` | tree | 6 | T_UNDERLIQUID, PY_FLOWWORKS_UNDERLIQUID_PARITY, PY_LIQUID_LOOK_TUNE, PY_FLOWWORKS_TANK_SHADOW, sc_fill_tiers, LOOK_BLIND_READER | OL_OWNER_LOOK_READS, LOOK_STAGE8 | all | yes |
| `one_still_surface` | tree | 6 | T_LEVEL, PY_FLOWWORKS_KERNEL_ORACLE, PY_FLOWWORKS_ONE_WATER_NUMBER, PY_FLOWWORKS_FLOOD_HOUR_CADENCE, sc_one_surface | T_CONSERVATION_ROUNDTRIP_OFFLINE, T_LEVEL_WATER_OFFLINE | all | yes |
| `source_pays_and_refills` | tree | 6 | T_STOCK, PY_FLOWWORKS_POND_OUTLET_FRACTIONAL, PY_PUMP_DRAW_CONSERVES, sc_source_pays | - | all | yes |
| `canal_fire_burns_back` | tree | 6 | T_FIRE, PY_FLOWWORKS_FUEL_MOAT, sc_canal_fire | T_REVIEW1022_SHEET_OFFLINE | all | yes |
| `slime_holds_the_crossing` | tree | 6 | T_SLIME, sc_slime | LOOK_BLIND_READER | all | yes |
| `pawn_height_follows_depth` | tree | 6 | T_SWIM, PY_SWIM_SHORE_REACH, sc_pawn_height | - | all | yes |
| `pit_reads_as_hole` | tree | 6 | T_PIT_DRAW, PY_FLOWWORKS_PIT_DRAW_CENSUS, PY_FLOWWORKS_PIT_FLOOR_GROUND, PY_FLOWWORKS_REVIEW1022_SUPERDEEP, T_PIT_LABEL, sc_pit_reads, LOOK_BLIND_READER | OL_OWNER_LOOK_READS | all | yes |
| `covered_pit_springs` | tree | 6 | T_PIT_COVER, PY_FLOWWORKS_COVER_BREAKS, PY_SPIKE_FLOAT32_PARITY, sc_covered_pit, LOOK_BLIND_READER | - | all | yes |
| `ways_in_and_out` | tree | 6 | T_PIT_ACCESS, PY_FLOWWORKS_DRAFTED_MOVE_PIT, PY_FLOWWORKS_PIT_TRAVEL_TAGS, sc_ways_out | T_PIT_LOOK_1114, PIT_LOOK_1114_LIVE, T_PLAYER_TRUTHS_ART_OFFLINE | all | yes |
| `sluice_drains_on_command` | tree | 6 | T_DOORS, PY_FW_GATE_LIFT, sc_sluice | - | all | yes |
| `hose_reads_as_hose` | tree | 6 | T_HOSE, PY_HOSE_OFFLINE, PY_HOSE_PORTS, PY_HOSE_LAY_SETTLE, PY_HOSE_FITTINGS, sc_hose_look, LOOK_BLIND_READER | T_HOSE_PIPE_SADDLE_OFFLINE, T_HOSE_PORT_OFFLINE | all | yes |
| `one_liquid_network` | tree | 6 | T_NET, PY_PUMP_STATION_PORTS, PY_FLOWWORKS_TANK_DRINK_RECHECK, PY_PIPE_SEAT, sc_one_network | sc_garden, T_REVIEW1022_LIQUIDNET_OFFLINE, T_PUMP_STATION_PORTS_COMPILED_OFFLINE | all | yes |
| `trench_gives_cover` | tree | 6 | T_TRENCH, sc_trench_cover_pawns | T_TRENCH_COVER_CSHARP_OFFLINE | all | yes |
| `hung_bridge_spans` | tree | 6 | T_BRIDGES, PY_FLOWWORKS_DRAWBRIDGE_POSE, PY_FLOWWORKS_SUSPENSION_LINKED, sc_hung_bridge, LOOK_BLIND_READER | T_SUSPENSION_REDESIGN_ART_OFFLINE, T_SUSPENSION_ART_OFFLINE | all | yes |
| `ice_cuts_and_melts` | tree | 6 | T_ICE, sc_ice | T_FROZEN_HANDOVER_OFFLINE | all | yes |
| `river_flows_endless` | tree | 6 | T_RIVER, PY_FLOWWORKS_RIVERS, PY_FLOWWORKS_RIVER_COLORS, PY_WEIR_INSTALLED, sc_river | - | all | yes |
| `moat_drains_and_burns` | tree | 6 | sc_moat_walkers, sc_hole_prison, sc_sluice, sc_toss_flame | T_SWIM, PY_SWIM_SHORE_REACH, T_DOORS, PY_FW_GATE_LIFT, T_PRISON, T_FIRE, PY_FLOWWORKS_FUEL_MOAT, T_BRIDGES, PY_FLOWWORKS_DRAWBRIDGE_POSE, PY_FLOWWORKS_SUSPENSION_LINKED, LOOK_STAGE8 | all | no |
| `drained_hole_is_a_prison` | tree | 6 | T_PRISON, T_PRISON_CARE_OFFLINE, sc_hole_prison | T_HOLE_PRISON_OFFLINE | all | yes |
| `toss_flame_from_rim` | tree | 6 | T_TOSS_FLAME_OFFLINE, sc_toss_flame | - | all | yes |
| `island_bridges_trap_and_fail` | tree | 6 | T_BRIDGES, PY_FLOWWORKS_DRAWBRIDGE_POSE, PY_FLOWWORKS_SUSPENSION_LINKED, sc_islands_walker | - | all | yes |
| `no_liquid_on_open_ground` | tree | 6 | T_SHEET, PY_FLOWWORKS_SHEET_DROWN_MESSAGE, T_LEVEL, PY_FLOWWORKS_KERNEL_ORACLE, PY_FLOWWORKS_ONE_WATER_NUMBER, PY_FLOWWORKS_FLOOD_HOUR_CADENCE, sc_dig_and_read | LOOK_BLIND_READER, T_SHEET_KERNEL_OFFLINE | all | yes |
| `no_full_source_after_draw` | tree | 6 | T_STOCK, PY_FLOWWORKS_POND_OUTLET_FRACTIONAL, PY_PUMP_DRAW_CONSERVES, sc_source_pays | T_POND_FILM_OFFLINE | all | yes |
| `no_snared_standing` | tree | 6 | T_PIT_DRAW, PY_FLOWWORKS_PIT_DRAW_CENSUS, PY_FLOWWORKS_PIT_FLOOR_GROUND, PY_FLOWWORKS_REVIEW1022_SUPERDEEP, sc_pit_reads | - | all | yes |
| `no_impossible_plumbing` | tree | 6 | T_NET, PY_PUMP_STATION_PORTS, PY_FLOWWORKS_TANK_DRINK_RECHECK, PY_PIPE_SEAT, T_HOSE, PY_HOSE_OFFLINE, PY_HOSE_PORTS, PY_HOSE_LAY_SETTLE, PY_HOSE_FITTINGS, sc_one_network | T_MODERN_FIT_OFFLINE, T_TANK_ART_EDGES_OFFLINE | all | yes |
| `walk_moat_season` | tree | 6 | sc_walk | LOOK_STAGE8, T_SETTINGS_SWEEP_OFFLINE | all | no |
| `inv_geyser_tub` | record | 6 | T_GEYSER_TUB, PY_FLOWWORKS_GEYSER_TUB, sc_geyser_tub | LOOK_STAGE8 | all | yes |
| `inv_liquid_coating` | record | 6 | T_LIQUID_COATING_OFFLINE, sc_coating_wash | LOOK_STAGE8 | all | yes |

## Tests

| test | kind | stage | file | runs today |
|---|---|---|---|---|
| `T_DIG` | offline | 4-5 | `src/RimMandrake/Utils/selftest_flowworks_stock.py` | PASS, 229.57s |
| `PY_FLOWWORKS_REVIEW1022_EXCAVATION` | offline | 4-5 | `src/RimMandrake/FlowWorks/selftest_flowworks_review1022_excavation.py` | PASS, 0.02s |
| `T_WALL_FACES` | offline | 4-5 | `src/RimMandrake/Utils/selftest_flowworks_stock.py` | PASS, 181.63s |
| `PY_FLOWWORKS_FLAT_SHADOW` | offline | 4-5 | `src/RimMandrake/FlowWorks/selftest_flowworks_flat_shadow.py` | PASS, 0.04s |
| `T_LEVEL` | offline | 4-5 | `src/RimMandrake/Utils/selftest_flowworks_stock.py` | PASS, 96.4s |
| `PY_FLOWWORKS_KERNEL_ORACLE` | offline | 4-5 | `src/RimMandrake/FlowWorks/Source/SelfTest/selftest_flowworks_kernel_oracle.py` | PASS, 378.63s |
| `PY_FLOWWORKS_ONE_WATER_NUMBER` | offline | 4-5 | `src/RimMandrake/FlowWorks/selftest_flowworks_one_water_number.py` | PASS, 1.37s |
| `PY_FLOWWORKS_FLOOD_HOUR_CADENCE` | offline | 4-5 | `src/RimMandrake/FlowWorks/selftest_flowworks_flood_hour_cadence.py` | PASS, 0.02s |
| `T_STOCK` | offline | 4-5 | `src/RimMandrake/Utils/selftest_flowworks_stock.py` | PASS, 102.16s |
| `PY_FLOWWORKS_POND_OUTLET_FRACTIONAL` | offline | 4-5 | `src/RimMandrake/FlowWorks/selftest_flowworks_pond_outlet_fractional.py` | PASS, 0.02s |
| `PY_PUMP_DRAW_CONSERVES` | offline | 4-5 | `src/RimMandrake/FlowWorks/selftest_pump_draw_conserves.py` | PASS, 0.08s |
| `T_SHEET` | offline | 4-5 | `src/RimMandrake/Utils/selftest_flowworks_stock.py` | PASS, 237.12s |
| `PY_FLOWWORKS_SHEET_DROWN_MESSAGE` | offline | 4-5 | `src/RimMandrake/FlowWorks/selftest_flowworks_sheet_drown_message.py` | PASS, 0.02s |
| `T_ROSTER` | offline | 4-5 | `src/RimMandrake/Utils/selftest_flowworks_stock.py` | PASS, 96.87s |
| `PY_LIQUID_DEFS_HAZARDS` | offline | 4-5 | `src/RimMandrake/FlowWorks/Tools/selftest_liquid_defs_hazards.py` | PASS, 0.03s |
| `PY_WATER_TERRAINS_NAME_LIQUID` | offline | 4-5 | `src/RimMandrake/FlowWorks/Tools/selftest_water_terrains_name_liquid.py` | PASS, 0.6s |
| `PY_LAVA_ROW` | offline | 4-5 | `src/RimMandrake/FlowWorks/Tools/selftest_lava_row.py` | PASS, 0.05s |
| `PY_FLOWWORKS_HOT_WET_TERRAIN` | offline | 4-5 | `src/RimMandrake/FlowWorks/selftest_flowworks_hot_wet_terrain.py` | PASS, 0.06s |
| `T_FIRE` | offline | 4-5 | `src/RimMandrake/Utils/selftest_flowworks_stock.py` | PASS, 308.44s |
| `PY_FLOWWORKS_FUEL_MOAT` | offline | 4-5 | `src/RimMandrake/FlowWorks/selftest_flowworks_fuel_moat.py` | PASS, 0.04s |
| `T_SLIME` | offline | 4-5 | `src/RimMandrake/Utils/selftest_flowworks_stock.py` | PASS, 483.75s |
| `T_PIT_DRAW` | offline | 4-5 | `src/RimMandrake/Utils/selftest_flowworks_stock.py` | PASS, 636.63s |
| `PY_FLOWWORKS_PIT_DRAW_CENSUS` | offline | 4-5 | `src/RimMandrake/FlowWorks/selftest_flowworks_pit_draw_census.py` | PASS, 0.17s |
| `PY_FLOWWORKS_PIT_FLOOR_GROUND` | offline | 4-5 | `src/RimMandrake/FlowWorks/selftest_flowworks_pit_floor_ground.py` | PASS, 0.02s |
| `PY_FLOWWORKS_REVIEW1022_SUPERDEEP` | offline | 4-5 | `src/RimMandrake/FlowWorks/selftest_flowworks_review1022_superdeep.py` | PASS, 0.02s |
| `T_PIT_LABEL` | offline | 4-5 | `src/RimMandrake/Utils/selftest_flowworks_stock.py` | PASS, 271.71s |
| `T_PIT_COVER` | offline | 4-5 | `src/RimMandrake/Utils/selftest_flowworks_stock.py` | PASS, 96.18s |
| `PY_FLOWWORKS_COVER_BREAKS` | offline | 4-5 | `src/RimMandrake/FlowWorks/selftest_flowworks_cover_breaks.py` | PASS, 0.07s |
| `PY_SPIKE_FLOAT32_PARITY` | offline | 4-5 | `src/RimMandrake/FlowWorks/Tools/selftest_spike_float32_parity.py` | PASS, 3.1s |
| `T_PIT_ACCESS` | offline | 4-5 | `src/RimMandrake/Utils/selftest_flowworks_stock.py` | PASS, 251.78s |
| `PY_FLOWWORKS_DRAFTED_MOVE_PIT` | offline | 4-5 | `src/RimMandrake/FlowWorks/selftest_flowworks_drafted_move_pit.py` | PASS, 0.02s |
| `PY_FLOWWORKS_PIT_TRAVEL_TAGS` | offline | 4-5 | `src/RimMandrake/FlowWorks/selftest_flowworks_pit_travel_tags.py` | PASS, 0.35s |
| `T_PRISON` | offline | 4-5 | `src/RimMandrake/Utils/selftest_flowworks_stock.py` | PASS, 143.37s |
| `T_DOORS` | offline | 4-5 | `src/RimMandrake/Utils/selftest_flowworks_stock.py` | PASS, 87.97s |
| `PY_FW_GATE_LIFT` | offline | 4-5 | `src/RimMandrake/FlowWorks/Tools/selftest_fw_gate_lift.py` | PASS, 0.19s |
| `T_BRIDGES` | offline | 4-5 | `src/RimMandrake/Utils/selftest_flowworks_stock.py` | PASS, 89.47s |
| `PY_FLOWWORKS_DRAWBRIDGE_POSE` | offline | 4-5 | `src/RimMandrake/FlowWorks/selftest_flowworks_drawbridge_pose.py` | PASS, 0.02s |
| `PY_FLOWWORKS_SUSPENSION_LINKED` | offline | 4-5 | `src/RimMandrake/FlowWorks/selftest_flowworks_suspension_linked.py` | PASS, 0.99s |
| `T_TRENCH` | offline | 4-5 | `src/RimMandrake/Utils/selftest_flowworks_stock.py` | PASS, 138.08s |
| `T_SWIM` | offline | 4-5 | `src/RimMandrake/Utils/selftest_flowworks_stock.py` | PASS, 88.22s |
| `PY_SWIM_SHORE_REACH` | offline | 4-5 | `src/RimMandrake/FlowWorks/selftest_swim_shore_reach.py` | PASS, 89.76s |
| `T_HOSE` | offline | 4-5 | `src/RimMandrake/Utils/selftest_flowworks_stock.py` | PASS, 179.94s |
| `PY_HOSE_OFFLINE` | offline | 4-5 | `src/RimMandrake/FlowWorks/selftest_hose_offline.py` | PASS, 0.28s |
| `PY_HOSE_PORTS` | offline | 4-5 | `src/RimMandrake/FlowWorks/selftest_hose_ports.py` | PASS, 0.88s |
| `PY_HOSE_LAY_SETTLE` | offline | 4-5 | `src/RimMandrake/FlowWorks/selftest_hose_lay_settle.py` | PASS, 0.56s |
| `PY_HOSE_FITTINGS` | offline | 4-5 | `src/RimMandrake/FlowWorks/selftest_hose_fittings.py` | PASS, 2.23s |
| `T_NET` | offline | 4-5 | `src/RimMandrake/Utils/selftest_flowworks_stock.py` | PASS, 90.56s |
| `PY_PUMP_STATION_PORTS` | offline | 4-5 | `src/RimMandrake/FlowWorks/selftest_pump_station_ports.py` | PASS, 0.09s |
| `PY_FLOWWORKS_TANK_DRINK_RECHECK` | offline | 4-5 | `src/RimMandrake/FlowWorks/selftest_flowworks_tank_drink_recheck.py` | PASS, 0.03s |
| `PY_PIPE_SEAT` | offline | 4-5 | `src/RimMandrake/FlowWorks/Tools/selftest_pipe_seat.py` | PASS, 0.86s |
| `T_CONVERT` | offline | 4-5 | `src/RimMandrake/Utils/selftest_flowworks_stock.py` | PASS, 91.82s |
| `T_THIRST` | offline | 4-5 | `src/RimMandrake/Utils/selftest_flowworks_stock.py` | PASS, 126.05s |
| `PY_WATER_NOT_FOOD` | offline | 4-5 | `src/RimMandrake/FlowWorks/Tools/selftest_water_not_food.py` | PASS, 0.08s |
| `PY_NATIVES_DRINK_OWN_WATER` | offline | 4-5 | `src/RimMandrake/FlowWorks/selftest_natives_drink_own_water.py` | PASS, 4.1s |
| `T_DRILL` | offline | 4-5 | `src/RimMandrake/Utils/selftest_flowworks_stock.py` | PASS, 114.35s |
| `T_SPRINKLER` | offline | 4-5 | `src/RimMandrake/Utils/selftest_flowworks_stock.py` | PASS, 103.75s |
| `T_RIVER` | offline | 4-5 | `src/RimMandrake/Utils/selftest_flowworks_stock.py` | PASS, 90.97s |
| `PY_FLOWWORKS_RIVERS` | offline | 4-5 | `src/RimMandrake/FlowWorks/selftest_flowworks_rivers.py` | PASS, 0.03s |
| `PY_FLOWWORKS_RIVER_COLORS` | offline | 4-5 | `src/RimMandrake/FlowWorks/selftest_flowworks_river_colors.py` | PASS, 0.17s |
| `PY_WEIR_INSTALLED` | offline | 4-5 | `src/RimMandrake/FlowWorks/Tools/selftest_weir_installed.py` | PASS, 37.7s |
| `T_MAP_CONTROLS` | offline | 4-5 | `src/RimMandrake/Utils/selftest_flowworks_stock.py` | PASS, 164.52s |
| `T_QUARRY` | offline | 4-5 | `src/RimMandrake/Utils/selftest_flowworks_stock.py` | PASS, 88.61s |
| `T_ICE` | offline | 4-5 | `src/RimMandrake/Utils/selftest_flowworks_stock.py` | PASS, 106.37s |
| `T_UNDERLIQUID` | offline | 4-5 | `src/RimMandrake/Utils/selftest_flowworks_stock.py` | PASS, 105.89s |
| `PY_FLOWWORKS_UNDERLIQUID_PARITY` | offline | 4-5 | `src/RimMandrake/FlowWorks/selftest_flowworks_underliquid_parity.py` | PASS, 0.18s |
| `PY_LIQUID_LOOK_TUNE` | offline | 4-5 | `src/RimMandrake/FlowWorks/selftest_liquid_look_tune.py` | PASS, 0.03s |
| `PY_FLOWWORKS_TANK_SHADOW` | offline | 4-5 | `src/RimMandrake/FlowWorks/selftest_flowworks_tank_shadow.py` | PASS, 0.02s |
| `T_STYLES` | offline | 4-5 | `src/RimMandrake/Utils/selftest_flowworks_stock.py` | PASS, 105.12s |
| `PY_FW_OFFLINE_ART` | offline | 4-5 | `src/RimMandrake/FlowWorks/Tools/selftest_fw_offline_art.py` | PASS, 17.62s |
| `PY_LIQUID_LOOKS` | offline | 4-5 | `src/RimMandrake/FlowWorks/Tools/selftest_liquid_looks.py` | PASS, 0.07s |
| `PY_FLOWWORKS_PIPE_POLE_ART` | offline | 4-5 | `src/RimMandrake/FlowWorks/selftest_flowworks_pipe_pole_art.py` | PASS, 0.02s |
| `T_GEYSER_TUB` | offline | 4-5 | `src/RimMandrake/Utils/selftest_flowworks_stock.py` | PASS, 246.45s |
| `PY_FLOWWORKS_GEYSER_TUB` | offline | 4-5 | `src/RimMandrake/FlowWorks/selftest_flowworks_geyser_tub.py` | PASS, 0.81s |
| `T_SETTINGS_SWEEP_OFFLINE` | offline | 4-5 | `src/RimMandrake/Utils/selftest_flowworks_stock.py` | PASS, 139.75s |
| `PY_SETTINGS_REGISTRY` | offline | 4-5 | `src/RimMandrake/FlowWorks/northstar/selftest_settings_registry.py` | PASS, 0.04s |
| `PY_SETTINGS_SEARCH` | offline | 4-5 | `src/RimMandrake/FlowWorks/selftest_settings_search.py` | PASS, 1.17s |
| `PY_FLOWWORKS_NORTHSTAR` | offline | 4-5 | `src/RimMandrake/FlowWorks/northstar/selftest_flowworks_northstar.py` | PASS, 33.74s |
| `PY_VALIDATION_V2_OFFLINE` | offline | 4-5 | `src/RimMandrake/FlowWorks/northstar/validation_v2.py` | PASS, 57.51s |
| `T_TOSS_FLAME_OFFLINE` | offline | 4-5 | `src/RimMandrake/FlowWorks/selftest_stage3_owed.py` | PASS, 0.37s |
| `T_FETCH_FALLEN_OFFLINE` | offline | 4-5 | `src/RimMandrake/FlowWorks/selftest_stage3_owed.py` | PASS, 0.6s |
| `T_PRISON_CARE_OFFLINE` | offline | 4-5 | `src/RimMandrake/FlowWorks/selftest_stage3_owed.py` | PASS, 0.08s |
| `T_DIG_TIME_ARITHMETIC` | offline | 4-5 | `(specified, Stage 3)` | not run: specified, not built |
| `sc_dig_and_read` | live_minimal | 6 | `src/RimMandrake/FlowWorks/northstar/extensions.py` | not run (offline only); entry exists |
| `sc_dig_finds` | live_minimal | 6 | `src/RimMandrake/FlowWorks/northstar/extensions.py` | not run (offline only); entry exists |
| `sc_fill_front` | live_minimal | 6 | `src/RimMandrake/FlowWorks/northstar/concept_scenes.py` | not run (offline only); entry exists |
| `sc_fill_tiers` | live_minimal | 6 | `src/RimMandrake/FlowWorks/northstar/extensions.py` | not run (offline only); entry exists |
| `sc_one_surface` | live_minimal | 6 | `src/RimMandrake/FlowWorks/northstar/concept_scenes.py` | not run (offline only); entry exists |
| `sc_source_pays` | live_minimal | 6 | `src/RimMandrake/FlowWorks/northstar/concept_scenes.py` | not run (offline only); entry exists |
| `sc_canal_fire` | live_minimal | 6 | `src/RimMandrake/FlowWorks/northstar/validation_v2.py` | not run (offline only); entry exists |
| `sc_slime` | live_minimal | 6 | `src/RimMandrake/FlowWorks/northstar/extensions.py` | not run (offline only); entry exists |
| `sc_pawn_height` | live_minimal | 6 | `src/RimMandrake/FlowWorks/northstar/concept_scenes.py` | not run (offline only); entry exists |
| `sc_pit_reads` | live_minimal | 6 | `src/RimMandrake/FlowWorks/northstar/extensions.py` | not run (offline only); entry exists |
| `sc_covered_pit` | live_minimal | 6 | `src/RimMandrake/FlowWorks/northstar/extensions.py` | not run (offline only); entry exists |
| `sc_ways_out` | live_minimal | 6 | `src/RimMandrake/FlowWorks/northstar/live_session.py` | not run (offline only); entry exists |
| `sc_sluice` | live_minimal | 6 | `src/RimMandrake/FlowWorks/northstar/extensions.py` | not run (offline only); entry exists |
| `sc_hose_look` | live_minimal | 6 | `src/RimMandrake/FlowWorks/northstar/concept_scenes.py` | not run (offline only); entry exists |
| `sc_one_network` | live_minimal | 6 | `src/RimMandrake/FlowWorks/northstar/extensions.py` | not run (offline only); entry exists |
| `sc_trench_cover_pawns` | live_minimal | 6 | `src/RimMandrake/FlowWorks/northstar/concept_scenes.py` | not run (offline only); entry exists |
| `sc_hung_bridge` | live_minimal | 6 | `src/RimMandrake/FlowWorks/northstar/suspension_bridge_proof.py` | not run (offline only); entry exists |
| `sc_ice` | live_minimal | 6 | `src/RimMandrake/FlowWorks/northstar/concept_scenes.py` | not run (offline only); entry exists |
| `sc_river` | live_minimal | 6 | `src/RimMandrake/FlowWorks/northstar/river_scenes_walk.py` | not run (offline only); entry exists |
| `sc_moat_walkers` | live_minimal | 6 | `src/RimMandrake/FlowWorks/northstar/concept_scenes.py` | not run (offline only); entry exists |
| `sc_hole_prison` | live_minimal | 6 | `src/RimMandrake/FlowWorks/northstar/concept_scenes.py` | not run (offline only); entry exists |
| `sc_toss_flame` | live_minimal | 6 | `src/RimMandrake/FlowWorks/northstar/concept_scenes.py` | not run (offline only); entry exists |
| `sc_islands_walker` | live_minimal | 6 | `src/RimMandrake/FlowWorks/northstar/concept_scenes.py` | not run (offline only); entry exists |
| `sc_walk` | live_full | 6 | `src/RimMandrake/FlowWorks/northstar/concept_scenes.py` | not run (offline only); entry exists |
| `sc_garden` | live_minimal | 6 | `src/RimMandrake/FlowWorks/northstar/concept_scenes.py` | not run (offline only); entry exists |
| `LOOK_STAGE8` | look | 8 | `(his walk)` | not run: Stage 8 |
| `LOOK_BLIND_READER` | look | 6 | `src/RimMandrake/FlowWorks/northstar/blind_reader.py` | not run (offline only); entry exists |
| `OL_OWNER_LOOK_READS` | live_minimal | 6 | `src/RimMandrake/FlowWorks/northstar/owner_look_regressions.py` | not run (offline only); entry exists |
| `sc_geyser_tub` | live_minimal | 6 | `src/RimMandrake/FlowWorks/northstar/concept_scenes.py` | not run (offline only); entry exists |
| `T_LIQUID_COATING_OFFLINE` | offline | 4-5 | `src/RimMandrake/FlowWorks/selftest_stage3_owed.py` | PASS, 0.6s |
| `sc_coating_wash` | live_minimal | 6 | `src/RimMandrake/FlowWorks/northstar/concept_scenes.py` | not run (offline only); entry exists |
| `T_PIT_LOOK_1114` | offline | 4-5 | `src/RimMandrake/Utils/selftest_flowworks_stock.py` | PASS, 206.52s |
| `PIT_LOOK_1114_LIVE` | live_minimal | 6 | `src/RimMandrake/FlowWorks/northstar/pit_look_1114_live.py` | not run (offline only); entry exists |
| `T_MODERN_FIT_OFFLINE` | offline | 4-5 | `src/RimMandrake/FlowWorks/Tools/selftest_fw_modern_fit.py` | RED rc 1, 3.41s |
| `T_PIPE_ATLAS_CELL_OFFLINE` | offline | 4-5 | `src/RimMandrake/FlowWorks/Tools/selftest_pipe_atlas_cell_geometry.py` | PASS, 0.26s |
| `T_PLAYER_TRUTHS_ART_OFFLINE` | offline | 4-5 | `src/RimMandrake/FlowWorks/Tools/selftest_player_truths_art.py` | PASS, 1.08s |
| `T_WEIR_LOOKS_OFFLINE` | offline | 4-5 | `src/RimMandrake/FlowWorks/Tools/selftest_weir_looks.py` | PASS, 37.64s |
| `T_WEIR_MATERIAL_OFFLINE` | offline | 4-5 | `src/RimMandrake/FlowWorks/Tools/selftest_weir_material.py` | PASS, 0.02s |
| `T_WEIR_SPILL_OFFLINE` | offline | 4-5 | `src/RimMandrake/FlowWorks/Tools/selftest_weir_spill_animated.py` | PASS, 1.5s |
| `T_MODERN_BRIDGE_ART_OFFLINE` | offline | 4-5 | `src/RimMandrake/FlowWorks/art_source/ModernBridge/selftest_modern_bridge_art.py` | PASS, 3.04s |
| `T_SUSPENSION_REDESIGN_ART_OFFLINE` | offline | 4-5 | `src/RimMandrake/FlowWorks/art_source/SuspensionRedesign/selftest_suspension_redesign.py` | PASS, 12.51s |
| `T_CONSERVATION_ROUNDTRIP_OFFLINE` | offline | 4-5 | `src/RimMandrake/FlowWorks/northstar/selftest_conservation_roundtrip.py` | PASS, 0.18s |
| `T_HOLE_PRISON_OFFLINE` | offline | 4-5 | `src/RimMandrake/FlowWorks/northstar/selftest_hole_prison.py` | PASS, 97.28s |
| `T_JAWA_SHALLOWS_OFFLINE` | offline | 4-5 | `src/RimMandrake/FlowWorks/northstar/selftest_jawa_shallows_proof.py` | PASS, 0.03s |
| `T_LEVEL_WATER_OFFLINE` | offline | 4-5 | `src/RimMandrake/FlowWorks/northstar/selftest_level_water.py` | PASS, 4.71s |
| `T_POND_CAPACITY_RULE_OFFLINE` | offline | 4-5 | `src/RimMandrake/FlowWorks/northstar/selftest_pond_capacity_rule.py` | PASS, 0.04s |
| `T_BELT_FIXES_H_OFFLINE` | offline | 4-5 | `src/RimMandrake/FlowWorks/selftest_flowworks_belt_fixes_h.py` | PASS, 0.03s |
| `T_CALL_SITES_OFFLINE` | offline | 4-5 | `src/RimMandrake/FlowWorks/selftest_flowworks_call_sites.py` | PASS, 1.47s |
| `T_DRAWBRIDGE_ART_OFFLINE` | offline | 4-5 | `src/RimMandrake/FlowWorks/selftest_flowworks_drawbridge_art.py` | PASS, 0.19s |
| `T_FROZEN_HANDOVER_OFFLINE` | offline | 4-5 | `src/RimMandrake/FlowWorks/selftest_flowworks_frozen_handover.py` | PASS, 0.01s |
| `T_GPT_B_FIXES_OFFLINE` | offline | 4-5 | `src/RimMandrake/FlowWorks/selftest_flowworks_gpt_b.py` | PASS, 0.05s |
| `T_GPT_BATCH_A_FIXES_OFFLINE` | offline | 4-5 | `src/RimMandrake/FlowWorks/selftest_flowworks_gpt_batch_a.py` | PASS, 0.05s |
| `T_GPT_C_FIXES_OFFLINE` | offline | 4-5 | `src/RimMandrake/FlowWorks/selftest_flowworks_gpt_c.py` | PASS, 0.15s |
| `T_LOOKS_ROUND_OFFLINE` | offline | 4-5 | `src/RimMandrake/FlowWorks/selftest_flowworks_looks_round.py` | PASS, 0.02s |
| `T_REVIEW1022_LIQUIDNET_OFFLINE` | offline | 4-5 | `src/RimMandrake/FlowWorks/selftest_flowworks_review1022_liquidnet.py` | PASS, 0.01s |
| `T_REVIEW1022_SHEET_OFFLINE` | offline | 4-5 | `src/RimMandrake/FlowWorks/selftest_flowworks_review1022_sheet.py` | PASS, 0.01s |
| `T_SALT_BREAK_POTABLE_OFFLINE` | offline | 4-5 | `src/RimMandrake/FlowWorks/selftest_flowworks_salt_break_potable.py` | PASS, 0.03s |
| `T_SPREADING_FUEL_IRRIGATION_OFFLINE` | offline | 4-5 | `src/RimMandrake/FlowWorks/selftest_flowworks_spreading_fuel_irrigation.py` | PASS, 0.02s |
| `T_SUSPENSION_ART_OFFLINE` | offline | 4-5 | `src/RimMandrake/FlowWorks/selftest_flowworks_suspension_art.py` | PASS, 26.91s |
| `T_SWALE_STATIC_OFFLINE` | offline | 4-5 | `src/RimMandrake/FlowWorks/selftest_flowworks_swale.py` | PASS, 0.02s |
| `T_FREEZE_BIG_MAP_OFFLINE` | offline | 4-5 | `src/RimMandrake/FlowWorks/selftest_freeze_big_map.py` | PASS, 0.04s |
| `T_HEAVY_TRUSS_LABELS_OFFLINE` | offline | 4-5 | `src/RimMandrake/FlowWorks/selftest_heavy_truss_labels.py` | PASS, 0.02s |
| `T_HOSE_PIPE_SADDLE_OFFLINE` | offline | 4-5 | `src/RimMandrake/FlowWorks/selftest_hose_pipe_saddle.py` | PASS, 0.05s |
| `T_HOSE_PORT_OFFLINE` | offline | 4-5 | `src/RimMandrake/FlowWorks/selftest_hose_port.py` | PASS, 0.71s |
| `T_PIPE_GIRTH_OFFLINE` | offline | 4-5 | `src/RimMandrake/FlowWorks/selftest_pipe_girth_half.py` | PASS, 0.18s |
| `T_PUMP_STATION_PORTS_COMPILED_OFFLINE` | offline | 4-5 | `src/RimMandrake/FlowWorks/selftest_pump_station_ports_compiled.py` | PASS, 0.02s |
| `T_TANK_ART_EDGES_OFFLINE` | offline | 4-5 | `src/RimMandrake/FlowWorks/selftest_tank_art_edges.py` | PASS, 0.33s |
| `T_THERMOSTAT_SUBNOTCH_OFFLINE` | offline | 4-5 | `src/RimMandrake/FlowWorks/selftest_thermostat_subnotch.py` | PASS, 0.12s |
| `T_WRECKED_LINKS_OFFLINE` | offline | 4-5 | `src/RimMandrake/FlowWorks/selftest_wrecked_links_draw_in.py` | PASS, 0.34s |
| `T_POND_FILM_OFFLINE` | offline | 4-5 | `src/RimMandrake/Utils/selftest_flowworks_pond_film.py` | PASS, 0.02s |
| `T_SHEET_KERNEL_OFFLINE` | offline | 4-5 | `src/RimMandrake/Utils/selftest_flowworks_sheet.py` | PASS, 97.39s |
| `T_TRENCH_COVER_CSHARP_OFFLINE` | offline | 4-5 | `src/RimMandrake/Utils/selftest_flowworks_trench_cover.py` | PASS, 167.07s |

## Held look statements placed (103 rows)

| row | bars | test | stage | kind |
|---|---|---|---|---|
| 2026-11-12#1 | fill_level_legible, inv_looks, inv_liquid_roster | T_UNDERLIQUID + OL_OWNER_LOOK_READS | 4-5 and 6 | offline law + in-game state read |
| 2026-11-12#2 | fill_level_legible, inv_looks | T_UNDERLIQUID + OL_OWNER_LOOK_READS | 4-5 and 6 | offline law + in-game state read |
| 2026-11-12#3 | fill_level_legible, inv_looks | T_UNDERLIQUID + OL_OWNER_LOOK_READS | 6 | approval kept for re-check: in-game state read |
| 2026-11-12#4 | fill_level_legible, inv_looks, ways_in_and_out | T_UNDERLIQUID + OL_OWNER_LOOK_READS | 6 | in-game state read |
| 2026-11-12#5 | fill_level_legible, inv_looks, sluice_drains_on_command | T_UNDERLIQUID + OL_OWNER_LOOK_READS | 6 | approval kept for re-check: in-game state read |
| 2026-11-12#6 | fill_level_legible, inv_looks | T_UNDERLIQUID + OL_OWNER_LOOK_READS | 6 | in-game state read |
| 2026-11-12#7 | - | none: his question, answered by row 13 of the same file | - | question (answered) |
| 2026-11-12#8 | fill_level_legible, inv_looks, ways_in_and_out | T_UNDERLIQUID + OL_OWNER_LOOK_READS | 6 | in-game state read |
| 2026-11-12#9a | fill_level_legible, inv_looks | T_UNDERLIQUID + OL_OWNER_LOOK_READS | 4-5 and 6 | offline law + in-game state read |
| 2026-11-12#9b | fill_level_legible, inv_looks | T_UNDERLIQUID + OL_OWNER_LOOK_READS | 4-5 and 6 | offline law + in-game state read |
| 2026-11-12#9c | fill_level_legible, inv_looks | T_UNDERLIQUID + LOOK_STAGE8 | 4-5 and 8 | offline parity + look only (wash colour has no reader) |
| 2026-11-12#9d | fill_level_legible, inv_looks | T_UNDERLIQUID + OL_OWNER_LOOK_READS | 4-5 and 6 | offline law + in-game state read |
| 2026-11-12#9e | fill_level_legible, inv_looks | T_UNDERLIQUID (PY_FLOWWORKS_UNDERLIQUID_PARITY: one law for every drawer) | 4-5 | offline selftest |
| 2026-11-12#10a | fill_level_legible, inv_looks, pit_reads_as_hole | OL_OWNER_LOOK_READS (brim_no_shade_outside capture row) | 6 | in-game capture |
| 2026-11-12#10b | fill_level_legible, inv_looks, pit_reads_as_hole | T_UNDERLIQUID + OL_OWNER_LOOK_READS | 4-5 and 6 | offline law + in-game state read |
| 2026-11-12#11a | covered_pit_springs | T_PIT_COVER + OL_OWNER_LOOK_READS | 6 | approval kept for re-check: in-game state read |
| 2026-11-12#11b | covered_pit_springs, inv_pits | T_PIT_COVER (PitCover_rests_on_two_banks) | 4-5 | offline selftest |
| 2026-11-12#12 | canal_reads_as_dug, inv_dig_depth | OL_OWNER_LOOK_READS + LOOK_STAGE8 (swale texture is art) | 6 and 8 | in-game state read + look only |
| 2026-11-12#13 | fill_level_legible, inv_looks, pit_reads_as_hole | T_UNDERLIQUID + OL_OWNER_LOOK_READS | 4-5 and 6 | offline law + in-game state read |
| 2026-11-12#14 | inv_looks | big pit review scene (northstar/selftest_big_pit_scene.py offline; the scene itself feeds LOOK_STAGE8) | 6 and 8 | staging for his look |
| 2026-11-12#15 | inv_looks | big pit review scene (BP*_furn rows) + OL_OWNER_LOOK_READS (OL_buildings_covered) | 6 | in-game state read |
| 2026-11-12#16 | - | harness: src/RimMandrake/Utils/selftest_validation_core_site.py (open-sky site) | 4-5 | harness, no FlowWorks bar (floor line test_isolation) |
| 2026-11-12#17 | - | harness: as row 16 | 4-5 | harness, no FlowWorks bar |
| 2026-11-12#18 | inv_looks | big pit review scene (per-thing rows, HP against spawn_baseline.json) | 6 | staging for his look |
| 2026-11-12#19 | inv_looks | as row 14 | 6 and 8 | staging for his look |
| 2026-11-12#20 | pit_reads_as_hole | T_PIT_LABEL (offline) + on-screen label text BLOCKED (RIMMANDRAKE_ADD_PIT_LABEL_STATE_READER_MOUSEOVER_HAS_NONE) | 4-5 and 6 | offline selftest + blocked in-game read |
| 2026-11-12#21 | inv_map_controls | T_MAP_CONTROLS (GodLiquid_*) | 4-5 | offline selftest |
| 2026-11-12#22 | fill_level_legible, inv_looks | T_UNDERLIQUID (parity: shallow end) + LOOK_STAGE8 | 4-5 and 8 | approval kept for re-check: offline parity + look |
| 2026-11-12#23 | fill_level_legible, inv_looks | T_UNDERLIQUID (parity: deep opacity; replaced by row 41) | 4-5 | offline parity |
| 2026-11-12#24 | fill_level_legible, inv_looks | T_UNDERLIQUID + LOOK_STAGE8 | 4-5 and 8 | offline parity + look only (taste) |
| 2026-11-12#25 | fill_level_legible, inv_looks, pit_reads_as_hole | T_UNDERLIQUID (dry floor = wet floor ground) + LOOK_STAGE8 | 4-5 and 8 | offline parity + look only |
| 2026-11-12#26 | - | harness: big pit scene wildlife_none_left rows | 6 | harness staging (and his question, answered) |
| 2026-11-12#27 | inv_looks | big pit review scene (pack_layout, BP*_inside_margin) | 4-5 and 6 | staging for his look |
| 2026-11-12#28 | fill_level_legible, inv_looks | T_UNDERLIQUID + OL_OWNER_LOOK_READS (OL_buildings_covered) | 4-5 and 6 | offline law + in-game state read |
| 2026-11-12#29 | fill_level_legible, inv_looks | T_UNDERLIQUID + OL_OWNER_LOOK_READS (OL_no_surface_shadow) | 4-5 and 6 | offline law + in-game state read |
| 2026-11-12#30 | - | process: capture_list.json puts the deepest copy first (Stage 7 pre-human check) | 7 | process instruction, no bar |
| 2026-11-12#31 | - | harness: src/RimMandrake/Utils/selftest_screenshot_mode_restored.py + OL_screenshot_mode_off | 4-5 and 6 | harness, no FlowWorks bar |
| 2026-11-12#32 | - | harness: as row 31 | 4-5 and 6 | harness, no FlowWorks bar |
| 2026-11-12#33a | inv_geyser_tub | T_GEYSER_TUB | 4-5 (live owed) | offline selftest; bar added by his card 2026-11-14 |
| 2026-11-12#33b | inv_geyser_tub | T_GEYSER_TUB + LOOK_STAGE8 (bubble art) | 4-5 and 8 | defect; bar added by his card 2026-11-14 |
| 2026-11-12#33c | inv_geyser_tub | T_GEYSER_TUB | 4-5 (live owed) | defect; bar added by his card 2026-11-14 |
| 2026-11-12#34 | fill_level_legible, inv_looks | OL_OWNER_LOOK_READS (OL_overlays_hidden; blocked on the overlay proof hook) | 6 | blocked on a proof hook |
| 2026-11-12#35 | fill_level_legible, inv_looks | OL_OWNER_LOOK_READS (OL_overlays_hidden; blocked on the overlay proof hook) | 6 | blocked on a proof hook |
| 2026-11-12#36 | fill_level_legible, inv_looks | OL_OWNER_LOOK_READS (OL_overlays_hidden; blocked on the overlay proof hook) | 6 | blocked on a proof hook |
| 2026-11-12#37 | inv_map_controls | T_MAP_CONTROLS (specified case GodLiquid_no_god_mode_in_names) | 2 and 4-5 | offline text check (specified) |
| 2026-11-12#38 | inv_map_controls | T_MAP_CONTROLS (specified case GodLiquid_pour_over_brim_overflows_never_no_room) + OL_OWNER_LOOK_READS (OL_pour_never_no_room) | 4-5 and 6 | offline (specified) + in-game read |
| 2026-11-12#39 | fill_flows_along_canal | LOOK_STAGE8 (motion over time) | 8 | look only |
| 2026-11-12#40 | fill_level_legible, inv_looks | T_UNDERLIQUID (specified parity: blue share rises with depth) + LOOK_STAGE8 | 4-5 and 8 | offline (specified) + look |
| 2026-11-12#41 | fill_level_legible, inv_looks | T_UNDERLIQUID (specified parity: 4 m hides >= DeepOpacity) + LOOK_STAGE8 | 4-5 and 8 | offline (specified) + look |
| 2026-11-12#42 | inv_geyser_tub | capture ring-luminance row of the geyser pit (specified) | 6 | defect; bar added by his card 2026-11-14 |
| 2026-11-12#43 | fill_level_legible, inv_looks | T_UNDERLIQUID + OL_OWNER_LOOK_READS (OL_corpses_covered) + overlay hook | 6 | in-game state read + blocked hook |
| 2026-11-12#44 | fill_level_legible, inv_looks | OL_OWNER_LOOK_READS (OL_overlays_hidden; blocked on the overlay proof hook) | 6 | blocked on a proof hook |
| 2026-11-12#45 | fill_level_legible, inv_looks | OL_OWNER_LOOK_READS (OL_overlays_hidden; blocked on the overlay proof hook) | 6 | blocked on a proof hook |
| 2026-11-12#46 | fill_level_legible, inv_looks | OL_OWNER_LOOK_READS (OL_overlays_hidden; blocked on the overlay proof hook) | 6 | blocked on a proof hook |
| 2026-11-12#47 | fill_level_legible, inv_looks | T_UNDERLIQUID + OL_OWNER_LOOK_READS (OL_opaque_hides on item Novel) | 6 | in-game state read (seen by the Conductor, not his words) |
| 2026-11-12#48 | - | rule: the holding store itself (README.md) | - | rule, no bar |
| 2026-11-13#1 | inv_geyser_tub | T_GEYSER_TUB + LOOK_STAGE8 | 8 | approval; bar added by his card 2026-11-14 |
| 2026-11-13#2 | inv_geyser_tub | T_GEYSER_TUB (vent, plume and pool square share one cell) | 4-5 | defect; bar added by his card 2026-11-14 |
| 2026-11-13#3 | - | process: every scene reads as its caption (Stage 7 pre-human check) | 7 | look only, process |
| 2026-11-13#4 | inv_geyser_tub | T_GEYSER_TUB + T_UNDERLIQUID (vent seen at its depth) | 4-5 | defect; bar added by his card 2026-11-14 |
| 2026-11-13#5 | ways_in_and_out | T_PIT_ACCESS + staging reachability read | 4-5 and 6 | offline + in-game read |
| 2026-11-13#6 | ways_in_and_out | T_PIT_ACCESS (LadderClimb_*) | 4-5 | approval kept for re-check: offline selftest |
| 2026-11-13#7 | ways_in_and_out | T_PIT_ACCESS (PY_FLOWWORKS_DRAFTED_MOVE_PIT) + sc_ways_out | 4-5 and 6 | offline + in-game read |
| 2026-11-13#8 | inv_liquid_coating | T_LIQUID_COATING_OFFLINE + sc_coating_wash (owed Stage 3) | 4-5 and 6 | defect; bar added by his card 2026-11-14 |
| 2026-11-13#9 | ways_in_and_out | pit exposure thought math (specified offline case in T_PIT_ACCESS) | 4-5 | offline (specified) |
| 2026-11-13#10 | inv_liquid_coating | T_LIQUID_COATING_OFFLINE + sc_coating_wash (owed Stage 3) | 4-5 and 6 | defect; bar added by his card 2026-11-14 |
| 2026-11-13#11 | inv_liquid_coating | T_LIQUID_COATING_OFFLINE + sc_coating_wash (owed Stage 3) | 4-5 and 6 | defect; bar added by his card 2026-11-14 |
| 2026-11-13#12 | inv_geyser_tub | T_GEYSER_TUB + PY_FLOWWORKS_GEYSER_TUB (heat only through the water over the vent: C# GeyserTub_heat_only_through_the_water_over_the_vent, python check 16) | 4-5 | defect; bar added by his card 2026-11-14 |
| 2026-11-13#13 | fill_level_legible, inv_looks | LOOK_STAGE8 | 8 | approval, look only (taste) |
| 2026-11-13#14 | fill_level_legible, inv_looks | OL_OWNER_LOOK_READS (OL_overlays_hidden; blocked on the overlay proof hook) | 6 | approval kept for re-check |
| 2026-11-13#15 | fill_level_legible, inv_looks | OL_OWNER_LOOK_READS (OL_overlays_hidden; blocked on the overlay proof hook) | 6 | blocked on a proof hook |
| 2026-11-13#16 | fill_level_legible, inv_looks | OL_OWNER_LOOK_READS (OL_overlays_hidden; blocked on the overlay proof hook) | 6 | approval kept for re-check |
| 2026-11-13#17 | ways_in_and_out, pit_reads_as_hole | T_PIT_ACCESS (PY_FLOWWORKS_DRAFTED_MOVE_PIT checks only the destination remap; the release ring and the pit's top rows are unchecked) + sc_ways_out | 4-5 and 6 | offline (partly specified) + in-game read |
| 2026-11-13#18 | - | harness: tier_cut_creature_check.py against proof-scene creatures | 2 | harness staging, no FlowWorks bar |
| 2026-11-13_dig_interface#1 | canal_reads_as_dug, inv_dig_depth | T_DIG_TIME_ARITHMETIC (specified; the speed target is 0.2.0 work) | 4-5 | offline arithmetic (specified); next version (FlowWorks 0.2.0 Divergent): the dig speed is a question inside the dig-interface redesign, his card 2026-11-13 10:12 PM PST ("All in the next version") |
| 2026-11-13_dig_interface#2 | - | none: next version (version/next_version/README.md) | - | next version (FlowWorks 0.2.0 Divergent): the dig-interface redesign, his card 2026-11-13 10:12 PM PST ("All in the next version") |
| 2026-11-13_evening#1 | inv_geyser_tub | T_GEYSER_TUB (fleck count, size, alpha in bounds; offline) | 4-5 | defect; bar added by his card 2026-11-14 |
| 2026-11-13_evening#2 | fill_level_legible, inv_looks | T_UNDERLIQUID (things lying flat draw under the sheet) | 4-5 | offline law |
| 2026-11-13_evening#3 | fill_level_legible, inv_looks, pit_reads_as_hole | T_UNDERLIQUID (every draw path enumerated; sprite inside the pit) | 4-5 | offline law |
| 2026-11-13_evening#4 | fill_level_legible, inv_looks | T_UNDERLIQUID (overlays follow the depth rule) + OL_OWNER_LOOK_READS | 4-5 and 6 | offline law + in-game read |
| 2026-11-13_evening#5 | fill_level_legible, inv_looks | T_UNDERLIQUID (NeedsPower and PowerOff fade with depth) | 4-5 | offline law |
| 2026-11-14#8b | inv_geyser_tub | T_GEYSER_TUB (GeyserTub_plume_is_bubbling_water) + LOOK_STAGE8 | 4-5 and 8 | approval (KEEP); bar added by his card 2026-11-14 |
| 2026-11-14#8c | inv_geyser_tub | sc_geyser_tub (Hot Tub on mouse-over; owed Stage 3) | 6 | defect; bar added by his card 2026-11-14 |
| 2026-11-14#1 | ways_in_and_out, inv_pit_access | T_PIT_LOOK_1114 (PitLook1114_pit_floor_walks_full_speed_readout_and_step) + PIT_LOOK_1114_LIVE | 4-5 and 6 | defect, fixed a9866498909a |
| 2026-11-14#2 | - | none: not this mod's | - | other mod: shared interaction spots (RIMMANDRAKE_ALLOW_SHARED_INTERACTION_SPOTS_TWO_BENCHES_ONE_STOOL) |
| 2026-11-14#3 | inv_pits | T_PIT_LOOK_1114 (PitLook1114_furniture_never_straddles_a_pit_edge) + PIT_LOOK_1114_LIVE | 4-5 and 6 | defect, fixed 7f25ff2060ea |
| 2026-11-14#4 | - | specified: RM_Swale is a TerrainDef, not a Building (RIMMANDRAKE_REBUILD_SWALE_AS_SOAKING_FLOOR_NOT_FURNITURE) | 4-5 | NO 0.1.0 BAR yet: no bar names the swale; Problem (a new bar now) or Divergent is his call |
| 2026-11-14#5 | inv_dig_depth | specified offline: a dig in sand, mud or loose snow is refused on every path (RIMMANDRAKE_REFUSE_PITS_IN_LOOSE_GROUND_EVEN_BY_BRIDGE) | 4-5 | defect, owed; the dig scenario's sand pad (tree.json canal_reads_as_dug) now contradicts his row: question |
| 2026-11-14#6 | - | none: staging | - | harness: the staged pits lost their water at the save-format change (diagnosed on RIMMANDRAKE_PROVE_UNDER_LIQUID_LAW_LIVE) |
| 2026-11-14#7 | inv_looks, fill_level_legible | T_UNDERLIQUID (Submerge_overlays_follow_their_thing, Submerge_murk_keeps_rising_to_the_plateau) + LOOK_STAGE8 | 4-5 and 8 | approval kept for re-check |
| 2026-11-14#7b | inv_looks | T_PIT_LOOK_1114 (PitLook1114_drowned_body_cover_is_the_pawns_own_picture) + LOOK_STAGE8 (the cover is a picture: his walk 2026-11-20 judged it FAIL; RIMMANDRAKE_REDRAW_FLOWWORKS_SUNK_PAWN_NOT_TWO_BLUE_PATCHES) | 4-5 and 8 | defect, fixed 3f774eb730 |
| 2026-11-14#8 | - | none: next version | - | next version (FlowWorks 0.2.0 Divergent): RIMMANDRAKE_SHORT_DROWNED_ELECTRONICS_LIKE_RAIN_DOES, his own words |
| 2026-11-14#9 | - | none: dev tooling | - | harness: approval of the debug Pour menu layout (dev tooling, no player bar) |
| 2026-11-14#9b | - | T_PIT_LOOK_1114 (PitLook1114_pour_steps_each_show_metres_on_one_tile, PitLook1114_no_fill_n_wording_in_visible_text) | 4-5 | harness: debug Pour menu wording (dev tooling), fixed 7acbbf887b |
| 2026-11-14#10 | - | none until designed | - | next version (FlowWorks 0.2.0 Divergent): RIMMANDRAKE_DESIGN_SPILLED_WATER_WET_GROUND_ONE_STATE (row 10f's ruling) |
| 2026-11-14#10b | - | stage.py b2_drain_all row | - | harness: approval of the debug Drain option (dev tooling) |
| 2026-11-14#10c | - | none until designed | - | next version (FlowWorks 0.2.0 Divergent): RIMMANDRAKE_DESIGN_SPILLED_WATER_WET_GROUND_ONE_STATE (row 10f's ruling) |
| 2026-11-14#10d | inv_overflow_sheet | T_SHEET (soak-in, freeze and thaw) + LOOK_STAGE8 | 4-5 and 8 | approval kept for re-check (evaporation); the wet ground left after is next version (row 10f) |
| 2026-11-14#10e | - | none: answered by row 10f | - | question, answered by row 10f |
| 2026-11-14#10f | - | none until designed | - | next version (FlowWorks 0.2.0 Divergent): his ruling of 2026-11-14 12:01 PM PST, all wetness one thin film (RIMMANDRAKE_DESIGN_SPILLED_WATER_WET_GROUND_ONE_STATE) |
| 2026-11-14#11 | inv_doors, sluice_drains_on_command | specified offline: the cell under a sluice gate reads the pit's level (RIMMANDRAKE_SEAL_SLUICE_AT_ITS_PANEL_NOT_ITS_SQUARE) | 4-5 | defect, diagnosed not fixed |
| 2026-11-14#12 | inv_pits | T_PIT_LOOK_1114 (PitLook1114_floor_on_a_pit_survives_water_and_is_named) + PIT_LOOK_1114_LIVE | 4-5 and 6 | defect, fixed f64db2c740 |
| 2026-11-14#12b | - | none until designed | - | next version (FlowWorks 0.2.0 Divergent): RIMMANDRAKE_LINE_PITS_WITH_FLOORS_AND_WALLS_ROCK_FREE, his own words |

## Judge corrections

FlowWorks has no coverage_verdict.json and no coverage_fixes.json: the Arbiter signed all 59 rows covered on 2026-11-05 at the locked tree and sheet; no judge correction is open (version/gaps_sorted.md).

## The settings sweep, moved offline

inv_settings: the per-toggle default check is decided offline by T_SETTINGS_SWEEP_OFFLINE (C# SettingsReset/MachinerySettings/Settings cases, the settings registry selftest, the settings search selftest, the northstar selftest's registry rows, and validation_v2.py --offline O2's C# toggle census). The game keeps only sc_walk's master switch off and on mid-game, which needs a running colony. validation_v2's live L2 'settings_default' read stays a harness precondition (installed settings equal shipped), not a bar. No bar text is edited.
