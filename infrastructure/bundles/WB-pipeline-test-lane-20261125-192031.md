# WB-pipeline-test-lane-20261125-192031: state (bundle ended 2026-11-25 ~20:05Z)

System: pipeline:test-lane. Host of this run: SteveDesktop (reaches Archmagi as `mandrake@archmagi-wsl`; live lines
take `host=archmagi`).

## Members

| member | outcome | commit | live reading |
|---|---|---|---|
| STEWARD_FIX_ENDS_ON_GREEN_NOT_RUNNING | closed, guard shown red | c87107226a | Archmagi: STALE_HEARTBEAT held at 736, 19:41Z-20:00Z |
| SELFTEST_NIGHTLY_SILENCE_KNOWN_REDS | closed; live line moved to rm-metronome.timer host=archmagi | 48c6bd7ab1 | promise checked at close |
| RIMMANDRAKE_PROBE_OFFLINE_MODEL_LINKING_REAL_GAME_CODE | closed, remainder RIMMANDRAKE_REPLAY_ENUMERATED_SITUATIONS_IN_HEADLESS_REAL_GAME | 3746bf74d9 | offline probe, 18 runs 5 throws |
| PREFLIGHT_BUILD_85_ROWS_OF_HINDSIGHT | dropped: needs a full-list load (retired) | - | - |
| BELT_WATER_HARNESS_1 | dropped: Miasma and Greentide not advancing | - | - |
| LIGHTSPEED_REPAIR_STUBS_TOOLS_EXIST_NOW | dropped: retired-era census | - | - |
| STEVE_LANE_MONITOR_PAUSE_FINDINGS | REFUSED BY BUNDLE: standing host by its title | - | - |
| RIMMANDRAKE_KEY_TESTQ_SKIP_CACHE_ON_INPUTS | REFUSED BY BUNDLE: design call on known_results' clock rule | - | nightly 0/107 answered |
| RIMMANDRAKE_CLEAN_NIGHTLY_SWEEP_ONCE_THEN_RED_RINGS | wait 2026-11-26: FlowWorks files held by the visit 13 routing run | - | - |
| RIMMANDRAKE_PROVE_SCENE_RUNNER_LIVE_SAME_ROWS_FEWER_CALLS | wait 2026-11-26: EK held by RIMMANDRAKE_BRUISE_KNOCKBACK_LANDING_ON_PAWN | - | UNRUN |

Fixed with no ticket: STEVE_LANE_UNSTICK_STALLED_UNOWNED_STALEHEARTBEAT_CDHWKZ dropped (a false alarm of the same cause).

## Learned

- testq-tick.service writes steward.json once, at its end; ticks run 6-10 min (longest 1386 s in 14 days).
- `rimflow file --not-now files-held:` reads only this machine's live runs, so a SteveDesktop helper cannot name an
  Archmagi run (polish, not filed).
- A `--publish` write can land on origin/main and leave its lines as a working-tree diff (lesson filed).

## Context size after each group

- after the steward group: 175874 of 1000000
- at the end: about 270000 of 1000000
