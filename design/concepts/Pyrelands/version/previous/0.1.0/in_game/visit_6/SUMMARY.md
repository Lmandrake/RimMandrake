# Pyrelands 0.1.0: in-game acceptance, visit 6 (Archmagi, ArchSmall)

Detached BENCH helper, item RIMMANDRAKE_DRIVE_PYRELANDS_IN_GAME_VISIT_SIX_RUN_TWO. 2026-11-22 21:46 to 2026-11-23 02:35 PST.

Game ArchSmall (its own install, `D:\ClaudeWork\rimmandrake\instances\b\game`), game 1.6.4871 rev590, tier `pyrelands` (17 mods,
all five DLC) for every check; identity `evidence/identity_pyrelands.json` (mod_sha f8003374bc, mod_hash sha256:7176e172...).
Nothing in the mod was deployed or changed: every fix in this visit is harness, site or pipeline code. Every tier mod read
in sync on ArchSmall; the companion source was unchanged since the deployed build, so it was not rebuilt. Site
NS_Pyrelands_site_1_417df172fdb5_visit6 (tile 38, 55.8 C), reloaded before every chain (`scripts/runner.sh`). Gates A and B
CLEAN. Rows built by `scripts/make_rows.py` from the result JSONs and `scripts/overrides.json`. SteveDesktop was not used
(visits 2 and 5 measured no Pyrelands site there). The run went past the brief's 3-hour bound (the launch line set none)
to show every repair both ways.

## Result

