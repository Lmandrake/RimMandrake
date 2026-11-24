# BOUNDARY: the disk sense reads only; the seat tidy lands in its own unit, Design Version 0.1.0

Code: `src/RimMandrake/Utils/seat_dirt.py`, its unit `src/RimMandrake/Utils/systemd/rm-seat-tidy.service`, and
`seat_dirt_reading` in `src/RimMandrake/Utils/ops_watch.py` (the `disk.seat_dirt` point of the disk family). Item:
`RIMMANDRAKE_UNBLIND_OPS_DISK_FAMILY_TWENTY_OVERRUNS_STRAIGHT`, written Sun 2026-11-22, 4:26 PM PST. Each promise has
a test of its name in `src/RimMandrake/Utils/selftest_disk_sense.py`.

## The danger the limits guard

- **The sense kill (`metronome_phases.json` phase `sense`).** Until 2026-11-23 it was 15 s, inside the beat; now the
  phase runs apart under a 120 s hang guard (`design/specs/2026-11-23-sense-apart-from-beat/boundary.md`). This page
  does not move it.
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

- **a-slow-read.** The slowest read alone can still pass 15 s on a loaded box. The first pass after the size record is
  lost walks every pool clone (13.0 s at load 20 on 2026-11-22; later passes 2.6 to 2.8 s). Then the family is blind
  for that beat.

## PROMISES (each one is owed a test of the same name)

- **the-disk-sense-starts-no-fetch-and-no-landing.** The beat's argv, with landable dirt in the seat clone, gives a
  measured `disk.seat_dirt` and starts no `git fetch`, no `land.sh` and no `seat_dirt.tidy`.
- **the-seat-tidy-runs-in-its-own-unit.** `seat_dirt.py tidy --all --apply` tidies every clone that `clones()` names.
  A clone whose tidy fails is named and costs only that clone; the run then exits non-zero. `rm-seat-tidy.service`
  runs that command from the deploy, `rm-seat-tidy.timer` exists, and `ops_clocks.json` names the timer as a clock.
- **a-safe-path-the-tidy-left-counts-as-dirt.** A landable path that is still dirty `TIDY_LATE_MIN` after its last
  change counts in the reading's `stale`, which `disk.seat_dirt` alarms on. A landable path younger than that does not.
- **a-closed-items-leftover-copy-is-removed-not-landed.** An untracked `items/<ID>.md` whose item origin has filed, when
  origin also holds `items/closed/<ID>.md`, is never landable: origin's check refuses that push, and on 2026-11-22 two
  such copies in the seat clone sank the whole land (`rm-seat-tidy.service`, 4:39 PM PST). The tidy removes a copy that
  is byte-identical to origin's closed prose, since nothing is lost. A copy that differs stays, and counts as dirt by age.
- **the-disk-reads-overlap.** `c_disk` runs the pool reading, the stranded-clone scan and the seat_dirt reading at the
  same time, and the seat_dirt reading reads its clones at the same time. The family's wall time is then the slowest
  read, not the sum. In series the reads took 21 to 29 s at load 45 on 2026-11-22. The pool is read with
  `cached_sizes=True` (the clone pool page's `the-sense-reading-walks-few-clones-a-pass`).
- **the-tidy-lands-a-shards-lines-never-the-whole-shard.** The tidy lands a ledger shard's appended lines with
  `publish.land_ledger`, which rebuilds them on the newest origin at each try. A line that a peer lands during the
  tidy's push stays on origin, and the clone's line lands once. A push that fails while origin moved is tried again,
  also when the pre-push lint is what refused it. A refusal with origin unmoved fails the tidy with the hook's words,
  and the clone keeps its line. (Landed as a whole file, 6 of 32 tidies were refused on 2026-11-23 and 24.)
- **a-ring-names-its-paths.** The filing of a `disk.seat_dirt` ring names the first path in its title. Each path that
  the title does not name, and each path that joins later, is told in a note on the ring's item.

Later lists beside this page: `polish.md`.
