# Pyrelands 0.1.0: in-game acceptance, visit 2 (Archmagi, game a, 2026-11-20 from 19:22 PST)

Detached BENCH helper, item RIMMANDRAKE_DRIVE_PYRELANDS_IN_GAME_VISIT_TWO_RUN_TWO. In progress.

## Progress
- 19:22 synced (bf7f9e1fe), precondition `in_game 0.1.0`, item claimed, bridge taken (BENCH), game a up (pid 5032). Skeleton written.
- 19:33 game a stopped; biomes composed deploy --apply (1 file, VERIFIED in sync); stale BENCH swap marker (gimmesomeslack, 2026-11-16) cleared by --restore-own (nothing written); tier pyrelands applied (18 mods, 5 DLC); game a launched (bridge 113 s).
- 19:35 site NS_Pyrelands_site_1_bf7f9e1fe4_visit2 built (tile 3, map 1); gate B CLEAN (5 rows). Identity: mod_sha 01853a05a6, game 1.6.4871 rev590, tier pyrelands (18).
- 19:40 batch a (7 chains): mapgen_log, animal_census, grass_cover, startup PASS; plant_census, ruins carry UNMEASURED sub-rows; ground_deep_ash's ash_fall_vs_clear_by_hour read 3 colonists "died" and the next chain found loadedMaps [] (HARNESS: raw rimworld/load_game race, the old map read mid-load). Repair: validation.py _load_site_save (menu, load, await map_ready, settle without ticks), 10 call sites; offline selftests green.
- 19:49 ground_deep_ash rerun with the repaired loader: no deaths, map stays current. ash_fall_vs_clear_by_hour FAIL (skyGlow 1.0 vs 1.0 at 13.6h): HARNESS, the mod dims through skyColorsDay (LightOverlay) and the row reads CurSkyGlow; no bridge read of the sky colour, filed RIMMANDRAKE_MEASURE_PYRE_ASHFALL_DIMMING_BY_SKY_NOT_GLOW. shore_ring FAIL: HARNESS (Mud counted as water); repaired (is_standing_water, red/green selftest) and now UNMEASURED SITE: the site has 0 water cells (GenStep census "water 0, mud 372, rich soil 769"), filed RIMMANDRAKE_TRACE_PYRE_SITE_WITH_NO_STANDING_WATER_LEFT.
- 19:58 testq J20261121T040348Z-49ee40 queued on SteveDesktop (burn_line, embergrass_regrow, fresh_burn_bonus, scorchfruit_spoils, scorchfruit_produces, ashfall_weather_accumulation, ashfall_drifts, opening_front) at e02accbb59.
- 20:10 pipeline defect filed: RIMMANDRAKE_REPAIR_PYRE_TABLE_LIVE_COMMANDS_THAT_NEVER_START (46 of 46 table live commands die under red_seen's shell; red-seen on a live decider is void). Local runner: one chain per reloaded site (scripts/runner.sh); WSLENV now carries RM_GAME_INSTANCE and the concurrency override to python.exe.
