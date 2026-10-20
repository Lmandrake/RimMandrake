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
    // WorldIce; else WorldTerrain. WorldIce draws a dark hex-plate ice look over the biome
    // texture, so a no-roads/no-rivers DESERT (RM_Stillsand, the substellar 18% of Ash'karr)
    // and RUT_Umbra rendered as dark grey hexes (in-game shot 2026-10-20). The flags stay as
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
            foreach (BiomeDef b in DefDatabase<BiomeDef>.AllDefsListForReading)
            {
                if (!IsOurs(b.defName) || b.texture.NullOrEmpty()) continue;
                if (b.allowRoads || b.allowRivers) continue;          // already WorldTerrain
                if (b == BiomeDefOf.Ocean || b == BiomeDefOf.Lake) continue;
                Material m = new Material(WorldMaterials.WorldTerrain);   // MaterialAllocator.Create is internal; it wraps this
                m.mainTexture = ContentFinder<Texture2D>.Get(b.texture);
                cached.SetValue(b, m);
                swapped.Add(b.defName);
            }
            if (swapped.Count > 0)
                Log.Message("[RimMandrake.Biomes] world terrain shader on " + swapped.Count + " no-road/no-river biomes: " + string.Join(", ", swapped));
        }

        static bool IsOurs(string n)
        {
            return n != null && (n.StartsWith("RM_") || n.StartsWith("RSW_") || n.StartsWith("RUT_"));
        }
    }
}
