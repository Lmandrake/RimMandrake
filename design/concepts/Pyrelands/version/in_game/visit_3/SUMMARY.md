# Pyrelands 0.1.0: in-game acceptance, visit 3 (Archmagi, game b, started 2026-11-21 08:33 PST)

Detached BENCH helper, item RIMMANDRAKE_DRIVE_PYRELANDS_IN_GAME_ACCEPTANCE_VISIT_THREE. In progress.

## Progress
- 08:33 synced (2c09917fc), precondition `in_game 0.1.0`, bridge archmagi.b taken (BENCH). Game b running (pid 7416). Skeleton written.
- 08:37 game b stopped; composed biomes deployed --prune (9 files; 9 orphan ash textures in game b's copy removed), UtinniPatches (2 files), BridgeTools --gm; the other tier mods in sync. Stale BENCH.b swap marker (flowworks, 2026-11-20) moved to D:\ClaudeWork\backups\pv3_swapmarker; tier pyrelands applied (17 mods, 5 DLC). Game b launched (bridge 126 s).
- 08:53 gate A refused: game a's dead FlowWorks call (unknown outcome, endpoint 5174) refused every game-b mutation. Pipeline defect RIMMANDRAKE_SCOPE_BRIDGE_MARKER_TO_ITS_GAME_A_STOPS_B filed, fixed, closed (19e7615934; selftest_bridge_reconcile_read 83/83, red on parent 81/83).
- 09:05 gate A HARNESS repairs (6ea9314ad1): 3.8.4 stamp ABSENT under python.exe (Windows git refuses the WSL clone) now read under WSL; 3.3 an empty-string default the bridge omits. Before: `evidence/gateA_before_repair.log` (3.8.4 FAIL, 3.3 UNMEASURED); after: GATE A CLEAN (12 rows), def fingerprint 417df172fdb5e402.
- 09:10 site NS_Pyrelands_site_1_417df172fdb5_visit3 built (tile 63294, map 1); gate B CLEAN (5 rows). Identity: mod_sha 6ea9314ad1, game 1.6.4871 rev590, tier pyrelands (17).
- 09:14 runner (`scripts/runner.sh`, site reloaded before every chain) batch 1 started: startup, mapgen_log, animal_census, grass_cover, ambient_ash_drift, plant_census, ruins.

## Exit

```
ingame_rows: {}
strange_open: 0
savegame: UNMEASURED
exit_met: false
```
