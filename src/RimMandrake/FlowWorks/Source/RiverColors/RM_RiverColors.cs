using HarmonyLib;
using RimWorld;
using RimWorld.Planet;
using UnityEngine;
using Verse;

namespace RimMandrake.FlowWorks.RiverColors
{
    // WORLD_RIVER_COLORS_1 (owner 2026-09-06) gave every river an elevation gradient; RIVER_WATER_BY_BIOME (below,
    // 2026-10-20) replaced it with water by biome after the owner saw it in game.
    //
    // MECHANISM (read off decompiled 1.6 source via mcp__rimsage__read_csharp_symbol,
    // never guessed):
    //   RiverDef (RimWorld/RiverDef.cs) has NO colour field -- only
    //   spawnFlowThreshold/spawnChance/degradeThreshold/degradeChild/branches/
    //   widthOnWorld/widthOnMap/debugOpacity.
    //   WorldDrawLayer_Rivers.Regenerate() (RimWorld/Planet/WorldDrawLayer_Rivers.cs)
    //   iterates every world tile once and calls the base class's
    //   WorldDrawLayer_Paths.GeneratePaths(subMesh, tile, outputs, riverColor,
    //   allowSmoothTransition: true) TWICE per tile (fill mesh, then border mesh),
    //   always passing the same private readonly `riverColor` field.
    //   GeneratePaths ALREADY writes a genuine per-vertex mesh colour
    //   (LayerSubMesh.colors) -- full alpha at the tile-centre/path-midpoint verts,
    //   MutateAlpha(0) at the fading path-end verts -- it is simply called with one
    //   constant colour for the whole world. So no mesh-authoring change is needed:
    //   only the colour ARGUMENT has to vary per tile.
    //
    // DECISION: classify by tile at draw time, not by chained RiverDef.degradeChild: the colour decision already
    // happens once per tile inside Regenerate()'s loop, and RiverDef instances are shared engine-wide singletons.
    //
    // THE PATCH: WorldDrawLayer_Paths.GeneratePaths is one non-virtual method shared
    // by every WorldDrawLayer_Paths subclass (WorldDrawLayer_Roads calls it too), so
    // the prefix scopes itself to `__instance is WorldDrawLayer_Rivers` and leaves
    // roads untouched. Color32 color is declared `ref` in the prefix signature --
    // Harmony's documented mechanism for a prefix to substitute the value an
    // otherwise-unmodified original method receives for a value-type parameter.
    //
    // OUT OF SCOPE, confirmed by source, not guessed: the propane lake's world-map
    // tint (RUT_PropaneLake) and any other biome's world colour is NOT this
    // mechanism. WorldDrawLayer_Terrain.Regenerate() (RimWorld/Planet/
    // WorldDrawLayer_Terrain.cs) picks `tile.PrimaryBiome.DrawMaterial` per tile --
    // DrawMaterial is built from the BiomeDef's own <texture> field (Source/RimWorld/
    // BiomeDef.cs), which is already a live lever
    // (src/RimUtinni/UtinniPatches/Defs/BiomeDefs/RUT_PropaneLake.xml currently points
    // it at World/Biomes/Jawa_SickWater). Retinting the lake is a texture-art task on
    // that field, not a C# patch, and is left undone here.
    // RIVERCOLORS_MERGE_RAINBOW_JOINS_THE_FLOW (owner 2026-10-16: "Add river colors into flowworks as part of
    // adding liquids to the world."): was the standalone mod mandrake.rut.rivercolors (src/RimUtinni/RiverColors).
    // No Harmony bootstrap of its own any more: RM_FlowWorksHarmony (RM_Patch_SuperdeepShooting.cs) applies every
    // [HarmonyPatch] class in this assembly, this one included, under the Harmony id mandrake.rm.flowworks.
    // Settings are the "River colours" section of FlowWorks' Mod Settings (RM_RiverColorsSettings).

    // RIVER_WATER_BY_BIOME (2026-10-20). Owner, looking at the in-game map: "the river is shown brown and red. Odd
    // colors for roads and rivers." The 2026-09-06 gradient coloured EVERY river by elevation (red high, olive-brown
    // middle), because its three anchors (AB_OcularForest, AB_FeraliskInfestedJungle, Wasteland) match no tile of the
    // planet. Now a river is WATER (cool blue-grey) everywhere, and only inside the biomes whose sheet says its water is
    // not clean does it take that biome's tint (design/Jawa/worldbuilding/biomes/):
    //   RM_Contagion     blood red    -- the_contagion.md R-H7 "The red water sterilizes on the way down"
    //   RM_Miasma        brackish     -- the_miasma.md: the dying sea's muck channels, "everything ends up here"
    //   RM_Wasteland     toxic green  -- wasteland.md: hypersaline salt basins, the dead-river termini
    //   RM_RustCathedral verdigris    -- the_rust_cathedral.md: the captured river is its coolant canals
    // The tint stops at the biome border (each tile draws its own half of every river link), which is the story: the
    // Contagion's water arrives in the lowlands clean. The bank is drawn by Baroque Biomes' RM_WorldPaths (water x 0.22).
    // Colour contrast: fill dE76 >= 20 and bank WCAG >= 3:1 against every face it crosses (world_paths_readable doc).
    public static class RiverTint
    {
        public static Color32 ColorFor(PlanetTile tile)
        {
            WorldGrid grid = Find.World?.grid;
            BiomeDef biome = null;
            if (grid != null && tile.tileId >= 0 && tile.tileId < grid.TilesCount)
                biome = grid[tile.tileId]?.PrimaryBiome;
            switch (biome?.defName)
            {
                case "RM_Contagion": return RM_RiverColorsSettings.contagionColor;
                case "RM_Miasma": return RM_RiverColorsSettings.miasmaColor;
                case "RM_Wasteland": return RM_RiverColorsSettings.wastelandColor;
                case "RM_RustCathedral": return RM_RiverColorsSettings.rustCathedralColor;
                default: return RM_RiverColorsSettings.waterColor;
            }
        }
    }

    // Scoped to WorldDrawLayer_Rivers only -- WorldDrawLayer_Roads shares this exact
    // base-class method and must render unmodified.
    [RimMandrake.Shared.PatchFeature("River colours on the planet map", typeof(RM_RiverColorsSettings), "riverColorsEnabled")]
    [HarmonyPatch(typeof(WorldDrawLayer_Paths), nameof(WorldDrawLayer_Paths.GeneratePaths))]
    public static class Patch_WorldDrawLayer_Paths_GeneratePaths
    {
        [HarmonyPrefix]
        public static void Prefix(WorldDrawLayer_Paths __instance, PlanetTile tile, ref Color32 color)
        {
            if (RM_RiverColorsSettings.riverColorsEnabled && __instance is WorldDrawLayer_Rivers)
                color = RiverTint.ColorFor(tile);
        }
    }
}
