using RimWorld;
using Verse;

namespace RimMandrake.TerminalBiomes
{
    // TWILIGHT_PANE_STRIKE_1. Defs are all in this same mod/assembly (never
    // optional, unlike the sea-hatch's cross-sea lookups in DivingInteraction),
    // so a plain [DefOf] is safe — no MayRequire, no silent-fail lookup needed.
    [DefOf]
    public static class RM_VeilFallDefOf
    {
        public static ThingDef RM_VeilFallIncoming;
        public static ThingDef RM_VeilPane;
        public static ThingDef RM_Filth_VeilFlakes;
        public static IncidentDef RM_VeilFallPaneStrike;

        static RM_VeilFallDefOf()
        {
            DefOfHelper.EnsureInitializedInCtor(typeof(RM_VeilFallDefOf));
        }
    }
}
