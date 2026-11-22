# Pyrelands 0.1.0: in-game acceptance, visit 5 (Archmagi, ArchBig, started 2026-11-22 04:13 PST)

Detached BENCH helper, item RIMMANDRAKE_DRIVE_PYRELANDS_IN_GAME_VISIT_FIVE_RUN_TWO. Game ArchBig (Steam's install).
33 of 38 checks touched since visit 4 (`rerun_relation.py --mod Pyrelands`, list in `scripts/touched.txt`); 5 keep their PASS.
Mod changes since visit 4's build ca2accf045: e63595716c (ember grass x1 on dry ash), 66ae940372 (venom fixtures fed),
3acf1ad82b (sprayer carrier foams its path), plus visit-4 harness repairs.

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

## Exit

```
ingame_rows: {}
strange_open: 0
savegame: (not yet written)
exit_met: false
```
