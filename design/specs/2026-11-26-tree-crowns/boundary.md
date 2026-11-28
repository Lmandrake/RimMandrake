# BOUNDARY: tree crowns cast Direct Sun shade by the sun's geometry, Design Version 0.1.0

Code: `src/RimMandrake/CreatureBehaviors/Source/RM_SunHeatMath.cs` (the crown section: `DrawnSize`, `CrownFootprint`,
`CrownOpacity`, `RasterDisc`, `CastCrown`, `DrawsCrownShadow`, `CrownShadowQuad`, `CrownShadowAlpha`, `StampCrownShadow`; `RM_TreeCrown`), `RM_TreeCrownExtension.cs`, `RM_TreeCrownPatches.cs`,
`RM_ShadeOverlay.cs`, `RM_MapComponent_ShadeGrid.cs` (`IsShadeTree`, `DrawnSizeNow`, `CastCrownOf`, `CasterHeight`,
`ShadeCauseAt`, `OverlayShade`, `RequestPlantRecompute`, the crown lines of `Recompute`), the cause word of
`RM_Gizmo_SunLoad.cs`, the canopy rows of `RM_CreatureBehaviorsMod.cs`, and `Patches/RM_TreeCrowns_Giants.xml`.
Items: `TREE_SHADE_BUILD_CROWNS_ON_STILTS`, `TREE_SHADE_SELFTEST_PROVE_FOREST_IS_SHADE`, written 2026-11-26; the drawn
crown shadow, the owner's experiment on one tree type (card 2026-10-19 Q3 option 3):
`RIMMANDRAKE_TRY_RENDERED_CROWN_SHADOW_ON_ONE_GIANT_TREE`, 2026-11-27.
Design: `design/RimMandrake/tree_shade_model_2026-10-19.md` §4 (the model), §6 (the adopt-or-fall-back test). The owner's
card of 2026-10-19 (`TREE_SHADE_DECIDE_CROWNS_OR_LIGHTS_OUT`): projected crowns, full shade, overlay and mouseover plus
the ground-tint experiment, anything drawn 1.5 cells or more. Each promise below has a test of its name in
`src/RimMandrake/Utils/selftest_tree_crowns.py`. This page covers only these parts of the files named.

## ACCEPTS (the only inputs this is built for)

- **a-plant-drawn-big.** A plant whose drawn size at full growth (`graphicData.drawSize.x` × `visualSizeRange.max`) is
  at least 1.5 cells. It is a tree for shade: a trunk strip and a crown disc, both sized by its drawn size at its growth.
- **a-crown-override-on-the-plant.** `RM_TreeCrownExtension` on a plant's ThingDef, with any of `crownRadiusFactor`,
  `crownHeightFactor`, `opacity`; unset fields keep the planet defaults (0.8, 0.5, 1).
- **a-map-with-or-without-a-sun-vector.** With a sun vector the disc lands `min(16, hc × cot E)` cells down-sun; without
  one (a day/night world, directional shade off) it lies under the crown, for the shade-seeking animals.

## DOES NOT SURVIVE (not promised)

- **a-sprite-that-misleads.** A species not overridden whose art is not a crown on a trunk (a column, a mast) shades by
  the defaults; only the six measured giants carry their own factors.
- **a-crown-with-thickness.** The crown is a flat disc. The ground between the trunk and the disc's shadow is shaded only
  by the trunk strip.
- **a-felled-tree-within-half-a-second.** A tree that leaves the map asks for a recompute; requests run at most once per
  30 ticks (a forest fire would otherwise rebuild the grid every tick), so its shade can stand for up to 30 ticks.
- **a-low-sun-on-a-small-clearing.** At E below about 38 degrees the up-sun edge tree of a 7x7 clearing of full-grown
  3.8-cell trees shades the clearing's centre (geometry: hc × cot E + r reaches it). Design §6 T2 guessed 30 degrees.
- **a-drawn-shadow-without-a-sun-vector.** The drawn crown shadow follows the sun: on a map with no sun vector (a
  day/night world, directional shade off) it is not drawn, and the ground tint shows the greatbole's crown.
