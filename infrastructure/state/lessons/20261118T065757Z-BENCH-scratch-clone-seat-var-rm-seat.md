A Codex lane started by systemd-run puts its scratch clone under /home/mandrake/rm/scratch/UNKNOWN/ even with --setenv=AGENT_SEAT=BENCH. scratch_clone.seat() reads RM_SEAT (then the claude-seat-* cgroup), not AGENT_SEAT or RIMFLOW_SEAT. Pass --setenv=RM_SEAT=BENCH. The Conductor log line of 2026-11-17 9:24 PM that says 'pass AGENT_SEAT' is wrong about the variable. Seen on rm-codex-lane-plan-225656 at 10:57 PM PST.
item: RIMMANDRAKE_PLAN_CLEANSE_APPLY_DRY_RUN_FOUR_ANSWERS
home: src/RimMandrake/Utils/scratch_clone.py
