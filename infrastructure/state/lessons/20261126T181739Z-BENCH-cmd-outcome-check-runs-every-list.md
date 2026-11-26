A cmd: outcome check runs on every list_effect beat (every 15 min) and every list_dispatch beat. Any temp file it leaves multiplies about 100 times a day: two acceptance scripts left 5,000 git repos in /tmp in 30 h, and the hourly reaper ran 2 h archiving them. list_effect.run now gives each cmd: check its own TMPDIR and deletes it (c188af79). A check that writes a literal /tmp path is still not covered.
item: RIMMANDRAKE_BOUND_SCRATCH_REAP_RUN_THAT_GREW_FOUR_MIN_TO_TWO_HOURS
home: design/specs/2026-11-22-list-outcome-checks/boundary.md
