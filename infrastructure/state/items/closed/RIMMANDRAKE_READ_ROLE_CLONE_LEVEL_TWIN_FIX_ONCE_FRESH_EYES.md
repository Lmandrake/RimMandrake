# RIMMANDRAKE_READ_ROLE_CLONE_LEVEL_TWIN_FIX_ONCE_FRESH_EYES

## spec

One fresh reader (a run that did not make the fix) reads fix `062867f85d` once, by
`src/RimMandrake/rimflow/roles/code_review.md`. The fix: `role_clones.level` runs `seat_sync` when every commit ahead
of origin/main is already on it, and reads `stranded` with the `seat_sync.py --superseded` line when the clone still
stays ahead. Cause item: `RIMMANDRAKE_TRACE_DESIGNER_TWIN_COMMIT_LAND_SAID_LEVEL`.

Read: `src/RimMandrake/rimflow/role_clones.py` (`level`), the tests `t_a_twin_only_clone_is_moved_never_read_level_while_ahead`
and `t_a_twin_held_by_dirt_is_stranded_with_its_fix` in `src/RimMandrake/rimflow/selftest_role_clone_level.py`, and the
two promises of the same names in `design/specs/2026-11-19-role-clone-level/boundary.md`.

## verify

The reader's note on this item names each significant finding with its test, or says none was found. A significant
finding is fixed test first; then the file is flagged (`code_review_status.py flag`).

## criteria

Acceptance test: none, a read by a fresh run is the deliverable; `python3 src/RimMandrake/rimflow/selftest_role_clone_level.py`
stays green after any fix.

## refs

file: src/RimMandrake/rimflow/role_clones.py
