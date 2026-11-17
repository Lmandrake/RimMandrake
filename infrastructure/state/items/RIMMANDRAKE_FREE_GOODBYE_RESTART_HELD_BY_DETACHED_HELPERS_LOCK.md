# RIMMANDRAKE_FREE_GOODBYE_RESTART_HELD_BY_DETACHED_HELPERS_LOCK

Owner, 2026-11-16 11:28 PM PST: *"You didn't honor the goodbye ritual."*

## spec

Measured in the Conductor log (`D:\ClaudeWork\rimmandrake\conductor\log.md`, 2026-11-17T07:06:50Z to 07:27:56Z): the
Conductor window said HANDOFF READY (07:10:04Z) and the owner said goodbye (07:26:36Z). `seat_restart.py` held the
restart with "bridge/driver lock held by BENCH" and "game action by BENCH: LOADING"; `restart_reconcile` then cancelled
the request as "unmatched 1072 s". The owner cleared the window by hand. The driver lock holder was pid 2125041, a
detached run (`rm-detached-bench-rimmandrake-launch-both-games-steam-refu-1794898927`, parent systemd), and the shared
bridge file read FREE since 06:40:42Z. A detached run survives the window's restart, so neither its lock nor its game
event is a reason to hold. `bridge_hold()` already says so, yet its bare first-branch message fired; the game-action
hold has no such exemption. Which branch fired and why is UNMEASURED until the fixer reproduces it from the records.

Fix both gates, and stop a goodbye or HANDOFF request being cancelled silently while its hold names something the
window cannot clear: it goes, or it raises one RAISE FIRST line naming the real holder.

Brief: `D:\ClaudeWork\rimmandrake\conductor\brief_RIMMANDRAKE_FREE_GOODBYE_RESTART_HELD_BY_DETACHED_HELPERS_LOCK.md`.

## verify

Acceptance test: written by the fixer first and watched failing on the base (not yet watched failing at filing). A
selftest in the seat_restart selftests covering six hold cases: bridge held by the window (holds), driver lock held by
a window child (holds), driver lock held by a detached run (does not hold), game LOADING stamped by the window (holds),
game LOADING stamped by a detached run (does not hold), holder pid unmeasurable (holds, and names UNMEASURED).
Command: `python3 src/RimMandrake/Utils/run_selftests.py --only <the seat_restart selftest>`; all six cases pass.

## criteria

- A goodbye or HANDOFF READY restarts the Conductor window while detached runs of its seat hold the driver lock or
  have the game loading.
- A hold by the window itself or its child still holds the restart.
- No goodbye or HANDOFF request ends as a silent "unmatched (cancelled)".

## refs

file: src/RimMandrake/rimflow/seat_restart.py
