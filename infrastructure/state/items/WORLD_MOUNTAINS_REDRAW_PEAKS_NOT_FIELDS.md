# WORLD_MOUNTAINS_REDRAW_PEAKS_NOT_FIELDS

Owner 2026-10-20 (after seeing the soft hills in game): "Mountains look ok, better than the sharp stamp from before, but now they are barely visible. Mountains dont look like mountains they look like farm fields or something. Any chance mountains could actually look like mountains?" and "Can we study the other worldmap graphics mods to see what they do and how they do it? Maybe we just need to get some inspiration."

Context: soft hill atlas (1d9bb09c0, RM_WorldLook.ApplyHills, TerminalBiomes RM_Hills) swapped onto the four vanilla hill materials; vanilla hill quads are a 2x2 atlas with RANDOM ROTATION, so a lit/shaded side cannot follow the sun without a custom mesh/shader. Study of other world-map mods: design/Jawa/worldbuilding/worldmap_mods_study_2026-10-20.md (agent running at filing).

NEXT: read the study, then design peaks that read as mountains (silhouette, lit/shade split along the substellar sun direction, ridge texture, snowcaps where cold), decide whether a rotation-free mesh/shader is needed, build with Mod Settings toggle, preview offline, deploy and judge in game.
