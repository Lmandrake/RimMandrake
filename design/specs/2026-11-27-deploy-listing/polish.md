# Polish beside design/specs/2026-11-27-deploy-listing/boundary.md

## (fresh read, WB-pipeline-read-utils-20261128-092119, 2026-11-28)
- `src/RimMandrake/Utils/deploy_listing.py` the clause 'An absent mod root is an empty inventory' has no test of its own (a planted `missing_ok` fault went red only by a side effect in selftest_game_hold_split_install); add to t_a_listing_that_still_fails_is_named_not_skipped a check that inventory() and xml_files() of a missing root return {}.
- `src/RimMandrake/Utils/deploy_def_guard.py` the NON_DEF_DIRS prune applies at any depth, so a Defs/Sounds/*.xml inside a non-target game copy is not walked; no repo mod has such a folder.
