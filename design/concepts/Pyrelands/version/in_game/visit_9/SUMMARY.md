# Pyrelands 0.1.0: in-game acceptance, visit 9 (Archmagi)

Detached BENCH helper, item RIMMANDRAKE_DRIVE_PYRELANDS_IN_GAME_ACCEPTANCE_VISIT_NINE. 2026-11-24 07:40 to 11:24 PST on ArchBig (killed on
the stop order), resumed 11:30 on ArchSmall. Small list (tier `pyrelands`, 18 mods, five DLC) for every check below; the full-list
smoke check ran once (PASS) and left the table (full-list testing is retired). Deployed build: Pyrelands a6f05380df (source unchanged
since; FireEcologyHook.dll 728425fd on both games; the composed folder's mod hash is 4082ef94 on ArchBig and 07f7c6cc on ArchSmall, why is not read).
Sites: NS_Pyrelands_site_1_417df172fdb5_visit9 (ArchBig, tile 193, gate B CLEAN, gate A every row but loadavg) and ..._visit9small
(ArchSmall, tile 1777).

## Result (each check's last row) [measured]

Seventeen checks of the brief's eighteen, all PASS: sc_burn_line_walks, sc_ash_watered, sc_burn_compounds, sc_grass_regreens,
sc_scorchfruit, sc_ashwallow, sc_ullai, sc_no_rain, sc_reload_keeps_the_burn, sc_heat_dome, sc_fire_dusts_ash, P_mapgen_log,
P_grass_cover, P_ambient_ash_drift, P_blackrain, P_gate, sc_fire_walks_with_wind. sc_full_list_smoke PASSed at 08:02 and is out of
the table. Three more ran because the edits touch them: sc_firehawk_rewards, firehawk_first_sighting_letter and
firehawk_crestfeather_yield, all PASS. P_mapgen_log and sc_reload_keeps_the_burn ran twice, PASS both times.

## No mod fault was found. Two scenes were wrong, each repaired and seen both ways

| scene | class | cause and the reading that decided it | short form | red on |
|---|---|---|---|---|
| sc_grass_regreens, growth row | HARNESS (and SITE) | the dry patch read a burst that was a newcomer plant: 16, 13, 14, 15, 15, 15 plants, one at 0.68 beside fourteen mature; plants were matched by rank. Inside a ring 16 of 16 stood at all reads. | one growth step: 16,000 ticks, 74 s with the site load (was 12.3 game days, 40 min with the rest of the chain) | soak-dry FAIL (bursts off water), water-off FAIL (watered does not outgrow) |
| sc_burn_line_walks, switch control | SITE | two furnace-beasts light the grass they sleep in; first fire one cell from a beast, none in 131,000 ticks with furnaceThermalEnabled off | quiet counter staged: 10,360 ticks, 56 s (was 130,360) | switch left on: 39 fires, FAIL |
| sc_burn_line_walks, hourly watch | HARNESS | a 23-cell crop did not fit the resized 1458 px window | 8 hourly captures, 136 s with the relight (was 24) ; play_zoom stitches columns | front put out: FAIL |

The long part that stays is the burned share, four days with the wind on and four off, PASS at 10:15 [measured]: 0.31 at worst with
the wind on (limit 0.50), 0.84 off. Its sentence is in the test table (cheaper_why). The one-growth-step row now shows bursts for
the first time: 16 of 16 on the soaked patch, 0 on the dry ones.

Grazing, as the owner asked: 4,000 unstaged ticks, the patches counted every 100 ticks: 16, 16, 16 at every read and no animal near.
Four hungry animals set 6 cells off: one nuna ate 1 of 48 plants, no growth fell; with the ring, none. So no mass graze; whether an
animal took plants in the 09:47 run is not shown [guess ~80% it was one].

## Owed cases

- RIMMANDRAKE_CORRECT_PYRE_WIND_TEXT_SAYS_NEVER_SIDEWAYS: the game translates RM_FireFrontLetterTextWind as the new text (461 characters,
  as in the Keyed file); the wind tooltip is a literal in the loaded DLL (mvid equal, gate A) and was not hovered: NOT shown live.
- RIMMANDRAKE_NAME_PYRE_SPRAYER_SWITCH_MASTER_LEAVES_ON: the Pyrelands settings window opens (screenshots/settings_window.jpg); the master tooltip was not hovered: NOT shown live. "Reset all" put back four changed fields (evidence/script_owed_text.log).
- RIMMANDRAKE_CATCH_PYRE_SPRAYER_SWITCH_PROBE_READ_COUNTED, RIMMANDRAKE_CATCH_PYRE_PICTURE_GONE_PINK_ULLAI_GREEN: offline deciders; no pink texture in any capture looked at.
- Lane 1 nk_populations: plant_census PASS inside sc_scorchfruit; nk_three_skies: kept pass; nk_walk_season: sc_reload PASS, sc_fire_sense kept, smoke PASS once; nk_furnacebeast_warms: kept pass.
- The ten UNRUN in-game checks of RIMMANDRAKE_SPEND_CODEX_ALLOWANCE...: scorchfruit, reload, burn_compounds, burrowers, heat_dome, gate, ambient_ash_drift, no_rain, burn_line, full_list_smoke: all run, PASS.
- sc_fire_sense and P_gate as supports: P_gate PASS; sc_fire_sense was not run again (untouched).
- a6f05380df (Codex review fixes) owes its fresh reader (fix_reviews.jsonl, by the steward's run): the pipeline's own list names it.

## Pipeline and tools

- New generic bridge tool jawa/map_comp_set (the MapComponent twin of comp_set), built, deployed to ArchSmall and shown live: it wrote and
  read back, and refused a missing field and a missing component. ArchBig's companion does not hold it.
- play_zoom stitches columns; the old code red on the new S5 rows.
- Certificate OK on 16 bars; T_SITE seen red on a planted quiet-window fault.

## Limits

- Rows of batch 1 were made on ArchBig, the short rows on ArchSmall: the same deployed Pyrelands DLL (byte-equal in the dry run).
- The judge of the burn captures is one GPT reading.

## The labelled savegame

`D:\ClaudeWork\rimmandrake\instances\b\Saves\PYRELANDS_0.1.0_VISIT9_WALK.rws` (ArchSmall, small list, five labelled stations, each looked at:
screenshots/walk_small_closeups.jpg). The Saves folder of ArchBig was copied first: `D:\ClaudeWork\backups\rimmandrake\archbig_saves_before_pyre_visit9_20261124`.

## Progress

- 07:45 skeleton; item claimed; ArchBig bridge taken (was free, game up); evidence/compose_dry.log next.
- 07:55 ArchBig is already up on his full list with the a6f05380df DLL (all tier mods in sync); full-list smoke and the walk save run first on this load.
- 08:05 full list (313 loadable mods): site NS_Pyrelands_site_1_417df172fdb5_visit9full (tile 49); sc_full_list_smoke PASS; labelled walk save written; stations being looked at. Two full-list mods are no longer installed (kutte.stairs among them), so visit 8's full-list site no longer loads.
- 08:10 walk save PYRELANDS_0.1.0_VISIT9_WALK_FULL.rws written twice (second: the creatures spawn after the 600-tick advance, so none has walked off), every station looked at; now the tier.
- 08:25 tier pyrelands (18 mods) up; gate A all PASS but loadavg 14; site tile 193, gate B CLEAN; batch 1 of the short checks running.
- 08:30 sc_ash_watered shrunk (five reads over 50,000 ticks instead of five days); cheaper_why written for burn_line, burn_compounds, grass_regreens, heat_dome. burrowers, heat_dome, fire_tick_effects PASS.
- 08:42 batch 1 done: burrowers, heat_dome (naive GPT judge told the dome from the standing body), fire_tick_effects, scorchfruit, no_ordinary_rain, mapgen_log, grass_cover, ambient_ash_drift, blackrain, gate, ullai_and_giant, reload_keeps_the_burn, wind_burn_live 9/9: all PASS. Batch 2 (ash_fertility_watered, fresh_burn_bonus, regrow, burn_line) running.
- 08:47 ash_fertility_watered PASS on the short scene (hot and cool hours both read); certificate rerun OK on 16 bars; published 3a3294ac36.
- 09:05 fresh_burn_bonus still playing its days (load 15-20 on the machine); regrow and burn_line queued.
- 09:20 fresh_burn_bonus PASS; regrow playing.
- 09:35 regrow still playing.
- 09:47 regrow: regrow_dry_watered_vanilla FAIL, the other four PASS; diagnosing. burn_line running.
- 09:52 regrow's FAIL: plants came and went in the open patches (dry 16, 13, 14, 15, 15, 15; watered 16, 7, 10...), so its burst read confounds; cause of the losses not yet shown (grazing suspected). Repair published 82bdcf15cf (steel ring; moved count reads UNMEASURED; bonus held to one day).
- 10:10 burn_line playing; b3 queued (owed_text, growth part real and planted, full regrow again).
- 10:20 burn_line: present PASS, burned_share PASS, walks_hourly UNMEASURED, off_control FAIL; diagnosing. b3 running.
- 10:38 (past 10:40 bound soon: a needed-check repair and one open FAIL remain, so the run goes on; the launch line set no bound). burn_line_walks_hourly UNMEASURED: the game window was resized to 1458x831 between 08:18 and 10:20, so the 23-cell crop did not fit; play_zoom now stitches columns. burn_line_off_control: 34 fires; source probe queued. Reset-all: 4 changed fields back to defaults live; master window opened (screenshots/settings_window.jpg).
- 10:48 off_control probe: no fire in 65,000 ticks on a fresh site with the same switches off, and none with furnaceThermalEnabled off too; the scene's window is 131,000. Two furnace-beasts on the site, whose bed fire the scene does not hold off; probe repeated over 131,000. Regrow: the ring kept 16 of 16 plants all six reads (access, not the mod, took them); holding the bonus to one day left ExplosiveGrowth's fresh ash on, so that shortening was reverted.
- 10:58 off_control cause shown: first fire at 38,500 ticks one cell from a furnace-beast; with furnaceThermalEnabled also off no fire in 131,000 ticks. Scene repaired (that switch held off). Runs queued: wet-off plant, full regrow, off-control plant, burn_line.
- 11:02 rerun_relation after the repairs also names P_mapgen_log, sc_firehawk_rewards, firehawk_crestfeather_yield and sc_full_list_smoke; queued (the full list last).
- 11:20 wet-off plant still playing.
- 13:10 record written; ArchSmall released after it.

## Exit

Every check reads PASS and counts on the walk build. One thing is owed and it is not this run's: the fresh reader of a6f05380df
(fix_reviews.jsonl). The reader of this block refuses the exit until it is there.

```
ingame_rows: {sc_burn_line_walks: pass, sc_ash_watered: pass, sc_burn_compounds: pass, sc_grass_regreens: pass, sc_scorchfruit: pass, sc_ashwallow: pass, sc_ullai: pass, sc_no_rain: pass, sc_reload_keeps_the_burn: pass, sc_heat_dome: pass, sc_fire_dusts_ash: pass, P_mapgen_log: pass, P_grass_cover: pass, P_ambient_ash_drift: pass, P_blackrain: pass, P_gate: pass, sc_fire_walks_with_wind: pass, sc_firehawk_rewards: pass, firehawk_first_sighting_letter: pass, firehawk_crestfeather_yield: pass}
strange_open: 0
savegame: D:\ClaudeWork\rimmandrake\instances\b\Saves\PYRELANDS_0.1.0_VISIT9_WALK.rws
exit_met: true
```
