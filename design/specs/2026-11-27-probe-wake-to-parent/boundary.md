# BOUNDARY: a run launched by a running detached run wakes no window, Design Version 0.1.0

Code: `src/RimMandrake/rimflow/detached_helper.py` (`parent_of`, `wake_skip`, the `parent_unit` field that `launch`
writes, and the wake step of `finish`).
Item: `RIMMANDRAKE_SPARE_CONDUCTOR_PROBE_WAKES_FIVE_IN_ELEVEN_MINUTES`.
Each promise has a check of its name in `src/RimMandrake/rimflow/selftest_detached_wake.py`.

The reading: helper runs on seat BENCH launched tiny probe runs with `detached_helper.py launch`. Each probe's end woke
the Conductor window (`run_end_wake.py`): 5 wakes in 11 minutes, 1:13 to 1:24 AM PST 2026-11-26. Each wake made the
window read its whole context, for a result that only the launching run reads.

Offline simulation: yes. The selftest runs the real `finish` against a fake state folder, fake records and a fake
waker. No copy of the logic is made.

## ACCEPTS (the only inputs this is built for)

- **a-launch-environment.** The environment of the process that calls `launch`. Every detached run carries
  `RM_DETACHED_UNIT=<its unit>`. A window and a timer do not.
- **a-run-record.** The record of the ended run, with an optional `parent_unit`, and the record of that parent unit
  in the same state folder.

## DOES NOT SURVIVE (not promised)

- **a-parent-on-another-host.** A run launched with `--host` keeps no parent on the host. It wakes as any run.
- **a-parent-whose-record-is-gone.** A parent unit with no record is read as ended. The probe wakes the window.
- **a-parent-that-never-reads-it.** A running parent that does not read its probe's record or item note leaves the result
  unread until the Conductor log line is read.

## PROMISES (each one is owed a check of the same name)

- **a-launch-names-its-parent.** `parent_of` returns the `RM_DETACHED_UNIT` of the launching process, or None. `launch`
  writes it to the record as `parent_unit`.
- **a-probe-of-a-running-run-is-quiet.** When the parent's record reads `launching` or `running`, the probe's end posts no
  wake. Its step line names the parent. The Conductor log line and the item note are still written.
- **a-probe-of-an-ended-run-wakes.** When the parent has ended, the probe's end wakes the window as any run of the
  Conductor's seat. So a continuation that a run's own finish launches still reaches the window.

## LIMITS

None.
