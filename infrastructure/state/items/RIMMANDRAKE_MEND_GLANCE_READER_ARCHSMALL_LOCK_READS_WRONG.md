## spec

Filed Sun 2026-11-22 by the Conductor helper of RIMMANDRAKE_WATCH_STEVE_LANE_IDLE_WHILE_VISIT_CHECKS_WAIT. That helper
met this on the way, outside its item, and did not fix it. Its assigned work would not have finished, and the cause is
unknown.

`python3 src/RimMandrake/rimflow/selftest_game_driver_readers.py` is red. It was reproduced twice in /home/mandrake/rm/bench
on 2026-11-22. The FAIL line:

    FAIL P-B1 for ArchSmall reads ArchSmall's lock (old read ArchBig's: FAIL while this seat held ArchSmall)  ('PASS', 'PASS')

It runs through `selftest_game_lock.py`, so `code_review_status.py check src/RimMandrake/rimflow/maturation_dispatch.py`
reads DIRTY even though neither selftest imports that file. That is a review blocker for every change to that file.
- The case came from commit 58ed9adf69 (RIMMANDRAKE_MOVE_TWO_MORE_GLANCE_READERS_CENSUS_MISSED, closed done).
- Guess (~50%): the frozen `old_p_b1` reads the live `bridge_holder.held_by` and identity, or the `RM_GAME_INSTANCE=b`
  lock path, so its expected FAIL depends on the live lock state at the time it runs.

Evidence:
- `D:\ClaudeWork\rimmandrake\helpers\idle_lane\gdr.txt`
- `D:\ClaudeWork\rimmandrake\helpers\idle_lane\gdr2.txt`

## verify

- `python3 src/RimMandrake/Utils/run_selftests.py --only selftest_game_driver_readers,selftest_game_lock` is green, and
  stays green whoever holds ArchBig or ArchSmall live.
- If the cause is a live read in the frozen old reader, a case pins it to the test's own temp lock dir.

## criteria

- The P-B1 ArchSmall case passes and is independent of the live locks.
- No check is edited to pass: the cause is found first.

## refs
file: src/RimMandrake/rimflow/selftest_game_driver_readers.py
