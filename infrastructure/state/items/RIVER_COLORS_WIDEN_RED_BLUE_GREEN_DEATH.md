# RIVER_COLORS_WIDEN_RED_BLUE_GREEN_DEATH

FlowWorks (BENCH owns all FlowWorks). Filed by FOUNDRY from the owner's card, 2026-10-24 07:55 PDT: "FlowWorks is supposed to allow world rivers to be in any color as well. We have need for that in some places. Our rivers are technically supposed to start red (in the mountains) and then immediately turn bluish, followed by a quick fade to thick green and then death. Not sure how much of that is realizable, but there is the vision."

## spec
What FlowWorks does today (read 2026-10-24, `src/RimMandrake/FlowWorks/Source/RiverColors/RM_RiverColors.cs`): a Harmony prefix on `WorldDrawLayer_Paths.GeneratePaths`, scoped to `WorldDrawLayer_Rivers`, swaps the colour argument per TILE. `RiverTint.ColorFor(tile)` is a switch on the tile's biome: RM_Contagion, RM_Miasma, RM_Wastes, RM_RustCathedral each get a settings colour, everything else gets `waterColor`. Vanilla already writes per-vertex colour (full alpha mid-path, alpha 0 at path ends), so only the argument varies. `RiverDef` has no colour field.
What is realizable:
- Any colour on any tile: yes, cheaply. Replace the biome switch with a lookup (per-tile override table, e.g. a WorldComponent or a def list of tile->colour, falling back to the biome rule).
- Red at source -> bluish -> quick fade to thick green -> dies: yes, as per-tile steps. Walk each river downstream from its head (links are known at Regenerate) and colour by steps-from-source: tile 0 red, 1 bluish, 2-3 thick green, then fading. Steps are hex-sized, because one tile draws one colour; a smooth ramp inside a tile needs a postfix that recolours the submesh's vertices (more work, still feasible).
- "Then death": visually yes (alpha and width fade to a dry trace on the last tiles). An actual end of the river is a link edit (authoring, not worldgen), separate from colour.

Ask: (1) per-tile colour override in FlowWorks' river colours; (2) the source ramp red -> bluish -> thick green -> fade/dies, keyed by steps from each river's head; (3) settings for the ramp colours. Look-side river drawing (width taper, banks, mouths) is FOUNDRY's RIVERS_ROADS_REDESIGN_WORTH_LOOKING_AT; agree the colour hand-off there (RM_WorldPaths draws the bank as water x 0.22).

## verify
Offline: a render of the ramp along a real Ash'karr river (links CSV) at three zooms; then an owner look in game.

## kind
C# in FlowWorks (winbuild + .srchash).

## toggles
Existing FlowWorks "River colours" section; ramp on/off as a new bool there.
