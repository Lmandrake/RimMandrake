using System;
using System.Collections.Generic;
using System.Reflection;
using HarmonyLib;
using RimWorld;
using RimWorld.Planet;
using UnityEngine;
using Verse;

namespace RimMandrake.Utinni.RiverColors
{
    // WORLD_RIVER_COLORS_1 (design/Jawa/worldbuilding/, owner 2026-09-06, verbatim:
    // "Red rivers in the mountains, turning immediately to brackish green/brown in the
    // jungles, and a toxic brown/blue near their end.").
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
    // DECISION: classify by tile at draw time, not by chained RiverDef.degradeChild.
    // The colour decision already happens once per tile inside Regenerate()'s loop
    // (`surfaceTile.tile` is right there), and RiverDef instances are shared,
    // engine-wide singletons -- degradeChild chains would need a NEW headwater/
    // jungle/terminus RiverDef and reassigned spawnFlowThreshold tuning to reproduce
    // what a live tile query gets for free. Classifying per tile is also what makes
    // the gradient continuous (owner, 2026-09-06: "add a gradient to it") instead of a
    // hard 3-colour seam at each RiverDef boundary.
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
    // Renamed from RiverColorsMod (MOD_OPTIONS_RETROFIT_1): that name now belongs
    // to the RimWorld `Mod` subclass in RiverColorsMod.cs, which owns Mod Settings.
    // This class is the Harmony bootstrap only — unrelated responsibility.
    [StaticConstructorOnStartup]
    public static class RiverColorsHarmonyLoader
    {
        static RiverColorsHarmonyLoader()
        {
            Harmony h = new Harmony("mandrake.rut.rivercolors");
            h.PatchAll(Assembly.GetExecutingAssembly());
            Log.Message("[RimMandrake.Utinni.RiverColors] loaded: WorldDrawLayer_Rivers "
                      + "will draw the headwater/jungle/terminus gradient.");
        }
    }

    public static class RiverGradient
    {
        // The owner's palette (item spec + the 2026-09-06 gradient amendment):
        // red headwater -> brackish green/brown jungle -> toxic brown/blue terminus,
        // interpolated continuously rather than three hard bands.
        //
        // MOD_OPTIONS_RETROFIT_1: the three anchor colours are now owned by
        // RiverColorsSettings (in-game Mod Settings, RGB sliders + swatch); these
        // are read live in ColorFor below, not cached here.

        // Grounded biome anchors (design/Jawa/worldbuilding/biomes/*.md; real defNames,
        // measured live via `measure csv` against world/ASHKARR_WORLDMAP_tiles.csv --
        // never invented): AB_OcularForest is "the Contagion" (the_contagion.md, red
        // spore/toxin runoff), AB_FeraliskInfestedJungle is the on-river "vicious
        // jungle" (ASHKARR_WORLD_DEFINITION.md hydrology), Wasteland is the dead salt
        // plain every river branch ends in (wasteland.md).
        private const string HeadwaterBiome = "AB_OcularForest";
        private const string JungleBiome = "AB_FeraliskInfestedJungle";
        private const string TerminusBiome = "Wasteland";

        // Rebuilt lazily, once per world (guarded by the World instance so a save
        // load / world regen invalidates the old graph automatically).
        private static World cachedWorld;
        private static Dictionary<int, float> tilePosition;

        public static Color32 ColorFor(PlanetTile tile)
        {
            EnsureBuilt();
            float t = 0.5f;
            if (tilePosition != null)
                tilePosition.TryGetValue(tile.tileId, out t);
            return Lerp3(
                RiverColorsSettings.headwaterColor,
                RiverColorsSettings.jungleColor,
                RiverColorsSettings.terminusColor,
                t);
        }

        private static void EnsureBuilt()
        {
            World world = Find.World;
            if (world == null || world == cachedWorld)
                return;
            cachedWorld = world;
            tilePosition = BuildTilePositions(world);
        }

        // One pass over every surface tile's potentialRivers, union-find into
        // networks (mirrors the same connected-components approach the offline
        // worldview.py mock used against the same river link data, so the in-game
        // result and the mock the owner reviewed first agree), then per network:
        // biome anchors pin t at 0 / 0.5 / 1, every other tile on that network gets
        // its elevation position normalized against the network's own min/max.
        private static Dictionary<int, float> BuildTilePositions(World world)
        {
            // WorldGrid.grid (World.cs:33) indexes straight to SurfaceTile
            // (WorldGrid.cs:69: `public SurfaceTile this[int tileID] => surface[tileID];`),
            // so no PlanetLayer/Tile cast is needed here.
            WorldGrid grid = world.grid;
            var parent = new Dictionary<int, int>();

            int Find_(int x)
            {
                while (parent[x] != x)
                {
                    parent[x] = parent[parent[x]];
                    x = parent[x];
                }
                return x;
            }
            void Union(int a, int b)
            {
                int ra = Find_(a), rb = Find_(b);
                if (ra != rb)
                    parent[ra] = rb;
            }

            for (int i = 0; i < grid.TilesCount; i++)
            {
                SurfaceTile st = grid[i];
                if (st?.potentialRivers == null)
                    continue;
                if (!parent.ContainsKey(i))
                    parent[i] = i;
                foreach (SurfaceTile.RiverLink link in st.potentialRivers)
                {
                    int j = link.neighbor.tileId;
                    if (!parent.ContainsKey(j))
                        parent[j] = j;
                    Union(i, j);
                }
            }

            if (parent.Count == 0)
                return null;

            var byRoot = new Dictionary<int, List<int>>();
            foreach (int tileId in parent.Keys)
            {
                int r = Find_(tileId);
                if (!byRoot.TryGetValue(r, out List<int> list))
                    byRoot[r] = list = new List<int>();
                list.Add(tileId);
            }

            var result = new Dictionary<int, float>();
            foreach (List<int> net in byRoot.Values)
            {
                float hi = float.NegativeInfinity, lo = float.PositiveInfinity;
                foreach (int tileId in net)
                {
                    float e = grid[tileId].elevation;
                    if (e > hi) hi = e;
                    if (e < lo) lo = e;
                }
                float span = (hi - lo) > 0.01f ? (hi - lo) : 1f;
                foreach (int tileId in net)
                {
                    BiomeDef biome = grid[tileId].PrimaryBiome;
                    string defName = biome?.defName;
                    float t;
                    if (defName == HeadwaterBiome) t = 0f;
                    else if (defName == TerminusBiome) t = 1f;
                    else if (defName == JungleBiome) t = 0.5f;
                    else t = Mathf.Clamp01((hi - grid[tileId].elevation) / span);
                    result[tileId] = t;
                }
            }
            return result;
        }

        private static Color32 Lerp3(Color32 a, Color32 b, Color32 c, float t)
        {
            if (t <= 0.5f)
                return Color32.Lerp(a, b, t / 0.5f);
            return Color32.Lerp(b, c, (t - 0.5f) / 0.5f);
        }
    }

    // Scoped to WorldDrawLayer_Rivers only -- WorldDrawLayer_Roads shares this exact
    // base-class method and must render unmodified.
    [HarmonyPatch(typeof(WorldDrawLayer_Paths), nameof(WorldDrawLayer_Paths.GeneratePaths))]
    public static class Patch_WorldDrawLayer_Paths_GeneratePaths
    {
        [HarmonyPrefix]
        public static void Prefix(WorldDrawLayer_Paths __instance, PlanetTile tile, ref Color32 color)
        {
            if (RiverColorsSettings.enabled && __instance is WorldDrawLayer_Rivers)
                color = RiverGradient.ColorFor(tile);
        }
    }
}
