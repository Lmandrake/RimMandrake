# Pyrelands 0.1.0: in-game acceptance, visit 3 (Archmagi, game b, 2026-11-21 08:33 to 12:10 PST)

Detached BENCH helper, item RIMMANDRAKE_DRIVE_PYRELANDS_IN_GAME_ACCEPTANCE_VISIT_THREE. Game b on Archmagi (its own install,
`D:\ClaudeWork\rimmandrake\instances\b\game`), game 1.6.4871 rev590, tier `pyrelands` (17 mods, all five DLC). Deployed the
composed biomes and UtinniPatches (`--instance b`, VERIFIED in sync) and the BridgeTools companion (`--gm`). Walk build:
mod_sha 6ea9314ad1, mod_hash sha256:fda33b70… (`evidence/identity_pyrelands.json`); no mod file changed after the deploy
(every change in this visit is test, harness or pipeline code, none deployed). Site NS_Pyrelands_site_1_417df172fdb5_visit3
(tile 63294, 250x250) built by northstar_site.py; gate A CLEAN (after two harness repairs), gate B CLEAN; the site was
reloaded before every chain (`scripts/runner.sh`), and the driver re-ran gate B each time. One chain per run, its JSON and
log in `evidence/` (`pv3_<run>.json`, `run_<run>.log`); rows built by `scripts/make_rows.py` (`overrides.json` holds the
classes and repairs). SteveDesktop was not used: visit 2 measured its queue running none of the Pyrelands chains (no
Pyrelands site there), so every chain ran here. The visit ran past its 3-hour bound (about 3 h 40 min) to re-run the checks
it repaired, as the rule for a wrong check requires.

## Result

