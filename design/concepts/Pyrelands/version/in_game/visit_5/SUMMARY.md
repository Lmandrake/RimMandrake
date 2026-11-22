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

## Exit

```
ingame_rows: {}
strange_open: 0
savegame: (not yet written)
exit_met: false
```
