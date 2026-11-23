# FlowWorks 0.1.0 — in-game acceptance, visit 8

Driver: detached helper, seat BENCH, item RIMMANDRAKE_DRIVE_FLOWWORKS_IN_GAME_ACCEPTANCE_VISIT_EIGHT, ArchBig on Archmagi.
Started 2026-11-23 2:28 AM PST (bound 5:28 AM).

Why this visit: `rerun_relation.py` reads 30 of 31 checks touched by the C# since their rows (stepped pit relief
52182cca96, floor depth ladder 5c870d5a36, and others).

Bridge released 04:53 PST. Continued by itself 04:58 PST (continuation 1): moat trace and six reruns, PIT_LOOK_1114_LIVE,
OL_OWNER_LOOK_READS and the big-pit screenshots, on ArchBig, same deployed build. See "Continuation 1" below.

## Build and lists

- ArchBig, RimWorld 1.6.4871 rev590. FlowWorks deployed in sync with the source (dry run "in sync (1079 files)"); the
  committed DLL matches its C# (`dll_source_stamp.py check`: MATCH) [measured]. No mod code changed in this visit.
- Lists: the 13-mod flowworks tier (modset_builder.py, all five DLC) for 28 checks; his full list (FULL.LATEST, 315 mods)
  for sc_walk. Every row carries `build_match.py identity`.

## Results: 28 PASS, 1 FAIL, 1 UNMEASURED of 30 [measured]

| check | verdict | runs | notes |
|---|---|---|---|
| 25 checks (fill, surface, toss, coating, geyser, trench, fetch, pit trap, hose, islands, pawn height, prison, source pays, the 8 extension chains, canal fire, hung bridge, ways out) | PASS | 1 | calm site verified on each |
| sc_garden | PASS | 2 | run 1 FAIL, class HARNESS (below); rerun PASS after fix 8380450 |
| sc_ice | PASS | 2 | run 1 UNMEASURED, class HARNESS (the same outside restore); rerun PASS |
| sc_walk | PASS | 1 | his full list, 196 s |
| sc_moat_raid | **FAIL** | 10 | 2 capture FAILs and 1 control FAIL (class MOD) in the first 3 counted runs, then 6 PASS in a row on the same build; not fixed, held by RIMMANDRAKE_HOLD_FLOWWORKS_PIT_PRISONERS_THREE_CAPTURE_FAULTS (below) |
| PIT_LOOK_1114_LIVE | PASS | 3 | evening_20261113 list, his sitting save; 19/19 rows, the same row set as visit 5; run 1 was the bridge client's lock refusal (HARNESS, no call made), run 2 lacked the site read |
| OL_OWNER_LOOK_READS | UNMEASURED | 1 | 1629 PASS, 0 FAIL, 1 BLOCKED, as visit 4; class HARNESS, unrepaired (below) |

### sc_garden: a pipeline defect, found and fixed in the sitting (HARNESS)

- GARDEN_filter_keeps_its_rate read 14 batches against a window of 32-33. The per-chunk log showed the filter at the base
  rate (one batch every 3 chunks) from chunk 7: the scene's converterRateMultiplier 4.1 had gone back to 1.
- A bare probe (`probe_conv_mult.py`, no scene) reproduced it: 4.1 for 7 chunks, then 1. Later probes kept 4.1 through
  30,000 ticks, so it was not the chunk size and not a fixed tick.
- `bridge_calls.jsonl` showed `wrapup.py` (not this run) writing that setting on port 5174 at 10:47:29Z and 10:54:53Z, and
  `D:\ClaudeWork\rimmandrake\wrapup\runs.jsonl` recorded restores of this run's own debts seconds after they were owed.
- The caller was caught live (`evidence/restore_caller_poll.log`): `./publish` tree checks running
  `selftest_conductor_acts.py`, whose `cli.py bridge release` on a throwaway ledger spawned the real
  `python.exe wrapup.py restore` against the real debt register and ArchBig.
- Fixes (RIMMANDRAKE_HOLD_WRAPUP_RESTORE_OFF_A_LIVE_OWNERS_DEBT, closed): 8380450 `wrapup.restore` leaves a debt whose
  owner process still runs (selftest_wrapup_restore R12, red on the parent); f459f47 a release on a throwaway ledger never
  replays the real register, and the conductor-acts selftest uses its own (selftest_wrapup_restore_at_release W7, red on
  the parent). Seen live after 8380450: outside restores at 11:17-11:24Z left this visit's debts "in flight".
- sc_ice run 1 (UNMEASURED: the ordered frozen cut never landed) ran while the same restore replayed its debts at 11:19:49Z;
  its rerun passed.

### sc_moat_raid: MOD, not fixed in the sitting

- Run 1 (03:45): MOAT_control_bridge_down_no_swim FAIL, 1 of 6 raiders swam with the leaf down.
- Run 2 (03:49): MOAT_two_held_and_captured FAIL, 2 held, 1 made prisoner in 900 ticks, 0 wardens downed.
- Run 3 (04:26): void (WSL interop fault, no game call).
- Run 4 (04:27): MOAT_two_held_and_captured FAIL, 3 held, 1 prisoner, 2 wardens downed.
- Continuation 1 (05:04-05:19 PST, the same deployed build 6b52871479): 6 PASS in a row, each with a per-poll trace of
  every unfinished capture's warden and captive (`moatCaptureTrace` in the evidence JSONs; the trace was a local harness
  edit, reverted before commit so no decider changed).
