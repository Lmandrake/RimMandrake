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
- `./acct can-use <account>` with no plan file answers the launch gate for this machine's live Claude account, not the account named (no program calls the CLI with an account; Codex's door uses `meter_answer`).
- `fresh_record` has no lower bound: a notice or decision stamped in the future counts as fresh until 20 min after that stamp (the allocator's `_plan_notice_live` refuses more than 5 min ahead).
- The hold branch of `tick` gives `machine_notice` a frame of only `now` and `rows`; it holds because `decide` returns `passive` on an active hold before it reads any other key.
- `old_shape` has no place for a step's `when`: the fleet runway and the pool count an account whose window ends inside their horizon as usable to its reset.
- `slot_allocator.lent_allowance` keeps its own copy of the lent rule (`slot_rules.json` `lent_accounts`: 48% used, 48 h, floor 10); only a temporary line comes from the plan file. Nothing acts on it while `advisory` is on.
- `account_pick.py` keeps its own `switch_when` line (10% of the week left) for its alarm; the plan stays on an account to its line. Its `hold` list is empty, so it holds no launch.
- With `advisory.enabled` true the allocator places `n_total` seats whatever the pace: Burn Mode's raise changes the paced figure and its reason line only.
- The remote account read adds 4 to 17 s to each timed pass for each listed machine.
