# WORLDMAP_REPAIR_LOST_BIOMES_ROCKY_TEXTURES

Owner 2026-10-18 night: the worldmap "looked VERY strange" and "made of mountainous terrain, unlike before". FOUNDRY measured both offline (donor-free save vs CANONICAL_ASHKARR_START_2026-09-12.rws); owner approved filing for BENCH to fold into its current work.

1. LOST BIOMES. 1,903 of 21,872 surface tiles (8.7%) are vanilla TemperateForest in CANONICAL_ASHKARR_START_2026-10-18_DONORFREE.rws. The save still held the old biome-name hashes of three renamed biomes; on load they matched nothing, fell back to TemperateForest, and the game re-saved that. Tile counts match world/ASHKARR_WORLDMAP_tiles.csv (a record): RUT_ForsakenCrags 1135 (now the Abyss, RM_Abyss), RUT_PoisonForest 546 (the Cauldron, RM_Cauldron / RUT_Cauldron), ZBiome_Grasslands 222 (the Pyrelands, RM_Pyrelands). The other 19,969 tiles are identical. Confirm each target name live before repointing (RM_ vs RUT_ twin).
   Fix: repoint those three groups (live via world tools + world_commit, or offline in a COPY of the save); do not overwrite the adopted save without a backup. Tile ids: diff the biome grids of the two saves (hash 59367 / 65189 / 58457 in the 09-12 save).

2. ROCKY TEXTURES. Hilliness, elevation, rainfall, temperature, rivers, roads are byte-identical to 09-12 (hilliness: 9360 flat, 6035 small, 3698 large, 2424 mountainous, 355 impassable), so the mountainous look is rendering, INFERRED not seen. Cause: BIOME_WORLDTEX_BUILD_EVERY_BIOME_A_FACE (ede2336a5) put 512px procedural placeholder textures on all 62 biomes; several read as relief at planet scale: Stillsand/ExtremeDesert (3969 tiles, ridged stripes), LongShade/Desert (2390, boulders with long shadows), Wasteland (1853, rocks), SleepingIce (1506, diagonal streaks), WeepingStones, CrackedLands, ChillCrater. Deployed to the game (UtinniPatches, byte-identical to src).
   Fix: look at the world in game first against Transient/biome_worldtex_2026-10-18/sheet.png; then flatten the high-contrast ones toward low-contrast colour fields (generator Transient/biome_worldtex_2026-10-18/gen.py, apply.py), redeploy. Keep each mean colour.

Owed: L4 owner looks at the world map after both.
