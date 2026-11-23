## spec
Pipeline defect found by the visit-6 steward (RIMMANDRAKE_ROUTE_PYRELANDS_VISIT_SIX_FAILURES_BACK, 2026-11-23).
`maturation_dispatch.full_list_only` decided "this visit needs ArchBig" from every stage-6 check of the test table
(38 for Pyrelands), not from the checks the visit owes (`to_run`). So a visit that owes only full-list checks (sc_walk,
the others counted from an earlier visit) is still offered ArchSmall when ArchBig is busy, runs there, records sc_walk
UNMEASURED ("ArchSmall cannot hold his full list beside ArchBig"), and the next visit repeats it. Visit 6 already ran on
ArchSmall with sc_walk owed and left bar walk_season_on_the_pyre undecided. Fix: `to_run` decides when the facts carry it.

## verify
Acceptance test: `python3 src/RimMandrake/rimflow/selftest_game_hold_split_install.py` (1 FAIL on the parent of the
fix: "a visit that owes only full-list checks needs game a"; ALL PASS on the fix; two must-stay-green cases added).

## criteria
- A visit whose owed checks are all full-list waits for ArchBig, whatever else the table holds.
- A visit that owes a tier check may still use ArchSmall.
