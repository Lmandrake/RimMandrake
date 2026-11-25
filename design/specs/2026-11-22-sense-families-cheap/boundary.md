# BOUNDARY: each sense family reads cheaply, and a family that stays unread raises an alarm, Design Version 0.1.0

Code: the sense pass of `src/RimMandrake/Utils/ops_watch.py` (`run --compose`: the blind reading, the kill stamp, the
alarm family's join, `git_window`, `c_process`, `tt_texts`, `c_tps`, `newest_progress_mtime`), the `--recent` read of
`src/RimMandrake/Utils/tps_record.py`, the day-folder skip of `readings` in
`src/RimMandrake/Utils/sim/csuite_codex_limits.py`, `epoch` in `src/RimMandrake/rimflow/role_use.py`, and
`World.doing_claims` in `src/RimMandrake/rimflow/wrapup.py`. Item: `RIMMANDRAKE_WATCH_OPS_SENSE_OVERRUN_MOST_FAMILIES_BLIND`,
written Sun 2026-11-22, 8:40 PM PST. Each promise has a test of its name in
`src/RimMandrake/Utils/selftest_ops_sense_blind.py`.

## The danger the limits guard

- **The sense kill (`metronome_phases.json` phase `sense`).** When this page was written it was 15 s, the sense
  phase's share of the 45 s beat: a pass past it pushed dispatch to the next beat (24 h to 2026-11-23 04:30Z: 10
  dispatch deferrals, each in a beat where sense ran its full 15 s). Since 2026-11-23 sense runs apart from the beat
  under a 120 s hang guard (`design/specs/2026-11-23-sense-apart-from-beat/boundary.md`).
- **Why the families overran it (measured 2026-11-22, each collector alone on a copy of the live store).** Not load
  alone: each slow family had its own large read. tps 9 s (`tps_record.py` read the whole 7-day TPS record, 145 files
  and 152 MB on `/mnt/c`, to judge 5 minutes). queues 8.4 s (each pass re-statted 4000 + 1728 + 1176 old names of the
  progress folders on `/mnt/d`). process 4.5 s and tokentalk 3.7 s (each ran its own 7-day `git log` over 8724
  commits). codex 3.5 to 4.5 s (a stat of 746 rollouts on `/mnt/c`). wrapup 3.7 s (one ledger read and replay per
  standing row). roles 3 s (621 000 `strptime` calls for about 39 000 stamps). The pass's own work was 0.85 s, and
  its series reads 0.6 s.
- **`PROGRESS_RESTAT` (250 old names a folder a pass).** It guards a progress file rewritten in place under an old
  name, which no listing shows. A miss can only make a queue read stalled while it moves (a loud alarm, never a silent
  one): a finish arrives as a new name, and each pass stats every new name.
- **`CODEX_LATE_WRITE_DAYS` (7 days).** A rollout lives in the day folder of its start. A day folder older than the
  lookback by more than this is not statted. It guards a session resumed days after its start. Measured
  2026-11-22: of 1497 rollouts on both sides, none was written more than 1 day after its folder's date.
- **`TPS_RECENT_SLACK_S` (600 s).** A segment last written before the verdict window, less this slack, holds no row of
  the window. The slack guards a clock step between Windows and WSL.
- **Why even a cheap family was killed (measured live 2026-11-22, the kill stamp).** 2 of 2 kills at 8:40 and 8:42 PM
  PST were in the stage `alarms`: a light pass filed what the alarm pass had deferred (two reopens, deferred 24 and 12
  times), through `rimflow live`, `raise` and a publish. That did not fit the beat, the kill came mid-filing, and the
  next light pass began it again. Before the stamp, maturation and pager (0.05 s collectors) were killed alone the same way.
- **Why the alarm pass was killed too (measured live 2026-11-22).** At 9:01 PM PST the pass of timers and flow was
  killed in the stage `alarms`: a new crossing was spawned in the beat. The detached filer then took 17.7 s of wall
  time for one held filing, more than the whole sense limit, so no filing fits a beat.
