# ExplosiveKnockback 0.1.0 — in-game acceptance, visit 5

Detached helper, seat BENCH, item RIMMANDRAKE_DRIVE_EXPLOSIVEKNOCKBACK_IN_GAME_VISIT_FIVE, run-1795478277, started 2026-11-23 16:08 PST on ArchBig.

## Progress
- 16:10 bridge taken; proof build, tier explosiveknockback_visit first, then one full-list load.
- 16:20 tier list: sc_spared, sc_frame_probe_check, sc_all_fly_no_cap, map_agreement (115 of 115), live_pipe_pole_menu PASS. Full list loading.
- 16:53 full list (314 mods): sc_barrage_perf PASS (run 1 spoiled by a vanilla Ancient danger letter), sc_walk_raid 18 of 18 PASS after the reload wait repair (run 2 UNMEASURED).
- 17:35 walk save EK_VISIT5_WALK_20261123_CLEAR written; plant (goods lost on reload) loading on the full list.

## Result
4 of 4 checks PASS [measured, last rows], ArchBig, RimWorld 1.6.4871. Proof DLL md5 102bdddb, mod_hash 673b9d80, src_id 51f9663608541267, source 8053792541. Tier rows: explosiveknockback_visit (23 mods). Full rows: 314 mods (koth.isid is listed, not installed).
- sc_spared PASS, sc_frame_probe_check PASS.
- sc_barrage_perf PASS: p99 22.1 ms in the window, limit 50, mod off 21.7. Run 1 was an ENVIRONMENT FAULT: a vanilla "Ancient danger" letter paused the game at 8.95 s (its window p99 was 25.0). The colonists were drafted for run 2.
- sc_walk_raid PASS, 18 of 18 rows. Run 1 COULD NOT LOOK (save refused: two recorded mods are no longer installed; loaded with --ignore-missing-mods after). Run 2 APPARATUS FAULT: arm B ended one tick past its target.

## Check repaired (HARNESS, fa3f95313d)
The reload arm now waits until the load's own PauseOnLoad tick is done. This line came back (visit 4: 9 ticks short). My earlier repair only added a step when the clock was short, so it could not fix a tick over. The cause is the tick landing after the game reads Playing. Offline W40 red then green. Live: planted goods-lost-on-reload FAIL (evidence/sc_walk_raid_plant.txt, full list, same save), real build PASS.

## The owed cases
- RIMMANDRAKE_MOVE_KNOCKBACK_GOODS_PINNED_AGAINST_WALLS_SHELVES: sc_all_fly_no_cap PASS (no scene stages the tumble itself); map_agreement 115 of 115 on the map model.
- Planted faults: not run again, the mod's code did not change. Seen by in-game checks in visit 4 (planted_rows.jsonl): SHIELD_NEVER, PIT_NEVER_READ (again this day), HEAVY_KNOCK_OFF, FIRE_SWITCH_IGNORED (sc_settings_sweep only), PAWN_LANDING_KEEPS_COVER, GOODS_LANDING_KEEPS_COVER, PAWN_ON_COVER_IGNORED. Not seen by any in-game check: PROOF_RESET_NOOP, PROOF_WALL_SCENE_DROPPED, PAWN_LANDING_NOT_STANDABLE; MAPAGREE_ALWAYS_OK and SAVELOAD_ALWAYS_OK read only (they are the instruments themselves).
- L1_GAS_SHOVE_PAWN_ON_INTACT_COVER and L1_FIRE_SWITCH_ON_UNPATCHED_FIRE_TYPE: no check stages them; Polish, as cycle 6 says. L1_NOT_KERNEL_GAME_SIDE: settled, its named scenes and the raid walk pass.
- unrun.jsonl: sc_walk_raid, sc_barrage_perf, map_agreement (115 of 115, small list; not the full list) and live_pipe_pole_menu PASS this visit; the other seven passed in visit 4 and keep that PASS.

## What was thin, and what went wrong
- Looking: 16 stations captured on one sheet plus station 13 again; no exploring beyond them. Fog hid station 13; the CLEAR save fixes it.
- Pipeline defect fixed: RIMMANDRAKE_KEEP_FULL_LIST_ROWS_WHEN_ONLY_TEST_SCRIPTS_MOVED (a test-script repair voided the barrage row that never reads it).
- Two full-list loads (one only for the plant: my list swap was refused because the game had not exited, and one force stop).
- Saves backup is partial: 430 files copied before the 5-minute limit, of 682 saves; save_keeper reported nothing changed.

## After the exit: the gas-corner fix (db80fab783, 2026-11-23 19:20 PST)
The mod's code changed. Build match: 54 of 56 count (rerun on ArchSmall, all PASS); sc_barrage_perf and sc_walk_raid are owed on ArchBig (RIMMANDRAKE_RUN_KNOCKBACK_FULL_LIST_CHECKS_AFTER_GAS_CORNER_FIX). Record: `gas_corner_fix/README.md`. The Exit block below is visit 5's, on 2993ae853e.

## Exit
```
ingame_rows: {sc_spared: pass, sc_frame_probe_check: pass, sc_barrage_perf: pass, sc_walk_raid: pass, sc_all_fly_no_cap: pass}
strange_open: 0
savegame: C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Saves\EK_VISIT5_WALK_20261123_CLEAR.rws
exit_met: true
```
