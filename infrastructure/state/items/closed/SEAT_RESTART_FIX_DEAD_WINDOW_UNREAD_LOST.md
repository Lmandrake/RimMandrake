## Finding
A window killed during a handoff can lose the owner's unread message. Proved by real SIGKILL
(`selftest_seat_restart_death.py`) and by TLC (`LiveHandoff.tla`, cases death_old_alone_safety/live: S5 and L3 fail).

Two routes: the window dies before the handoff record is written, or after it with input pending at the fence.
The handoff is cancelled or aborted, `seat_restart.py intile` exits 3, and no wake reads the message. The wake even
says "nothing to recover". A SIGKILLed window leaves its session file saying idle, so nothing downstream notices.

## Fix idea
In `_pending`, when there is no current record, the cursor is held and the pid is dead: write a live record and
relaunch or fall back. Never abort on a dead pid. seat_loop.sh exit 3 (login shell, no relaunch) must not be the
terminal state of a dead window with unread input.

## verify
- L0: GAP_DEAD rows in selftest_seat_restart_death.py flip to "message read"; death_old_alone_safety/live in
  check_models.py flip to expect ok, with the model changed only as far as the fix.

## criteria
- After a real SIGKILL of the window at each of the two points, a fresh window reads the unread message.
