# Pyrelands 0.1.0: in-game acceptance, visit 4 (Archmagi, game a, 2026-11-21 22:04 to 2026-11-22 01:35 PST)

Detached BENCH helper, item RIMMANDRAKE_DRIVE_PYRELANDS_IN_GAME_ACCEPTANCE_VISIT_FOUR. Game a on Archmagi (Steam's install),
game 1.6.4871 rev590, tier `pyrelands` (17 mods, all five DLC; his 315-mod list backed up by modset_builder and not
restored, by his rule). Deployed: composed biomes (`--prune`: 9 orphan ash textures removed), UtinniPatches (2 files),
BridgeTools `--gm`; the other tier mods were in sync. Walk build: mod_sha ca2accf045, mod_hash sha256:ff9c3350...
(`evidence/identity_pyrelands.json`); no mod file changed after the deploy (every change in this visit is test, harness or
pipeline code, none deployed). Site NS_Pyrelands_site_1_417df172fdb5_visit4 (tile 1504, 250x250) built by
northstar_site.py; gate A CLEAN (12 rows), gate B CLEAN (5 rows); the site was reloaded before every chain
(`scripts/runner.sh`). One chain per run, its JSON and log in `evidence/` (`pv4_<run>.json`, `run_<run>.log`); rows built
by `scripts/make_rows.py` (`scripts/overrides.json` holds classes and repairs). SteveDesktop was not used: visit 2 measured
its queue running none of the Pyrelands chains (no Pyrelands site there). Only the 31 checks the change since visit 3
touches ran (`rerun_relation.py`); the other 7 keep visit 3's PASS (carried by the reader). The visit ran about 30 minutes
past its 3-hour bound to show its repaired checks both ways; the deep-ash regrow rerun and sc_walk were not run.

## Result

27 PASS, 2 FAIL, 2 UNMEASURED of 31 checks [measured, `rows.jsonl`, each check's last row]. Exit NOT met: two MOD faults
not fixed in the sitting (`sc_firefoam_sprayer`, `sc_grass_regreens`, each filed with its acceptance test), one needed
check not counted (`sc_flamefang_venom`, owned by a filed item), and `sc_walk` not run (his full list on game a; owed to
this item's relaunch).

## What failed, and what was done (class first)

- **MOD, not fixed in the sitting, filed:** `sc_firefoam_sprayer`. Same fault as visit 3: the sprayer carrier laid 0
  Filth_FireFoam (jobs Harvest, Meditate, RM_PyreStepAwayFromFire), and the control's ring let a bare colonist reach the
  fruit unburned. Unfixed: when a carrier foams is undesigned (Designer first). Owner
  `RIMMANDRAKE_DESIGN_PYRE_SPRAYER_CARRIER_NEVER_FOAMS_ITS_PATH` (visit 3).
- **MOD (presumed, unproven), not fixed in the sitting, filed:** `sc_grass_regreens`. With its reader repaired, the
  first numbers ever read: ember grass grew +0.054 a day where its own def's rate wants >= 0.369 (vanilla Plant_Grass
  beside it +0.118; growDays 0.8 vs 2.5; its description says it regrows in a day or two); dry and watered identical;
  embergrass_regrows FAIL (green 0.23 on day 3, 0.42 on day 7; visit 3 read 0.38 and 0.73). Filed
  `RIMMANDRAKE_TRACE_PYRE_EMBERGRASS_GROWS_TENTH_OF_ITS_RATE`. Three harness or scene faults on the same check, repaired
  and not yet run (the visit's bound): the reader (897516fc92, '70% grown'; selftest_pyrelands_growth_lines.py red on
  the old reader, green on the fix), the census-first log (aa441a608f: it counted the driver's offline declaration pass
  of every skipped chain, 338 calls), the scene's ground (4fff1aa5e7: it laid soil, where the ash field never acts; the
  scene asks for deep ash). plant_density_one_control_map stays UNMEASURED by construction
  (`RIMMANDRAKE_BUILD_PYRE_GRASS_FOIL_SAME_SEED_DENSITY_ONE`).
- **SITE, repaired, shown both ways, now PASS:** `sc_firehawk`. 2 of 2 runs FAIL far_hawk_seeks_the_burn: the chain's
  first-row hawk and the map's own fire-hawks lit fires inside the seek floor. Repair 897516fc92 (other hawks killed
  first, 3 in the real run; a missing seek beside a stray fire reads UNMEASURED). Planted PYRE_PLANT_FARHAWK_NO_SEEK=1:
  FAIL; real: PASS.
