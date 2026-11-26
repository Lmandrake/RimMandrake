using Verse;

namespace RimMandrake.CreatureBehaviors
{
    /// <summary>
    /// TREE_SHADE_BUILD_CROWNS_ON_STILTS (design/RimMandrake/tree_shade_model_2026-10-19.md §4.2): an optional
    /// override of one tree species' crown, on the plant's ThingDef only (never a BiomeDef: the same tree shades the same
    /// in every biome). Unset fields keep the planet defaults of RM_TreeCrown. The six day-side giants get theirs from
    /// Patches/RM_TreeCrowns_Giants.xml, measured from their art (src/RimMandrake/HugeThings/tree_crowns_measured.json).
    /// </summary>
    public class RM_TreeCrownExtension : DefModExtension
    {
        /// <summary>Crown radius = this × drawn size / 2.</summary>
        public float crownRadiusFactor = RM_TreeCrown.RadiusFactorDefault;

        /// <summary>Crown height = this × drawn size (a wall is 1).</summary>
        public float crownHeightFactor = RM_TreeCrown.HeightFactorDefault;

        /// <summary>0..1, before the leafless factor and the canopy strength dial.</summary>
        public float opacity = RM_TreeCrown.OpacityDefault;

        public static float RadiusFactorOf(ThingDef def)
        {
            RM_TreeCrownExtension e = def?.GetModExtension<RM_TreeCrownExtension>();
            return e != null ? e.crownRadiusFactor : RM_TreeCrown.RadiusFactorDefault;
        }

        public static float HeightFactorOf(ThingDef def)
        {
            RM_TreeCrownExtension e = def?.GetModExtension<RM_TreeCrownExtension>();
            return e != null ? e.crownHeightFactor : RM_TreeCrown.HeightFactorDefault;
        }

        public static float OpacityOf(ThingDef def)
        {
            RM_TreeCrownExtension e = def?.GetModExtension<RM_TreeCrownExtension>();
            return e != null ? e.opacity : RM_TreeCrown.OpacityDefault;
        }
    }
}
