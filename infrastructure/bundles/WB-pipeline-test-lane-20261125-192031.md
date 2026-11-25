# WB-pipeline-test-lane-20261125-192031: state

System: pipeline:test-lane. Host of this run: SteveDesktop (reaches Archmagi as `mandrake@archmagi-wsl`; live lines
take `host=archmagi`).

## Done

| member | outcome | commit |
|---|---|---|
| SELFTEST_NIGHTLY_SILENCE_KNOWN_REDS | closed: selftest_known_reds green again; live line moved to rm-metronome.timer host=archmagi (rm-ops-watch.timer is retired) | 48c6bd7ab1 |
| PREFLIGHT_BUILD_85_ROWS_OF_HINDSIGHT | dropped, not worth the touch: A2 needs a full-list load (retired) | - |
| STEWARD_FIX_ENDS_ON_GREEN_NOT_RUNNING | fixed, guard shown red, live reading owed | c87107226a |

## Learned

- testq-tick.service writes steward.json once, at its end. Ticks run 6-10 min on 2026-11-25 (longest 1386 s in 14
  days). The watcher allowed 5 min, so it raised STALE_HEARTBEAT on nearly every tick (735 lines in Archmagi
  steward.jsonl). Fix: `steward.tick_run_start()` excuses a running tick under TICK_HUNG_S.
- FlowWorks visit 12 is done, so CLEAN_NIGHTLY's two FlowWorks guards (settings_screens, static_game_state) are free.
- The fill.stop expiry finding on STEVE_LANE_MONITOR_PAUSE_FINDINGS is fixed (2620cfed58).

## Next, in order

1. Live reading of STEWARD_FIX on Archmagi (STALE_HEARTBEAT count stops growing once /home/mandrake/rm/dispatch has
   c87107226a); close with `--live "unit=testq-tick.timer reading=/mnt/d/ClaudeWork/rimmandrake/testq/steward.json max_age=1h host=archmagi"`.
2. STEVE_LANE_MONITOR_PAUSE_FINDINGS: REFUSED BY BUNDLE note (standing host by its title).
3. CLEAN_NIGHTLY: the two FlowWorks guards, second_game_mutants at low load, the 41-file acceptance.
4. KEY_TESTQ_SKIP_CACHE, PROBE_OFFLINE_MODEL, LIGHTSPEED_REPAIR_STUBS, PROVE_SCENE_RUNNER, BELT_WATER_HARNESS_1 (live).

## Context size after each group

- after steward group: 175874 of 1000000
