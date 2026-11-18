# RIMMANDRAKE_ISOLATE_OWNER_HOLD_STALL_TEST_FROM_BORROWED_ENV

## spec
`src/RimMandrake/rimflow/selftest_mod_owner_hold.py` `test_stall_reader` calls `ops_watch._q_designer` with no
`state_file`, so the reader opens `$RM_DISPATCHER_STATE/state.json`. An earlier test in the same file imports
`selftest_designer_chain`, which imports `selftest_dispatcher`, which points `RM_DISPATCHER_STATE` at an empty temp dir:
the ready concept's chain-cap read raises FileNotFoundError and the test reads FAIL (red on origin/main 5b5a5eb07d, run
standalone). The reader is right to treat an unreadable state as blind (its caller wraps it); the test is not isolated.
Fix the test: give `_q_designer` its own dispatcher state file (`{"roles": {}}`) through `q["state_file"]`.

## verify
`python3 src/RimMandrake/rimflow/selftest_mod_owner_hold.py` reads 0 FAIL (red on base: `test_stall_reader raised
FileNotFoundError`), and its stall check still fails if held concepts are counted (mutation: make the reader ignore
holds).

## criteria
- test_stall_reader runs on its own dispatcher state, independent of any imported selftest's environment
- the held-concepts check still catches a reader that counts held concepts

## refs
file: src/RimMandrake/rimflow/selftest_mod_owner_hold.py
