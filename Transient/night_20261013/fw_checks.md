# FlowWorks short live checks — BENCH night helper, 2026-10-13

Owner AFK; order: short, directly measurable checks only (no full suites; longest single wait 3,000 governed ticks via
`jawa/safe_advance`). One game session, Steam launch, pid 23876, killed by PID at the end.
Build under test: FlowWorks at **d01603a685** (DLL from 4dcd4f7869; deployed 6 files, VERIFIED in sync), code run from a
`git archive` of d01603a685 at `D:\Luke\dev\_rmscratch\night_fw_20261013`. Tier: ratchet_pilot (22) + mandrake.rm.patches
= 23 mods (`Transient/bench_live_20261013c/ModsConfig.ratchet_pilot_plus_patches.xml`, md5 0bab16fa). Owner ModsConfig
md5 ee01dae9e30d121c78d88e474dacd8e8 before; `modset_builder --restore` put it back, verified ee01dae9. Game down, bridge released.
Evidence: `Transient/night_20261013/fw_live/` (probe scripts + result JSON + Player logs).

| item | check | result | closed / left |
|---|---|---|---|
| POND_VOLUME_UNIFY_DEEP_NOTCH_YARDSTICK | A1 no FluidDef/tank config error; A2 fresh tanks + classified ponds (`pond_probe.py`); A3 old save `NS_FlowWorks_TrialSite_v1` load + overfull tank (`overfull.py`) | A1 0 FlowWorks config errors (`Player.startup_pond.log`). A2 PASS: RM_LiquidTank cap 80, RM_UniversalCargoTank 160, deep pond N=9 cap 36, shallow N=6 cap 12 (`pond_probe_3.json`). A3 PASS: log "volume model 1 -> 2: 3 limited pond(s) rescaled", each 125/125->50/50, 20/20->8/8, 80/80->32/32 (fraction kept); overfull read COMPRESSED (no tank in any old save: capacity dropped by tankCapacityMultiplier 1->0.5): 80/40 units kept 250 ticks, inspect "overfull (old save): takes nothing in until drained below capacity" (`overfull.json`) | closed |
| POND_RETURN_LEG_BUILD_WATER_GOES_HOME | A1 short form: 6-cell limited pond -> pump -> tank -> pump Pour -> pond, L0 ledger (`ReportLedger` dev action) before/after (`pond_probe.py`); A3 dig a dry bed square + fill in + refill (`dugbed_probe.py`) | A1 short form PASS: ledger 240.000 -> 240.000 (draw: bodies 195 + tanks 45) -> 240.000, wet set == fresh snapshot, pond 12/12 receded 0 (`pond_probe_3.json`); the dug-B leg of A1 NOT run. A3 PASS: cap 12 -> dug 10 (5 cells) -> filled in 12 (6 cells), Mud, D=0; re-wet in 750 ticks at refillRateMultiplier 300 (COMPRESSED; slider max 5 re-wets in ~12k ticks, too long) (`dugbed_3.json`). A2 (occupants delay refill / item washes ashore) not run | left: A1 dug-B leg, A2 |
| FLOWWORKS_TANK_LOOP_ROW_WRONG_1 | `extension_proof --chains toggle_tank_loop` on the golden site | tank_loop_on FAIL "pour-in never ran: tank units [0...]" over 6000 ticks (tank Empty, Job: Store); differs from 2026-10-11 (rose, never fell). The spawned RM_Bottle_FreshWater logged "MakeThing error: ... madeFromStuff but stuff=null" (harness spawn without stuff, suspect). tank_loop_off UNMEASURED (upstream) (`ext_a.json`) | left |
| LIQUID_HEAT_PUSH_1 | `--chains liquid_heat` (rerun after the Megapede) + `heat_open.py` for A3 | chain 3/3 PASS (`ext_heat.json`). A3 PASS: open 3x3 RM_WaterBoilingShallow reads kind=1 outdoor=True; beside and 10 cells away read the same outdoor temp (22.7 -> 22.3 with the day), warmed=0 energy=0 over 1500 ticks (`heat_open.json`) | closed |
| FLOWWORKS_VISUAL_PRINCIPLES_1 | `--chains wall_faces` | cuts_draw_wall_faces PASS, wall_faces_off_hidden PASS (`ext_a.json`) | left: A2 other components, A3 Opus eval, A4 owner |
| RIVER_STEAM_ANIMATION_1 | `--chains toggle_river_steam` | UNMEASURED "owed, no predicate yet" (field write/read-back only) (`ext_b.json`) | left: needs a steam predicate + Pyrelands river map |
| LIQUID_INDUSTRY_SETPIECES_1 | `--chains machinery_found_works` | works_only_over_ruin PASS, build_anywhere_on PASS; ruins_mapgen / ruin_stock_mapgen / pipe_adapters UNMEASURED "no predicate yet" (`ext_b.json`) | left: A2-A4 forced set-piece spawns |
| LIQUID_FIRE_QUEUE_ORIGIN_1 | `--chains plot_E_fire,fire_explosion` | fire_reaches_reservoir PASS, explosion_lights_liquid PASS, explosion_off_does_not_light PASS (`ext_b.json`); none of these rows asserts A1 (sourceFireReach bound), A2 (torch beside a pending tar cell) or A3 (reload with a pending front) | left |
| FLOOD_DEBIT_MEND_DEEP_CELL_ONE_LEVEL | `flood_probe.py`: water release (volume 12) seeded on a dug 1x6 D4 channel | PASS: remainingVolume 12 -> 8 -> 4 -> 0 at floodedTileCount 0 -> 1 -> 2 -> 3: 4 x volumePerTile per D4 cell; channel holds 12 levels, 0 soil trace cells (`flood_probe_3.json`) | closed |
| FLOOD_DRIVER_OWNERSHIP_CONTRACT_1 | same release | PASS: 4 cells F=4 read past the release's expiry (1475, read 1585); their temp layer is the engine's RM_Fill_Water_Superdeep, never the flood's RM_Fill_Water_Trace. The 300,000-tick temp-terrain recede is INFERRED: the release wrote no trace cell anywhere, so it queued no removal to strip the fill | closed |
| FLOOD_SWITCH_RACE_MEND_ENGINE_OFF | legacyFloodViaEngineEnabled off, release seeded on a second dug D4 channel | PASS: all 6 cells terrain RM_Channel_Superdeep, temp none, D4 F0 before and after the release's expiry (`flood_probe_3.json`). The 300k recede leg is INFERRED (nothing was written, so nothing is queued) | closed |
| PUMP_FED_CHANNEL_STALL_PROVE_AFTER_RELOAD | `pumpfed_probe.py`: pump on Pour brims a 4-cell D2 outlet, save, load, dig on 4 cells out of the pump's reach | PASS: outlet [2,2,2,2] before save (1750 ticks); after reload + dig the far end took fill in 2500 ticks, ext [1,2,1,1]; tank 80 -> 20 (= 12 levels in channel + extension) (`pumpfed_1.json`). Throwaway save deleted | closed |
| WEIR_WASH_ITEM_LOSS_MEND_PLACE_FIRST | breach a weir holding a catch with every neighbour blocked | not run: needs a river map (river_site.py) and a staged blocked bank; `ProofBreach` places its own weir and catch, so the no-room case needs a new proof hook. Over the ~10 min bar | left |

