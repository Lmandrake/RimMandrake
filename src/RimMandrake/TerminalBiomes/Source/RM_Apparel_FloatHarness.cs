using RimWorld;
using Verse;

namespace RimMandrake.TerminalBiomes
{
    // TWILIGHT_CHANNEL_CURRENT_1 §5 rung 3 / §7 Q1 (RULED IN — deliberate,
    // one-way, weir-to-weir, forbidden in surge). "~40 lines... rides on
    // the carry component's cadence + arrest flags" (spec's own engine
    // table) — so this class carries no behaviour of its own beyond the
    // static helper RM_MapComponent_ChannelCurrent.CadenceFor already reads
    // (caps carried speed at MARGIN cadence even in the centre) and the
    // entry check below, which a future JobDriver for "wade in on purpose"
    // calls before letting a colonist start the ride. §5's "forbidden in
    // surge" and "weir mandatory downstream" are read here rather than
    // re-litigated: CanEnterCurrent is the single choke point.
    public class RM_Apparel_FloatHarness : Apparel
    {
        public static bool IsWorn(Pawn pawn)
        {
            return pawn?.apparel != null && pawn.apparel.WornApparel.Exists(a => a.def == RM_ThingDefOf.RM_FloatHarness);
        }

        // The gate a deliberate-entry job (or a future float-ride command)
        // must pass. Not called by the carry component itself — arrest is
        // unconditional on any weir cell per Q2 ("weirs catch people too"),
        // harnessed or not; this only gates STARTING a ride on purpose.
        public static bool CanEnterCurrent(Pawn pawn, Map map)
        {
            if (!IsWorn(pawn))
            {
                return false;
            }
            RM_MapComponent_ChannelCurrent current = map.GetComponent<RM_MapComponent_ChannelCurrent>();
            return current != null && !current.SurgeActive; // §5 rung 3: "forbidden in surge"
        }
    }
}
