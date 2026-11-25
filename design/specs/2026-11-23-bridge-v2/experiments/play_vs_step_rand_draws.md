# PLAY against STEP: where runs from one save part (2026-11-24)

Item `RIMMANDRAKE_MEASURE_PLAY_AGAINST_PAUSED_STEP_NEVER_COMPARED`. Hand-written readings beside the generated
`play_vs_step_result.md`. Game ArchBig, MINIMAL list (26 active mods as the game counts them), companion of `d9678136b4`.

## What was measured

1. **No arm repeats itself, and none agrees with the reference** `[measured]`. Plan `colony_drift.py` (1200 ticks, the
   square and the job of three colonists and a donkey on every tick), fixture `rm_fixture_play_vs_step` loaded fresh for
   every run, the random state of the arming run written back before every run and read back in every `open` record.
   Five runs of each arm: 0 of 10 pairs of runs equal in every arm (PLAY speed 1, speed 3, Ultrafast, STEP). The first
   difference is on tick 51, 101, 151, 201 or 301 of the run, always a pawn one or two squares off. The same reading came
   from two full sets, at 19:40 and 19:53 PST.
2. **The runs start equal and part on the random numbers that are drawn** `[measured]`. Plan `colony_drift_rand.py`
   records `static:Verse.Rand` `seed` and `iterations` as tracks (reading a field draws nothing). Three runs of PLAY
   speed 1 and three of STEP (`play_vs_step_rand_result.md`, `play_vs_step_rand_result_samples.jsonl`):
   - at arm, all seven runs read the same seed (3697589272) and `iterations` 251385;
   - the seed never changes; `iterations` differs between runs from tick 1 (one STEP run: 251541 against 251535),
     tick 3 or 4 (one more draw run of each mode), or tick 22;
   - on most ticks the runs draw the same count; a run that parts has drawn a few numbers more (+6 by tick 1, +12 by
     tick 3), and then its pawns choose other squares.
3. **The clock of PLAY was stopped from outside in 3 of 21 runs; that of STEP in none** `[measured]`. The arming run and
   one speed-1 run stopped on tick 771, one speed-3 run on tick 1071, with the `standard` calm profile on. `s.run`
   cancelled each after 60 s of a still clock. Each of those runs had already parted from the reference before it
   stopped. That a window which force-pauses the game stopped them is a `[guess ~70%]`: STEP calls `DoSingleTick` and so
   does not obey a forced pause, and nothing else that PLAY obeys and STEP does not is known.
4. **Ticks per second** `[measured]`, 1200-tick runs that were not stopped: PLAY speed 1 about 57, speed 3 about 255,
   Ultrafast about 510, STEP about 480. The full list: UNMEASURED (no full-list load was scheduled to ride).

## What it decides

- **No arm other than PLAY at speed 1 counts for a bar** (the rule on `src/RimMandrake/Utils/scene_contracts/run.md`):
  none was shown to agree with the reference on this scene.
- **One fixture save and one written-back random state do not repeat a run.** A scene that needs "the same moment
  again" cannot get it from these two alone, and a scene of this kind (pawns that choose) is kind B in every arm.
- **A faster driver is not yet decided.** STEP and Ultrafast are about nine times faster than speed 1, but equality cannot
  be shown while the reference does not repeat. The comparison is worth running again only after the extra draws are
  found and held still.

## The next question (filed)

Which code draws from `Verse.Rand` outside the tick's own work, or a different count from one run to the next? Two
causes stay apart: a draw between ticks (frame work: UI, sound, visuals), and a draw inside a tick whose count depends on
frame timing. A Harmony counter on `Rand` with the caller's phase (inside `DoSingleTick` or not) tells them apart in one run.
Filed as `RIMMANDRAKE_FIND_RAND_DRAWS_PARTING_RUNS_EVEN_STEP`.