## Harness defects met
- `northstar/pond_pump.py` terrain(): read `ci["terrain"]`, but `rimworld/get_cell_info` answers `{"cell": {"terrainDefName"}}`; every terrain read was None. Fixed (selftest_pond_pump 11/11).
- My own probes, fixed before the recorded runs: flood "no temp terrain" mistook the engine's own fill terrain for the flood's (now: no Trace terrain); a release that spends all its volume destroys itself, so "last seen remaining" must count as 0; dugbed_probe let a GovernorStop escape without recording why (below).
- Pour in pond_probe/pumpfed_probe needs a Dump tank; the probes switch tank jobs off (`hose set:tankModesEnabled=False`, a Mod Setting) and restore defaults after.

## Threats met (each → TESTENV_* item)
| threat | where | action | item |
|---|---|---|---|
| VEF "New faction" modal (Dialog_NewFactionSpawning) x5 on loading the golden save: Geonosian Foundry Hive, The Junkers, Jawa Trade Moot, Wildsteam Clan + one (RimUtinni Patches factions absent from the save); force-pause, first chain UNMEASURED | NS_FlowWorks_TrialSite_v1 load | clicked "Do nothing" x5 via click_ui_target; reran | TESTENV_FACTION_DIALOG_HARDEN_FIVE_KNOCKS |
| VFEI2_Megapede + 3 Spelopede (Insect) arrived during liquid_heat; safe_advance stopped at 60/600 | golden site, tick ~41k | jawa/kill_hostiles (4); liquid_heat rerun 3/3 | TESTENV_MEGAPEDE_HARDEN_GATECRASHER |
| safe_advance GovernorStop during the pump draw on a fresh quicktest; reason not captured (the probe did not catch GovernorStop) | dugbed run 2 | reran on the same map, clean | TESTENV_GOVERNOR_STOP_DIAGNOSE_NO_NOTE_LEFT |
Info only: "Technologist role activated" letter every 125 ticks during toggle_tank_loop (golden site).

## Teardown
Game killed by PID 23876; throwaway save NS_night_pumpfed_20261013.rws deleted; `modset_builder --restore` verified md5
ee01dae9e30d121c78d88e474dacd8e8; `./game --why "night FlowWorks checks done" down`; `rimflow bridge release`.
