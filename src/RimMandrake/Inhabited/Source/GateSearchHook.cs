using RimWorld;
using Verse;

namespace RimMandrake.Inhabited
{
    /// <summary>
    /// The departure-time gate-search check -- SETTLEMENT_VISIT_LOOP_1.
    ///
    /// Spec: "Gate searches replace Visit Settlements' omniscient departure
    /// check: a faction searches leavers only if its profile says so (Empire
    /// pats down, Junkers wave through)."
    ///
    /// A STUB by design. This reads the settlement's SecurityProfileDef and
    /// rolls whether a search fires; it does not inspect the leaving party's
    /// inventory, does not read RM_Property claim state, and has no
    /// consequence beyond a log/message line and a casing record. Real
    /// per-faction tuning and what a search actually DOES (confiscation,
    /// social fallout, a fence's provenance check) is SETTLEMENT_VERBS_WAVE_1
    /// territory -- this proves the hook fires at the right moment and reads
    /// the right def field, nothing more.
    /// </summary>
    public static class GateSearchHook
    {
        /// <summary>Evaluate and record a gate search for one departure.
        /// Returns whether a search fired, for callers that want to log or
        /// test the outcome.</summary>
        public static bool EvaluateDeparture(WorldObject_InhabitedSettlement settlement)
        {
            if (settlement == null)
            {
                return false;
            }

            SecurityProfileDef profile = settlement.manifest?.securityProfile;
            bool searched = profile != null && profile.searchesLeavers && Rand.Chance(profile.searchChance);

            if (settlement.casing == null)
            {
                settlement.casing = new SettlementCasing();
            }
            settlement.casing.RecordGateSearch(searched);

            if (searched)
            {
                Messages.Message("InhabitedGateSearched".Translate(settlement.LabelCap),
                    MessageTypeDefOf.CautionInput, historical: false);
                Log.Message("[RimMandrake.Inhabited] gate search at " + settlement.LabelCap
                    + " (" + profile.defName + ")");
            }
            else
            {
                Log.Message("[RimMandrake.Inhabited] no gate search at " + settlement.LabelCap
                    + (profile == null ? " (no security profile set)" : " (" + profile.defName + " waves through)"));
            }

            return searched;
        }
    }
}