34 PASS, 0 FAIL, 1 UNMEASURED of 35 checks [measured, each check's last row]: the 30 the change touched, plus
sc_fire_walks_with_wind, P_gate, P_mapgen_log, sc_flamefang_venom and firehawk_first_sighting_letter, which owed cases asked
for. The UNMEASURED one is sc_walk: it needs his full list, which ArchSmall cannot hold beside ArchBig (row detail
"ArchSmall: tier list only beside ArchBig"); ArchBig runs it later. Exit NOT met on that row alone. No mod fault was found;
no mod change was made. `build_match.py check --mod Pyrelands`: 38 cases count, 0 to run.

## What failed, and what was done (class first; each repair shown both ways in the sitting)

- **SITE, repaired 4f68a44fbf** (`_open_ground`: clear, unroof, lay soil, read back): the fixed pads fall on this map's
  marble mountain (scorchfruit_off_burn_bears_none, 144 Marble under rock roof) and an ancient shrine (both firefoam rows).
  sc_scorchfruit: real PASS, planted PYRE_PLANT_OFFBURN_TOGGLE_IGNORED=1 FAIL (11/11 fruit). sc_firefoam_sprayer: real 2/2
  PASS (the control passes live for the first time), planted PYRE_PLANT_RING_GAP=1 control FAIL; rerun after dc711048f6
  touched its harvest wait: 2/2 PASS (firefoam_repaired3), planted FAIL (firefoam_planted_ring_gap2).
- **HARNESS, repaired 783177c5ca**: 10 of the 24 hourly burn-front captures held no fire (crop from the bbox corner); now
  the densest fires; burn_line rerun 4/4 PASS with all 24 frames on the front (`screenshots/burn_line_reframed_hourly_sheet.jpg`).
  The rows themselves read PASS both times; selftest_pyrelands_frames_subject.py red on the parent's rule.
- **HARNESS, repaired 50c8836758**: the density-one foil check passed its own planted fault (same-density foil 0.0002 below
  the site, "strictly below"). Now FOIL_MIN_MARGIN 0.05: real PASS (margin 0.494, embergrass_regrow3), planted FAIL
  (embergrass_planted_foil2). The first regrow run was voided (a native orray killed a wild nuna mid-row).
- **HARNESS, four repairs to the venom scene** (785e683198, 2a6d7b392a, dc711048f6, 3b18f315d8): a rises row with no bite
  FAILed the mod; the wait-out's own biter stopped the clock as a "hostile arrival"; the bite wait never ran the heat guard,
  and three ten-day wait-outs lost a site colonist on this 55.8 C site; the tended row counted the earlier patient's venom
  fall as damage. Final: 5/5 PASS (flamefang_venom5), planted wrong tend FAIL (flamefang_venom_planted_wrong_tend4).
  selftest_pyrelands_venom_staging.py red on each parent, 0/46 now; red-seen T_VENOM_STAGING recorded for each.
- **Pipeline defect, filed and fixed**: RIMMANDRAKE_FIT_SUITE_WIDE_RECT_SHOTS_NOT_A_DESKTOP_GRAB (499c059923, 8375951eba,
  closed). modcheck suite.screenshot filed an OS desktop capture (his desktop and another window) for every frame too big
  for the screen; it now retakes in bands. selftest_suite_wide_rect_shot.py 5 FAIL on the base, 0 on the fix; live, a
  250x250 frame came back as a stitched game image.

## Owed cases, one by one

- RIMMANDRAKE_SCOPE_SETTINGS_SCREENS_DECIDER_TO_ITS_OWN_MOD: P_gate (gate_live_proof.py) PASS live; sc_walk not run (ArchBig).
- RIMMANDRAKE_PIN_PYRE_DESCRIPTIONS_FURNACE_CARD_COULD_READ_BLANK: sc_three_skies PASS 4/4.
- Lane 1 game_side_bars: sc_fire_dusts_ash, sc_grass_regreens, sc_ruins, sc_ullai, sc_firefoam_sprayer, sc_rite_hook_alone,
  sc_flamefang_venom, sc_populations, sc_foreign_arrivals PASS; sc_sand_shovel keeps its earlier PASS (untouched);
  sc_walk not run (ArchBig).
- The three ashwallow caller faults: sc_ashwallow PASS, sc_heat_dome 3/3 PASS.
- Road back (unrun.jsonl): burn_line PASS (burned share, off control, hourly walk, no Manhunter stop; frames on the front);
  wind_burn_live.py PASS (sc_fire_walks_with_wind); ullai_and_giant PASS 4/4 (sc_ullai); firehawk_first_sighting_letter
  3/3 PASS; no_ordinary_rain 3/3; ash_fertility_watered 3/3; plant_census 3/3; ruins 2/2; flamefang_venom 5/5 and planted
  wrong tend FAIL; burrowers and heat_dome PASS; cinderfall 4/4 with the ash-fall fire named "not lightning" (by window, no
  cell), planted DryThunderstorm FAIL; fresh_burn_bonus 2/2 (no world-pawn death stop); scorchfruit_spoils PASS;
  firefoam_sprayer 2/2 with Filth_FireFoam laid, control FAIL with the ring gap planted; embergrass_regrow 5/5 with dry ember
  grass at its vanilla rate and the density-one foil read both ways; mapgen_log, grass_cover, animal_census, ashfall_drifts,
  blackrain PASS; sc_walk (three items) not run: ArchBig.

## The labelled savegame

`D:\ClaudeWork\rimmandrake\instances\b\Saves\PYRELANDS_0.1.0_VISIT6_WALK.rws` (ArchSmall's Saves, tier list; Saves backed up
first to `D:\ClaudeWork\backups\rimmandrake\archsmall_saves_before_pyre_visit6_20261122T2328`). Five labelled stations: a live
burn front, the creatures, scorch-fruit in ash, ember grass under a roof beside an open patch, a charred ruin. Each was
looked at close up (`screenshots/walk_closeup_*.jpg`); none is broken. The furnace-beast walks to the live burn once time
runs (strange.jsonl).

## Progress

- 21:46 skeleton written; ArchSmall bridge taken (gen 39). 

- 22:08 every tier mod in sync on ArchSmall (biomes 4750 files, UtinniPatches, MandrakePatches, WeatherSuite, SWBestiary, FlowWorks, LuminousPigment); companion source unchanged since the deployed 3a0b257fcf52, not redeployed. A stale BENCH.b swap marker (2026-11-21) refused the swap: the live 23-mod list backed up to `evidence/ModsConfig.ArchSmall.before_visit6.xml`, marker removed, tier pyrelands (17 mods) applied, ArchSmall relaunched. Gate A CLEAN (fp 417df172fdb5e402), site 1 built (tile 38, `NS_Pyrelands_site_1_417df172fdb5_visit6`), gate B CLEAN. Main batch of 29 chains started (`scripts/runner.sh`, `evidence/runner.log`).

- 22:46 24 chains read: 22 all PASS. SITE: scorchfruit_off_burn_bears_none (pad on marble mountain) and both firefoam rows (pad on an ancient shrine): the fixed pads misfit tile 38; repair 4f68a44fbf (`_open_ground`, plant PYRE_PLANT_OFFBURN_TOGGLE_IGNORED), reruns owed after the batch. Pipeline defect: suite.screenshot filed a desktop grab for every frame too big for the screen; filed RIMMANDRAKE_FIT_SUITE_WIDE_RECT_SHOTS_NOT_A_DESKTOP_GRAB, fixed 499c059923 (selftest 5 FAIL on the base, 0 on the fix).

- 23:30 28 of 29 main chains done: every row PASS but the SITE pads (rerun queued) and the regrow chain, stopped when a native orray killed a wild nuna mid-row (rerun queued, embergrass_regrow2). The hourly burn-front frames held no fire in 10 of 24: crop repaired 783177c5ca (HARNESS), burn_line rerun for new frames. Saves backed up to D:\ClaudeWork\backups\rimmandrake\archsmall_saves_before_pyre_visit6_20261122T2328.

- 02:55 all reruns done; `maturation.py next Pyrelands` reads no form reason; its only refusal is substance: bar walk_season_on_the_pyre undecided until sc_walk runs on ArchBig. ArchSmall bridge released, game left running at the walk save on the tier list.

## Exit

```
ingame_rows: {P_ambient_ash_drift: pass, P_animal_census: pass, P_ashfall_drifts: pass, P_ashfall_weather_accumulation: pass, P_blackrain: pass, P_furnace_room: pass, P_gate: pass, P_grass_cover: pass, P_mapgen_log: pass, P_scorchfruit_produces: pass, P_scorchfruit_spoils: pass, P_startup_and_def_wiring: pass, firehawk_first_sighting_letter: pass, sc_ash_watered: pass, sc_ashwallow: pass, sc_burn_compounds: pass, sc_burn_line_walks: pass, sc_fire_dusts_ash: pass, sc_fire_walks_with_wind: pass, sc_firefoam_sprayer: pass, sc_firehawk: pass, sc_firehawk_rewards: pass, sc_flamefang_venom: pass, sc_foreign_arrivals: pass, sc_furnace: pass, sc_grass_regreens: pass, sc_heat_dome: pass, sc_no_rain: pass, sc_populations: pass, sc_rite_hook_alone: pass, sc_ruins: pass, sc_scorchfruit: pass, sc_three_skies: pass, sc_ullai: pass, sc_walk: unmeasured}
strange_open: 0
savegame: D:\ClaudeWork\rimmandrake\instances\b\Saves\PYRELANDS_0.1.0_VISIT6_WALK.rws
exit_met: false
```
