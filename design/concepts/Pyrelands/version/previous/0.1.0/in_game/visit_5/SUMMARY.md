# Pyrelands 0.1.0: in-game acceptance, visit 5 (Archmagi, ArchBig, 2026-11-22 04:13 to 08:35 PST)

Detached BENCH helper, item RIMMANDRAKE_DRIVE_PYRELANDS_IN_GAME_VISIT_FIVE_RUN_TWO. Game ArchBig (Steam's install), game
1.6.4871 rev590. Tier `pyrelands` (17 mods, all five DLC) for every check but sc_walk; sc_walk on his full list (315 mods),
the list restored at 07:11 and left live. Walk build: composed biomes as deployed (all in sync, nothing applied),
companion BridgeTools --gm deployed; mod_hash sha256:9c2c8828... on both lists (`evidence/identity_pyrelands.json`,
`evidence/identity_full.json`); no mod file was deployed after the identity: every change in this visit is test or harness
code (validation.py, selftests, the table command), none deployed. Sites: NS_Pyrelands_site_1_417df172fdb5_visit5
(tier, tile 1496, reloaded before every chain, `scripts/runner.sh`) and ..._visit5full (his list, tile 178). Gates A and B
CLEAN on the tier; on his list gate B CLEAN, gate A's 3.8.3 and 3.2.3 refusals explained in strange.jsonl. Rows built by
`scripts/make_rows.py` (`scripts/overrides.json` holds classes, repairs and planted runs). SteveDesktop was not used (visit 2
measured its queue running none of the Pyrelands chains: no Pyrelands site there). The visit ran past the brief's 3-hour
bound (the run's own launch line set no wall bound) to run sc_walk on his full list.

## Result

32 PASS, 0 FAIL, 3 UNMEASURED of 35 checks [measured, `rows.jsonl`, each check's last row]: the 33 the change touched plus
sc_fire_walks_with_wind and P_gate, which owed cases asked for. Exit NOT met: three needed checks not counted, each with an
owner. No mod fault was found that a check could decide; no mod change was made in the sitting.

## What failed, and what was done (class first)

- **SITE, unrepaired, filed:** `sc_firefoam_sprayer`. The sprayer row PASSes (13 Filth_FireFoam cells: the 3acf1ad82b fix
  foams live), but the control cannot be made to work in the sitting: one map_fire lights 41-54 of 72 ring cells, both
  colonists (with and without the sprayer) walk through the gaps and wait about 1500 ticks for the ring to burn down, and
  the planted ring gap read PASS while the real ring read FAIL (chance, not the ring). Tried: 3-cell ring (15431f983f),
  the sprayer row's foam cleared first (ab3a14c6f5). Owner RIMMANDRAKE_SEAL_PYRE_SPRAYER_RING_BOTH_COLONISTS_WAIT_IT_OUT.
- **HARNESS (by construction), owned:** `sc_grass_regreens`. Every component PASS on the rerun (embergrass_regrows,
  regrow_dry_watered_vanilla, grass_census_first: the e63595716c rate fix works live) except plant_density_one_control_map,
  UNMEASURED by construction (no tool regenerates the seed at plantDensity 1.0). Owner
  RIMMANDRAKE_BUILD_PYRE_GRASS_FOIL_SAME_SEED_DENSITY_ONE. The first run was voided: a site colonist died of Plague mid-row.
- **HARNESS, repaired in part, owned:** `sc_walk` (his full list). Walk 1: every part stopped on ordinary life of his list
  (a wild nuna downed by a predator, a visiting villager downed, a fire-wasp downed, colonist panic) and the gate-off day
  counted the walk's own spreading fires. Repaired bd8963f26d, baf24e6627, 70e08b2bab (the walk resumes past harm to
  pawns not the player's and a colonist's panic flight, read back; the off days start extinguished; selftest 37/37).
  Walk 2: walk_firecast_thirst_and_colonists PASS, walk_gate_off_then_on PASS (repaired; its planted run not made),
  walk_reload_keeps_the_state FAIL (one regrowth cell a day-bin older after the reload, totals equal: presumed the read's
  tick, repaired 43491722c4, not run), walk_master_off_then_on FAIL on the probe's own exception (ProbeBurnHistory reads its
  count before it prunes: red seen live, `scripts/probe_burnhist_red.py` exit 1; its repair touches the mod DLL), the rest
  UNMEASURED. Owner RIMMANDRAKE_FIX_PYRE_BURN_HISTORY_PROBE_COUNTS_BEFORE_IT_PRUNES, then a full-list walk.
- **Repaired and shown both ways in the sitting (now PASS):** `sc_ruins` (HARNESS 2613e2e96a: overlapping ruin samples
  read once; planted footprint soil FAIL, real PASS), `sc_firehawk` (SITE e8cb081456: the far hawk wandered into carry
  reach before its first think; planted no-seek FAIL, real PASS), `sc_scorchfruit` (HARNESS 15431f983f: the table command
  ran without its census; planted unburned fruit FAIL, real PASS). No `maturation.py red-seen` was recorded: each edited
  decider is a live check whose file is validation.py itself, which red-seen refuses as a plant site.

## Owed cases, one by one

- RIMMANDRAKE_SCOPE_SETTINGS_SCREENS_DECIDER_TO_ITS_OWN_MOD: `selftest_settings_screens.py --mod Pyrelands` 14/14 ok; P_gate
  (gate_live_proof.py) PASS live; sc_walk's switch parts: the gate-off day PASS, the master part blocked by the probe.
- RIMMANDRAKE_PIN_PYRE_DESCRIPTIONS_FURNACE_CARD_COULD_READ_BLANK: sc_three_skies PASS 4/4; selftest_pyrelands_defs_offline.py
  11 facts, 22 of 22 mutants red.
- Lane 1 game_side_bars: sc_fire_dusts_ash, sc_ruins, sc_ullai, sc_sand_shovel, sc_rite_hook_alone, sc_flamefang_venom,
  sc_populations, sc_foreign_arrivals PASS; sc_grass_regreens, sc_firefoam_sprayer, sc_walk not counted (above).
- The three ashwallow caller faults: sc_ashwallow PASS, sc_heat_dome 3/3 PASS.
- Road back (unrun.jsonl): burn_line 4/4 PASS (burned share, off control, hourly walk; no Manhunter stop); wind_burn_live.py
  PASS (sc_fire_walks_with_wind); ullai_and_giant PASS (sc_ullai, sc_furnace_giant); firehawk_first_sighting_letter PASS;
  no_ordinary_rain PASS; ash_fertility_watered 3/3; plant_census 3/3; ruins PASS (repaired); flamefang_venom 5/5 PASS and
  the planted wrong-tend FAIL (second try; the first voided by a downed patient); burrowers and heat_dome PASS; frames on
  subject: the captures frame their subjects (the ullai themselves read as rubble: filed); cinderfall 4/4 PASS with the
  ash-fall fire named 'not lightning', planted DryThunderstorm FAIL; fresh_burn_bonus 2/2 and scorchfruit_spoils PASS (no
  world-pawn death stop); sprayer: foams live, control SITE (filed); embergrass rate: PASS on deep ash (the visit-4 parent
  read 0.054/day); sc_walk: run on his full list, not counted (above).

## Filed in this visit

RIMMANDRAKE_WIDEN_PYRE_FIRE_TRAILS_RUN_AS_RULER_STRAIGHT_LANES (the hourly burn captures show straight one-cell lanes),
RIMMANDRAKE_SEAL_PYRE_SPRAYER_RING_BOTH_COLONISTS_WAIT_IT_OUT, RIMMANDRAKE_JUDGE_PYRE_ULLAI_HERD_READS_AS_GREY_RUBBLE,
RIMMANDRAKE_FIX_PYRE_BURN_HISTORY_PROBE_COUNTS_BEFORE_IT_PRUNES. Savegames: PYRELANDS_0.1.0_VISIT5_WALK_FULL (his list,
the labelled walk save, every station looked at in `screenshots/walk_full_station_*.jpg`) and PYRELANDS_0.1.0_VISIT5_WALK
(the tier). Saves folder backed up first: D:\ClaudeWork\backups\rimworld_saves_a_pre_pyre_visit5_20261122.

## Progress

- 04:13 precondition `in_game 0.1.0`; item claimed; skeleton written (b4ece5f613).
- 04:20 bridge ArchBig taken by BENCH. Deploy dry runs: composed biomes, UtinniPatches, FlowWorks, LuminousPigment, MandrakePatches, WeatherSuite, SWBestiary all in sync with ArchBig's Mods (nothing to apply). Companion BridgeTools --gm deployed to ArchBig (readback sha256 baa4faefb480064b). Tier pyrelands applied (17 mods, 5 DLC; his 315-mod list backed up by modset_builder). ArchBig launching.
- 04:22 ArchBig started directly (Steam answered WaitingPrevProcess beside ArchSmall), bridge after 119 s. Gate A refused once on 3.8.12 loadavg 10.25 (transient); rerun CLEAN (12 rows), def fingerprint 417df172fdb5e402.
- 04:29 site NS_Pyrelands_site_1_417df172fdb5_visit5 built (tile 1496, map 1); gate B CLEAN (5 rows). Identity: mod_sha e63595716c, game 1.6.4871 rev590, tier pyrelands (17), mod_hash sha256:9c2c8828... (`evidence/identity_pyrelands.json`).
- 04:30 batch 1 started (`scripts/runner.sh b1`, site reloaded before every chain): 26 shorter chains.
- 04:40-04:50 first reads: ruins/ruins_scorched FAIL 'get_terrain_batch read 88 of 90 cells': two ruin samples overlap by 2 cells and the tool reads a cell once (JawaBenchTerrainTools.cs keys by cell). HARNESS, repaired 2613e2e96a (distinct-cell count; selftest_pyrelands_terrain_union.py 0/6 on the fix, 2/6 with --old); planted switch PYRE_PLANT_RUIN_FOOTPRINT_SOIL=1. firehawk/far_hawk_seeks_the_burn UNMEASURED: the hawk's first GotoWander took it 58 -> 54 cells, straight into carry reach, so the seek had no think to fire on; the 'stray' fires were its own drops after the carry. SITE + HARNESS, repaired e8cb081456 (hawk starts 100 cells off; strays after the hawk's first carry/seek do not void). Real and planted reruns queued after batch 1.
- 04:57 batch 1 done (26 chains, 04:30-04:57): every component PASS except ruins_scorched, far_hawk_seeks_the_burn, scorchfruit_fire_born and the sprayer control. flamefang_venom 5/5 PASS; sprayer_reaches_the_fruit PASS (13 Filth_FireFoam cells: the 3acf1ad82b fix works live).
- 04:59 batch 2 started. 05:00 ruins repaired PASS, planted soil FAIL ('0% deep ash or charred floor'). 05:03 firehawk repaired PASS (seek taken at 100 cells, then the carry), planted no-seek FAIL. 05:06 Saves folder backed up to D:\ClaudeWork\backups\rimworld_saves_a_pre_pyre_visit5_20261122 (7.5 GB, 599 files).
- 05:09 scorchfruit table command repaired (HARNESS, 15431f983f: it ran without plant_census, UNMEASURED by construction): real PASS 5/5, planted unburned fruit FAIL at (125,125).
- 05:13 sprayer control with a 3-cell ring (SITE, 15431f983f: a 2-cell ring is crossed between two of vanilla Fire's 150-tick ignite tries): the ring's west edge refused fire, 9 of 9 cells under the sprayer row's Filth_FireFoam. SITE, repaired ab3a14c6f5 (the control's ground cleared of filth first); real and planted reruns queued after batch 2.
- 05:19-06:12 batch 2 long chains: venom planted wrong-tend read UNMEASURED (RESTART: a patient downed during the row; rerun queued). cinderfall 4/4 PASS (10 strikes under cinderfall, 0 under ash fall; the ash-fall window-1 fire named 'not lightning'); planted DryThunderstorm strike FAIL (5 strikes under ash fall): the owed lightning case is met. ash_fertility_watered 3/3, scorchfruit_spoils, fresh_burn_bonus 2/2 PASS (no world-pawn death stop). embergrass_regrow stopped: site colonist Human75831 downed then died of Plague 0.9 (with Scratch/Leg and Bite/Arm) at 1140 ticks into a 2000-tick step; every regrow row RESTART (SITE, damage to the test). A health probe of the reloaded fixture and a rerun are queued.
- 06:33-07:08 batch 3: health probe (the Plague colonist carries Scratch/Bite from the site build, no disease at reload); sprayer control with foam cleared FAIL again, planted ring gap PASS (the fire spread into the waiting colonist's cell): the control reads chance, not the ring; both colonists, with and without the sprayer, walk through the ring's gaps (one map_fire lights 41-54 of 72 cells) and wait it out. Not repairable in the sitting (the scene is a design call): filed RIMMANDRAKE_SEAL_PYRE_SPRAYER_RING_BOTH_COLONISTS_WAIT_IT_OUT; sc_firefoam_sprayer not counted. Venom planted wrong-tend FAIL (owed case met). herd_look: 16 ullai stand at (50..85, 147..158) and read as grey rubble at play zoom (filed RIMMANDRAKE_JUDGE_PYRE_ULLAI_HERD_READS_AS_GREY_RUBBLE). patch_probe: the black patch is an AncientConcrete pad with 2 AncientShipBeacons. embergrass_regrow rerun: embergrass_regrows, regrow_dry_watered_vanilla, grass_census_first PASS (the e63595716c fix works live); plant_density_one_control_map UNMEASURED by construction (owner RIMMANDRAKE_BUILD_PYRE_GRASS_FOIL_SAME_SEED_DENSITY_ONE). wind_burn_live PASS (rc 0), gate_live_proof PASS (rc 0).
- 06:45 the hourly burn_line captures show the fire's trail as ruler-straight one-cell lanes: filed RIMMANDRAKE_WIDEN_PYRE_FIRE_TRAILS_RUN_AS_RULER_STRAIGHT_LANES (the bar asks a judge for 'natural').
- 07:08 walk save PYRELANDS_0.1.0_VISIT5_WALK written on the reloaded tier site (stat-diff: that file alone new, 27.9 MB); every station looked at in a tight cell-rect capture (screenshots/walk_station_*.jpg).
- 07:12 rows built (make_rows.py): 32 PASS, 3 UNMEASURED of 35 checks (33 touched + sc_fire_walks_with_wind and P_gate, owed). Next: sc_walk on his full list (ArchBig restart).
- 07:11 ArchBig stopped; his full list restored by modset_builder --restore (315 active, md5-verified); launched directly, bridge after 787 s. Gate A on the full list: 3.8.3 (extra mods, the list itself) and 3.2.3 (running sha != file: Prepatcher; the module ids match the tier run's) refused, every other row PASS, def fingerprint 417df172fdb5e402. 07:32 full-list site NS_Pyrelands_site_1_417df172fdb5_visit5full (tile 178) built, gate B CLEAN; identity --full (mod_hash 9c2c8828..., the tier's). walk_season started with PYRE_WALK=1.
- 07:32-07:52 walk_season on his full list: every part but one UNMEASURED: safe_advance stopped on a wild nuna downed by a predator (with a colonist's PanicFleeFire), a visiting villager downed (bitten, dehydrated, starving) and a fire-wasp downed; walk_gate_off_then_on FAIL with 928 fires: the day began with the walk's own 30 fires, which spread by vanilla. All HARNESS: repaired bd8963f26d and baf24e6627 (the walk resumes past harm to pawns not the player's and a colonist's panic flight, read back by list_pawns; the gate-off and roster-off days start extinguished; planted switch PYRE_PLANT_GATE_IGNORED; selftest_pyrelands_walk_shield.py 35/35). 07:55 the walk rerun on the reloaded full-list site; the planted run follows.
- 08:10-08:40 the walk's digest and starving repairs (43491722c4, 70e08b2bab); the probe fault reproduced live and filed; the labelled walk save made again on his full list (PYRELANDS_0.1.0_VISIT5_WALK_FULL, stat-diff: that file alone new) and its stations looked at; build_match: 38 of 38 count.

## Exit

```
ingame_rows: {P_ambient_ash_drift: pass, P_animal_census: pass, P_ashfall_drifts: pass, P_ashfall_weather_accumulation: pass, P_blackrain: pass, P_furnace_room: pass, P_gate: pass, P_grass_cover: pass, P_mapgen_log: pass, P_scorchfruit_produces: pass, P_scorchfruit_spoils: pass, P_startup_and_def_wiring: pass, sc_ash_watered: pass, sc_ashwallow: pass, sc_burn_compounds: pass, sc_burn_line_walks: pass, sc_fire_dusts_ash: pass, sc_fire_walks_with_wind: pass, sc_firefoam_sprayer: unmeasured, sc_firehawk: pass, sc_firehawk_rewards: pass, sc_flamefang_venom: pass, sc_foreign_arrivals: pass, sc_furnace: pass, sc_grass_regreens: unmeasured, sc_heat_dome: pass, sc_no_rain: pass, sc_populations: pass, sc_rite_hook_alone: pass, sc_ruins: pass, sc_sand_shovel: pass, sc_scorchfruit: pass, sc_three_skies: pass, sc_ullai: pass, sc_walk: unmeasured}
strange_open: 0
savegame: C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Saves\PYRELANDS_0.1.0_VISIT5_WALK_FULL.rws
exit_met: false
```
