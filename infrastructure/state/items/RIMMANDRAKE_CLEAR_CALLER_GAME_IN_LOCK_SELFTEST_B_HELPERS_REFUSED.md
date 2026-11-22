# RIMMANDRAKE_CLEAR_CALLER_GAME_IN_LOCK_SELFTEST_B_HELPERS_REFUSED

`selftest_game_lock.py` inherits the caller's `RM_GAME_INSTANCE`; from a detached game-b helper it reads game b, so it
fails and `./publish` refuses that helper's commit. Caused by RIMMANDRAKE_DRIVE_GIMMESOMESLACK_IN_GAME_VISIT_THREE_RUN_TWO.

## spec
Measured 2026-11-21 ~8:05 PM PST in the GSS visit-3 clone (env RM_GAME_INSTANCE=b, game b's bridge held by this run):
`python3 src/RimMandrake/rimflow/selftest_game_lock.py` -> 3 failed ("a game a run record names is shown with the lock's
reading of now", "the tick's free-game reading is the lock's", "its holder gone, the tick reads game a free at once");
under `./publish` the python.exe timing check also read 103-112 ms (limit 50). With the three game variables unset: 0
failed. Cause: the in-process checks do `os.environ.update(bx.env)`, which adds and never removes the caller's game.
Fix: the selftest pops the caller's game variables at import.

## refs
file: src/RimMandrake/rimflow/selftest_game_lock.py

## verify
Acceptance test: `RM_GAME_INSTANCE=b python3 src/RimMandrake/rimflow/selftest_game_lock.py` -> `0 failed`.
Seen red on 83fb77dd87: `3 failed`.

## criteria
The selftest reads the same with and without a caller's RM_GAME_INSTANCE.
