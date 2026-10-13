# closer: triage of built/validated items (FlowWorks, GSS, Pyrelands), 2026-10-13

Evidence sittings: `Transient/bench_live_20261012g/` (7589d73ef6), `bench_live_20261013/` (365b428d7b), `bench_live_20261013b/` (dbe92f0c92), `bench_live_20261013c/` (dbdfef28f7). Long-duration properties are INFERRED, not closed on absence.
Skipped by order: POND_*, PYRE_REGROW_*.

| item | closed/left | evidence |
|---|---|---|
| RIVER_COLORS_FIRST_SCRIPT_1 | closed f5b3f4bc9d26 | `Transient/modcheck/RiverColors_20261007T191723Z.json` PASS 2/FAIL 0, all_green |
| FLOODED_CANYON_FIRST_SCRIPT_1 | closed 8ca92b2aa6 | `Transient/modcheck/FloodedCanyon_20261008T044538Z.json` 41 PASS/0 FAIL/12 UNMEASURED, each reasoned |
| FLOWWORKS_NORTHSTAR_BASELINE_RUN_1 | closed dbe92f0c92 | `bench_live_20261013b/v2_20261013b.json` 61/61 GREEN; run-2 pass supersedes run-1 FAILs |
| THICK_LIQUID_CREEP_1 | closed dbe92f0c92 | v2_20261013b.json X7_tar_front_lags_water PASS, X7n PASS (staircase, not 40-cell channel) |
| FLOWWORKS_CHECKOUT_SCOPE_1 | left | only 5 of 54 ext chains ran; step-4 full run + modcheck record in one sitting |
| FLOWWORKS_TANK_LOOP_ROW_WRONG_1 | left | `extension_proof.py --live --chains toggle_tank_loop` (~5 min) |
| LIQUID_BOTTLE_LOOP_1, LIQUID_THIRST_CHAIN_1, FLOWWORKS_CONTAINER_MATERIALS_1 | left | blocked on fill-job bug; chains toggle_bottle_loop/bottle_revert |
| LIQUID_HEAT_PUSH_1 | left | chain liquid_heat (~3 min) |
| FLOWWORKS_QUARRY_DIGGING_1, RIVER_TOGGLE_PROOFS_BUILD_ELEVEN_UNCLAIMED, SURFACE_RIVER_WEIRS_1 | left | placer/flood_refill UNMEASURED SITE (FW_RIVER_SITE_DIAGNOSE_NOBODY_SWEPT_AWAY); river toggles + SeasonalFlood spawn |
| PUMP_FED_CHANNEL_STALL_*, FLOOD_DEBIT_MEND_*, FLOOD_SWITCH_RACE_MEND_*, FLOOD_DRIVER_OWNERSHIP_CONTRACT_1, WEIR_WASH_ITEM_LOSS_MEND_* | left | one flood-release/reload probe batch (~25 min total) |
| LIQUID_LOOK_MATERIAL_OWNERSHIP_1, LIQUID_FIRE_QUEUE_ORIGIN_1, WATER_LEDGER_DOUBLE_CHARGE_1, HAZARD_TAR_TERRAIN_FROM_LIQUIDS_1 | left | named chain/probe, 3-5 min each |
| CHILL_AURORA_*, CHILL_SUIT_*, CHILL_DIVE_DENSITY_*, CHILL_AIR_PUMP_1 | left | no Chill row in these sittings; AIR_PUMP owes owner L4 only |
| GLOW_TANK_LIQUID_FEED_1, GLOW_TANK_SEED_LIVE_SOW_1 | left | live feed/sow probes (~5 min each) |
| GSS_SWITCHES_PROVE_TWENTY_UNFLIPPED | left | no fallenWire*/keepWiresOnGravship flip rows in proof_all 106/106 |
| LAVA_LIQUID_BUILD_PROMISED_BY_CARD, MISSION_TANK_GOAL_REWIRE_TO_DEST | left | startup-log grep / mission chain |
| FLOWWORKS_LADDER_RAISE_LOWER_1, FLOWWORKS_VISUAL_PRINCIPLES_1, FLOWWORKS_BUILD_PROGRAM_1, HOSE_RULINGS_*, LIQUID_LEDGER_BUILD_NO_UNIT_LOST | left | owner L4 criteria remain; NS_ rows not run live |
| FLOWWORKS_NORTHSTAR_TRIAL_1, FLOWWORKS_NORTHSTAR_GREEN_FULL_1, PYRELANDS_GREEN_MINIMAL_1, PYRELANDS_GREEN_FULL_1 | left | need full-list or full Pyrelands run, not short |
| PYRE_SITE_TEMP_REPAIR_PROBE_HIT_ROCK, PYRE_SITE_FOOD_REPAIR_COLONY_STARVES | left | 13c half-colony PASS only; need gate-B line in JSON and a 6-alive full run |
| RIVER_STEAM_ANIMATION_1, WORLDMAP_LIQUID_TAGS_1, LIQUID_INDUSTRY_SETPIECES_1, BACTA_TANK_CORE_1, SCALD_WATER_AGITATION_FLECKS_1, FEVERWOOD_WATER_TOPOLOGY_SERVICE_1, BELT_WATER_HARNESS_1, MOVINGDUNES_WATER_BANKS_SAND_1 | left | not in these sittings; short tier probes noted on each item |

Each "left" item carries one `rimflow note` naming its short live check. Counts: 4 closed, 46 left (50 noted/closed incl. non-listed).
