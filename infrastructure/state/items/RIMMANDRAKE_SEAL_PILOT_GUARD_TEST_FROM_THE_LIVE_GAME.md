# RIMMANDRAKE_SEAL_PILOT_GUARD_TEST_FROM_THE_LIVE_GAME

## spec

`src/RimMandrake/rimflow/acceptance/guard_pilot_launch_live_run_accept.py` says it is offline on a temp root, but its
`in_game: nothing live still launches` row calls `maturation_dispatch.pilot_launch`, whose `pick_game` reads the real
driver lock when no `bridge` stand-in is passed. So whenever any helper holds a game, the row fails and every `./publish`
touching a pipeline file is refused (measured 2026-11-17 08:4x: game a held by BENCH for Gimme Some Slack; the publish
of RIMMANDRAKE_BUILD_ART_BRIEF_CALIBRATION_NOTHING_TO_RUN was refused on it). Fix: the test passes a stand-in
`bridge` reading in its fx, as selftest_maturation_dispatch.py does.

## verify

Acceptance test: `python3 src/RimMandrake/rimflow/acceptance/guard_pilot_launch_live_run_accept.py` prints `PASS 7/7`
while a game is held. Watched failing on the base (2026-11-17, game a held): `FAIL 1 of 7`.

## criteria

- The guard test reads no live game state.

## refs

file: src/RimMandrake/rimflow/acceptance/guard_pilot_launch_live_run_accept.py
