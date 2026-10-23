// VEE_DEEP_ORES_MIGRATE_RICH_AND_POOR (design/RimMandrake/vee_port_plan_2026-10-22.md §2 group O). Verse-free; SelfTest compiles it.
//
// The world-tile resource mutators ported from Vanilla Exploration Expanded, rebuilt from their descriptions (no VEE code read):
//   RM_DeepOreRich      "rich in deep ores"           -> every deep lump a ground-penetrating scanner finds holds more per cell
//   RM_DeepOreDevoid    "deep ores almost non-existent" -> the scanner finds nothing here (base rock can still be drilled)
//   RM_MineralDevoid    "mineral devoid"               -> no ore veins in the rock: scattered ore lumps become plain rock
//   RM_MineableComponentSpacer                         -> lumps of advanced compacted machinery in the rock
using System;
using System.Collections.Generic;

namespace RimMandrake.DeepDrill
{
    /// <summary>What a tile mutator does to deep ores. The NUMBER for Rich lives in Mod Settings, never in the def.</summary>
    public enum RM_DeepOreKind
    {
        None,
        Rich,
        Devoid,
    }

    public static class RM_TileResourceKernel
    {
        /// <summary>Shipped deep-ore factor of a Rich tile. PROVISIONAL: VEE's x1.25, tune live.</summary>
        public const float DefaultRichFactor = 1.25f;

        /// <summary>The factor on deep-ore abundance for a tile carrying these kinds: any Devoid -> 0; else the Rich factor once
        /// if any Rich (one category, so two Rich never stack); else 1. Disabled -> 1.</summary>
        public static float DeepOreFactor(IEnumerable<RM_DeepOreKind> kinds, float richFactor, bool enabled)
        {
            if (!enabled || kinds == null) return 1f;
            bool rich = false;
            foreach (RM_DeepOreKind k in kinds)
            {
                if (k == RM_DeepOreKind.Devoid) return 0f;
                if (k == RM_DeepOreKind.Rich) rich = true;
            }
            return rich ? Math.Max(0f, richFactor) : 1f;
        }

        /// <summary>The count a deep cell holds after the factor: rounded, never below 1 for a factor above 0, inside the grid's ushort.</summary>
        public static int ScaledCount(int count, float factor)
        {
            if (count <= 0 || factor == 1f) return count;
            if (factor <= 0f) return 0;
            double v = Math.Round(count * (double)factor, MidpointRounding.AwayFromZero);
            if (v < 1) v = 1;
            if (v > 65535) v = 65535;
            return (int)v;
        }

        /// <summary>Lumps to scatter for a mineable-deposit mutator: the map's resource blotches per 10k cells x the def's blotch factor
        /// x the settings scale (0 = none).</summary>
        public static float ScatterPer10k(float blotchesPer10k, float blotchFactor, float scale)
        {
            float v = blotchesPer10k * blotchFactor * scale;
            return v > 0f ? v : 0f;
        }

        /// <summary>Mineral devoid: a natural-rock edifice is stripped to plain rock when it is an ore vein (a resource rock that the ore
        /// scatter places, commonality above 0) whose yield is not on the keep list (components: machinery is not a mineral).</summary>
        public static bool StripsToPlainRock(bool isResourceRock, float mineableScatterCommonality, string mineableThingDefName, ICollection<string> keep)
        {
            if (!isResourceRock || mineableScatterCommonality <= 0f) return false;
            if (mineableThingDefName != null && keep != null && keep.Contains(mineableThingDefName)) return false;
            return true;
        }
    }
}