- **`HELD_FILER_MAX_S` (600 s, the detached filer's `RuntimeMaxSec`).** A hang guard. Each rimflow call in
  `real_filer` is bounded at 120 s, and a real held filing takes about 10 to 40 s.
- **The blind bound.** A family is blind when its newest series record is older than `compose_max_age_s` (the same
  bound past which its carried points read UNMEASURED). It guards the round robin's worst healthy round, so a family
  that is merely waiting for its turn never alarms.

## ACCEPTS (the only inputs this is built for)

- **the-beat-argv.** `ops_watch.py run --compose --file-alarms --metronome-gen N --family F [--family G]` from the
  metronome's sense phase, killed by SIGTERM (then SIGKILL) at the phase limit.
- **the-live-sources.** The seat clone `/home/mandrake/rm/bench` (git), the series and stores under the ops_watch
  folder, the TPS record folder, the Codex session trees and the queue folders. The shared ops ledger reader uses
  `/home/mandrake/rm/dispatch`'s local `refs/remotes/origin/main`, refreshed by `testq-tick`.

## DOES NOT SURVIVE (not promised)

- **a-box-at-load-45.** Every read is then about three times slower, and a pair of the slower families can still pass
  15 s. Then that family is blind for that turn, and the blind alarm names it once it stays unread past the bound.
- **a-kill-by-sigkill-alone.** A pass killed without SIGTERM leaves no kill line. Its family still counts as blind by
  age; only the stage is unknown.

## PROMISES (each one is owed a test of the same name)

- **a-family-left-unread-raises-the-blind-alarm.** A compose pass counts in `sense.families_blind` every family whose
  newest series record is older than the blind bound, and names each one. The alarm pass files it on one fixed item,
  `OPS_SENSE_FAMILY_READING_RESTORE_<twist>`. A family inside the bound does not count.
- **an-unreadable-series-is-not-blind.** A family whose series file cannot be read in a compose pass (any `OSError`
  but a missing file, e.g. `ENOMEM` on the 9p read of `/mnt/d`) is never counted blind and never reads "no record in
  the series window": `sense.families_blind` reads UNMEASURED, naming each such family with its error and the blind
  count of the rest, and the family's `._collector` point says its series could not be read. A missing series file is
  the empty set and still counts as blind. Item: `OPS_SENSE_FAMILY_READING_RESTORE_XAOE` (2026-11-24 8:18 AM PST, 5
  fresh families alarmed while the box returned `ENOMEM` on `/mnt/c` and `/mnt/d` reads).
- **a-blind-familys-points-say-why.** The carried UNMEASURED points of a blind family say how many sense passes on it
  were killed since it last read, and the stage the last one was in.
- **a-killed-pass-leaves-its-stage.** SIGTERM to a `run --compose` pass appends one line to `sense_kills.jsonl` with its
  families, its stage and its seconds, and the pass exits non-zero.
- **the-alarm-family-joins-when-it-is-blind.** When the alarm family (flow) has no series record within the blind
  bound, a compose pass measures it too, so the alarms still run.
- **tps-reads-only-the-recent-segments.** `tps_record.py --recent` opens only the segments written within the window
  and its slack, and its summary of a fresh session equals the whole read's.
- **the-week-of-commits-is-read-once.** `git_window` reads only the commits since its cached head, and its answer
  equals a whole `git log` read. A head that does not descend from the cached head, or a changed process regex, reads
  whole. process and tokentalk both take their commits from it.
- **few-old-progress-names-are-restatted.** A pass stats every new name in a progress folder and at most
  `PROGRESS_RESTAT` old ones; a rewrite in place under an old name is still seen once the cursor reaches it.
- **codex-skips-day-folders-past-the-lookback.** `readings(newer_than=…)` stats no rollout in a day folder older than
  the lookback by more than `CODEX_LATE_WRITE_DAYS`, and reads every rollout in a newer folder.
- **a-light-pass-files-nothing-inside-the-beat.** A compose pass that does not measure the alarm family files no alarm
  itself. When alarms are held, it starts `ops_watch.py file-held` as its own user unit (outside the beat's cgroup), one
  at a time; a filer that cannot start is said in the flags. `file-held` files the held alarms with no beat deadline.
- **an-alarm-pass-in-a-beat-files-nothing-inside-it.** In a beat, the alarm pass decides each crossing and clearing
  as before, but files nothing: a spawn or a reopen goes PENDING for the detached filer, and a note is queued for it
  (the newest wording of each note). `file-held` files the held alarms, says the queued notes and makes the book's
  queued blocks, then empties the note queue; a note it could not say is queued again by the next alarm pass.
- **the-ledger-and-the-stamps-are-read-once.** `World.doing_claims` reads and replays the ledger once for a whole
  `standing()`, and `role_use.epoch` parses each stamp once, with the same answers as before.

Later lists beside this page: `polish.md`.
