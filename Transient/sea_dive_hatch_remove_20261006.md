# SEA_DIVE_HATCH_REMOVE_1 — NOT DONE, precondition unmet (2026-10-06)
- Layer exists (2db33bf23, on origin/main) but is Phase 1 only: RM_SeabedLayer.cs says "Descent is Phase 2".
- SEABED_DESCENT_ASCENT_1 is `proposed`, needs bridge: no ship descent/ascent exists.
- SEA_DIVE_HATCH_RETIRE_1 close reason: DESCENT_ASCENT_1 + FLOOR_GENERATORS_1 must land first; hatch "is the only route to the authored floors today".
- Hatch also still feeds RM_SeaDiveGenerators.xml (pocket generators) and RM_PlaceSeaDiveExit in 4 generators; deleting now strands the authored floors.
- No files changed.
