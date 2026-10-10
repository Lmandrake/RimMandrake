# FOUNDRY HugeFootprints fix prove 2026-10-10

## Progress
- 15:04 start; bridge taken
- 15:04 claimed both items; evidence archived to D:\Luke\dev\_rmscratch\player_log_archiveulllist_550_20261010 (Player.log pid27132 988 KB, Player-prev pid1568, 34 tps + 6 health jsonl, ModsConfig)
- 15:05 BEFORE measurement on old DLL (pid 27132) running: Transient/foundry_hugefix_measure_20261010.py before
- 15:09 BEFORE (old DLL, live map): HugeFootprints 62.6 ms/tick (map_comp_timing, max 516 ms); TPS 13.3/12.4/12.3 at Normal/Fast/Superfast; GC ~11/min; gapMax 553-589 ms; private 29.6 GB; giants 2744, blockers 7365->7447. Saved map as Saves\HUGEFIX_ROT_AB_20261010.rws (new file, nothing else changed) for like-for-like after. Added DebugCounts probe; building.
- 15:15 preflight offline: only HugeThings DLL differs (plus waived game-only leftovers FlowWorks/WreckedMachines, RealFoW, tormentmaster, 38 absent, O14 failed_ops); archive verified; killing pid 27132
- 15:16 deployed HugeThings (46c194cac: f3774dd15 fix + DebugCounts) and companion 1e7fc0876b7c (gm; includes meter fix fb4735735 = d0c8ace23 rebased); profile test valid to 2026-10-11T12Z; ModsConfig 550; launching
- 15:16 launch_ready --profile full started; RimWorldWin64 pid 39048
- 15:17 loading (watchdog ok)
- 15:22 loading, log 111 KB, 0 exceptions, ws 3.7 GB
- 15:27 defs phase, log 150 KB, 2 exceptions (expected Worldbuilder ConfigErrors)
- 15:32 post-defs, log 457 KB, 5 exceptions
- 15:34 READY pid 39048, 550 mods, 1100 s; receipt D:\Luke\dev\_rmscratch\launch_receipts\launch_20261010T153436.json; first exception Worldbuilder ConfigErrors (donor, same as before); HAR brtrue NULL also present in prior log. Loading HUGEFIX_ROT_AB_20261010
- 15:35 save loaded (tick 5803, compatible 550/550). DebugCounts: giants=2739 realized=7447 pending=1248 dirty=0 (= save-time list_things: giants 2739, blockers 7447). PAWN_ORIGIN A5: 20/20 pawns 'origin unknown', ourInvolvement unknown, 0 PRE_LOAD claims, epoch 1. Running AFTER measurement.
- 15:39 AFTER: HugeFootprints 0.98 ms/tick (max 11.5) vs 62.6; TPS 48.2/141.9/145.0 (Normal/Fast/Superfast) vs 13.3/12.4/12.3; GC 1.5/min vs ~11; private 29.1 GB vs 29.6; giants 2739 unchanged; blockers 7447->8135 and pending 1248->1368 over ~15k ticks (growth; old code grew at the same ~0.05/tick). Normal ratio 0.87 is eaten by two one-off gameComp stalls (tg 5821 2.9 s just after load, tg 7501 6.8 s) - not HugeFootprints. Re-measuring Normal steady state + footprint spot-check.
- 15:41 clean 60 s Normal: 57.8 TPS ratio 0.963, gapMax 359 ms, 1 GC, top tl:Normal every window (mapComp gone). Spot-check 6 giants (GiantAgarilux/WitchesOyster/PaleTree): 5-34 blockers in a 9x9 around each; DebugCounts giants=2738 realized=8141 pending=1370. Evidence Transient/foundry_hugefix_check_20261010.json
- 15:42 awareness: INCIDENT A3 PASS (ShortCircuit + AnimalInsanityMass forced: returned false, no 'fired' wording), A4 PASS (queued ResourcePodCrash fired at tick 31457 by the queue, chain bridge:jawa/incident_schedule > incident:ResourcePodCrash); PAWN_ORIGIN A5 PASS (20/20 origin unknown after load, 0 PRE_LOAD), A6 PASS (meters per aware.* copied into game_health_record.md); VISITOR A2 NOT proven (3/3 spawns delivered the requested kind: no substitution occurred to detect).
- 16:13 preflight --live (--accept-deps): all PASS except O04/L04 tormentmaster (waived) -> Transient/foundry_hugefix_preflight_live_20261010.txt. Closed HUGE_FOOTPRINTS_FIX_PROVE_SIXTY_ON_ROT + AWARENESS_METERS_DEPLOY_HOOK_BODY_ONLY at 5af889844; INCIDENT_JOURNAL auto-closed (A3+A4). Filed GAMECOMP_STALL_HUNT_SEVEN_SECONDS. Bridge released; game left UP (pid 39048, 550 list, HUGEFIX_ROT_AB_20261010 loaded, paused).

## Result
| | before (old DLL) | after (f3774dd15) |
|---|---|---|
| HugeFootprints ms/tick (map_comp_timing, 300 ticks) | 62.6 (max 516) | 0.98 (max 11.5) |
| TPS Normal / Fast / Superfast (45 s blocks) | 13.3 / 12.4 / 12.3 | 48.2* / 141.9 / 145.0 |
| clean 60 s Normal | - | 57.8 TPS, ratio 0.963, top tl:Normal |
| GC / min | ~11 | ~1.5 |
| worst frame gap | 553-589 ms | 359-372 ms steady; one-off gameComp stalls 2.9 s + 6.8 s (*ate the 45 s Normal block) |
| private / WS | 29.6 / 17.6 GB | 29.1 / 17.8 GB (unchanged) |
Same save both sides. Giants 2739 = save; blockers 7447 = save at load; growth to 8141 + pending 1248->1370 is maturing giants (old code grew at the same ~0.05 blockers/tick). Blockers Impassable live; spot-check of 6 giants all carry blockers.
Owed: VISITOR A2 (no substitution occurred), A4; PAWN_ORIGIN A2 (fresh map + early generation), A4; GAMECOMP_STALL_HUNT_SEVEN_SECONDS; memory 29 GB private is not this.
