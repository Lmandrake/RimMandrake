# FlowWorks 0.1.0 — in-game acceptance, visit 8

Driver: detached helper, seat BENCH, item RIMMANDRAKE_DRIVE_FLOWWORKS_IN_GAME_ACCEPTANCE_VISIT_EIGHT, ArchBig on Archmagi.
Started 2026-11-23 2:28 AM PST (bound 5:28 AM).

Why this visit: `rerun_relation.py` reads 30 of 31 checks touched by the C# since their rows (stepped pit relief
52182cca96, floor depth ladder 5c870d5a36, and others).

Bridge released 04:53 PST; ArchBig left running on his full list at the sc_walk map (healthy).

## Build and lists

- ArchBig, RimWorld 1.6.4871 rev590. FlowWorks deployed in sync with the source (dry run "in sync (1079 files)"); the
  committed DLL matches its C# (`dll_source_stamp.py check`: MATCH) [measured]. No mod code changed in this visit.
- Lists: the 13-mod flowworks tier (modset_builder.py, all five DLC) for 28 checks; his full list (FULL.LATEST, 315 mods)
  for sc_walk. Every row carries `build_match.py identity`.

## Results: 27 PASS, 1 FAIL, 2 not run of 30, last row each [measured]

| check | verdict | runs | notes |
|---|---|---|---|
| 25 checks (fill, surface, toss, coating, geyser, trench, fetch, pit trap, hose, islands, pawn height, prison, source pays, the 8 extension chains, canal fire, hung bridge, ways out) | PASS | 1 | calm site verified on each |
| sc_garden | PASS | 2 | run 1 FAIL, class HARNESS (below); rerun PASS after fix 8380450 |
| sc_ice | PASS | 2 | run 1 UNMEASURED, class HARNESS (the same outside restore); rerun PASS |
| sc_walk | PASS | 1 | his full list, 196 s |
| sc_moat_raid | **FAIL** | 4 | class MOD, not fixed: filed RIMMANDRAKE_TRACE_FLOWWORKS_MOAT_CAPTURE_FAILS_TWO_IN_THREE_ON_NEW_BUILD (below) |
| PIT_LOOK_1114_LIVE, OL_OWNER_LOOK_READS | not run | 0 | out of time (the bound); neither decides a bar; owed in the LEFT OPEN note |

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
- These rows passed in visits 5, 6 and 7. 15 C# commits landed since, among them 5d9004b9ce (stranded colonist rescue) and
  ba94149031 (pawns walk under pit covers): candidates, not traced. Not fixed: the cause is not known and the bound did not
  allow a capture-stage probe. Filed with its acceptance test (three PASS runs in a row). Bar moat_raid_sequence stays undecided.

## Owed cases

- Road back: sc_walk, sc_fill_front, sc_fill_tiers, sc_garden, sc_hose_look, sc_pit_trap_raid, sc_source_pays,
  sc_trench_cover, sc_fetch_fallen, sc_geyser_tub, sc_ice, sc_hole_prison, sc_ways_out, sc_covered_pit, sc_hung_bridge:
  each PASS on this build. sc_hole_prison and sc_hung_bridge ran once here, not three times in a row.
- Road back on OL_OWNER_LOOK_READS and PIT_LOOK_1114_LIVE: not run (time).
- Blind cycle 4: sc_garden PASS on this build (the four Problems' scene). No planted fault ran this visit; visits 3 and
  4's readings stand.

## Beyond the checks

No screenshots and no exploration this visit: the bound went to the garden diagnosis and the pipeline fix. Owed.
Two strange things, both in `strange.jsonl`: the mid-run setting reset (filed, fixed) and the interop fault (explained).

## The savegame

No new savegame. The walk save stays visit 4's, as in visits 5 to 7. It loads with today's deployed build, so the
looks are today's, but its staged scenes were not re-checked on this build:
`C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Saves\FLOWWORKS_OWNER_REVIEW_VISIT4_FULL_20261121_1727.rws`

## Items filed

RIMMANDRAKE_HOLD_WRAPUP_RESTORE_OFF_A_LIVE_OWNERS_DEBT (pipeline, fixed and closed, 8380450 and f459f47);
RIMMANDRAKE_TRACE_FLOWWORKS_MOAT_CAPTURE_FAILS_TWO_IN_THREE_ON_NEW_BUILD (MOD, open).

## Exit
```
ingame_rows: {sc_dig_and_read: pass, sc_dig_finds: pass, sc_fill_front: pass, sc_fill_tiers: pass, sc_one_surface: pass, sc_source_pays: pass, sc_canal_fire: pass, sc_slime: pass, sc_pawn_height: pass, sc_pit_reads: pass, sc_covered_pit: pass, sc_ways_out: pass, sc_sluice: pass, sc_hose_look: pass, sc_one_network: pass, sc_trench_cover: pass, sc_hung_bridge: pass, sc_ice: pass, sc_moat_raid: fail, sc_hole_prison: pass, sc_toss_flame: pass, sc_fetch_fallen: pass, sc_islands: pass, sc_walk: pass, sc_pit_trap_raid: pass, sc_garden: pass, OL_OWNER_LOOK_READS: unmeasured, sc_geyser_tub: pass, sc_coating_wash: pass, PIT_LOOK_1114_LIVE: unmeasured}
strange_open: 0
savegame: C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Saves\FLOWWORKS_OWNER_REVIEW_VISIT4_FULL_20261121_1727.rws
exit_met: false
```
