# WORLD_RIVER_COLORS_1 — color the worldmap's rivers and liquids by what is in them

Owner, 2026-09-06, verbatim in intent: *"Red rivers in the mountains, turning immediately
to brackish green/brown in the jungles, and a toxic brown/blue near their end. Propane
would be a sort of slate cyan color, very alien indeed."*

## the fact this rests on (MEASURED)
Vanilla `RiverDef` has NO color field — its fields are `spawnFlowThreshold`,
`spawnChance`, `degradeThreshold`, `degradeChild`, `branches`, `widthOnWorld`,
`widthOnMap`, `debugOpacity`. The world draws every river with one shared material in the
river world-layer. So color is C#: a Harmony patch on the river world-layer (find the
class: `WorldLayer_Rivers` or its 1.6 successor — read the decompiled source, never guess)
that picks a material/tint per river SEGMENT.

## spec
1. **Segment classes** as data (rules must be data): `headwater` (red — the Contagion's
   runoff, `the_contagion.md` §3), `jungle` (brackish green/brown — the green squares
   below), `terminus` (toxic brown/blue — the dead-river ends and salt basins,
   `wasteland.md`), `propane` (slate cyan — the lake under Umbra, `the_propane_lakes.md`).
   Consider distinct `RiverDef`s per class chained by `degradeChild` (headwater →
   jungle → terminus) so the class is carried by the def, not computed each frame; else
   classify by the tile's biome at draw time.
2. **The patch**: per-segment material selection in the river layer; the same approach
   for the propane lake's world tiles (`LIQUID_BIOMES_MAP_1`) and any lake/ocean tint
   the four liquid biomes want (boiling ocean, brine seas).
3. **Map level** is already solved by terrain color (the Ocular red-water terrain
   precedent, `GU_RedWater*`) — reuse per biome; this item is the WORLD view.
4. Colors are the owner's: red · brackish green/brown · toxic brown/blue · slate cyan.
   Render a `worldview.py` mock first so he can see the palette before C# is written.
5. Naming per the tier grammar (`RUT_`); anti-bullseye irrelevant (rivers follow terrain).

## verify
The world map shows a red headwater turning green/brown into a jungle and brown/blue at
its salt end, and a slate-cyan propane lake; screenshots for the owner; no frame-rate
regression on the globe.
