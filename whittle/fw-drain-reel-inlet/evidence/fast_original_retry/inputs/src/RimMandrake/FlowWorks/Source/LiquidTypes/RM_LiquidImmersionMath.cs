using System.Collections.Generic;

namespace RimMandrake.FlowWorks.LiquidTypes
{
    // IMMERSION_DAMAGE_WIRE_NEVER_APPLIED: which of an RM_LiquidProperties' two damage specs a pawn standing on a liquid
    // square takes. Verse-free so the SelfTest project sweeps it against the shipped Defs.
    //
    // A pawn is IMMERSED in chest-deep or deeper liquid; anything shallower is CONTACT. Depth is read from what the defs
    // say about depth, never from path cost (path cost is thickness: RM_TarShallow costs 300, RM_OozeDeep 200):
    //   - Impassable: vanilla WaterDeepBase (Core Terrain_Water.xml: Impassable, pathCost 300) and every deep liquid
    //     def that keeps it (RM_AcidDeep, RM_AmmoniaDeep, ...).
    //   - the deep or chestDeep member of a LiquidDef's terrainSuite: the deep defs that turn Standable (the slimes).
    //   - the canal ladder's deep tag, WaterFreshDeep (the chest-deep Brim and the Superdeep fills carry it; the
    //     ankle-to-knee Trace and knee-to-waist Half fills do not).
    public static class RM_LiquidImmersionMath
    {
        public const string DeepTag = "WaterFreshDeep";

        public enum Exposure
        {
            None,
            Contact,
            Immersion,
        }

        public static bool IsImmersing(bool impassable, bool liquidSuiteDeep, IEnumerable<string> tags)
        {
            if (impassable || liquidSuiteDeep)
            {
                return true;
            }
            if (tags != null)
            {
                foreach (string t in tags)
                {
                    if (t == DeepTag)
                    {
                        return true;
                    }
                }
            }
            return false;
        }

        // Immersed: the immersion spec, or the contact spec when the liquid authors none (deep liquid touches you too).
        // Not immersed: the contact spec only; an immersion-only liquid (RM_SlimeGreen) does nothing in the shallows.
        public static Exposure Select(bool immersing, bool contactLive, bool immersionLive)
        {
            if (immersing && immersionLive)
            {
                return Exposure.Immersion;
            }
            return contactLive ? Exposure.Contact : Exposure.None;
        }
    }
}