- **HARNESS, repaired, shown both ways, now PASS:** `sc_burn_line_walks`. The off-control's window fitted one reseed
  attempt (probe: with the burn line on, 1-2 relit fires at every sample from the window's end to 15000 ticks past);
  it now waits four retries (a0e6da8ce3). Planted (toggle left on): FAIL, 21 fires; real: PASS, 0 fires; the burn_line
  chain 4/4 PASS. Closed `RIMMANDRAKE_FIND_PYRE_BURNLINE_OFF_CONTROL_THAT_CAN_FAIL`.
- **SITE/HARNESS, repaired, not counted:** `sc_flamefang_venom`. Run 1: the plain-bite control bled out inside the next
  row (SITE: healed). Run 2: venom_tended_vs_untended FAIL in hour 1 only (HARNESS: the series started at the tend
  order; the tend lands inside hour 1); the wait-out's subject cleared the venom by day 3 with no death (the dose fix
  holds), but a still-drafted bystander was downed. Repairs a0e6da8ce3: the series starts once the doctor's TendPatient
  job ends; fixtures undrafted and not the wait-out's subjects; planted state PYRE_PLANT_VENOM_TEND_WRONG_PATIENT=1.
  Run 3 (real): bite rows and tended-vs-untended PASS; the wait-out stopped on a starving bystander. The planted run was
  voided by a death. Not shown both ways: owner `RIMMANDRAKE_FEED_PYRE_VENOM_FIXTURES_HUNGER_STOPS_WAITOUT` (filed).
- `sc_walk`: UNMEASURED, not run (his full list on game a: a 315-mod cold load, a full-list site, two game weeks with
  three reloads, about two hours [guess ~60%]). Owed to this item's relaunch.