- So the build reads 2 capture FAILs and 1 control FAIL in 9 counted runs; visits 5-7 read 4 PASS in 4. That is no evidence
  of a new-build regression (0 of 4 at a ~22% rate is likely by chance) [guess ~75%]. The failures are the known capture
  faults of RIMMANDRAKE_HOLD_FLOWWORKS_PIT_PRISONERS_THREE_CAPTURE_FAULTS: a capture that stalls with its warden able
  (run 2), and wardens downed beside held raiders (run 4). The trace of run T050452 shows a held raider in AttackMelee at
  the lip during the capture window. Melee from the pit floor to the rim is current design
  (`RM_Patch_SuperdeepShooting.cs`: "denying it would be a change to melee, which ruling 23 does not authorise"), so the
  fix is a design call, not known in the sitting. The trace item was superseded into that item, with this evidence noted.
- The earlier MOD rows stand: the exit reader rightly refuses a later PASS that carries no mod fix. Bar moat_raid_sequence
  stays undecided.

### OL_OWNER_LOOK_READS: UNMEASURED, HARNESS, unrepaired

- Big pit staged on the calm site (evening_20261113 list): plan, stage (186 s), fill, verify 253 PASS + 1 UNMEASURED (the
  known label reader row). OL with --acts: 1629 PASS, 0 FAIL, 0 UNMEASURED, 1 BLOCKED (OL_no_surface_shadow_under_sheet).
- The blind row needs a shadow draw-queue field in the mod's C# proof reader; a check repair may not touch the mod. Its
  item, RIMMANDRAKE_REPORT_SUBMERGE_SHADOW_QUEUE_JUDGE_CANNOT_SEE_ORDER, was dropped 2026-11-23 as not worth the touch.
  OL decides no bar. For the Conductor: fund the reader, or rule the blind row out of OL.

## Owed cases

- Road back: sc_walk, sc_fill_front, sc_fill_tiers, sc_garden, sc_hose_look, sc_pit_trap_raid, sc_source_pays,
  sc_trench_cover, sc_fetch_fallen, sc_geyser_tub, sc_ice, sc_hole_prison, sc_ways_out, sc_covered_pit, sc_hung_bridge:
  each PASS on this build. sc_hole_prison and sc_hung_bridge ran once here, not three times in a row.
- Road back on PIT_LOOK_1114_LIVE: PASS (pour labels 100, 1000 and 2048000 read). On OL_OWNER_LOOK_READS: run, UNMEASURED
  (one BLOCKED row, above); the big-pit stage-reset row is absent and the spare pit is planned and dug (verify 253 PASS).
- Blind cycle 4: sc_garden PASS on this build (the four Problems' scene). No planted fault ran this visit; visits 3 and
  4's readings stand.

## Beyond the checks

Continuation 1 took the big-pit captures (overview and the seven copies, dry to brim and 1.5 m tar) and looked at them.
Small copies in `screenshots/` (under 1 MB each); full size in `D:\ClaudeWork\rimmandrake\flowworks_visit8_shots\`.
Three strange things, all in `strange.jsonl`: the mid-run setting reset (filed, fixed), the interop fault (explained), and
corpse wound overlays drawn on top of opaque tar (filed, RIMMANDRAKE_CUT_FLOWWORKS_CORPSE_WOUNDS_FLOAT_ON_TAR).

## The savegame

No new savegame. The walk save stays visit 4's, as in visits 5 to 7. It loads with today's deployed build, so the
looks are today's, but its staged scenes were not re-checked on this build:
`C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Saves\FLOWWORKS_OWNER_REVIEW_VISIT4_FULL_20261121_1727.rws`

## Items filed

RIMMANDRAKE_HOLD_WRAPUP_RESTORE_OFF_A_LIVE_OWNERS_DEBT (pipeline, fixed and closed, 8380450 and f459f47);
RIMMANDRAKE_TRACE_FLOWWORKS_MOAT_CAPTURE_FAILS_TWO_IN_THREE_ON_NEW_BUILD (superseded into
RIMMANDRAKE_HOLD_FLOWWORKS_PIT_PRISONERS_THREE_CAPTURE_FAULTS); RIMMANDRAKE_CUT_FLOWWORKS_CORPSE_WOUNDS_FLOAT_ON_TAR (MOD, open).

## Exit
```
ingame_rows: {sc_dig_and_read: pass, sc_dig_finds: pass, sc_fill_front: pass, sc_fill_tiers: pass, sc_one_surface: pass, sc_source_pays: pass, sc_canal_fire: pass, sc_slime: pass, sc_pawn_height: pass, sc_pit_reads: pass, sc_covered_pit: pass, sc_ways_out: pass, sc_sluice: pass, sc_hose_look: pass, sc_one_network: pass, sc_trench_cover: pass, sc_hung_bridge: pass, sc_ice: pass, sc_moat_raid: fail, sc_hole_prison: pass, sc_toss_flame: pass, sc_fetch_fallen: pass, sc_islands: pass, sc_walk: pass, sc_pit_trap_raid: pass, sc_garden: pass, OL_OWNER_LOOK_READS: unmeasured, sc_geyser_tub: pass, sc_coating_wash: pass, PIT_LOOK_1114_LIVE: pass}
strange_open: 0
savegame: C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Saves\FLOWWORKS_OWNER_REVIEW_VISIT4_FULL_20261121_1727.rws
exit_met: false
```
