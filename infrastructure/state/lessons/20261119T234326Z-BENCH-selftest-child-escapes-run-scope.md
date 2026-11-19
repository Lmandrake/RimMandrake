A detached run's own scope kill does not end the selftests it started: run_selftests.py puts each test in its own scope in rm-harness.slice, outside the run's cgroup. Find a run's leftovers by the RM_ROLE_UNIT=<unit> marker every child inherits (detached_helper.scan_marked_live), not by cgroup. Measured 2026-11-18: two .det clones held by a 20-minute-old selftest child after the run ended.
item: RIMMANDRAKE_REAP_SELFTEST_CHILD_ENDED_RUN_LEFT_HOLDING_CLONE
home: skills/clone-landing-commits/SKILL.md
