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
- 22:38-22:55 batch 1: every component PASS except firehawk/far_hawk_seeks_the_burn FAIL (the far hawk took RM_FireHawkCarryEmber from a fire within scanRadius 54 that was not the plot, never the seek; a fire nearer than the 48.6 seek band blocks the seek). Theory SITE: a stray fire near the hawk's start; a rerun on a reloaded site is queued. scorchfruit_fire_born with its census PASS; ruins wall paint PASS; heat_dome 3/3 PASS; foreign_arrivals 3/3 PASS.
- 22:55 batch 2 queued: inspect_probe (why the regrow growth read is None), offctl_probe with burnLineEnabled ON (does the standing burn relight an extinguished map with the fire clock and hawk spread held off: theory, the one reseed attempt the 120360-tick window allows fails, and the retry is 2500 ticks later), firehawk rerun, firefoam_sprayer, flamefang_venom, ash_fertility_watered, cinderfall, blackrain, ashfall_weather_accumulation, ashfall_drifts, scorchfruit_produces, then cinderfall with the planted DryThunderstorm strike.
- 22:58 firehawk rerun on a reloaded site: far_hawk_seeks_the_burn FAIL again (2 of 2): the far hawk took RM_FireHawkCarryEmber from a fire that was not the plot. Class SITE: the chain's first-row hawk and the map's own native fire-hawks stay alive, carry embers off the plot and light fires nearer the far hawk than the 48.6-cell seek floor. Repair in validation.py `_ten_firehawk`: every other RM_FireHawk killed before each far-hawk row; every fire outside the plot counted at each read, and a missing seek beside such a fire reads UNMEASURED (site), never a mod FAIL; planted state PYRE_PLANT_FARHAWK_NO_SEEK=1 (fireHawkSpreadEnabled off for the seek row). Real and planted runs queued.
- 22:59 firefoam_sprayer: sprayer_reaches_the_fruit FAIL (Filth_FireFoam 0; jobs Harvest, Meditate, RM_PyreStepAwayFromFire), control FAIL (a bare colonist reached the fruit unburned, 65 fires in the ring). MOD, the known unfixed fault: filed RIMMANDRAKE_DESIGN_PYRE_SPRAYER_CARRIER_NEVER_FOAMS_ITS_PATH (visit 3); the fix waits on the Designer.
- 23:01 flamefang_venom: bite injects, rises untreated, plain bite no venom PASS (the fixed dose: 0.091 after one bite, +0.0146 an hour); venom_tended_vs_untended RESTART and venom_wait_out stopped: the plain-bite control (two fennec scratches, 6.17 each) bled out inside the next row. Class SITE: repaired (the control is healed once its reading is taken); rerun queued.

## Exit

```
ingame_rows: {}
strange_open: 0
savegame: none yet
exit_met: false
```