- No mod file changed in this visit, so no mod fix needs a fresh reader (`fix_reviews.jsonl` is not owed). The
  validation.py repairs are live test code, run by the table's live commands; no offline decider's file was edited
  except selftest_pyrelands_venom_staging.py (its fake answers the doctor's job read; 0 of 21) and
  selftest_pyrelands_round6_parts.py (it pins the off-control's new wait; 0 of 95). No `red-seen` was recorded: visit 2
  measured that red_seen's shell cannot start the table's live commands, so a recorded red would be a crash.

## Owed cases, one by one

- Problem `RIMMANDRAKE_SCOPE_SETTINGS_SCREENS_DECIDER_TO_ITS_OWN_MOD` (inv_settings_gate): the table command
  `selftest_settings_screens.py --mod Pyrelands` 14/14 ok (`evidence/selftest_settings_screens_pyrelands.log`); P_gate keeps
  visit 3's live PASS (untouched); sc_walk not run. Partly shown.
- Problem `RIMMANDRAKE_PIN_PYRE_DESCRIPTIONS_FURNACE_CARD_COULD_READ_BLANK` (inv_art_and_text): sc_three_skies PASS; the live
  defs read 9 of 9 descriptions present, none blank, the furnace-beast's included (`evidence/script_desc_probe.log`).
- Lane 1 game_side_bars: each settles by its scene's last row (Exit block); sc_ullai, sc_sand_shovel and the other 5
  untouched checks keep visit 3's PASS.
- Road back, UNRUN until this visit:
  - `RIMMANDRAKE_MEASURE_PYRE_BURNED_SHARE_FLOOD_ALSO_MOVES`: burn_line_burned_share PASS.
  - `RIMMANDRAKE_REVERSE_PYRE_WIND_BEARING_ONE_DIRECTION_STAGED`, `RIMMANDRAKE_CORRECT_PYRE_STALE_TEXT_THREE_ADVISORY_LEFTOVERS`,
    `RIMMANDRAKE_REPAIR_PYRE_TABLE_LIVE_COMMANDS_THAT_NEVER_START` (sc_fire_walks_with_wind, sc_furnace_giant, sc_ullai): untouched
    since visit 3's PASS rows, not rerun.
  - `RIMMANDRAKE_FIX_PYRE_HAWK_LETTER_BLANKS_FOUR_NAMED_SLOTS`: firehawk_first_sighting_letter 3/3 PASS.
  - `RIMMANDRAKE_BUILD_PYRE_CONTROLS_NO_BRIDGE_TOOL_CAN_RUN`: sc_no_rain 3/3, sc_ash_watered 3/3, sc_populations 3/3, sc_ruins
    2/2 PASS; sc_flamefang_venom see above; sc_walk not run.
  - `RIMMANDRAKE_FIX_PYRE_ASHWALLOW_SHADE_DASH_BEATS_FIRE_DIVE`: sc_ashwallow PASS, sc_heat_dome 3/3 PASS.
  - `RIMMANDRAKE_FRAME_PYRE_CHAIN_SHOTS_ON_THEIR_SUBJECT`: the captures looked at are on their subjects (the animal census
    shot frames six ashwallows that read as rocks at that zoom: strange.jsonl).
  - `RIMMANDRAKE_RENEW_SAFE_ADVANCE_AUTO_ARM_HOURLY`: the long waits of embergrass_regrow and burn_line ran with no lapse.
  - `RIMMANDRAKE_REORDER_PYRE_BURN_WALK_BEFORE_ITS_FRONT_DIES`: burn_line_walks_hourly PASS.
  - `RIMMANDRAKE_SHIELD_PYRE_WALK_FROM_FULL_LIST_EVENTS`: sc_walk not run.
  - `RIMMANDRAKE_STAGE_PYRE_FLAMEFANG_BITES_LAND_ONCE_NOT_MAUL`: one landed bite per patient in each run.
  - `RIMMANDRAKE_TRACE_PYRE_ASHFALL_FIRE_IN_FIRST_LIGHTNING_WINDOW`: real cinderfall_lightning PASS (19 strikes under
    cinderfall, 0 under ash fall; the ash-fall window-1 fire named 'not lightning'); planted DryThunderstorm FAIL (6 strikes).
  - `RIMMANDRAKE_TRACE_PYRE_FIREHAWK_TURNS_MANHUNTER_IN_BURN_WALK`: burn_line on the 17-mod tier reached its share verdict
    (PASS) with no Manhunter stop.
  - `RIMMANDRAKE_IGNORE_OFFMAP_COLONIST_DEATH_HEART_ATTACK_TWICE`: fresh_burn_bonus and scorchfruit_spoils ran to their
    verdicts (PASS); no world-pawn death happened, so the latch was not exercised.
  - `RIMMANDRAKE_TUNE_PYRE_FLAMEFANG_BITE_KILLS_BEFORE_IMMUNITY`: one untended bite peaked at 0.577 and was gone by day 3,
    no death (one run); the wait-out row itself is not counted (above).

## Pipeline defects fixed in this run

- `RIMMANDRAKE_IMPORT_WRAPUP_RESTORE_DIES_ON_WINDOWS_FCNTL`, closed at 61e38119d3: every bridge release ran
  `python.exe wrapup.py restore`, which imported role_clones' top-level `import fcntl` and died (owed settings never
  restored). selftest_role_clones_no_fcntl.py red on the parent, green on the fix; the live restore now ends with its
  tally. (selftest_role_clones.py's one failing check fails identically on the parent: not this change.)

## Beyond the checks

9 strange things: 9 explained, 0 filed, 0 open (`strange.jsonl`). Looked at: the heat-dome pair, scorch-fruit in its
scar (two fires beside it burn a bone-wall ruin in the firebreak ring: fires_probe), the furnace-beast room beside its
empty control room, the charred ruin, the ash dusting, the census frame, and the five walk stations. Copies under 1 MB
are in `screenshots/`; originals in game a's Screenshots folder and `Transient/pv4/`.

## Savegame

`C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Saves\PYRELANDS_0.1.0_VISIT4_WALK.rws`
(26.8 MB, game a, the 17-mod `pyrelands` tier), staged by `scripts/walk_save.py` on the reloaded visit-4 site, five
labelled stations (a live burn front; ullai herd, furnace-beast giant, ashwallows; scorch-fruit; roofed vs open ember
grass; the charred ruin, 41 charred walls in its cluster), each capture looked at; the ullai were turned side-on and the
save written again (`scripts/walk_station1_fix.py`). Stat-diffs: that file alone new, then that file alone changed. Game
a's Saves folder was backed up first: `D:\ClaudeWork\backups\rimworld_saves_a_pre_pyre_visit4_20261121` (7.3 GB).

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
- 23:11-23:31 ash_fertility_watered 3/3, cinderfall 4/4 (owed lightning case: real cinderfall_lightning PASS, 19 strikes under cinderfall and 0 under ash fall, the ash-fall window-1 fire named 'not lightning'; planted PYRE_PLANT_ASHFALL_STRIKE=DryThunderstorm FAIL, 6 strikes under ash fall), blackrain 3/3, ashfall_weather_accumulation, ashfall_drifts, scorchfruit_produces PASS.
- 23:32 inspect probe: the live inspect line is '70% grown' (English key PercentGrowth '{0} grown') or 'Mature.', never 'Growth: N%': the regrow reader's regex could not match, the whole cause of visit 3's None-on-every-day (HARNESS). Repaired (`plant_growth_of_lines`; new selftest_pyrelands_growth_lines.py 0 of 6 failed on the fix, 3 of 6 failed with --old, the parent's reader); planted state PYRE_PLANT_REGROW_WET_ROOTS_OFF=1 (the ash field's water off from the sowing on). The table command of sc_grass_regreens now runs grass_cover with embergrass_regrow (its grass_census_first reads grass_cover's census from the same run). plant_density_one_control_map stays (the bar's oracle names the plantDensity 1.0 control; owned by RIMMANDRAKE_BUILD_PYRE_GRASS_FOIL_SAME_SEED_DENSITY_ONE), so sc_grass_regreens stays not counted this visit.
- 23:36 firehawk repaired (897516fc92): far_hawk_seeks_the_burn PASS (3 other hawks killed first; the seek taken, the hawk closed); planted PYRE_PLANT_FARHAWK_NO_SEEK=1: FAIL ('never took RM_FireHawkSeekBurn'). Shown both ways.
- 23:40 offctl probe (burnLineEnabled on, fire clock and hawk spread held off, map extinguished): 1-2 burn-line fires at every sample from 120360 to 135360 ticks after: the relight happens on this site. Visit 3's planted 0 fires fits one reseed attempt in the window missing (40 random tries, retry 2500 ticks later). Repair: the off-control waits four more retries (OFF_CONTROL_WAIT_TICKS); real and planted runs queued after the long chains.
- 23:45 fires probe: the two fires beside the scorch-fruit pad burn a map-generated bone-wall ruin standing in the firebreak ring (explained, strange.jsonl).
- 23:44 venom rerun with the control healed: bite rows 3/3 PASS; venom_tended_vs_untended FAIL in hour 1 only (tended rise 0.0152 = 13 untended 200-tick updates: the doctor's ordered tend lands inside hour 1, and the hourly series started at the order); venom_wait_out RESTART: the plain-bite control, still drafted by _bite_until, was downed inside the wait-out's days (the subject's own course: 0.228, 0.577, 0.213, gone by day 3, no death). Class HARNESS (the hour-1 start) and SITE (a drafted bystander). Repairs: the hourly series starts once the doctor's TendPatient job has run and ended; the control is undrafted and healed; the chain's earlier fixtures are not the wait-out's subjects. Planted state PYRE_PLANT_VENOM_TEND_WRONG_PATIENT=1 (the doctor tends the untended patient). selftest_pyrelands_venom_staging's fake answers the doctor's job read (0 of 21 checks failed). Real and planted runs queued.
- 23:45 long chains started: fresh_burn_bonus, scorchfruit_spoils, grass_cover+embergrass_regrow (repaired reader), burn_line (repaired off-control window); then embergrass planted, off-control real and planted, venom real and planted.
- 00:01 fresh_burn_bonus 2/2 PASS (no world-pawn death in the run, so the off-map latch was not exercised; no stop). 00:12 scorchfruit_spoils PASS.
- 00:37 grass_cover+embergrass_regrow on the repaired reader: every patch and day now reads a number. regrow_dry_watered_vanilla FAIL: dry and watered ember grass identical, 0.05 -> 0.32 over 5 days (+0.054/day), vanilla Plant_Grass on the same ground +0.118/day; with growDays 0.8 vs 2.5 the row wants >= 0.369/day for ember grass. embergrass_regrows FAIL (green share 0.23 on day 3, 0.42 on day 7; visit 3 read 0.38 and 0.73 and passed). grass_census_first FAIL (338 'mutations' before the census: the driver's offline declaration pass of every skipped chain was logged; HARNESS, repaired, aa441a608f: live calls only). plant_density_one_control_map UNMEASURED (no tool; owned by RIMMANDRAKE_BUILD_PYRE_GRASS_FOIL_SAME_SEED_DENSITY_ONE).
- 00:45 classes: the regrow scene lays RM_FE_Ground_Soil where its scene asks for dry and watered deep ash (cells read ashField False, so water could not act): SITE, repaired (deep ash laid; a patch not on the ash field reads UNMEASURED). The slow ember grass (about a tenth of its def's rate at the biome's heat on soil; its description says it regrows in a day or two) is classed MOD, presumed, unproven: the deep-ash rerun is queued to read it on its own ground before filing. The planted wet-off regrow run is cancelled (a planted FAIL cannot show the reader both ways while the real run fails).
- 00:50 a published edit (the off-control's longer wait) turned selftest_pyrelands_round6_parts red (1 of 95: the test pins the off-control's wait); fixed in aa441a608f (0 of 95). Every Pyrelands selftest that reads validation.py is green.
- 01:04-01:35 burn_line 4/4 PASS; off-control real PASS / planted FAIL; venom repaired (real tended-vs-untended PASS, wait-out stopped on a starving bystander; planted voided by a death); walk save written and looked at (station 1 re-shot side-on); descriptions probe 9/9; the deep-ash regrow rerun skipped at the bound. Bridge released 01:17 (its wrapup restore crashed on fcntl under python.exe: pipeline defect fixed, 61e38119d3). Items filed: RIMMANDRAKE_TRACE_PYRE_EMBERGRASS_GROWS_TENTH_OF_ITS_RATE, RIMMANDRAKE_FEED_PYRE_VENOM_FIXTURES_HUNGER_STOPS_WAITOUT; closed RIMMANDRAKE_FIND_PYRE_BURNLINE_OFF_CONTROL_THAT_CAN_FAIL, RIMMANDRAKE_IMPORT_WRAPUP_RESTORE_DIES_ON_WINDOWS_FCNTL. maturation.py next: exit not_met, substance only (sc_grass_regreens MOD FAIL first); no form reason.

## Exit

```
ingame_rows: {P_ambient_ash_drift: pass, P_animal_census: pass, P_ashfall_drifts: pass, P_ashfall_weather_accumulation: pass, P_blackrain: pass, P_furnace_room: pass, P_grass_cover: pass, P_mapgen_log: pass, P_scorchfruit_produces: pass, P_scorchfruit_spoils: pass, P_startup_and_def_wiring: pass, sc_ash_watered: pass, sc_ashwallow: pass, sc_burn_compounds: pass, sc_burn_line_walks: pass, sc_fire_dusts_ash: pass, sc_firefoam_sprayer: fail, sc_firehawk: pass, sc_firehawk_rewards: pass, sc_flamefang_venom: unmeasured, sc_foreign_arrivals: pass, sc_furnace: pass, sc_grass_regreens: fail, sc_heat_dome: pass, sc_no_rain: pass, sc_populations: pass, sc_rite_hook_alone: pass, sc_ruins: pass, sc_scorchfruit: pass, sc_three_skies: pass, sc_walk: unmeasured}
strange_open: 0
savegame: C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Saves\PYRELANDS_0.1.0_VISIT4_WALK.rws
exit_met: false
```
