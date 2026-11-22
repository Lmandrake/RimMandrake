# Pyrelands 0.1.0: in-game acceptance, visit 5 (Archmagi, ArchBig, started 2026-11-22 04:13 PST)

Detached BENCH helper, item RIMMANDRAKE_DRIVE_PYRELANDS_IN_GAME_VISIT_FIVE_RUN_TWO. Game ArchBig (Steam's install).
33 of 38 checks touched since visit 4 (`rerun_relation.py --mod Pyrelands`, list in `scripts/touched.txt`); 5 keep their PASS.
Mod changes since visit 4's build ca2accf045: e63595716c (ember grass x1 on dry ash), 66ae940372 (venom fixtures fed),
3acf1ad82b (sprayer carrier foams its path), plus visit-4 harness repairs.

## Progress

- 04:13 precondition `in_game 0.1.0`; item claimed; skeleton written (b4ece5f613).
- 04:20 bridge ArchBig taken by BENCH. Deploy dry runs: composed biomes, UtinniPatches, FlowWorks, LuminousPigment, MandrakePatches, WeatherSuite, SWBestiary all in sync with ArchBig's Mods (nothing to apply). Companion BridgeTools --gm deployed to ArchBig (readback sha256 baa4faefb480064b). Tier pyrelands applied (17 mods, 5 DLC; his 315-mod list backed up by modset_builder). ArchBig launching.
- 04:22 ArchBig started directly (Steam answered WaitingPrevProcess beside ArchSmall), bridge after 119 s. Gate A refused once on 3.8.12 loadavg 10.25 (transient); rerun CLEAN (12 rows), def fingerprint 417df172fdb5e402.
- 04:33 site NS_Pyrelands_site_1_417df172fdb5_visit5 built (tile 1496, map 1); gate B CLEAN (5 rows). Identity: mod_sha e63595716c, game 1.6.4871 rev590, tier pyrelands (17), mod_hash sha256:9c2c8828... (`evidence/identity_pyrelands.json`).
- 04:35 batch 1 started (`scripts/runner.sh b1`, site reloaded before every chain): 26 shorter chains.

## Exit

```
ingame_rows: {}
strange_open: 0
savegame: (not yet written)
exit_met: false
```
