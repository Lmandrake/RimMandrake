# BOUNDARY: PLAY against STEP (`scene.py compare`), Design Version 0.1.0

Code: `src/RimMandrake/Utils/scene_compare.py`. Item `RIMMANDRAKE_MEASURE_PLAY_AGAINST_PAUSED_STEP_NEVER_COMPARED`. Each promise has a
check of its name in `src/RimMandrake/Utils/selftest_scene_compare.py`. The live run: `python.exe src\RimMandrake\Utils\scene.py compare
--plan <plan.py> --arms play1,play3,ultra,step --n 5`, which writes `design/specs/2026-11-23-bridge-v2/experiments/play_vs_step_result.md` and
`design/specs/2026-11-23-bridge-v2/experiments/play_vs_step_comparisons.json`.

One plan (a Python file with `SAVE`, `LIMIT` and `plan(c)`), one fixture save loaded fresh for every run. A first run of the
reference records the random state at arm; it is not a sample. Every later run writes that state back (`jawa/run_until`
`randState`). Arms in order of trust: `play1` (speed 1, the reference), `play3` (Superfast), `ultra` (Ultrafast), `step`.

## ACCEPTS

- traces of schema `scene_trace_v1`, and sample records (arm, rows, save name and sha256, the random state asked for,
the replay flag, wall seconds, ticks).

## WHAT IS COMPARED

- each track's state and value at the end of every tick (offset from the start tick); acts (name, ok); faults (what);
taps and every other record kind, all fields except wall time; the end (state, hit tick, ticks executed). Never compared: the
fields that carry wall time, frames, sequence numbers or run ids.

## DOES NOT SURVIVE (not promised)

- a difference inside one tick that the end-of-tick sample does not see; per-frame effects that
leave no value in a track (an overlay, an animation). Ticks per second include up to one poll interval (0.3 s) of latency.

## PROMISES (each one is owed a test of the same name)

- **equal-traces-compare-equal**.
- **track-or-tap-difference-names-tick-and-value**: in a track or a tap, the first tick and both values.
- **wall-time-only-is-no-difference**.
- **missing-tick-range-is-could-not-compare**, never equal.
- **replay-is-never-a-sample**.
- **runs-not-from-one-save-are-refused**: the save's name and sha256 and the start tick.
- **run-whose-rand-was-not-written-back-is-refused**.
- **comparison-under-another-key-is-not-used**: the key is the plan hash, our mods' loaded hashes, the companion's source hash,
  the mod list fingerprint and the arm.


## LIMITS

None. The live driver's waits are those of `s.run` and `scene.open` (`design/specs/2026-11-23-scene-library/boundary.md`).
