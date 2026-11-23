# BOUNDARY: the disk sense reads only; the seat tidy lands in its own unit, Design Version 0.1.0

Code: `src/RimMandrake/Utils/seat_dirt.py`, its unit `src/RimMandrake/Utils/systemd/rm-seat-tidy.service`, and
`seat_dirt_reading` in `src/RimMandrake/Utils/ops_watch.py` (the `disk.seat_dirt` point of the disk family). Item:
`RIMMANDRAKE_UNBLIND_OPS_DISK_FAMILY_TWENTY_OVERRUNS_STRAIGHT`, written Sun 2026-11-22, 4:26 PM PST. Each promise has
a test of its name in `src/RimMandrake/Utils/selftest_disk_sense.py`.

## The danger the limits guard

- **The sense kill (15 s, `metronome_phases.json` phase `sense`).** It guards a beat that hangs: a hung sense pass
  would hold the beat and every later phase. Its danger and evidence are on the phase's own `reason`. This page does
  not move it.
- **Why the disk family overran it (measured 2026-11-22).** From 11:02 to 16:20 PST every disk sense run was killed at
  about 15.1 s, and every `disk.*` point read UNMEASURED. The seat clone `/home/mandrake/rm/bench` held three
  safe-class paths. With `--file-alarms`, the disk family ran `seat_dirt.tidy` on them: a `git fetch` (5.4 s), a
  classify, then `land.sh` (a fetch, a build and a push). The kill always came before the land ended, so the paths
  never landed and the next beat did the same work again. The read-only parts of the family took about 4 s.
- **`TIDY_LATE_MIN` (90 min: `STALE_MIN` + 30).** It guards a tidy that does not run or does not land. Then safe-class
  dirt grows in the seat clone and no reading says so. The tidy unit runs every 15 min, so a live tidy has had several
  passes before the line.

## ACCEPTS (the only inputs this is built for)

- **a-seat-and-role-clones.** The seat clone (`RM_SEAT_CLONE`) and the role clones under `RM_ROLE_CLONE_ROOT`, each a
  git work tree with an `origin`.
- **the-beat-argv.** `ops_watch.py run --compose --file-alarms --metronome-gen N --family disk` from the metronome's
  sense phase.

## DOES NOT SURVIVE (not promised)

- **a-slow-read.** The disk family's reads (pool walk, stranded-clone scan, git status per clone) still take seconds,
  more under load. A box loaded enough to push those reads past 15 s still blinds the family.

## PROMISES (each one is owed a test of the same name)

- **the-disk-sense-starts-no-fetch-and-no-landing.** The beat's argv, with landable dirt in the seat clone, gives a
  measured `disk.seat_dirt` and starts no `git fetch`, no `land.sh` and no `seat_dirt.tidy`.
- **the-seat-tidy-runs-in-its-own-unit.** `seat_dirt.py tidy --all --apply` tidies every clone that `clones()` names.
  A clone whose tidy fails is named and costs only that clone; the run then exits non-zero. `rm-seat-tidy.service`
  runs that command from the deploy, `rm-seat-tidy.timer` exists, and `ops_clocks.json` names the timer as a clock.
- **a-safe-path-the-tidy-left-counts-as-dirt.** A landable path that is still dirty `TIDY_LATE_MIN` after its last
  change counts in the reading's `stale`, which `disk.seat_dirt` alarms on. A landable path younger than that does not.

Later lists beside this page: `polish.md`.
