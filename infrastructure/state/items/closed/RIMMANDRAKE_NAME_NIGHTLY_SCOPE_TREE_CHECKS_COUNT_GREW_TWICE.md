# RIMMANDRAKE_NAME_NIGHTLY_SCOPE_TREE_CHECKS_COUNT_GREW_TWICE

## spec
`src/RimMandrake/Utils/selftest_nightly_scope.py` check 6 ("the 13 publish tree checks stay, and publish still runs
them before the pipeline checks") pins `len(tc["checks"]) == 13`. Its intent (277260bc81, 2026-11-15) is that no tree
check was dropped when the pipeline door was added. Two checks were added after it (6b4fb634a7 modledger_tree,
3928fbe2da stage_folders_in_record): 15 now, so the test is red on origin/main (measured at 643ccb6459) though nothing
was dropped. Fix the test, not the list: name the 13 tree checks it was written against and assert each is still in
`publish_tree_checks.json` (a superset passes, a dropped one fails), keeping the publish.py order assertion.

## verify
`python3 src/RimMandrake/Utils/selftest_nightly_scope.py` reads GREEN on the current 15-check list, and RED when any of
the 13 named checks is removed from a copy of the list (watched). Red on base 643ccb6459 (`6 the 13 publish tree checks
stay ... -- 15`).

## criteria
- check 6 passes on a list that grew
- check 6 fails when one of the 13 original tree checks is dropped
- check 6 still fails when publish.py stops running tree checks before pipeline checks

## refs
file: src/RimMandrake/Utils/selftest_nightly_scope.py
file: src/RimMandrake/Utils/publish_tree_checks.json
