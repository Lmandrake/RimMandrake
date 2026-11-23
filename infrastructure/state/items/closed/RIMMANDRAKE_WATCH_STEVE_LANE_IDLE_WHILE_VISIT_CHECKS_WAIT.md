## spec

Filed Sun 2026-11-22 by a Conductor helper (owner-authority brief, CONDUCTOR_AUTHORITY_DECIDE_NO_ASKING_MOM). The owner
asked: "And shouldn't Operations have noted SteveDesktop being idle and said something about it to you?"

The failure (measured): the SteveDesktop lane sat BRAKED or on filler from 21:14Z to 02:45Z (5.5 h) while 28 Pyrelands
(visit 6) and 6 FlowWorks (visit 8) checks with a testq block waited for it. No alarm fired, because:
- `queues.testq.stalled_min` reads only queued jobs, and these checks were never queued;
- `steve.unowned_stall_min` reads only faults, and a filler brake is not a fault;
- `maturation.idle_owed_max_min` reads only `offline_build` mods, never `in_game` ones;
- `seats.idle_with_work_min` reads only Claude seats;
- `steve.last_done_age_min` has no target.

The build: one reading plus its rule in the existing collectors and rules.
- The dispatch tick writes `reading.json` `ingame_testq`, the takeable checks per in-game mod
  (`maturation_dispatch.ingame_testq`). The source costs 21 s, too slow for the ops_watch sense, so the tick carries it.
- ops_watch `c_steve_takeable` reads that block in the steve family and gives `steve.idle_with_takeable_min`, with four
  answers: busy (0) / quiet (0) / waiting (minutes) / UNMEASURED.
- The rule fires over 30 min and raises the fixed alarm `OPS_STEVE_FEED_IDLE_LANE` (it reopens), with a line in the
  Conductor log.
- "Takeable" means a `to_run` check of an in-game mod that carries a testq block, is not on the owner's hold, and has
  no row in the visit's folder.

Boundary page: `design/specs/2026-11-22-steve-idle-takeable/boundary.md`. Routing the work to the lane is NOT this item
(`RIMMANDRAKE_ROUTE_VISIT_TESTQ_CHECKS_AHEAD_OF_FILLER`). Neither are the Arch games
(`RIMMANDRAKE_WATCH_INGAME_VISIT_OWED_NO_DRIVER_UNSEEN`).

## verify

- `python3 src/RimMandrake/Utils/run_selftests.py --only selftest_steve_idle_takeable` passes: 25 cases, worst 360 min
  against the line 30. It was seen red before the code (13 FAIL).
  - Today's planted state reads 330 min, state `waiting`, 28 + 6, and the rule crosses.
  - "Nothing takeable" reads 0 quiet.
  - An unreadable source reads UNMEASURED.
- `python3 src/RimMandrake/Utils/mutate_steve_idle_takeable.py`: the control is green, and 15 of 15 planted faults are
  caught.
- A live dry read on 2026-11-23 ~03:30Z: the block was built from live facts into a scratch dispatch dir.
  - The point read 633 min, waiting FlowWorks 10 and Pyrelands 25, with the lane on filler job
    J20261123T031031Z-8400b9 (SWBestiary). The rule crossed.
  - Evidence: `D:\ClaudeWork\rimmandrake\helpers\idle_lane\dry.txt`.
- Live: once the dispatch clone runs this code, the ops_watch reading holds `steve.idle_with_takeable_min` as MEASURED
  (not UNMEASURED) and newer than the commit.

## criteria

- The six promises of the boundary page pass their tests.
- The live ops_watch reading carries the point within 30 min of the dispatch clone updating. Close with
  `--live "reading=D:\ClaudeWork\rimmandrake\ops_watch\status.json max_age=30m"` only once it is live.

## refs
file: src/RimMandrake/Utils/ops_watch.py
file: src/RimMandrake/Utils/ops_watch_rules.json
file: src/RimMandrake/rimflow/maturation_dispatch.py
file: src/RimMandrake/Utils/selftest_steve_idle_takeable.py
file: src/RimMandrake/Utils/mutate_steve_idle_takeable.py
file: design/specs/2026-11-22-steve-idle-takeable/boundary.md
