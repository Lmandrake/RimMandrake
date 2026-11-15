# RIMMANDRAKE_RUN_FIX_TICKETS_WHILE_PAUSED

## spec

Seen 2026-11-15 on Pyrelands: judging stopped (coverage_stop), the mod paused, and its open fix ticket
`RIMMANDRAKE_FIX_PYRELANDS_ROUND_SIX_SEVENTEEN_GAPS` sat with nothing to launch it. In
`maturation_autonomy.resolve` the coverage_stop branch is the first branch: it pauses the mod and drops its launches,
so the road back (`_road_back`, commit 76c578b59e) is never reached.

Fix (extends the road back, no second mechanism): while judging is stopped, the mod's own fix tickets still get their
one fixer run each, inside `_gate` (max_live, fix_cap_usd, once per item). Its own fix tickets are the open road-back
items and the tickets a granted release waits on (RIMMANDRAKE_GRANT_LOOK_AFTER_FIXES_CLOSE). A live run seen on a
ticket (a hand launch) counts as its one fixer run, so the tick never launches a second. The status line names the
ticket: moving on it, or PAUSED with the ticket and its spent run.

Acceptance test: `python3 src/RimMandrake/rimflow/selftest_maturation_autonomy.py` checks "paused-fix": a
coverage-stopped mod with an open granted ticket launches one fixer on it (status names the ticket), a full slot waits,
a live unit on the ticket is counted and never doubled, and a coverage-stopped mod with no ticket is still never
launched on. It fails on 437b7391b3.
