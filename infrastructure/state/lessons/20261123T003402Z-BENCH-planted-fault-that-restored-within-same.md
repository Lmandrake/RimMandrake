A planted fault (a mutation) in a .py that is restored, or re-tested, within the same second at the same byte length leaves Python's stale .pyc in place: Python compares mtime in seconds and file size (the pyc check is mtime-plus-size), so the restored source still runs the planted code, or the planted code never runs and the fault reads NOT CAUGHT. After each plant, edit or restore of a .py, delete its __pycache__ entry (or run with PYTHONDONTWRITEBYTECODE=1 and clear __pycache__) before you trust the next run.

Sightings:
- 2026-11-22 (red census): role_launch.py's 'tot += run_spend(r)' planted as 'tot += 0  # PLANTED' (both 27 chars), restored by cp; both role-cap selftests then read red on a correct tree.
- Filed 2026-11-24: a mutation that swaps a word for one of the same length (subprocess for own_cgroup) and is restored within the same second: the mutant keeps running after the restore.
- Filed 2026-11-26Z: a mutation harness that edits a .py file and re-runs its test within the same second can read a stale __pycache__ .pyc when the planted fault keeps the byte size ('t > now' -> 't < now'): the old code runs and the fault reads NOT CAUGHT. Delete the module's .pyc before trusting a NOT CAUGHT.
item: RIMMANDRAKE_SLIM_TICK_MEMORY_PAGE_BUILD_HITS_ONE_GIG_TICK_TOOK_FIVE_MIN
item: RIMMANDRAKE_LAUNCH_ROAD_BACK_BUNDLE_BY_TICK_READS_BLOCKED
home: ~/dev/MandrakeWorkflows/skills/mutate-your-checker/SKILL.md