33 PASS, 2 FAIL, 3 UNMEASURED of 38 checks [measured, `rows.jsonl`, each check's last row]. Exit NOT met: two MOD faults not fixed in the sitting (`sc_firefoam_sprayer`, `sc_flamefang_venom`, each filed with its acceptance test), two needed checks not counted (`sc_burn_line_walks`'s off-control cannot fail; `sc_grass_regreens`' growth read is blind; each owned by a filed item), and `sc_walk` waits for game a (his full list). Build match: 38 of 38 rows count against the walk build (`build_match.py check --mod Pyrelands`). Every check ran; 53 rows in all, earlier runs kept with their class.

## What failed, and what was done (class first)

- **MOD, not fixed in the sitting, filed:** `sc_firefoam_sprayer`. The colonist carrying the firefoam sprayer, ordered to
  harvest scorch-fruit inside a burning ring, laid **0 `Filth_FireFoam`** in 3 of 3 runs on this build (s3, s4, gap
  plant). Its jobs were Harvest, the mod's `RM_PyreStepAwayFromFire` and GoSwimming. The sprayer is a `Verb_Shoot` gun,
  and no mod code makes a carrier use it on the fire in its way. Visit 2's PASS and run 1's PASS were chance: a colonist
  crossing a 2-cell fire unburned, which is the leaf's own false pass. Unfixed because the fix is not known: when a
  carrier foams (on its own on a job's path, or player-ordered) is undesigned, so the Designer goes first.
  Filed `RIMMANDRAKE_DESIGN_PYRE_SPRAYER_CARRIER_NEVER_FOAMS_ITS_PATH`, with its acceptance test.
  Its control (SITE, unrepaired, same owner): a bare colonist crossed the 2-cell grass ring unburned and took 3 fruit (s3).
- **HARNESS, repaired, shown both ways, now PASS:**
  - `sc_ruins` (wall paint): a whole-map export stopped at 2000 rows in the grass carpet. It now reads the unowned Wall
    cells from the complete building census, then takes a paint census of them. Planted (327 of 327 walls unpainted)
    FAIL; real PASS. Commit f779129ade.
  - `sc_no_rain`: the row compared the weather dict with the def name. Planted (pyrelandsEnabled off for the row) FAIL
    "weather is Rain"; real 3/3 PASS. Commit f779129ade.
- **HARNESS or SITE, re-run (no criterion changed), now PASS:** `sc_firehawk` (first run had no site reload; the
  capture of the flying hawk is removed, by the owner's flyer rule); `sc_scorchfruit` (needs plant_census in the same
  run); `sc_burn_compounds` (a world-pawn colonist's heart attack stopped the advance; filed
  `RIMMANDRAKE_IGNORE_OFFMAP_COLONIST_DEATH_HEART_ATTACK_TWICE`).
- **HARNESS, not counted, owned by a filed item:**
  - `sc_burn_line_walks`: the off-control counted the fire clock's fronts, which run on their own switch. Repaired to
    hold the other fire sources, it then read PASS on its planted state too (toggle left on), so it cannot fail.
    `RIMMANDRAKE_FIND_PYRE_BURNLINE_OFF_CONTROL_THAT_CAN_FAIL`. Its rerun's components all read PASS (`evidence/run_burn_line_rerun.log`, the hourly walk now captured to the map edge), but the check is not counted.
  - `sc_grass_regreens`: daily growth read None for all patches on all days; cause not found.
    `RIMMANDRAKE_READ_PYRE_REGROW_GROWTH_NONE_ON_ALL_SIX_DAYS`.
- **SITE/HARNESS, venom wait-out:** MOD, not fixed in the sitting, filed `RIMMANDRAKE_TUNE_PYRE_FLAMEFANG_BITE_KILLS_BEFORE_IMMUNITY`. Four bite rows PASS; `venom_wait_out` FAIL: one untended bite read 0.434, then 0.784 a day later, and the colonist died by day 2, before immunity completes (def: +0.35/day untended, immunity at day 2, lethal 1.0). The offline model assumes 0.2 per bite. The row needed four repairs to reach that reading. It had read a dead subject as "venom gone", which would have PASSED a death. Earlier patients and a starving bystander voided it, and a venom death stopped its advance. Unfixed: which number moves (dose or immunity rate) is the Designer's tuning call, and a fix means a redeploy plus all 38 checks rerun.
- `P_scorchfruit_spoils`: a world-pawn heart attack voided its first run (filed `RIMMANDRAKE_IGNORE_OFFMAP_COLONIST_DEATH_HEART_ATTACK_TWICE`); the rerun PASS.
- `sc_walk`: UNMEASURED by the brief (needs his full list; game b runs a tier list beside game a).
- No mod file changed in this visit, so no mod fix needs a fresh reader (`fix_reviews.jsonl` is not owed). The
  validation.py repairs are test code. `T_SITE`'s reads changed; its file did not, and it was re-run green. No offline
  decider's file was edited, so no `red-seen` is owed.

## Owed cases, one by one

- Problem `RIMMANDRAKE_REPAIR_PYRE_GATE_DECIDER_FOUR_FAULTS_GREEN` (inv_settings_gate): `P_gate` PASS live
  (A1 ShellPresent=True On=True). The gate's off path ran live in two places: `sc_no_rain`'s gate-off control (with
  pyrelandsEnabled off, the forced roll gives Rain) and `firehawk`'s spread-off control, both PASS. The kernel gates under
  the master switch in a walk day (`sc_walk`) did not run on game b. Partly shown.
- Polish `RIMMANDRAKE_NOTE_PYRE_WIND_FAULTS_LIVE_ONLY_TO_SEE`: recorded. `sc_fire_walks_with_wind` PASS 9/9 with the wind
  set by SetWindForTest, so it cannot see FF_wind_not_from_scar.
- Planted faults. None was planted live: each needs a DLL rebuild and two game restarts, and the mod hash then moves.
  Each answer below is read from the check's code:
  - `B_line_lit_along_the_wind`: no [guess ~70%]. wind_burn_live lights its own line, so the front's bearing is never read.
  - `H_wind_ignores_its_switch`: yes [guess ~75%]. Row B (wind off) would lean like F.
  - `H_carry_never_marked`: sc_fire_walks_with_wind yes [guess ~65%] (its "fires ≤ 3× cells lit" row); sc_burn_line_walks
    no [guess ~60%].
  - `H_douses_under_a_roof`: no [guess ~80%]. Every black-rain pad is unroofed.
  - `H_stamp_caller_skips_gate`: P_gate no [guess ~90%] (it reads getters only); sc_walk not run.
  - `AB_promises_worldgen`: no [guess ~90%]. No in-game check reads About.xml.
  - `SIM_fire_makes_two`: no [guess ~95%]. An offline simulator.
  - `FF_line_any_bearing`: no [guess ~70%].
  - `FF_wind_not_from_scar`: no [guess ~90%].
- Lane 1 UNSETTLED rows (38): each is settled or not by its scene's last row in `rows.jsonl` (Exit block below).
- Road back, UNRUN until this visit:
  - `RIMMANDRAKE_MEASURE_PYRE_BURNED_SHARE_FLOOD_ALSO_MOVES`: burn_line_burned_share PASS.
  - `RIMMANDRAKE_REVERSE_PYRE_WIND_BEARING_ONE_DIRECTION_STAGED`: sc_fire_walks_with_wind PASS (R runs west 8, east 0).
  - `RIMMANDRAKE_CORRECT_PYRE_STALE_TEXT_THREE_ADVISORY_LEFTOVERS` (sc_furnace_giant, now in ullai_and_giant):
    giant_furnace_beast and giant_margin_over_roster PASS.
  - `RIMMANDRAKE_FIX_PYRE_HAWK_LETTER_BLANKS_FOUR_NAMED_SLOTS`: firehawk_first_sighting_letter 3/3 PASS.
  - `RIMMANDRAKE_REPAIR_PYRE_TABLE_LIVE_COMMANDS_THAT_NEVER_START`: the table's own commands started and ran (sc_ullai PASS).
  - `RIMMANDRAKE_BUILD_PYRE_CONTROLS_NO_BRIDGE_TOOL_CAN_RUN`: sc_no_rain PASS (after the repair); sc_ash_watered 3/3 PASS;
    sc_populations 3/3 PASS; sc_ruins PASS (after the repair); sc_ullai PASS; sc_flamefang_venom see above; sc_walk not run.
  - `RIMMANDRAKE_FIX_PYRE_ASHWALLOW_SHADE_DASH_BEATS_FIRE_DIVE`: sc_ashwallow PASS, sc_heat_dome 3/3 PASS.
  - `RIMMANDRAKE_FRAME_PYRE_CHAIN_SHOTS_ON_THEIR_SUBJECT`: every chain named PASS except sc_burn_line_walks (an edge-frame
    capture out of bounds, clamped since).
  - `RIMMANDRAKE_RENEW_SAFE_ADVANCE_AUTO_ARM_HOURLY`: sc_grass_regreens' long waits ran, with no monitor lapse
    (embergrass_regrows PASS); sc_burn_line_walks' share PASS.
  - `RIMMANDRAKE_REORDER_PYRE_BURN_WALK_BEFORE_ITS_FRONT_DIES`: burn_line_walks_hourly read fires every hour up to
    hour 23's capture (UNMEASURED there, clamped since).
  - `RIMMANDRAKE_SHIELD_PYRE_WALK_FROM_FULL_LIST_EVENTS`: sc_walk not run (game a, his full list).
  - `RIMMANDRAKE_STAGE_PYRE_FLAMEFANG_BITES_LAND_ONCE_NOT_MAUL`: one bite per patient in every venom run (bite rows 4/4 PASS).
  - `RIMMANDRAKE_TRACE_PYRE_ASHFALL_FIRE_IN_FIRST_LIGHTNING_WINDOW`: real cinderfall_lightning PASS, with ash-fall window
    1's fire named "not lightning"; planted DryThunderstorm FAIL (8 strikes).
  - `RIMMANDRAKE_TRACE_PYRE_FIREHAWK_TURNS_MANHUNTER_IN_BURN_WALK`: burn_line on the 17-mod tier (no pyrelandsmechanics)
    ran its share to a verdict (PASS), with no Manhunter stop.

## Pipeline defects fixed in this run

- `RIMMANDRAKE_SCOPE_BRIDGE_MARKER_TO_ITS_GAME_A_STOPS_B`, closed at 19e7615934, plus its second layer, 1d27205b91.
  An unknown-outcome marker, or a live client, on game a refused every game-b mutation and site load. Tests:
  selftest_bridge_reconcile_read 83/83 (81/83 on the parent) and selftest_bridge_concurrency_guard (crashed on the parent).
- Gate A harness (6ea9314ad1): the stamp is read under WSL from python.exe, and an empty-string default reads as empty.
  Before: `evidence/gateA_before_repair.log`; after: GATE A CLEAN.

## Beyond the checks

11 strange things: 8 explained, 3 filed, 0 open (`strange.jsonl`). Looked at: the heat-dome pair ("Burrowed!" dome sprite), scorch-fruit glowing in a fresh scar, the ash dusting, the furnace-beast room beside its empty control room, the charred ruin (a row of vanilla AncientPipelineSection crossing it), and the five walk stations. Copies under 1 MB are in `screenshots/`; the originals are in game b's Screenshots folder and `Transient/pv3/shots/`. Polish lines: `polish.md`.

## Savegame

`D:\ClaudeWork\rimmandrake\instances\b\Saves\PYRELANDS_0.1.0_VISIT3_WALK.rws` (27.5 MB, game b, the 17-mod `pyrelands`
tier). It was staged by `scripts/walk_save.py` on the reloaded visit-3 site; the stat-diff shows that file alone new and
nothing changed (`evidence/script_walk_save.log`). It has five labelled stations, and each capture was looked at
(`screenshots/pv3_walk_station_*.jpg`): a live burn line in fresh ember grass; the creatures (six ullai, a furnace-beast
giant, two ashwallows); scorch-fruit in a burned pad; ember grass under a roof beside an open patch; and the charred ruin
(the densest cluster, 68 of 327 charred walls). His walk is on his full list in game a; this save is on the tier list. It
is a new file in game b's Saves only, and nothing was written to his Saves folder. Game b's Saves folder was backed up
first: `D:\ClaudeWork\backups\rimworld_saves_b_pre_pyre_visit3_20261121` (58 files, 651 MB).

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
- 09:50-09:58 cinderfall with the owed plant (PYRE_PLANT_ASHFALL_STRIKE=DryThunderstorm): cinderfall_lightning FAIL (8 strikes under ash fall), the unplanted run PASS with the ash-fall fire named "not lightning". firefoam sampled runs: the timelines show the "taken" fruit of the old control burned (its colonist never moved), and the sprayer colonist never foams.
- 10:00 flamefang_venom 4/5 PASS; venom_wait_out RESTART: the first row's untended patient died of the venom (one bite, 0.45 severity; untended +0.35/day against immunity at 0.5/day: lethal near day 1.6). The row's daily read took a dead subject for "venom gone" (would PASS a death): repaired (corpses read, the subject's death is the row's FAIL, earlier patients retired, bystanders fed daily).
- 10:10 ash_fertility_watered 3/3 PASS. firefoam s3/s4/gap-planted: 0 Filth_FireFoam in 3 of 3 sprayer runs: MOD, filed RIMMANDRAKE_DESIGN_PYRE_SPRAYER_CARRIER_NEVER_FOAMS_ITS_PATH. The control (harvest read by the colonist inside the ring or a yield stack, not by plant loss): planted ring gap FAIL, s4 PASS, s3 FAIL (a bare colonist crossed the 2-cell ring unburned): SITE, unrepaired, owned by that item.
- 10:20 queue 6: venom rerun, scorchfruit with its census, the three scripts, the walk save, then fresh_burn_bonus, burn_line, scorchfruit_spoils, embergrass_regrow (the long chains; their end will pass the 3-hour mark by about 15 min [guess ~60%]).
- 10:50-12:10 burn_line (share PASS; hourly capture out of bounds at the map edge, clamped; off-control counted the fire clock's fronts, repaired, then its plant read PASS too: not counted, filed); scorchfruit_spoils and fresh_burn_bonus voided by a world-pawn heart attack, both rerun PASS; embergrass_regrow growth reads blind (filed); burn_line rerun 4/4 components PASS; venom wait-out FAIL on the build (died day 2; filed MOD).
- 12:11 the run was stopped before its record was published; resumed from the clone's bundle (store/orphans/bundles/20261121T201126Z-...), evidence and record restored unchanged.

## Exit

```
ingame_rows: {P_ambient_ash_drift: pass, P_animal_census: pass, P_ashfall_drifts: pass, P_ashfall_weather_accumulation: pass, P_blackrain: pass, P_firefoam_aim: pass, P_furnace_room: pass, P_gate: pass, P_grass_cover: pass, P_mapgen_log: pass, P_scorchfruit_produces: pass, P_scorchfruit_spoils: pass, P_startup_and_def_wiring: pass, firehawk_crestfeather_yield: pass, firehawk_first_sighting_letter: pass, sc_ash_watered: pass, sc_ashwallow: pass, sc_burn_compounds: pass, sc_burn_line_walks: unmeasured, sc_fire_dusts_ash: pass, sc_fire_walks_with_wind: pass, sc_firefoam_sprayer: fail, sc_firehawk: pass, sc_firehawk_rewards: pass, sc_flamefang_venom: fail, sc_foreign_arrivals: pass, sc_furnace: pass, sc_grass_regreens: unmeasured, sc_heat_dome: pass, sc_no_rain: pass, sc_populations: pass, sc_rite_hook_alone: pass, sc_ruins: pass, sc_sand_shovel: pass, sc_scorchfruit: pass, sc_three_skies: pass, sc_ullai: pass, sc_walk: unmeasured}
strange_open: 0
savegame: D:\ClaudeWork\rimmandrake\instances\b\Saves\PYRELANDS_0.1.0_VISIT3_WALK.rws
exit_met: false
```
