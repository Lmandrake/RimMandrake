# WEEPINGSTONES_HEAT_WINDHOUR_TEXT_1 — declare the heat kind (sun angle from latitude, overhang shade) and rewrite the twelve dead "wind-hour" sentences

Caused by `WEEPINGSTONES_SCORING_SITTING_1` (turn 1). **Free tier**, `mandrake.rm.weepingstones`. Design:
`design/Jawa/worldbuilding/biomes/weepingstones_bedazzle_review_2026-10-02.md` §1 (f) and "one more", §4 row 0, §8. Ruling: build first, land what was decided plus the giant's story
(decision taken by question card 2026-10-02 12:53 PDT; the card's text: *set its heat by the sun's height,
shade under the overhangs is what saves you at noon*). One-heat law (owner, 2026-09-29/30: *"It can't be a new
"kind" of heat."*; *"The biome takes its sun angle from its latitude"*). Wind-hour ruled DEAD (*"nah"*, 2026-09-24).

## What exists

- `RM_WeepingStones` carries **no** `RM_SunHeatExtension` (median 35 °C, p90 57 °C, max 63.5 °C, sheet §0).
- `RM_SunHeatExtension` (`RimMandrake.CreatureBehaviors`) with `overheadAboveElevationDegrees`; shape in
  `src/RimMandrake/Stillsand/Defs/BiomeDefs/RM_Stillsand_Biome.xml`. `RM_MapComponent_ShadeGrid.ShadeAt` already
  treats overhangs and roofs as shade. System: `SOLAR_HEAT_EXPOSURE_1`.
- **12** def descriptions in `mandrake.rm.weepingstones` name the cancelled wind-hour (the mirrik's dance, the
  skarrin's arcs, the vizhik's escape, the murrin's rings and others; files: `RM_WeepingStonesNatives.xml`,
  `RM_StockedPoolFauna.xml`, `RM_StockedPoolCatchItems.xml`, `RM_WeepingStonesFish_Items.xml`,
  `RM_PoolBreedingStock.xml`) plus `RM_MapComponent_PoolStock.cs`'s *"One pulse is roughly a wind-hour's worth"*.

## spec

1. `RM_SunHeatExtension` on `RM_WeepingStones`, sun angle from the **tile's latitude** (overhead on high-sun
   tiles, low sun near the terminator), never region prose. `heatOffsetC` an `// INVENTED` first value for the
   owner-watched tuning. One def carries one kind; the vent-fed seep oases are not split (§1 f). Vanilla
   temperature only. Add the Weeping Stones to `SOLAR_HEAT_EXPOSURE_1`'s list of extreme-heat biomes.
2. Rewrite every "wind-hour" sentence to what actually happens in game (the mirrik dance over pools at dusk, the
   murrin's rings when fed, the vizhik's escape when a pen is overfull), never to a daily event. Comment in the
   C# says "per pulse". Text only; no behaviour change.
3. Do not add the twin's text; `RUT_WeepingStones` is frozen.

## criteria

- Loaded `RM_WeepingStones.modExtensions` contains `RM_SunHeatExtension` (def read).
- Live: a colonist standing in the open at noon on a high-sun Weeping Stones tile gains vanilla heat exposure
  faster than one under an overhang (`ShadeAt` true); no new hediff appears.
- Case-insensitive search for "wind-hour" / "wind hour" in `src/RimMandrake/WeepingStones` returns nothing.
