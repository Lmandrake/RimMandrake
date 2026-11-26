# Pyrelands 0.1.0: in-game acceptance, visit 8 (Archmagi, ArchBig)

Detached BENCH helper, item RIMMANDRAKE_DRIVE_PYRELANDS_IN_GAME_ACCEPTANCE_VISIT_EIGHT. 2026-11-23 18:55 to 2026-11-24 PST. The run
went past the brief's 3-hour bound (the launch line set none).

Game ArchBig, 1.6.4871 rev590. Tier `pyrelands` (18 mods, five DLC) for every check but the full-list ones; his full list (315
active, 314 loadable) for sc_walk and sc_full_list_smoke. Deployed on the game: Huge Things and MandrakePatches (were stale), the
bridge companion, and from 20:58 the composed biomes with the fire-hawk fix (mod_hash sha256:4125a4a0...). Sites built fresh:
`NS_Pyrelands_site_1_417df172fdb5_visit8` (tier, tile 178) and `..._visit8full2` (his list, tile 23589). Gate B CLEAN on both; gate A
on the tier every row PASS but loadavg (other agents' work); gate A on the full list did not finish in 420 s (load 50).

## What the brief asked, and what changed under it

The brief named sc_burn_line_walks, sc_walk and P_furnace_room. While the run held the game, the owner ruled sc_walk out (077f18f8b0,
RIMMANDRAKE_SPLIT_PYRELANDS_SEASON_WALK_TO_MINIMUM_TESTS): sc_reload_keeps_the_burn, sc_fire_sense and sc_full_list_smoke replace it.
All three were run here. The long walk was stopped; what it had read is in "The long walk" below.

## Result (each check's last row) [measured]

| check | verdict | reading |
|---|---|---|
| P_furnace_room | PASS | beast room 81.8 C, its control 56.0 C, 0 open roof cells, Huge Things at its defaults |
| sc_burn_line_walks | PASS | 4/4 twice (burn_line2, burn_line3); worst burned share 0.24 (limit 0.50), wind off 0.84; naive judge YES; strand share 0.046, no one-cell lane |
| sc_fire_walks_with_wind | PASS | wind_burn_live 9/9 |
| sc_reload_keeps_the_burn | PASS | plants front_lost and old_save FAIL |
| sc_fire_sense | PASS | 5/5 after a HARNESS repair; gate-off plant FAIL |
| sc_full_list_smoke | PASS | after a SITE repair: fires 11, 15, 11; centre moved 4.2 cells (bar 3.0); no error names Pyrelands; plants no_front and log_error FAIL |
| touched by this run's edits and run again | PASS | sc_ashwallow, sc_firehawk, sc_firehawk_rewards, firehawk_first_sighting_letter, sc_scorchfruit, sc_fire_dusts_ash, sc_furnace, sc_burn_compounds, sc_grass_regreens, P_animal_census |

## Mod fault found and fixed in the sitting (one)

A fire-hawk already carrying an ember dropped it after "Mod enabled" went off: a fire 500 ticks after the switch, 236 fires a day later.
Fix 4a9d62cae0: JobDriver_RUT_FireHawkCarryEmber fails every toil once the gate or its switch is off. Before and after: the settings
sweep's new fact job_ends_off (rc 1 on the parent, rc 0 on the fix; 3 new mutants red; red-seen recorded for T_SETTINGS_SWEEP_OFFLINE);
live, gate_off_source.py: a fire at 500 ticks on the parent DLL, no fire in 60,000 ticks on the fix. It owes its fresh reader
(fix_reviews.jsonl, by the steward's run).

## What was wrong in a check or a scene, and its repair

| check | class | what | repair | planted |
|---|---|---|---|---|
| sc_burn_line_walks, sc_burn_compounds, sc_grass_regreens | APPARATUS FAULT | safe_advance stops on harm to wildlife the read does not look at | wildlife shield 05d3da7407, f83b30b60a, 6e9257a1af | selftest can-fail cases (a colonist's harm, a mental state) |
| sc_firehawk | SITE | the far hawk was thirsty and flew to water inside the ember reach | f83b30b60a | NO_SEEK: FAIL |
| sc_fire_sense | HARNESS | the feeder filled the urgently hungry colonist (visit 2's F9) | 694d79e5b8 | gate off: FAIL |
| sc_full_list_smoke | SITE | its pad was never-burned soil, so the centre moved 3.0 (run 2 PASS) and 2.7 cells (run 3 FAIL) on one mod | 177a585e57 (deep ash) | no_front, log_error: FAIL |
| sc_full_list_smoke run 1 | APPARATUS FAULT | stopping the long walk had left Mod enabled off | master put back | - |

Pipeline: rerun_relation read a creature name as a row id (259988da10) and a chain registration as a change to every check (07b02b8468,
998f10d62e); RIMMANDRAKE_RELATE_CHECKS_BY_ROW_ID_NOT_CREATURE_NAME, its selftest red on each parent.

## The long walk (sc_walk, no longer in the table)

Run 1 (site tile 193): every part UNMEASURED; the site had no water and colonists died of Dubs Bad Hygiene thirst (SITE). Run 2 (tile 23589,
58 water cells, 2 weeks, 3 colonists alive): walk_reload_keeps_the_state PASS, walk_second_pass_and_switches PASS,
walk_firecast_thirst_and_colonists PASS, walk_master_bed_fire_resumes PASS; gate, roster, roof and master parts UNMEASURED (a colonist was
generated with a feather addiction and a heart blockage). On the tier with the fix: gate, roster, roof, thirst, bed, master all PASS
(walk_parts_tier, walk_master_real), and each planted fault FAIL (gate ignored, roster ignored, master left on, master left off, bed
left on, bed left off). Those parts' code (the relight-long off spells, the staged sleeper) stays in validation.py.

## Owed cases, one by one

- RIMMANDRAKE_CORRECT_PYRE_WIND_TEXT_SAYS_NEVER_SIDEWAYS, RIMMANDRAKE_NAME_PYRE_SPRAYER_SWITCH_MASTER_LEAVES_ON: text, deployed; offline sweep
  facts wind_tooltip and master_tooltip ok; P_gate was not run again (untouched). NOT shown live: nobody opened the settings window.
- RIMMANDRAKE_CATCH_PYRE_SPRAYER_SWITCH_PROBE_READ_COUNTED, RIMMANDRAKE_CATCH_PYRE_PICTURE_GONE_PINK_ULLAI_GREEN: offline deciders; nothing in the game
  changed. No pink texture in the captures looked at.
- Lane 1 nk_populations, nk_three_skies: sc_populations (plant_census PASS inside scorchfruit's run); sc_three_skies keeps its pass.
- Lane 1 nk_walk_season_on_the_pyre: the three small scenes PASS; his walk is the rest. nk_furnacebeast_warms: furnace_warmth PASS, furnace_room PASS.
- RIMMANDRAKE_MEASURE_PYRE_BURNED_SHARE, RENEW_SAFE_ADVANCE (burn_line), REORDER_PYRE_BURN_WALK, TRACE_PYRE_FIREHAWK_TURNS_MANHUNTER, FRAME (burn_line),
  WIDEN_PYRE_FIRE_TRAILS, WIDEN_PYRE_LONE_FIRE (burn_line): burn_line 4/4 twice; 24 hourly captures; no Manhunter stop; lanes_probe PASS.
- REVERSE_PYRE_WIND_BEARING, WIDEN_PYRE_LONE_FIRE (wind): wind_burn_live 9/9 PASS.
- FIX_PYRE_HAWK_LETTER_BLANKS: letter 3/3 PASS. BUILD_PYRE_CONTROLS (sc_walk, sc_grass_regreens...), SHIELD_PYRE_WALK, FIX_PYRE_BURN_HISTORY_PROBE
  (sc_walk): the long walk's readings above. SPARE_PYRE_FURNACE_BARN_ROOF: furnace_room PASS at Huge Things' defaults.
- FIX_PYRE_ASHWALLOW_SHADE_DASH (sc_ashwallow): burrowers PASS. IGNORE_OFFMAP_COLONIST_DEATH (fresh_burn): PASS. TRACE_PYRE_EMBERGRASS,
  BUILD_PYRE_DENSITY_ONE_FOIL (sc_grass_regreens), RENEW_SAFE_ADVANCE (sc_grass_regreens): regrow2 5/5 PASS.
- NOT run again here, kept from visit 7 (untouched by the change): the owed runs for sc_ullai, sc_three_skies, sc_populations' own chain,
  sc_ruins, sc_ash_watered, sc_no_rain, sc_heat_dome, sc_flamefang_venom, sc_firefoam_sprayer, P_mapgen_log, P_grass_cover's own row, P_ashfall_drifts,
  P_blackrain, P_scorchfruit_spoils: each had its PASS in visit 7.

## Limits (read before counting a row)

- The judge of the burn captures was this driver (not the maker) and one GPT reading; the dense blocks' cause is read from vanilla's source,
  not at a block's terrain [guess ~85%].
- The deployed mod hash moved between 02:43 and 03:13, while another run (Alpha Biomes retirement) held ArchBig; sc_full_list_smoke run 4 and
  sc_reload_keeps_the_burn run 2 read the new one, the other rows the old one. No file under src/RimMandrake/Pyrelands that ships changed.
- sc_full_list_smoke run 4's identity joins two readings (its row says so).
- Other mods of his list were stale on ArchBig (evidence/deploy_all_dry.log, 12 mods); only Pyrelands' own files and two dependencies were deployed.
- Two of this run's own runners overlapped once (19:41) and hung the game; half an hour was lost. Nothing from that overlap is counted.

## The labelled savegame

`C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Saves\PYRELANDS_0.1.0_VISIT8_WALK_FULL.rws` (his full list, five labelled stations; the save
differs from the Saves folder before it by that one file). Every station looked at: screenshots/walk_closeups_sheet.jpg and _sheet2.jpg.
The Saves folder was copied first: `D:\ClaudeWork\backups\rimmandrake\archbig_saves_before_pyre_visit8_20261123T2018`.

## Progress

- 18:57 skeleton written; item claimed; ArchBig bridge taken (free, at the main menu on a 15-mod list).
- 19:20 ArchBig: Huge Things and MandrakePatches deployed (drift), companion rebuilt and deployed, tier pyrelands (18 mods), launched pid 43680. Gate A every row PASS but loadavg 13.7 (other agents).
- 19:24 site NS_Pyrelands_site_1_417df172fdb5_visit8 (tile 178, 52.8 C), gate B CLEAN. P_furnace_room PASS (beast room 81.8 C, control 56.0, 0 open roof cells). burn_line running.
- 19:40 sc_walk part walk_master_bed_fire_resumes (UNMEASURED by design in visit 5: it waited for a chance sleeper) rewritten to stage its own sleeper, master off then on; planted switches PYRE_PLANT_BED_MASTER=left_off|left_on; selftest_pyrelands_walk_bed_resume 0/18 on the parent, 18/18.
- 19:38 burn_line run 1: burn_line_present and the 24-hour watch PASS; burn_line_burned_share spoiled on day 4 (a wild barbslinger downed a wild fire wasp; safe_advance stopped). Shield added (05d3da7407). wind_burn_live 9/9 PASS. 19:42 two runners overlapped for a minute (my queue error), both killed; burn_line rerun from a reloaded site.
- 20:16 the game hung since 19:41 (two runners loading at once; my error, 30 min lost); ArchBig stopped and relaunched on the tier; the runner now stops on a failed reload.
- 20:37 burn_line2 (reloaded site, shield): 4/4 PASS.
- 20:42 bed-fire part on the tier: real PASS (off 11250 ticks no fire, on lit), planted left_on FAIL, planted left_off FAIL. 20:48 walk_gate_off_then_on on the tier: real FAIL, 236 fires after a gate-off day; planted GATE_IGNORED read PASS (its plant cannot fire on a map whose burn is quiet). 20:55 first-fire probe: 500 ticks after "Mod enabled" off a fire-hawk already carrying dropped its ember and lit grass: MOD. Fixed in the sitting (JobDriver_RUT_FireHawkCarryEmber fails every toil once the gate or its switch is off; settings sweep fact job_ends_off red on the parent, 3 mutants red).
- 21:04 fire-hawk fix live: before (parent DLL) a fire at 500 ticks after "Mod enabled" off; after (4a9d62cae0) no fire in 60,000 ticks (evidence/script_gate_off_source.log, script_gate_off_source_fixed.log). Deployed to ArchBig. The relation names 7 more checks touched by the walk edits (their settings name matches); queued on the tier, then his full list and sc_walk.
- 21:22 tier5 reruns: burrowers, scorchfruit (plant_census), fire_tick_effects, furnace_warmth, letter PASS. firehawk far_hawk_seeks_the_burn FAIL: SITE (the thirsty hawk took RM_DrinkFromTerrain, flew from 104 to 44 cells to water inside the ember reach, so the carry took over; repaired: it starts watered and fed). fresh_burn_bonus spoiled (a barbslinger downed a fire-hawk on day 1; shield applied to the two long ground chains). Reruns queued with the NO_SEEK plant.
- 21:50 tier rehearsal of the walk's later parts on the hawk-fixed build: gate, roster, roof, thirst, bed fire PASS; walk_master_off_then_on FAIL "back on, no front walked over the day": HARNESS (the standing burn relights after two quiet days, the on spell was one; its net-ash rule read decay). Repaired: both spells run the relight window, hour-by-hour ash; gate and roster off spells run it too, with planted switches for each. rerun_relation read defName strings as row ids (RIMMANDRAKE_RELATE_CHECKS_BY_ROW_ID_NOT_CREATURE_NAME): fixed.
- 22:49 regrow2 5/5 PASS, fresh_burn_bonus2 2/2 PASS, firehawk2 3/3 PASS (NO_SEEK plant FAIL). tier9 (planted walk parts, burn_line3) running.
- 23:10 walk_master_off_then_on on the tier: real PASS; planted left_on FAIL, left_off FAIL. walk_gate_off_then_on planted (gate ignored) FAIL. Roster plant and burn_line3 running.
- 23:40 tier9: roster plant FAIL, animal_census PASS, burn_line3 4/4 PASS. 23:45 his full list (315 active, restore-full) on ArchBig, launching.
- 00:20 full list up (bridge after ~18 min under load; ArchBig pid 47988), full-list site NS_Pyrelands_site_1_417df172fdb5_visit8full (tile 193); gate B above; sc_walk started.
- 00:33 sc_walk run 1 on his full list: every part UNMEASURED: SITE. The full-list site (tile 193) holds no water cell at all (evidence/script_need_peek.log), so colonists died of Dubs Bad Hygiene dehydration and one of a bite. Site rebuilt with water required.
- 00:45 site NS_Pyrelands_site_1_417df172fdb5_visit8full2 (tile 23589, 58 shallow water cells), gate B above; sc_walk run 2 started.
- 01:10 sc_walk run 2 still in its first week.
- 01:47 sc_walk run 2: walk_reload_keeps_the_state PASS, walk_second_pass_and_switches PASS (two weeks, 3 colonists alive); walk_gate/roster/roof UNMEASURED: colonist Gutierrez went down twice from GR_FeatherdustAddiction and heart artery blockage he was generated with (SITE); later parts still running. Scene repair: the walk's colonists start with no generated ailment.
- 01:58 sc_walk run 2 done: reload, second pass, thirst/colonists, bed fire PASS; gate, roster, roof, master UNMEASURED (the generated addiction). Later parts rerun on pyre_walk_end (walk_parts_full) with the colonists cleared of it.
- 02:05 the owner's ruling landed on main during this run (077f18f8b0, RIMMANDRAKE_SPLIT_PYRELANDS_SEASON_WALK_TO_MINIMUM_TESTS): sc_walk is gone from the test table; sc_reload_keeps_the_burn, sc_fire_sense (tier) and sc_full_list_smoke (full list) replace it. The running walk was stopped; its record stays (run 2: reload, second pass, thirst, bed fire PASS).
- 02:07 sc_full_list_smoke run 1 read FAIL on an APPARATUS FAULT of this run: stopping the long walk had left "Mod enabled" off in the running game (evidence/script_settings_peek.log); the master put back, rerun. Its two plants (no_front, log_error) FAIL.
- 02:10 sc_full_list_smoke run 2 PASS (18, 35, 56 fires; centre moved 3.0 cells; no error of ours; 99.7% of his list). 02:20 labelled walk save PYRELANDS_0.1.0_VISIT8_WALK_FULL on his full list, every station looked at (screenshots/walk_closeups_sheet*.jpg; a fire lit on a paused map drew nothing before its first ticks, so the save advances 600 ticks). Then back to the tier for the two small scenes.
- 02:25-02:41 tier: reload_keeps_the_burn PASS (plants front_lost, old_save FAIL); fire_sense run 1: hungry_eats_first FAIL is HARNESS (the feeder filled the hungry colonist; visit 2's F9), repaired, run 2 5/5 PASS, gate-off plant FAIL; the hawk letter 3/3 PASS. 02:43 bridge released; another run took ArchBig. 5411bd360c (the split run) changed walk_small_live.py after these runs, so sc_reload_keeps_the_burn and sc_full_list_smoke run once more when ArchBig is free. rerun_relation also reads a registration loop (its <module> change had touched 33 checks).

- 03:13 ArchBig retaken (free), his full list loaded (802 s). 03:30 sc_full_list_smoke run 3 FAIL on its own ground (2.7 cells); SITE, repaired 177a585e57; 03:32 run 4 PASS (4.2 cells), both plants FAIL. 03:41 tier again: sc_reload_keeps_the_burn PASS. 03:42 bridge released; ArchBig left on the tier list.

## Exit

Every check of the table reads PASS and counts on the walk build. One thing is owed and it is not this run's: the fresh reader of the mod fix
4a9d62cae0 (fix_reviews.jsonl); the reader of this block refuses the exit until it is there.

```
ingame_rows: {P_furnace_room: pass, P_animal_census: pass, firehawk_first_sighting_letter: pass, sc_ashwallow: pass, sc_burn_compounds: pass, sc_burn_line_walks: pass, sc_fire_dusts_ash: pass, sc_fire_sense: pass, sc_fire_walks_with_wind: pass, sc_firehawk: pass, sc_firehawk_rewards: pass, sc_full_list_smoke: pass, sc_furnace: pass, sc_grass_regreens: pass, sc_reload_keeps_the_burn: pass, sc_scorchfruit: pass}
strange_open: 0
savegame: C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Saves\PYRELANDS_0.1.0_VISIT8_WALK_FULL.rws
exit_met: true
```
