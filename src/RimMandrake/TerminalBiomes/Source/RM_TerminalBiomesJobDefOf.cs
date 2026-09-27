using RimWorld;
using Verse;

namespace RimMandrake.TerminalBiomes
{
    // TWILIGHT_DANGER_LIGHTWEB_1. Same shape as CreatureBehaviors' own
    // RM_JobDefOf — one static class per assembly, resolved once at load.
    [DefOf]
    public static class RM_TerminalBiomesJobDefOf
    {
        public static JobDef RM_FeedOnGlow;

        static RM_TerminalBiomesJobDefOf()
        {
            DefOfHelper.EnsureInitializedInCtor(typeof(RM_TerminalBiomesJobDefOf));
        }
    }
}