- **the-tint-on-any-renderer.** The ground tint draws at filth altitude and counts on plants and pawns writing depth;
  how it looks is the owner's look, not a test.

## PROMISES (each one is owed a test of the same name)

- **no-biome-carries-a-crown-field.** No BiomeDef under `src/`, and no patch value aimed at a BiomeDef, carries a crown
  or canopy shade field or `RM_TreeCrownExtension` (XML parsed as elements). So a tree shades the same in every biome.
- **the-giants-carry-their-measured-crowns.** `RM_TreeCrowns_Giants.xml` gives `RM_Greatbole`, `RM_Nogtyl`,
  `RSW_Plant_HydenockTree_Wild`, `RM_CorriskTree`, `RM_Veluthar` and `RM_Kaddrath` the factors measured from their art
  (`src/RimMandrake/HugeThings/tree_crowns_measured.json`, rounded to 0.01), each on a plant ThingDef under `src/`.
- **the-extension-sits-on-plant-thingdefs-only.** Every `RM_TreeCrownExtension` in XML under `src/` sits on a ThingDef.
- **the-canopy-settings-match-the-design.** Creature Behaviors has tree canopy shade (on), canopy shade strength (100%),
  the shade overlay button (on) and the ground tint (on), each saved with that default and named in the Direct Sun
  group; no per-biome canopy switch.
- **the-grid-casts-crowns-and-clears-on-despawn.** `Recompute` casts each tree's crown through
  `RM_SunHeatMath.CastCrown` at its growth and folds it into the cast layer; a shade tree's `DeSpawn` asks for a
  recompute; the readout, the sun-load line and the overlay read the grid's cause and the exposure array.

- **the-greatbole-alone-draws-its-shadow-down-sun.** Only `RM_Greatbole` carries `renderedShadow` true. The grid records
  its drawn shadow behind `RM_SunHeatMath.DrawsCrownShadow` (crowns on, a sun vector, the flag, a crown that casts) from
  the footprint it shades (`CrownShadowQuad` with the grid's own sun vector and cap), the drawer stamps the grid's list
  into one shadow layer by `StampCrownShadow`, which keeps the max (two crowns that overlap cast one shadow, not a
  darker one), and the ground tint skips the cells a drawn shadow owns (the setting `renderedCrownShadows`, on, in the Direct Sun
  group). Test: `drawn_shadow` of `selftest_tree_crowns.py`; the geometry is the C# case below.

## PROMISES KEPT BY THE C# SELFTEST

These are named cases of `src/RimMandrake/CreatureBehaviors/Source/SelfTest/Program.cs`, run by
`python3 src/RimMandrake/Utils/selftest_sun_heat.py`; each crown mutant of
`python3 src/RimMandrake/Utils/mutate_creaturebehaviors_fuzz.py "crown:"` is caught by one of them (7 of 7 on
2026-11-27; "radius halved" is caught by the T1 disc case, which writes r = k x s / 2 itself).

- "tree crowns: the same tree at the same E casts the same footprint in every biome" (T1)
- "tree crowns: at E 90 the disc lies under the crown; at E 14 it moves hc x cot 14, capped at 16" (T1)
- "tree crowns: a seedling casts by its drawn size, leafless thins it, the dial scales it, off casts only the trunk" (T1)
- "tree crowns: a synthetic dense Greentide forest is mostly shade, at least 60%" (T2, offline)
- "tree crowns: a 7x7 clearing is sunlit at its centre once hc x cot E + r falls short of its edge" (T2, offline)
- "tree crowns: removing a tree and recomputing clears its footprint; growing it widens it" (T4)
- "tree crowns: a 275x275 raster at Greentide density takes at most 15 ms" (T5; it prints the measured time)
- "tree crowns: a rebuilt grid from the same trees is bit-identical, in any order" (T6)
- "drawn crown shadow: the greatbole's soft disc sits on the cells its crown shades, down-sun, and only with a sun
  vector" (every shaded cell under the full-dark core, drawn 12 and 16, E 14, 40 and 89, four bearings; two
  overlapping discs read one shadow, alpha 1, seen red at alpha 2 on the additive blend)
