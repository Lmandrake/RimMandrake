# RIMMANDRAKE_REBUILD_MOAT_SCENE_FAKE_AFTER_BRIM_FULL_REWRITE

## spec
`src/RimMandrake/FlowWorks/northstar/selftest_moat_scene.py` is red on origin (red census 2026-11-22,
RIMMANDRAKE_CENSUS_RED_TESTS_ON_ORIGIN_SEVEN_REPORTED_NONE_OWNED). Cause: eb15c22de9 (2026-11-21, sc_moat_raid: brim-full
3 m moat, control ends at the crossing, capture by the pit-trap idiom) rewrote 136 lines of the scene in
`northstar/concept_scenes.py`, and the selftest's fake game still models the old scene. The census run repaired two
layers at b9ebf18482 (the fake now answers `jawa/flowworks_excavation_drive` with depth and waterM, and takes hinge A or
B in `ProofMakeDrawbridge`). Still red: the healthy fake no longer reads every row PASS (the capture rows and the
staging row), because the fake does not model the pit-trap capture and the crossing control.
Fix: bring the fake in line with the scene as eb15c22de9 wrote it. Change the fake only, never the scene's rows or
the bars. Each planted case in the file (raiders stop at the bank, a sluice that drains nothing, a dry ring that holds
nobody, fire_raid answering success) must still read as its docstring says.

## verify
Offline. No game.

## criteria
Acceptance test: `python3 src/RimMandrake/FlowWorks/northstar/selftest_moat_scene.py` exits 0 and prints
`selftest_moat_scene: ok`. Seen red at e06bd5f6e5 (4 FAIL lines, first: "healthy fake ... every row PASS").

## refs
file: src/RimMandrake/FlowWorks/northstar/selftest_moat_scene.py
file: src/RimMandrake/FlowWorks/northstar/concept_scenes.py
