## spec

Filed Sun 2026-11-22 by the Conductor helper of RIMMANDRAKE_WATCH_STEVE_LANE_IDLE_WHILE_VISIT_CHECKS_WAIT. That item
reads only the SteveDesktop lane (testq). An in-game visit can also be owed work that only a Claude driver can do on
ArchBig or ArchSmall: the checks with no testq block, driven over the bridge.

No ops_watch reading notices such a visit when no one drives it (measured 2026-11-22):
- no key reads an open in-game visit, owed work, and no driver lock held on either Arch game;
- `seats.idle_with_work_min` reads only the Dispatcher seats' journal;
- `maturation.idle_owed_max_min` reads only `offline_build` mods.

So an owed in-game visit with no driver can sit as long as the lane did, and nothing fires.

The want: one reading in the existing collectors and rules, with the same shape as `steve.idle_with_takeable_min`.
- It reads the minutes since an open in-game visit was owed bridge work (to_run checks with no testq block, not held,
  no row in the visit folder) while neither ArchBig nor ArchSmall has a driver lock held for it.
- Its four answers are busy, quiet, ALARM and UNMEASURED.
- It raises a fixed alarm that reopens, with a line in the Conductor log.
- The source is `game_lock.py query all` and the dispatch reading. A lock that cannot be read is UNMEASURED.

## verify

Acceptance test, red today:
- Set up an in-game mod with an open visit, owing a check that has no testq block.
- Leave both Arch locks free for 60 min.
- The new point must read state `waiting` and a value over 30, and the rule must cross.
- Today no such key exists, so `ops_watch.target_state` has nothing to read.
- The test also reads quiet when nothing is owed, busy when a driver lock is held for the mod, and UNMEASURED when the
  lock state cannot be read.

## criteria

- The test is red first, then green. It passes a mutation run in the shape of
  `src/RimMandrake/Utils/mutate_steve_idle_takeable.py`.

## refs
file: src/RimMandrake/Utils/ops_watch.py
file: src/RimMandrake/Utils/ops_watch_rules.json
