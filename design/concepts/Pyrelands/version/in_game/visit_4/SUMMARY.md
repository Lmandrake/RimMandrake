# Pyrelands 0.1.0: in-game acceptance, visit 4 (Archmagi, game a, 2026-11-21 from 22:04 PST)

Detached BENCH helper, item RIMMANDRAKE_DRIVE_PYRELANDS_IN_GAME_ACCEPTANCE_VISIT_FOUR. In progress.

## Progress
- 22:04 synced (161d0f385), precondition `in_game 0.1.0`, item claimed, bridge archmagi (game a) taken by BENCH. Skeleton written.
- 22:10 rerun_relation: 31 checks touched (venom defs 11fca75b4b, validation.py harness repairs of visit 3), 7 untouched keep visit 3's PASS.
- 22:16-22:24 game a stopped (soft stop ignored; forced, my hold), composed biomes deployed --prune (9 orphan ash textures removed from game a's copy), UtinniPatches (2 files), BridgeTools --gm --instance a; FlowWorks, LuminousPigment, MandrakePatches, WeatherSuite, SWBestiary already in sync. Tier pyrelands applied (17 mods, 5 DLC; his 315-mod list backed up by modset_builder to deployed/config/ModsConfig.before-tier-pyrelands.xml). Game a launched directly (Steam answered WaitingPrevProcess beside game b), bridge after 110 s.
- 22:27 gate A refused: 3.8.12 loadavg 17.3 (WSL pipeline ticks, transient) and 3.8.snapshot (no dir given). 22:34 rerun with --snapshot Transient/pv4_snapshot: GATE A CLEAN (12 rows), def fingerprint 417df172fdb5e402.
- 22:37 site NS_Pyrelands_site_1_417df172fdb5_visit4 built (tile 1504, map 1, 250x250); gate B CLEAN (5 rows). Identity: mod_sha ca2accf045, game 1.6.4871 rev590, tier pyrelands (17).
- 22:40 batch 1 started (`scripts/runner.sh`, site reloaded before every chain): startup, mapgen_log, animal_census, grass_cover, ambient_ash_drift, plant_census, plant_census+scorchfruit_fire_born, ruins, firehawk, furnace_warmth, burrowers, heat_dome, fire_tick_effects, rite_hook_alone, firehawk_first_sighting_letter, foreign_arrivals, furnace_room, no_ordinary_rain.
SteveDesktop is not used: visit 2 measured its queue running none of the Pyrelands chains (no Pyrelands site there).

## Exit

```
ingame_rows: {}
strange_open: 0
savegame: none yet
exit_met: false
```
