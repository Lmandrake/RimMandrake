# BOUNDARY: one failed write does not kill the SteveDesktop fault monitor's unit, Design Version 0.1.0

Code: `src/RimMandrake/Utils/testq/fault_monitor.py`, the writes that `tick` makes: `write_try`, `write_json_try`,
`mirror_merge` (and `merge_mirror`, which returns its union), `regprobe_section`'s read of the mirror, `snapshot`'s file write, `io_lines`, `state_streak` and the
lock open of `tick`. Item `OPS_TIMER_REPAIR_PRXC_XKGA`, written 2026-11-27. Each promise has a test of its name in
`src/RimMandrake/Utils/testq/selftest_fault_monitor_write.py`. The class guard, red on the code before this page:
`rimflow guard OPS_TIMER_REPAIR_PRXC_XKGA`. This page covers only these parts of the file; the rest of the file has its own
page (`design/specs/2026-11-23-steve-two-games-lane/boundary.md`).

Why: `rm-steve-fault.service` exited 1 once, at 2026-11-27 14:21:39 PST. `merge_mirror`'s `f.write` of
`/mnt/d/ClaudeWork/rimmandrake/testq/regprobe.log.tmp` raised `OSError [Errno 12] Cannot allocate memory`. The mirror is on the
Windows drive (`LIVE_QHOME` in `testq.py`). The next tick, 2 minutes later, passed. The death cost one false TIMER_FAILED
alarm; it was the fifth death of that alarm item. Class: one write to the Windows drive fails for a moment (ENOMEM, EIO,
EAGAIN), and a timer unit dies of it.

## ACCEPTS (the only inputs this is built for)

- **a-tick-every-two-minutes.** `rm-steve-fault.timer` runs `fault_monitor.py tick` every `TICK_S` (120 s).
- **an-oserror-from-a-write.** An `OSError` raised by a write or open-for-write of a file in the queue home (the mirror
  `regprobe.log`, `steve_audio_driver.json`, `fault_windows.json`, `fault_state.json`, `fault_monitor.lock`, a snapshot).
- **a-mirror-that-cannot-be-read.** An `OSError` or `ValueError` (a file that is not UTF-8) raised by the read of the mirror.

## DOES NOT SURVIVE (not promised)

- **a-failed-write-in-another-program.** `testq.py` (`cmd_pause`, `cmd_resume`, `move`), `ingest.py`, and this file's
  `rerun_job`, `quarantine_move` and `release` also write to the drive. They run in other units (ingest) or by hand; their
  writes are not guarded here (`polish.md` beside this page).
- **an-exception-that-is-not-an-oserror.** A `TypeError` in a writer is a fault in the code, and still raises.
- **a-windows-drive-that-stays-short-of-memory.** Ten ticks in a row fail the unit by design. The cause is Windows', not this
  file's.

## PROMISES (each one is owed a test of the same name)

- **one-failed-write-does-not-kill-the-unit-and-the-output-says-so.** A write of the mirror that raises `OSError(ENOMEM)`
  once: the tick returns 0, its output names the mirror as `NOT WRITTEN this tick` with the errno, its reading (the JSON line
  and the state file) is the same as with a good write, and the next tick writes the mirror.
- **a-write-that-fails-every-try-fails-the-unit-with-its-cause.** The same file not written (or the mirror not read) on
  `WRITE_DEAD_TICKS` (10) ticks in a row: that tick returns non-zero, after it wrote `fault_state.json`, and its output reads
  `FAIL <file> not written for 10 ticks in a row` with the errno. The count is `fault_state.json`'s `write_fail`; for
  `fault_state.json` itself, the age of the state that the last good tick left. The limit guards a mirror that nobody sees dead:
  the evidence is this death, which recovered at the next tick (1 tick); the limit is 10 times that, 20 min, inside
  `STALE_S` (30 min), so the unit fails before `check` calls the reading stale.
- **a-good-write-is-as-today.** With no failing write, the mirror holds the stable-sorted union of the mirror and Steve's
  lines, the tick returns 0, the output says `mirror: written` (new lines) or `mirror: nothing new`, and the state files are as
  before.
- **a-mirror-that-cannot-be-read-says-could-not-look.** A damaged mirror: the tick returns its reading from the lines that
  Steve sent, the output reads `mirror: could not look` with the cause, never `written` or `nothing new`, and the damaged
  file is not overwritten (the bad read would throw its history away). It counts toward the ticks in a row. `report` and `check` read
  it as `UNMEASURED(could not look)`.
- **a-failed-write-of-the-state-files-does-not-kill-the-unit-either.** `steve_audio_driver.json`, `fault_windows.json`,
  `fault_state.json`, the lock file and a snapshot file each fail once: the tick (or the snapshot) names the file and the errno
  and does not raise; the tick returns 0. `fault_state.json` that cannot be written for 10 ticks fails the unit.
- **a-good-tick-between-failures-restarts-the-count.** Nine failed ticks and one good tick, three times over: the unit never
  fails.
