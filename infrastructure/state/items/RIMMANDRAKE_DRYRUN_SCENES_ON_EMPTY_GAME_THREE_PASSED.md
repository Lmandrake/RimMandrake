# RIMMANDRAKE_DRYRUN_SCENES_ON_EMPTY_GAME_THREE_PASSED

## spec
Guard "Scenes can ask", part 2, of `design/specs/2026-11-15-cheap-guards-at-every-door.md` (section 3.4). After RIMMANDRAKE_CERTIFY_BARS_BEFORE_JUDGE_RED_TEST_WENT_IN
(it adds a clause to that certificate).
Protects against: a check that reads PASS with nothing on the map. Evidence: FlowWorks visit 1 (USD 21.68): "several
drafts had passed with nothing on the map to test". Measured by the filing seat with a 25-line prototype: on the
visit-1 scene file (99ff70d91a) three rows read PASS when every bridge call answers a bare success (scene_fetch_fallen;
scene_pit_trap_raid PTR_control_open_pit_no_one_falls; scene_source_pays SRC_flow_stops_when_empty); on ed7e3b5389 one
still does, SRC_flow_stops_when_empty.

Build `src/RimMandrake/Utils/scene_empty_game.py` (`EmptyGame`, `rows_on_empty`, `vacuous`; contract in the test's
docstring), fix `SRC_flow_stops_when_empty` so it reads UNMEASURED or FAIL when the flow was never seen running, and add
the clause `asks_on_empty_game` to `judge_certificate.certify(..., to="in_game")` for the FlowWorks scene harness. A
mod whose scenes use another harness (the modcheck `Suite` scenes of Graffiti and Pyrelands) reads "did not run" with
the adapter it would need named; do not build that adapter here unless it is a few lines.

The builder does not edit the acceptance test; a clause believed wrong goes to the Conductor with the evidence.
A guard that cannot run says "did not run" and lets the work through; every refusal carries evidence, would_pass and
smallest_fix (standing_rulings.md, A refusal carries its path to pass).

## refs
item: RIMMANDRAKE_CERTIFY_BARS_BEFORE_JUDGE_RED_TEST_WENT_IN
new: src/RimMandrake/Utils/scene_empty_game.py
file: src/RimMandrake/FlowWorks/northstar/concept_scenes.py
file: src/RimMandrake/FlowWorks/northstar/selftest_fill_scenes_dig_first.py
file: src/RimMandrake/rimflow/acceptance/guard_empty_game_accept.py
file: design/specs/2026-11-15-cheap-guards-at-every-door.md

## verify
python3 src/RimMandrake/rimflow/acceptance/guard_empty_game_accept.py

## criteria
- A1: the acceptance test prints `PASS 8/8` and exits 0 (its backtest clause must find the three visit-1 rows).
- A2: the FlowWorks scene selftests stay green.
- A3: the close note says, for the modcheck-style scenes, what an adapter needs and files it as its own item with its test if it is more than a few lines.

## acceptance
Acceptance test: `python3 src/RimMandrake/rimflow/acceptance/guard_empty_game_accept.py` exits 0 with `PASS 8/8`.
Watched failing at ed7e3b5389: `FAIL 1/8`, exit 1 (no module; the one that passes reads the old scene file from git).
Passability: the prototype (same EmptyGame, same loader) gave exactly the three rows on 99ff70d91a and the one row on
ed7e3b5389; the certificate clause and the row fix are not yet built.
