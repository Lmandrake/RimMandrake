A mutation harness that edits a .py file and re-runs its test within the same second can read a stale __pycache__ .pyc when the planted fault keeps the byte size ('t > now' -> 't < now'): the pyc check is mtime-plus-size, so the old code runs and the fault reads NOT CAUGHT. Delete the module's .pyc (or run with PYTHONDONTWRITEBYTECODE=1 and clear __pycache__) after each edit before trusting a NOT CAUGHT.
item: RIMMANDRAKE_LAUNCH_ROAD_BACK_BUNDLE_BY_TICK_READS_BLOCKED
home: ~/dev/MandrakeWorkflows/skills/mutate-your-checker/SKILL.md
