# ROLE_LAUNCH_DECIDE_SEAT_AND_GATES

role_launch.py (DISPATCHER_BUILD_ROLE_LAUNCH_FROM_SCHEDULE) runs on builder defaults that need a decision before
the Conductor or Operations is enabled on Wednesday:

1. seat / clone / model: both roles run as seat BENCH in `/home/mandrake/rm/bench` with model `sonnet`
   (Agent_Policy.md: prose a human reads and acts on). rimflow has no CONDUCTOR/OPERATIONS seat; a headless run in
   the bench clone shares the BENCH shard and working tree with the owner's BENCH window. Alternatives: a dedicated
   seat + clone, or the dispatch clone (which RUNNER ingest commits in).
2. UNMEASURED / stale ops reading: roles/conductor.md's table puts UNMEASURED or status.json > 45 min old in AMBER;
   the build brief said refuse loudly. The code refuses (noted alarm, slot retried next tick, missed after
   slot_late_s). Correct conductor.md or the code.
3. Operations has no throttle bands in operations.md: it runs at x1.0 whatever the runway.
4. Not launched by the Dispatcher: the Conductor's "his message" and "his presence (session)" triggers, and
   session_week_pct_cap / session_helpers_max (session-mode rules, not quick checks).
5. The alarm-run baseline: ops_watch alarms already OPEN when Operations is first seen enabled are not run
   (the next scheduled run covers them).
