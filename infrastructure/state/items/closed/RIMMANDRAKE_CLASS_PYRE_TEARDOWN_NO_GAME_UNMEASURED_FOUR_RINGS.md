# RIMMANDRAKE_CLASS_PYRE_TEARDOWN_NO_GAME_UNMEASURED_FOUR_RINGS

## spec
`_tear_down` in `src/RimMandrake/Pyrelands/validation.py` records a teardown FAIL when the game has no current map
(the bridge refuses `jawa/map_info` and `jawa/weather_set` with `state.hasCurrentGame` False). With no game loaded, no
fire or locked weather can carry into a later chain, so this is a wrong check, not a mod fault. Four findings in two
days have this one cause (PYRELANDS_TEARDOWN_FAILS_85ADCD, PYRELANDS_TEARDOWN_FAILS_889CC1,
PYRELANDS_TEARDOWN_FAILS_085B13, and one more burn_line teardown on 2026-11-21). Each one rang the flow incident
`flow.untriaged_findings`.

The first fault each time is a SteveDesktop site load that fails (`UNMEASURED SITE: could not make a Pyrelands site
current`, the game drops to Entry). That fault is the Pyrelands visit run's to read; this ticket is the teardown class
only.

Fix: a refusal whose `state.hasCurrentGame` is False skips the fire and weather parts, with a note on stderr. The
settings restore still runs and still records FAIL when a setting does not come back.

## criteria
- No game loaded: `_tear_down` records no teardown FAIL.
- A loaded map where a teardown call is refused: the teardown FAIL stays.
- A loaded map where every call succeeds: no teardown FAIL.

## verify
Acceptance test: `python3 src/RimMandrake/Pyrelands/accept_teardown_no_game.py` from the repo root. On the base commit
it reads `2 PASS 1 FAIL` (watched 2026-11-22). A correct fix reads `3 PASS 0 FAIL`.

## refs
file: src/RimMandrake/Pyrelands/validation.py
file: src/RimMandrake/Pyrelands/accept_teardown_no_game.py
