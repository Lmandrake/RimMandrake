# Pyrelands 0.1.0: in-game acceptance, visit 9 (Archmagi, ArchBig)

Detached BENCH helper, item RIMMANDRAKE_DRIVE_PYRELANDS_IN_GAME_ACCEPTANCE_VISIT_NINE. Started 2026-11-24 07:40 PST. Bound 3 hours (10:40).

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
