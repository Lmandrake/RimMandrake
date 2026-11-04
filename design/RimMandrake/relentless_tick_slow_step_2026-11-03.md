# The slow step in a Relentless tick (RELENTLESS_TICK_TUNE_FIFTEEN_MINUTE_NAPS, 2026-11-03)

**The slow step was one deploy plan inside the tick.** It was not the clones and not the memory peak.

A 1 Hz sample of a running tick's process tree gave 433 samples:

| child process | samples |
|---|---|
| `deploy_custom_mods.py --compose biomes --with ...` | 257 (59%) |
| the tick's own Python, no child running | 60 |
| `scratch_clone.py clone` | 27 |
| `tasklist.exe` | 26 |
| `powershell.exe` | 22 |

The plan comes from `relentless_live_round._plan_into`, called by `game_mod_gap` and `game_batch_gap`. It compares every
byte over the Windows mount and runs the def guard, but a gap reads only the mod headers and DLL drift. Plans with
different arguments each cost the full time, which is how ticks reached the unit's 20 minute kill on 2026-11-03.

## What changed

- `deploy_custom_mods.py --gate` reads headers and compares `*.dll` only, with no def guard. On the real
  `--compose biomes --with SWBestiary --with Shokk --with UtinniPatches` it took 35 s, against about 260 s for the full
  plan. `_plan_into` uses it, with `live.gate_plan_max_s` 180 as its timeout.
- `relentless_live.run` still gates on the full plan, so any other drifting file is caught before a proof runs.
- `game_reading` serves one reading for 30 s, because each read is tasklist, netstat and powershell.
- `tick_game_budget_s` went from 420 to 240.
- `staffing.json` and `reading.json` carry their write time. The staffing arithmetic and the journal row's `at` stay on
  the tick's start.
- The tick's journal row now has whole-tick `wall_s`, `phases`, and `slow_steps` (any item's step of 20 s or more), so the
  next slow tick names its own step.
- `relentless.tick_age_s` is back to 10 min.

## Measured after

The first three ticks on the new code had `wall_s` of 61, 173 and 135. The last of these included two `game_mod_gap` acts.
The same day's ticks before the change ran 3-8 min. Three ticks are a small sample, and none of the three is known to have
run a plan with new arguments on a busy mount, so `phases` and `slow_steps` are the thing to read if the alarm returns.
