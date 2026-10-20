using System.Collections.Generic;
using System.Reflection;
using RimWorld;
using UnityEngine;
using Verse;
using RimWorld.Planet;

namespace RimMandrake.Biomes
{
    // WORLDMAP_BIOME_APPEARANCE_1: our biomes paint the globe with the TERRAIN shader.
    //
    // Vanilla BiomeDef.DrawMaterial (1.6) picks the material from gameplay flags, not from
    // anything about looks: Ocean/Lake -> WorldOcean; (!allowRoads && !allowRivers) ->
    // WorldIce; else WorldTerrain. WorldIce draws an ice look over the biome texture, wrong for a
    // no-roads/no-rivers DESERT (RM_Stillsand, the substellar 18% of Ash'karr) and RUT_Umbra.
    // (The dark grey hexes seen in game 2026-10-20 were NOT this: they were the sea-floor layer
    // drawing through the planet; see Patch_SeabedLayerCoplanarHide.cs.) The flags stay as
    // they are (they mean "no roads, no rivers"); this only swaps the material, once, at
    // startup, for BiomeDefs in our three tiers (RM_/RSW_/RUT_). It fills the def's private
    // cachedMat exactly as DrawMaterial would have, with the terrain material instead.
    [StaticConstructorOnStartup]
    public static class RM_WorldTerrainShader
    {
        static RM_WorldTerrainShader()
        {
            FieldInfo cached = typeof(BiomeDef).GetField("cachedMat", BindingFlags.Instance | BindingFlags.NonPublic);
            if (cached == null)
            {
                Log.Warning("[RimMandrake.Biomes] BiomeDef.cachedMat not found; world terrain shader swap skipped.");
                return;
            }
            var swapped = new List<string>();
            var water = new List<string>();
            foreach (BiomeDef b in DefDatabase<BiomeDef>.AllDefsListForReading)
            {
                if (!IsOurs(b.defName) || b.texture.NullOrEmpty()) continue;
                if (b == BiomeDefOf.Ocean || b == BiomeDefOf.Lake) continue;
                // WORLDMAP_IN_GAME_AUDIT 2026-10-20: our seas are water, so they get the OCEAN
                // material. Vanilla gives WorldOcean to Ocean/Lake by def identity only, so every
                // sea of ours drew as flat land: WorldTerrain, and the terrain layer clamps any
                // non-ocean vertex below 0 m to 0 m, throwing the -350 m depth away. Seen in game
                // as the grey Grey Sea. WorldOcean reads that depth from the mesh uvs.
                if (b.isWaterBiome)
                {
                    Material w = new Material(WorldMaterials.WorldOcean);
                    w.mainTexture = ContentFinder<Texture2D>.Get(b.texture);
                    cached.SetValue(b, w);
                    water.Add(b.defName);
                    continue;
                }
                if (b.allowRoads || b.allowRivers) continue;          // already WorldTerrain
                Material m = new Material(WorldMaterials.WorldTerrain);   // MaterialAllocator.Create is internal; it wraps this
                m.mainTexture = ContentFinder<Texture2D>.Get(b.texture);
                cached.SetValue(b, m);
                swapped.Add(b.defName);
            }
            if (swapped.Count > 0)
                Log.Message("[RimMandrake.Biomes] world terrain shader on " + swapped.Count + " no-road/no-river biomes: " + string.Join(", ", swapped));
            if (water.Count > 0)
                Log.Message("[RimMandrake.Biomes] world ocean shader on " + water.Count + " water biomes: " + string.Join(", ", water));
        }

        static bool IsOurs(string n)
        {
            return n != null && (n.StartsWith("RM_") || n.StartsWith("RSW_") || n.StartsWith("RUT_"));
        }
    }
}
