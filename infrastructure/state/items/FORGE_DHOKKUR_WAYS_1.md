# FORGE_DHOKKUR_WAYS_1 — dhokkur ways

Split from `FORGE_GPT_ENRICHMENT_1` §6 (owner-picked).

## already built

The dormant graphic swap exists. `RM_Dhokkur` seals between rains through `RM_CompForgeCycleDormancy`, renders
`RM_DhokkurDormant` through `RM_PawnRenderNodeWorker_DormantBody`, and wakes in the boiling rain.

## owed

1. Clues on a dormant dhokkur: converging gutter lines and worn depressions (art, or terrain around it).
2. Rain wake: a stone groan, and water pouring through its plates (sound plus flecks).
3. A path-memory MapComponent: the tracks it walks, kept across cycles and shown as glass-polished trail terrain
   (needs terrain art).
4. Walls in its way are shoved aside rather than destroyed.

## built offline 2026-10-06 (uncommitted at time of writing; unproven live)

`Source/RM_ForgeDhokkurWays.cs`: `RM_CompDhokkurWays` on `RM_Dhokkur` (owed 2, 4, and 1 as terrain) and
`RM_MapComponent_DhokkurPaths` (owed 3), with terrain `RM_DhokkurPolishedTrail` (`Defs/TerrainDefs/RM_DhokkurTrail.xml`,
temp-terrain layer, Odyssey's `SmoothVolcanicRock` texture darkened). Wake sounds are Core `Emergence_Quake` and
`EmergeFromWater`. Eight Mod Settings fields. The two open questions below became settings, with provisional
defaults: a shove moves the wall intact, then minifies it, then damages it (25%); tracks last forever, with fade off.
Still owed: bespoke trail and gutter art; a live run; north-star components (the fields are `UNCOVERED` in
`validation.py`).

## open questions (owner)

1. "Shoved aside": does the wall move to a free cell intact, get minified and dropped, or take damage? How much?
2. Do the tracks last forever, or fade if the dhokkur stops walking them?
