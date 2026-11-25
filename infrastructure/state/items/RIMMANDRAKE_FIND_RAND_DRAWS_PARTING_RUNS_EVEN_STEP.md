# RIMMANDRAKE_FIND_RAND_DRAWS_PARTING_RUNS_EVEN_STEP

Found by `RIMMANDRAKE_MEASURE_PLAY_AGAINST_PAUSED_STEP_NEVER_COMPARED` on 2026-11-24. The readings:
`design/specs/2026-11-23-bridge-v2/experiments/play_vs_step_rand_draws.md`.

## spec

- **The fault:** runs that start from one fixture save with one written-back random state do not repeat. In five runs of
  each arm (PLAY speed 1, speed 3, Ultrafast, STEP), 0 of 10 pairs of runs were equal, and the first difference was on
  tick 51 to 301 `[measured]`. `Verse.Rand` `seed` and `iterations` are equal at arm in every run. `iterations` parts
  between runs by tick 1 to 22, with a few more draws in one run (+6 by tick 1, +12 by tick 3) `[measured]`.
- **Find:** which code draws from `Verse.Rand` a different number of times from one run to the next. Two causes stay
  apart: a draw between ticks (frame work: UI, sound, visuals), and a draw inside a tick whose count depends on frame
  timing.
- **Experiment:** a counter on `Rand`'s draws (a Harmony postfix on the value getter, or the iteration count read at
  `TickPre` and `TickPost`) that records the caller and the phase (inside `DoSingleTick` or not), for one STEP run of
  `src/RimMandrake/Utils/scene_compare_plans/colony_drift_rand.py`. A new Harmony patch site joins
  `src/RimMandrake/bridgetools/HOOKS.md`.
- **What it decides:** whether a scene can get "the same moment again" from a save and a random state (for example
  with a tick-private random stream that the kernel saves and restores around each tick), and whether a faster arm can
  ever be shown equal to PLAY at speed 1.

## verify

Acceptance test: none offline. The oracle is live: three STEP runs of `colony_drift_rand.py` through
`python.exe src\RimMandrake\Utils\scene.py compare --plan src\RimMandrake\Utils\scene_compare_plans\colony_drift_rand.py --arms play1,step --n 3`
whose `static:Verse.Rand.iterations` tracks are equal on every tick, or the draws that differ named by caller and
phase. Seen red on 2026-11-24 (`play_vs_step_rand_result.md`: every run diverges on `iterations` by tick 22).

## criteria

- The draws that part the runs are named by caller and phase, with the run that shows them.
- A fix, if one is built, is shown both ways: the three STEP runs equal on `iterations` with it, and parted without it.
