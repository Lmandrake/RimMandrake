## spec

Filed Sun 2026-11-22 by the Conductor helper of RIMMANDRAKE_WATCH_STEVE_LANE_IDLE_WHILE_VISIT_CHECKS_WAIT. The brief
(owner authority) said: do not build the routing; file it as its own ticket, with an acceptance test that is red today.

The defect (measured): the SteveDesktop lane takes filler work, which the steward picks per mod with `testq.fill_plan`
in `src/RimMandrake/Utils/testq/steward.py` and `testq/brake_release.py`. It does that while an open in-game visit has
`to_run` checks that carry a testq block and could run on the lane. Nothing sends a visit's testq checks to the lane.
- 2026-11-22: 5.5 h of BRAKED or filler time (21:14Z to 02:45Z) with 28 Pyrelands and 6 FlowWorks checks waiting.
- On 2026-11-23 ~03:30Z the lane was still on filler (J20261123T031031Z-8400b9, SWBestiary) with 35 checks waiting.

The want: while a takeable check waits, the lane's next job is that check's chain on its mod, ahead of filler.
- The waiting list already exists: `reading.json` `ingame_testq` from the dispatch tick (`maturation_dispatch.ingame_testq`).
- It honours the owner's hold, the owner gate, and the visit's own rows.
- The job is submitted with the visit's requester, so its result lands where the visit reads it.

## verify

Acceptance test, red today:
- Set up the dispatch reading's `ingame_testq` block naming one waiting check, with its chain.
- Leave the lane idle or on a filler job on another mod.
- Run one steward tick.
- `ops_watch.c_steve_takeable` must then read state `busy`: the lane runs, or has ready, a job on that mod and chain.
- Today it reads state `waiting` and the minutes since the visit opened. Live, it read 633 min on 2026-11-23 ~03:30Z
  (`D:\ClaudeWork\rimmandrake\helpers\idle_lane\dry.txt`).
- Write it as a selftest beside `src/RimMandrake/Utils/selftest_steve_idle_takeable.py`, reusing its fixtures. See it red
  before the fix.

Live: with an in-game visit open and checks waiting, `steve.idle_with_takeable_min` in
`D:\ClaudeWork\rimmandrake\ops_watch\status.json` stays under 30 min.

## criteria

- The acceptance selftest is seen red, then green.
- The owner's hold and the owner gate still stop a check from being sent (the takeable tests stay green).
- No filler job is queued while a takeable check waits and the lane is free.

## refs
file: src/RimMandrake/Utils/testq/steward.py
file: src/RimMandrake/Utils/testq/testq.py
file: src/RimMandrake/rimflow/maturation_dispatch.py
