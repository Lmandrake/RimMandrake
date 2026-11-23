## spec
The Maturation tick sent a decider to the offline builder route when its red run was stale. A decider refused on
`green` and also on `ran_on_this_build` (its red run is of an older build or command) was in `red_deciders`. The tick
then launched an offline builder for a red that a zero-token rerun clears. `stale_key` returned None for it, so the
rerun never came first.
Found 2026-11-23 by RIMMANDRAKE_RESUME_KNOCKBACK_HE_WANTS_IT_FINISHED_OFF_SINCE_NOV_EIGHTEEN. Explosive Knockback's
T_SETTINGS_SCREEN was red on the unscoped `selftest_settings_screens.py` (855/856, FlowWorks' row). Its command was
scoped to `--mod ExplosiveKnockback` (7/7) in 5d28a31ed2. The certificate then read it as a red decider.
Boundary page: design/specs/2026-11-23-stale-red-rerun-first/boundary.md.

## verify
Acceptance test: `python3 src/RimMandrake/rimflow/selftest_stale_red_rerun_first.py` prints ALL PASS (4 of 4). On the
parent it read 2 of 4 FAIL: the stale-red case launched the red route, and the mixed case named both deciders.

## criteria
- A stale red decider gets the zero-token rerun, not a builder.
- A fresh red decider still gets the builder.
- The stale key for stale stamps alone is unchanged.
