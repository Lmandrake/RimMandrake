# Pyrelands 0.1.0: in-game acceptance, visit 3 (Archmagi, game b, started 2026-11-21 08:33 PST)

Detached BENCH helper, item RIMMANDRAKE_DRIVE_PYRELANDS_IN_GAME_ACCEPTANCE_VISIT_THREE. In progress.

## Progress
- 08:33 synced (2c09917fc), precondition `in_game 0.1.0`, bridge archmagi.b taken (BENCH). Game b running (pid 7416). Skeleton written.
- 08:37 game b stopped; composed biomes deployed --prune (9 files; 9 orphan ash textures in game b's copy removed), UtinniPatches (2 files), BridgeTools --gm; the other tier mods in sync. Stale BENCH.b swap marker (flowworks, 2026-11-20) moved to D:\ClaudeWork\backups\pv3_swapmarker; tier pyrelands applied (17 mods, 5 DLC). Game b launched (bridge 126 s).
- 08:53 gate A refused: game a's dead FlowWorks call (unknown outcome, endpoint 5174) refused every game-b mutation. Pipeline defect RIMMANDRAKE_SCOPE_BRIDGE_MARKER_TO_ITS_GAME_A_STOPS_B filed, fixed, closed (19e7615934; selftest_bridge_reconcile_read 83/83, red on parent 81/83).
- 09:05 gate A HARNESS repairs (6ea9314ad1): 3.8.4 stamp ABSENT under python.exe (Windows git refuses the WSL clone) now read under WSL; 3.3 an empty-string default the bridge omits. Before: `evidence/gateA_before_repair.log` (3.8.4 FAIL, 3.3 UNMEASURED); after: GATE A CLEAN (12 rows), def fingerprint 417df172fdb5e402.
- 09:10 site NS_Pyrelands_site_1_417df172fdb5_visit3 built (tile 63294, map 1); gate B CLEAN (5 rows). Identity: mod_sha 6ea9314ad1, game 1.6.4871 rev590, tier pyrelands (17).
- 09:14 runner (`scripts/runner.sh`, site reloaded before every chain) batch 1 started: startup, mapgen_log, animal_census, grass_cover, ambient_ash_drift, plant_census, ruins.

- 09:16-09:20 the concurrency guard refused game-b site loads on game a's live FlowWorks client (second layer of the same cause; fixed in 1d27205b91, guard selftest red on parent), then on the runner's own earlier steps (fixed by a lineage token in runner.sh). Rows run before 09:20 are void (no reload); none is used.
- 09:20-09:24 batch 1: startup, mapgen_log, animal_census, grass_cover, ambient_ash_drift, plant_census (3/3) PASS; ruins: ruins_scorched PASS, ruin_walls_charred_paint UNMEASURED ("no unowned walls" while the census lists 453 unowned ruin buildings): HARNESS, export_things stops at 2000 rows inside the grass carpet; repaired (unowned Wall cells from the complete census, then a paint census of those cells), to be shown both ways.
- 09:24 batch 2 started. So far PASS: firehawk (ran without its reload: rerun owed), furnace_warmth, burrowers, heat_dome, fire_tick_effects, sand_shovel, rite_hook_alone, firehawk_first_sighting_letter, firehawk_crestfeather_yield, foreign_arrivals. firefoam_sprayer: sprayer row PASS, control FAIL (the colonist without the sprayer took 3 fruit unburned); diagnosis owed while the game is up.
- 09:31-09:44 batch 2 (cont.): PASS furnace_room, cinderfall (4/4), blackrain (3/3), ashfall_weather_accumulation, ashfall_drifts, scorchfruit_produces, ullai_and_giant (4/4). no_ordinary_rain: forced_rain_becomes_black_rain FAIL on a black-rain reading: HARNESS, the row compared jawa/weather_get's weather dict with the def name (and its hour-later half could not see Rain); repaired (weather_name). scorchfruit_fire_born: UNMEASURED without plant_census in the same run (rerun paired). firehawk chain captured the hawk's rect after a sortie read flying=True: the capture is removed (owner's flyer rule; no bar reads it).
- 09:44-09:50 batch 3, both ways: ruins repaired PASS / planted (327 of 327 unowned walls unpainted) FAIL; no_ordinary_rain repaired 3/3 PASS / planted (pyrelandsEnabled off for the row) FAIL "weather is Rain"; firehawk rerun on a reloaded site 3/3 PASS. firefoam sampled: both runs stopped at tick 240 by the advance monitor on the sprayer colonist's hand burn (UNMEASURED); repaired: the harvest window advances with the bite rows' stop list (a burn is what the row measures).
- 09:51 batch 4 queued (firefoam again, venom, watered ash, scorchfruit with its census, the three scripts, the walk save, then the four long chains). Game b Saves backed up to D:\ClaudeWork\backups\rimworld_saves_b_pre_pyre_visit3_20261121 (58 files, 651 MB).

## Exit

```
ingame_rows: {}
strange_open: 0
savegame: UNMEASURED
exit_met: false
```
