using System;
using RimWorld;
using Verse;

namespace RimMandrake.EnvironmentalHazards
{
    /// <summary>
    /// ROT_MOD_SETTINGS_WIRING_1: the seam that lets a biome mod's own Mod Settings screen gate the shared
    /// mechanics living here. A biome mod registers delegates at startup; with none registered every query
    /// answers "on, factor 1, no extra extension source", so this assembly behaves exactly as before.
    /// Keys: acceleratedRot, livingProduceHeat, warmGround, sheenExposure, sporeCloud, livePrepStrict.
    /// </summary>
    public static class RM_KitFronts
    {
        /// <summary>(mechanicKey, mapBiome) -> may the mechanic run on a map of this biome.</summary>
        public static Func<string, BiomeDef, bool> enabled;

        /// <summary>(mechanicKey, mapBiome) -> intensity multiplier (1 = shipped).</summary>
        public static Func<string, BiomeDef, float> factor;

        /// <summary>mapBiome -> a donor biome whose extensions apply to this map too (cross-biome opt-in), or null.</summary>
        public static Func<BiomeDef, BiomeDef> extensionDonor;

        public static bool Enabled(string key, BiomeDef biome)
        {
            return enabled == null || enabled(key, biome);
        }

        public static float Factor(string key, BiomeDef biome)
        {
            return factor == null ? 1f : factor(key, biome);
        }

        /// <summary>The biome's own extension, else the cross-biome donor's.</summary>
        public static T Extension<T>(BiomeDef biome) where T : DefModExtension
        {
            T own = biome?.GetModExtension<T>();
            if (own != null)
            {
                return own;
            }
            BiomeDef donor = extensionDonor?.Invoke(biome);
            return donor?.GetModExtension<T>();
        }
    }
}
