# Pyrelands 0.1.0: in-game acceptance, visit 6 (Archmagi, ArchSmall)

Detached BENCH helper, item RIMMANDRAKE_DRIVE_PYRELANDS_IN_GAME_VISIT_SIX_RUN_TWO. Started 2026-11-22 21:46 PST.

## Progress

- 21:46 skeleton written; ArchSmall bridge taken (gen 39). 

- 22:08 every tier mod in sync on ArchSmall (biomes 4750 files, UtinniPatches, MandrakePatches, WeatherSuite, SWBestiary, FlowWorks, LuminousPigment); companion source unchanged since the deployed 3a0b257fcf52, not redeployed. A stale BENCH.b swap marker (2026-11-21) refused the swap: the live 23-mod list backed up to `evidence/ModsConfig.ArchSmall.before_visit6.xml`, marker removed, tier pyrelands (17 mods) applied, ArchSmall relaunched. Gate A CLEAN (fp 417df172fdb5e402), site 1 built (tile 38, `NS_Pyrelands_site_1_417df172fdb5_visit6`), gate B CLEAN. Main batch of 29 chains started (`scripts/runner.sh`, `evidence/runner.log`).

- 22:46 24 chains read: 22 all PASS. SITE: scorchfruit_off_burn_bears_none (pad on marble mountain) and both firefoam rows (pad on an ancient shrine): the fixed pads misfit tile 38; repair 4f68a44fbf (`_open_ground`, plant PYRE_PLANT_OFFBURN_TOGGLE_IGNORED), reruns owed after the batch. Pipeline defect: suite.screenshot filed a desktop grab for every frame too big for the screen; filed RIMMANDRAKE_FIT_SUITE_WIDE_RECT_SHOTS_NOT_A_DESKTOP_GRAB, fixed 499c059923 (selftest 5 FAIL on the base, 0 on the fix).

## Exit
```
ingame_rows: {}
strange_open: 0
savegame: none yet
exit_met: false
```
