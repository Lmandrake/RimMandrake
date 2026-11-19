# RIMMANDRAKE_MEND_BOUNDARY_ACCEPT_FIXTURE_NOW_NEEDS_MAIN

## spec
The acceptance test of RIMMANDRAKE_BUILD_BOUNDARY_CHECK_PROMISE_WITHOUT_TEST_REFUSED fails on origin/main
(27d7b30553, measured 2026-11-19 06:17 AM PST): `FAILED 2`. Its fixture `selftest_x.py` has no `main()`.
Commit 60274d0df2 made boundary_check count a promise only if `main()` runs its test, and a file with no
`main()` reads UNREADABLE (exit 3). The fixture was not updated. The tool is right; the fixture is stale.
Fix: the fixture writes a `main()` that runs its tests by name. Found by
RIMMANDRAKE_PROVE_PIPELINE_CONTROL_ASKS_MET_HE_ASKED_BEFORE.

## verify
python3 src/RimMandrake/rimflow/acceptance/boundary_check_accept.py   # exit 0, prints PASS boundary_check_accept (4 checks)
Watched failing on 27d7b30553: exit 1, `FAILED 2` (both fixture checks read UNREADABLE: no main()).

## criteria
- boundary_check_accept.py exits 0 with 4 checks.

## refs
file: src/RimMandrake/rimflow/acceptance/boundary_check_accept.py
