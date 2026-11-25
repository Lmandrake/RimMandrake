# Polish list: the account plan (a record; nobody works these lines)

- `commit` waits on the plan lock with no bound. A writer that is stopped while it holds the lock blocks every write.
- `history.jsonl` holds two whole plans per line and is read whole at each write. After some thousand writes it is megabytes.
- Steps that have ended stay in the plan file until someone removes them (`./acct plan` marks them ENDED). A `tidy` command would drop them.
- The old plan's `window_margin_min` (no switch to Steve's account in the last 10 min of his window) has no twin here.
- `./acct order A B` with a meter account in the list is refused; the text could name `./acct step move`.
- `measures` uses the lines of the plan as it is now for past weeks; the tool's own log could give the line of each past reset.
- The week ahead uses one burn rate for the whole week. Weekday and weekend rates differ.
- `account_plan_replay.py` models a switch as instant and the burn of two machines as one stream.
- `status` prints the full reason line on one long line; a terminal wraps it.
- not handled: another account's reset passes while a rescue drain is in flight. The pass's poll rewrites the old
  actuator's notice, so the `rescue.drain_h` bound starts again (again at each poll while that account stays unreadable).
- `./acct import-legacy --replace` drops `driver`, holds, pins and requests: after the cut-over it puts the old engine back
  and its answer does not say so.
- A `switch A` written while A is already live is never marked done: the request stays open until its end (24 h), and the
  machine can go back to A when A is left and refills inside that day.
- `undo` takes the whole plan back to before that revision, the driver included; its answer lists the revisions, not the driver.
- The old actuator's brake before a poll: at the warning line with no run live and every target's reading over 6 min old,
  the pass stops the fleet before it polls, and switches from the stop 5 min later. The old engine does the same.
