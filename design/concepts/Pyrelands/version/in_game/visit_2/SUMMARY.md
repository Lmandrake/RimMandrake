# Pyrelands 0.1.0: in-game acceptance, visit 2 (Archmagi, game a, 2026-11-20 from 19:22 PST)

Detached BENCH helper, item RIMMANDRAKE_DRIVE_PYRELANDS_IN_GAME_VISIT_TWO_RUN_TWO. In progress.

## Progress
- 19:22 synced (bf7f9e1fe), precondition `in_game 0.1.0`, item claimed, bridge taken (BENCH), game a up (pid 5032). Skeleton written.
- 19:33 game a stopped; biomes composed deploy --apply (1 file, VERIFIED in sync); stale BENCH swap marker (gimmesomeslack, 2026-11-16) cleared by --restore-own (nothing written); tier pyrelands applied (18 mods, 5 DLC); game a launched (bridge 113 s).
- 19:35 site NS_Pyrelands_site_1_bf7f9e1fe4_visit2 built (tile 3, map 1); gate B CLEAN (5 rows). Identity: mod_sha 01853a05a6, game 1.6.4871 rev590, tier pyrelands (18).
- 19:40 batch a (7 chains): mapgen_log, animal_census, grass_cover, startup PASS; plant_census, ruins carry UNMEASURED sub-rows; ground_deep_ash's ash_fall_vs_clear_by_hour read 3 colonists "died" and the next chain found loadedMaps [] (HARNESS: raw rimworld/load_game race, the old map read mid-load). Repair: validation.py _load_site_save (menu, load, await map_ready, settle without ticks), 10 call sites; offline selftests green.
