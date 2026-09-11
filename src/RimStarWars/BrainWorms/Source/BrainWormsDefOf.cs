using RimWorld;
using Verse;

namespace RimMandrake.StarWars.BrainWorms
{
    /// <summary>
    /// BRAINWORM_MOD_BUILD_1. Every def this mod's C# reaches for by name, in one
    /// place, resolved by RimWorld's own DefOf machinery so a rename explodes at
    /// load rather than silently returning null at the point of use.
    ///
    /// RSW_BrainWorm exists twice on purpose - a ThingDef (the race) and a
    /// PawnKindDef (what you spawn). DefOf resolves each field by its declared
    /// type, so the shared defName is not a collision.
    /// </summary>
    [DefOf]
    public static class BrainWormsDefOf
    {
        public static ThingDef RSW_BrainWorm;
        public static PawnKindDef RSW_BrainWormKind;
        public static ThingDef RSW_BrainWormEggCluster;
        public static HediffDef RSW_BrainWormInfection;
        public static MentalStateDef RSW_BrainWormPuppet;

        static BrainWormsDefOf()
        {
            DefOfHelper.EnsureInitializedInCtor(typeof(BrainWormsDefOf));
        }
    }
}
