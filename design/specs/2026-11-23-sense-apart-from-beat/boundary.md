# BOUNDARY: the sense phase runs apart from the beat, under a hang guard, Design Version 0.1.0

Code: the apart phase of `src/RimMandrake/Utils/metronome.py` (`phase_dir`, `apart`, the `apart` command, the apart
rules of `load_table`, `beat`, `run_phase`'s reads, `health`, `read` and `publish`), the sense row of
`src/RimMandrake/Utils/systemd/metronome_phases.json`, the units `rm-metronome-sense.service` and
`rm-metronome-sense.timer`, and `compose_round_bound_s` in `src/RimMandrake/Utils/ops_watch.py`. Item:
`RIMMANDRAKE_SIZE_SENSE_STEP_LIMIT_FIFTEEN_SECONDS_NOBODY_CAN_SOURCE`, written Sun 2026-11-22, 10:20 PM PST. Each
promise has a test of its name in `src/RimMandrake/Utils/selftest_metronome_apart.py`.

## Where the old 15 s came from

- `limit_s: 15` first appears in a09d26c480 (2026-11-03, OPS_METRONOME_PROVE_IN_SHADOW). Its message says "Phase limit_s
  values are ESTIMATES; two ops_watch family pairs overran 15 s on the first real beats." The strategy
  (`design/RimMandrake/operations_metronome_strategy_2026-11-02.md` §2) sets the 45 s beat budget and no sense limit.
  No measurement and no owner word chose 15 s. Later reason texts counted its overruns and kept it.
- It was tight because sense ran inside the beat, before dispatch: a long sense pass left dispatch no room, and
  dispatch went to the next beat (24 h to 2026-11-23 04:30Z: 10 deferrals, each in a beat where sense ran 15 s).

## The danger the limits guard

- **The sense hang guard (`limit_s` 120 s, `cleanup_s` 5 s).** It is the call-deadline class of CLAUDE.md §No limit
  without the danger it guards: a hang guard set far above a real run. It guards a read that never returns (a stat on
  a stuck drvfs mount, a git lock, a subprocess that waits): without it, sense would stop for good and every family
  would go blind. No such hang of the sense pass has been measured. The slowest real runs measured: about 13 s for
  one family alone before 2026-11-22's cheap reads, 6.4 s completed after them, and 73 s for the old whole pass of
  every family (strategy §2). 120 s is above all of these.
- **The sense unit's `TimeoutStartSec` (150 s).** A second hang guard, for a metronome process that itself hangs. It
  is above the 125 s the phase can take.
- **The sense timer (`OnUnitInactiveSec` 60 s).** One pass a minute after the last one ends, as the beat was. A slow
  pass only delays the next sense pass.

## ACCEPTS (the only inputs this is built for)

- **a-phase-table.** `metronome_phases.json`, where a phase may carry `"apart": true`.
- **the-two-units.** `rm-metronome.timer` runs `metronome.py beat`; `rm-metronome-sense.timer` runs
  `metronome.py apart --phase sense`.

## DOES NOT SURVIVE (not promised)

- **a-sense-pass-that-hangs-past-sigkill.** A process in an uninterruptible wait is not killed by SIGKILL; it holds
  the sense lock, and every later sense run logs `duplicate` until it ends. The blind alarm names the families.

## PROMISES (each one is owed a test of the same name)

- **the-beat-never-runs-an-apart-phase.** `beat` neither runs nor defers a phase with `apart`, and its budget check
  does not count it. Dispatch then starts at the same time in a beat however long sense takes.
- **an-apart-phase-runs-in-its-own-dir.** `apart` runs the phase with its own state, lock, generation, fence and
  output under `<dir>/apart/<phase>`, and writes its lines to the shared `beats.jsonl`, each marked `apart`. The
  child gets that dir as `METRONOME_DIR`, so its fence reads its own generation.
- **a-slow-collector-completes.** A sense pass that takes 20 s completes inside the hang guard: it exits 0 and
  publishes, and its family is read.
- **a-hung-collector-is-stopped.** A sense pass that never returns is killed at `limit_s` and its generation is
  fenced, and the next `apart` run is not blocked.
- **a-reader-finds-an-apart-output.** A phase that `reads` an apart phase, and `metronome.py read`, find the output in
  the apart phase's dir.
- **the-round-bound-reads-the-sense-unit.** For an apart sense phase, `compose_round_bound_s` takes its gap from
  `rm-metronome-sense.timer` and each pass's length from `limit_s + cleanup_s`, and counts no retry beats (a kill is
  no longer a normal turn).

Later lists beside this page: `polish.md`.
