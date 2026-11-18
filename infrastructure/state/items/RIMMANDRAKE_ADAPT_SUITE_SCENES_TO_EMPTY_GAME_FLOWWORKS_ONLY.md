# RIMMANDRAKE_ADAPT_SUITE_SCENES_TO_EMPTY_GAME_FLOWWORKS_ONLY

## spec
The certificate's `asks_on_empty_game` clause (RIMMANDRAKE_DRYRUN_SCENES_ON_EMPTY_GAME_THREE_PASSED, 9879c70256) runs
in-game scenes on an empty game only for FlowWorks' `concept_scenes.py` harness. Every other versioned mod's scenes are
modcheck `Suite` chains (`validation.py`: Pyrelands, LeaningScrub, GimmeSomeSlack, Graffiti, part of ExplosiveKnockback)
and read "did not run: no empty-game adapter". Build `scene_empty_game.suite_vacuous(suite)`: run each live chain on a
`modcheck.TestContext` over an empty session (every call a bare success; `things_at` empty; ticks a no-op) and list the
components whose verdict is PASS; then use it in `judge_certificate._asks_on_empty_game` for a live test whose file has a
module-level `suite` and whose entry names one of its chains. Loading a mod's validation.py must stay in its own bounded
process (as the FlowWorks path does) and read did_not_run when it cannot load. Graffiti and the five other held mods
(mod_owner_hold.json) are read, never edited, by this work.

## refs
item: RIMMANDRAKE_DRYRUN_SCENES_ON_EMPTY_GAME_THREE_PASSED
file: src/RimMandrake/Utils/scene_empty_game.py
file: src/RimMandrake/rimflow/judge_certificate.py
file: src/RimMandrake/Utils/modcheck/suite.py
new: src/RimMandrake/rimflow/acceptance/guard_empty_game_suite_accept.py

## verify
python3 src/RimMandrake/rimflow/acceptance/guard_empty_game_suite_accept.py

## criteria
- A1: the acceptance test prints `PASS 7/7` and exits 0.
- A2: `maturation.py certificate Pyrelands --to in_game` no longer lists validation.py under "no empty-game adapter"; its vacuous rows (or `[]`, looked and none) are in the close note.

## acceptance
Acceptance test: `python3 src/RimMandrake/rimflow/acceptance/guard_empty_game_suite_accept.py` exits 0 with `PASS 7/7`.
Watched failing on 9879c70256: `FAIL 4/7`, exit 1 (no `suite_vacuous`; the four that pass are "is not listed" clauses,
true when nothing is listed, which a correct build must keep). Medium: a TestContext over a fake session, plus the
certificate wiring.
