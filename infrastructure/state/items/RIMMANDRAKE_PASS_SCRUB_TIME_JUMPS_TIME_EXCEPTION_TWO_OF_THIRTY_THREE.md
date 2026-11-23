# RIMMANDRAKE_PASS_SCRUB_TIME_JUMPS_TIME_EXCEPTION_TWO_OF_THIRTY_THREE

## spec
`src/RimMandrake/Utils/selftest_time_set_ticks_callers.py` is red on origin (red census 2026-11-22): 33 call sites, 2
without `timeException`: `src/RimMandrake/LeaningScrub/validation.py:2520` and `:2527` (the arm-regrowth season jump,
637e7ac118, 2026-11-16). The companion refuses `jawa/time_set_ticks` on a map with colonists unless `timeException=true`,
so these two components would be refused live. LeaningScrub is held by the owner (`mod_owner_hold.json`): the fix waits
for the hold to lift. It is two arguments in one harness file, no mod code.
Fix: pass `timeException=True` at both calls (the scene's test map has colonists), then rerun the selftest.

## verify
Offline. No game.

## criteria
Acceptance test: `python3 src/RimMandrake/Utils/selftest_time_set_ticks_callers.py` exits 0 ("missing timeException: 0").
Seen red at f43dea3fa7 with exactly these 2 FAIL lines.

## refs
file: src/RimMandrake/LeaningScrub/validation.py
file: src/RimMandrake/Utils/selftest_time_set_ticks_callers.py
