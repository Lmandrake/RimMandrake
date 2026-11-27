using System.Collections.Generic;
using RimWorld;
using Verse;

namespace RimMandrake.Pyrelands
{
    /// <summary>
    /// What every Pyrelands mechanic reads first: RM_PyrelandsSettings.pyrelandsEnabled ("Mod enabled"), a plain on/off for
    /// the whole mod with no biome in it. Each mechanic then reads its own switch and its own conditions (a fire near, scorchable
    /// ground, a grass-watered animal), never the map's biome (bar mechanics_switch_plain_no_biome, his cards of 2026-11-21).
    /// The Baroque Biomes shell's per-biome "Pyrelands" toggle no longer gates any mechanic (conversion list row code 10).
    /// </summary>
    public static class PyrelandsMechanicsGate
    {
        public static bool On => RM_PyrelandsSettings.pyrelandsEnabled;
    }

    /// <summary>
    /// A biome's own fire traits: biome DATA, read off the BiomeDef like its weather table and its plant and animal roster, so
    /// another biome can opt in by XML (Patches/RM_Pyrelands_BiomeTraits.xml gives RM_Pyrelands all three). No trait here is a
    /// mechanic's gate: a mechanic runs wherever its conditions hold; these say what the biome itself brings.
    /// </summary>
    public class RM_PyrelandsBiomeTraits : DefModExtension
    {
        /// <summary>The biome keeps a burn standing: the fire clock sends fronts and a quiet map is re-lit out in the grass.</summary>
        public bool standingBurn;
        /// <summary>The biome's ordinary rain falls as black rain (its weather is ash and cinders, never plain rain).</summary>
        public bool ordinaryRainFallsBlack;
        /// <summary>Only the biome's own animals arrive: herd migrations and manhunter packs pick from its roster alone.</summary>
        public bool onlyOwnAnimalsArrive;

        private static readonly Dictionary<BiomeDef, RM_PyrelandsBiomeTraits> cache = new Dictionary<BiomeDef, RM_PyrelandsBiomeTraits>();

        /// <summary>The biome's traits, or null. Cached per BiomeDef (defs do not change after load).</summary>
        public static RM_PyrelandsBiomeTraits Of(BiomeDef biome)
        {
            if (biome == null) return null;
            if (!cache.TryGetValue(biome, out RM_PyrelandsBiomeTraits t))
            {
                t = biome.GetModExtension<RM_PyrelandsBiomeTraits>();
                cache[biome] = t;
            }
            return t;
        }

        public static bool StandingBurn(BiomeDef biome) => Of(biome)?.standingBurn ?? false;
        public static bool OrdinaryRainFallsBlack(BiomeDef biome) => Of(biome)?.ordinaryRainFallsBlack ?? false;
        public static bool OnlyOwnAnimalsArrive(BiomeDef biome) => Of(biome)?.onlyOwnAnimalsArrive ?? false;
    }
}
