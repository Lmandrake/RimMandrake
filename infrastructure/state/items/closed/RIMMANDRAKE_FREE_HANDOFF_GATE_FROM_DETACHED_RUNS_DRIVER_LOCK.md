# RIMMANDRAKE_FREE_HANDOFF_GATE_FROM_DETACHED_RUNS_DRIVER_LOCK

## spec

Measured 2026-11-17 2:04 AM PST: `python3 src/RimMandrake/Utils/handoff.py` refused "BRIDGE still held by BENCH —
release it before rebooting: driver lock: HELD BENCH 2360170" while pid 2360170 was a detached run (the resumed Slack
Fable, parent systemd). A detached run survives the window's reboot; its lock is no reason to refuse a handoff. Same
class as RIMMANDRAKE_FREE_GOODBYE_RESTART_HELD_BY_DETACHED_HELPERS_LOCK (fixed a6279cfd2dc3 in seat_restart.py): make
handoff.py's gate (and `--check`) judge the bridge and driver lock by the holder's process, reusing seat_restart's
`bridge_hold`, not a second copy. Also: the Conductor's question watcher (a Monitor background command) holds the
context backstop restart and its own command text matched its own grep in the escalation line; give the role file
`src/RimMandrake/rimflow/roles/conductor.md` one line on arming the watcher with a timestamp-anchored grep that
excludes `restart:BENCH`, and stopping it before HANDOFF READY.

## verify

Acceptance test: a selftest for handoff.py's gate with four cases: driver lock held by a detached run (passes the
gate), by the window or its child (refuses), shared bridge held by the window (refuses), holder pid unmeasurable
(refuses, names UNMEASURED). Fails on the base (the measured refusal above); not watched failing at filing. Command:
`python3 src/RimMandrake/Utils/run_selftests.py --only <the handoff selftest>`; four cases pass.

## criteria

- A handoff is not refused because a detached run of the seat holds the driver lock or bridge.

## refs

file: src/RimMandrake/Utils/handoff.py
