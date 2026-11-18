## spec
Graffiti's pass 4, the first on game B, recorded in `/home/mandrake/rm/scratch/BENCH/ralph_graffiti/ralph/PROGRESS.md` (2026-11-07) that `ralph/steve.sh tier` refuses with "swap marker ... missing or changed". The pass worked around it because game B already ran the graffiti_solo list. A dry run of the same tier in `~/rm/gameb` at 13:46 PST printed no refusal.

Suspected cause, UNMEASURED: `deployed/config/ModsConfig.swap-active.json` and `ModsConfig.before-tier-graffiti_solo.xml` are tracked files, and `ralph/steve.sh sync` runs `git checkout -qf` in Steve's clone. So a sync after a tier puts the committed marker back under the list that tier wrote. The marker is also one per clone, not one per game, which matters if a clone ever swaps both games' lists.

Done when: the refusal is reproduced or ruled out by one `deploy` then `tier` in `~/rm/gameb`, and either fixed (marker per instance, or not reset by sync) or recorded as harmless. A selftest covers the fix.
