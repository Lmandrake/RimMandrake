using Verse;

namespace RimMandrake.TerminalBiomes
{
    // TWILIGHT_LIGHT_ECONOMY_1 §4.2. RM_SkylightRight: a paper keyed to ONE
    // well's ledger id. "It grants sow/hunt/gather/anchor inside that
    // well's cells" — the actual gating of those actions against a
    // holder's rights is NOT wired here (no sow/hunt/gather/anchor
    // interception exists in this codebase yet to hook into); this comp is
    // the paper's own state: which well it names, and whether that well is
    // still open — "expires when the well closes, not on a calendar."
    public class RM_CompProperties_SkylightRight : CompProperties
    {
        public RM_CompProperties_SkylightRight()
        {
            compClass = typeof(RM_Comp_SkylightRight);
        }
    }

    public class RM_Comp_SkylightRight : ThingComp
    {
        public int wellId = -1;

        public RM_CompProperties_SkylightRight Props => (RM_CompProperties_SkylightRight)props;

        public override void PostExposeData()
        {
            base.PostExposeData();
            Scribe_Values.Look(ref wellId, "rmSkylightRightWellId", -1);
        }

        public bool IsExpired()
        {
            Map map = parent.MapHeld;
            if (map == null || wellId < 0)
            {
                return false; // no map to check against (e.g. in a caravan) — never expire silently mid-transit
            }
            RM_MapComponent_WellLedger ledger = RM_MapComponent_WellLedger.GetFor(map);
            return ledger != null && !ledger.IsWellOpen(wellId);
        }

        public override string CompInspectStringExtra()
        {
            if (wellId < 0)
            {
                return null;
            }
            return IsExpired()
                ? "RM_SkylightRight_Expired".Translate()
                : "RM_SkylightRight_Active".Translate(wellId);
        }
    }
}
