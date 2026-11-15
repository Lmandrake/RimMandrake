# Pyrelands 0.1.0 — in-game acceptance, visit 1

Started 2026-11-15 02:55 PST by a detached BENCH helper (item RIMMANDRAKE_ACCEPT_PYRELANDS_IN_GAME_RAIN_FIX_NEVER_RUN).

## Progress
- 02:55 bridge taken; skeleton written. Game was already up.
- 03:05 game closed; composed biomes + UtinniPatches + SWBestiary deployed (FireEcologyHook.dll sha256 be276fb1 in game == repo); tier `pyrelands` (17 mods, 5 DLC) applied; launched (bridge in 103 s).
- 03:15 site NS_Pyrelands_site_1_090cd707f5_visit1 built (tile 178, map 1); gate B CLEAN (5 rows).
- 03:18 batch a: 7 PASS; `ruins` FAIL -> judged a stale check (ruin floors are charred by design, CharFloor); screenshot shows the dark charred flagstone.
- 03:22 batch b: ash_fertility_watered PASS, fire_tick_effects PASS, ullai_wired + giant PASS; herd row FAIL (20% < 30%); scorchfruit_fire_born UNMEASURED (needs plant_census in the same run).
- 03:30 herd diagnosed live: direction right (A, never B); pace ~19 cells/1000 ticks, RM_ShadeDash (noon Direct Sun) preempts 2 of 10, 1 has no reachable cell; over 12,500 ticks the centroid closed 66%.
- 03:30 flamefang_venom: victim fled unbitten (HARNESS) -> drafted + latch narrowed, PASS (db9b7d66).
- 03:40 weather chains + furnace_sleep PASS; three-skies clauses read by hand: black rain does NOT put fires out (filed).
- 03:50 fresh reload: plant_census, scorchfruit_fire_born, burn_line PASS; opening_front old-save row misreads a new fixture (filed); anchorless herd shown live (anchor invalid, goAsh 8/8, none near fire).
- 04:00 embergrass regrow PASS on the real clock (33.6% day 3, 69.5% day 7) via a resumable replica; scorchfruit produces/spoils PASS; firefoam aim + gate proofs PASS.
- 04:10 Saves backed up (D:\ClaudeWork\backups\rimworld_saves_pre_pyre_visit1_20261115, 408 files); walk save written and every station looked at; 6 items filed (findings.md).
- 04:25 rain postfix shown live (forced ordinary rain -> black rain). Owed still: sc_rite_hook_alone (list without pyrelandsmechanics), sc_walk (full list).

## Exit
```
ingame_rows: {}
strange_open: 0
savegame: none
exit_met: false
```
