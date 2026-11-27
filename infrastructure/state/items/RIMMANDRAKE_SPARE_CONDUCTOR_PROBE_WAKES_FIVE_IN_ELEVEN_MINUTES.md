# RIMMANDRAKE_SPARE_CONDUCTOR_PROBE_WAKES_FIVE_IN_ELEVEN_MINUTES

## spec

Helper runs on seat BENCH launched tiny probe runs with `detached_helper.py launch`. Each probe's end woke the Conductor
window (`run_end_wake.py`): 5 wakes in 11 minutes, 1:13 to 1:24 AM PST 2026-11-26, from the probes of
RIMMANDRAKE_TEST_SHARED_STARTING_CONTEXT_TWO_TINY_LAUNCHES and RIMMANDRAKE_STRIP_CONDUCTOR_IDENTITY_HELPERS_TOLD_DELEGATE.
Each wake made the window read its whole context and answer the owner about nothing.

The need: a run launched from inside another detached run reports to that run while it runs. Its end posts no wake to
the Conductor window. When the launching run has ended, the probe's end wakes the window as any run, so nothing is left
unread. The Conductor log line and the item note are written in both cases.

The fix: `launch` records `parent_unit` from `RM_DETACHED_UNIT` (every detached run carries it). `finish` asks
`wake_skip`, which posts no wake while the parent record reads `launching` or `running`.
Page: `design/specs/2026-11-27-probe-wake-to-parent/boundary.md`.

## verify

`python3 src/RimMandrake/Utils/run_selftests.py --only src/RimMandrake/rimflow/selftest_detached_wake.py`: the checks
`a-launch-names-its-parent`, `a-probe-of-a-running-run-is-quiet` and `a-probe-of-an-ended-run-wakes` pass. The quiet
check was seen FAIL with the parent branch of `wake_skip` removed, and PASS on the fix.

## criteria

- A probe whose launching run still runs posts no wake, and its step line names that run.
- A probe whose launching run has ended wakes the window as any run of the Conductor's seat.
- The Conductor log line and the item note are still written for each probe.

## refs

file: src/RimMandrake/rimflow/detached_helper.py
file: src/RimMandrake/rimflow/selftest_detached_wake.py
new: design/specs/2026-11-27-probe-wake-to-parent/boundary.md
