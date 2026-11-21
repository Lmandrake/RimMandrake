# RIMMANDRAKE_HIDE_FLOWWORKS_PIT_WALLS_UNDER_CONCEALED_COVER

From his FlowWorks walk of 2026-11-20: `design/RimMandrake/validation_holding/flowworks_walk_20261120.md` row #17 (his words, the picture, the station).

## spec

A wholly covered concealed pit draws its walls, wall light and black outline over the cover's ground print. The cover prints the surrounding terrain in that terrain's own material (render queue 2000 + precedence, `src/RimMandrake/FlowWorks/Source/Pits/Building_PitCover.cs:276-281`); the pit faces, light and outline use queues 2440-2449 (`Source/Superdeep/RM_FaceMaterial.cs:28-46`), so they draw after it whatever the altitude, and `RM_ExcavationWalls` never asks whether a square is covered [measured]. Bar `covered_pit_springs`: "the pit is visible as a pit under its cover" is its false pass.

## verify

Stage a covered 3x3 pit (planks over a 2 m pit, every square lidded) beside bare ground; capture it zoomed. Also an open pit with one lid (a lid in an open pit shows its planks by design) as the control.

## criteria

Acceptance test: a live zoomed capture of the covered pit shows no outline or wall pixels inside the cover, and the control still shows its pit. Red today by his picture 6; not yet watched red by a test (the game was his).

## absorbed

Absorbed by RIMMANDRAKE_REBUILD_FLOWWORKS_PITS_AS_RELATIVE_TERRAIN (his card 2026-11-20, FlowWorks 0.1.0): the same draw layer is rebuilt; fix this there, in the same run, and close both on its sha.
