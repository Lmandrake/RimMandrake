using RimWorld;
using Verse;

namespace RimMandrake.TerminalBiomes
{
    // TWILIGHT_CHANNEL_CURRENT_1. Stable refs for the defs THIS item ships
    // (never for the bed/silt/ford terrain content drop §8.2 owes — those
    // stay behind GetNamedSilentFail lookups in the genstep/component
    // because they may not exist yet; see those files' own comments).
    [DefOf]
    public static class RM_TerminalBiomesDefOf
    {
        public static HediffDef RM_Hediff_Sunk;
        public static GameConditionDef RM_GameCondition_Undersurge;

        static RM_TerminalBiomesDefOf()
        {
            DefOfHelper.EnsureInitializedInCtor(typeof(RM_TerminalBiomesDefOf));
        }
    }

    // Split from RM_TerminalBiomesDefOf so a ThingDef-only consumer (the
    // harness's static helper, called from a hot cadence path) resolves a
    // smaller DefOf. Both are initialized the same way; the split is
    // organizational only.
    [DefOf]
    public static class RM_ThingDefOf
    {
        public static ThingDef RM_FloatHarness;
        public static ThingDef RM_CargoFloat;
        public static ThingDef RM_BankStake;
        public static ThingDef RM_BankWeir;
        public static ThingDef RM_SiltTrap;

        static RM_ThingDefOf()
        {
            DefOfHelper.EnsureInitializedInCtor(typeof(RM_ThingDefOf));
        }
    }
}
