# FEVERWOOD_BOUGH_SOIL_TERRAIN_1 — the crown cannot grow anything

## spec

🔴 **MEASURED 2026-09-23:** `src/RimUtinni/UtinniPatches/Defs/TerrainDefs/RUT_Boughway.xml`
ships **`fertility 0`** and an empty `<affordances>` block. ⇒ **Nothing can root in the
crown** — in a biome whose entire premise is that *the crown is where the life is*
(`the_fever_wood.md` §3, §7b).

**Owner ruling, 2026-09-23** (decision taken by question card): crown flora grows on a
**bespoke high-fertility terrain** painted along the boughways and trunk tops.

Authority: `design/Jawa/worldbuilding/biomes/fever_wood_deep_and_mud_2026-09-23.md` §6b.

## the build

✅ **The painting machinery already exists and needs no new C#.**
`RM_GenStep_RootCauseways` gained a multi-pass `additionalPasses`
(`List<RM_RootCausewayPass>`) field during `FEVER_WOOD_MECHANICS_1`'s F6 build, precisely
so one GenStep can run several differently-tuned profiles over the same anchor set. A
second profile painting bough-soil is the **existing shape**, not new machinery.

- New `TerrainDef` (working name *bough-soil*) with real fertility, Light/Medium
  affordances at most — ⛔ never Heavy: sheet ban 4 and `RUT_Boughway`'s own INVENTED
  affordance tier ("platforms yes, bunkers no").
- ⚠️ `basinTerrains` on that pass acts as an **allowlist**, which doubles as the exclude
  that keeps lanes off registered pools. Do not break that property —
  `RUT_MapComponent_TheTenant`'s terrain-grid scan loses a cell if a pool is overwritten.

## open, and NOT to be guessed

- **The fertility value.** Unset by the owner.
- **Which cells get it** — boughway decks only, or trunk tops as well. §6b's accepted cost
  is that crown plants exist only where the network reaches, so trunk tops away from a lane
  will be bare unless this pass paints them.

## why it blocks other work

🔴 **Eight of the 18 rows in `FEVERWOOD_FLORA_ROSTER_1` cannot grow until this lands** —
the whole crown layer, including `RM_Plennith` (which is the in-fiction *maker* of this
soil) and `RM_Cistrel` (the biome's only safe drinking water).

## Watch out

⛔ Editing `RUT_FeverWood.xml`'s `terrainsByFertility` is governed by
`BIOME_PAINT_ONCE_AT_THE_END_1`, and a `MayRequire`-gated defName referenced from the
shipped BiomeDef risks a dangling cross-reference — the same trap
`FEVER_WOOD_MECHANICS_1`'s continuation pass declined to walk into. Paint via the GenStep;
do not reach for the fertility table.
