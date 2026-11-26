Mirroring a polygon for the other side (x -> 1 - x) flips its winding; reverse the vertex order too, or Unity culls it as a back face and the piece silently draws nothing (FlowWorks one-sheet water: the east walls of stations 20 to 22 drew dry, 2026-11-25). A SelfTest that asserts every emitted polygon's signed area has the floor quads' sign catches it offline.
item: RIMMANDRAKE_DRILL_FLOWWORKS_WATER_LAYERS_HE_SAW_STACKED_BLUE
home: skills/rimworld-modding/references/project-engine-facts.md
