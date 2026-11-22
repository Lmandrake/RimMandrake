# RIMMANDRAKE_TRACE_FLOWWORKS_AWAKE_PRISONER_MEAL_SKIPPED_ONE_RUN_IN_TWO

Found by FlowWorks in-game visit 5 (item RIMMANDRAKE_DRIVE_FLOWWORKS_IN_GAME_ACCEPTANCE_VISIT_FIVE), 2026-11-21.

## spec

`sc_hole_prison` (bar `drained_hole_is_a_prison`) ran twice on game a, flowworks tier, one build (bdd56c6ff6), calm site
verified both times. Run 1 (7:03 PM PST) FAILed at `concept_scenes.py:298`: "awake prisoner gets no ordinary meal
delivery". The prisoner stood (downed False), food 0.65 set to 0.1, rest 0.74; `Care(warden, prisoner, deliver, start)`
returned no DeliverFood job. Run 2 (7:07 PM PST) PASSed the whole scene. Visit 4 PASSed it once on the same build.
Evidence: `design/concepts/FlowWorks/version/in_game/visit_5/evidence/sc_hole_prison_20261121T190312.json` (FAIL) and the
later `sc_hole_prison_*.json` (PASS). Cause unknown: MOD (the warden food job giver for a pit prisoner) or HARNESS (the
order of the need set, the item clear and the job scan) [guess ~50%]. The job that `Care` returned was not recorded.

## verify

First make `concept_scenes.py` record the job string that `Care` returned, then run the scene until it fails once and read it.

## criteria

Acceptance test: `sc_hole_prison` PASS on three consecutive runs on one build (`python.exe -u
src/RimMandrake/FlowWorks/northstar/concept_scenes.py --scene scene_hole_prison --out <json>`, bridge held, flowworks
tier). Seen red: 1 of 2 runs on 2026-11-21.

## refs

file: src/RimMandrake/FlowWorks/northstar/concept_scenes.py
