using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.StarWars.Droidworks
{
    /// <summary>
    /// Unprompted recharge-seeking: a droid below the power threshold paths to
    /// the nearest free socket/dock on its own. Nimbus chargers (radius > 0,
    /// CompDWCharger) are excluded from the search - those charge passively via
    /// CompTick and need no job at all.
    ///
    /// Inserted into the vanilla Humanlike think tree via the
    /// ThinkTreeDefs_DWRecharge.xml insertion hook (insertTag
    /// Humanlike_PreMain), wrapped in a ThinkNode_ConditionalNeedPercentageAbove
    /// with invert="true" - the exact shape vanilla itself uses for its own
    /// below-threshold need-seeking (Idle Joy at 90%, Core/ThinkTreeDefs/
    /// Humanlike.xml), per BENCH's own instruction to mirror it rather than
    /// invent a WorkGiver. Harmless on non-droid pawns:
    /// Patch_ShouldHaveNeed_Power.cs gates RSW_DW_Power to
    /// FleshType == RSW_DW_FleshType_Droid, so TryGiveJob below returns null
    /// immediately and nothing else in this class ever runs for them.
    /// (Corrected 2026-09-02, re-review pass: this used to be true because
    /// the need was broken and reached NOBODY, droids included - fixing
    /// that exposed that the need had no gate at all and would have
    /// reached EVERY pawn without this patch. See NeedDefs_Droidworks.xml.)
    /// </summary>
    public class JobGiver_DWRecharge : ThinkNode_JobGiver
    {
        protected override Job TryGiveJob(Pawn pawn)
        {
            Need_Power need = pawn.needs?.TryGetNeed<Need_Power>();
            if (need == null) return null;
            if (pawn.Map == null || pawn.Downed || pawn.InMentalState) return null;

            Thing charger = GenClosest.ClosestThingReachable(
                pawn.Position,
                pawn.Map,
                ThingRequest.ForGroup(ThingRequestGroup.BuildingArtificial),
                PathEndMode.InteractionCell,
                TraverseParms.For(pawn),
                9999f,
                t => IsUsableCharger(pawn, t));

            return charger != null ? JobMaker.MakeJob(DroidworksDefOf.RSW_DW_Recharge, charger) : null;
        }

        private static bool IsUsableCharger(Pawn pawn, Thing t)
        {
            CompDWCharger comp = t.TryGetComp<CompDWCharger>();
            if (comp == null || comp.Props.radius > 0f) return false;
            // Fixed 2026-09-02 (opus code review, re-review pass): this never
            // checked power/switch state, so a droid would path to and charge
            // from an unpowered or switched-off socket/dock - the same defect
            // the nimbus fix addressed, on the path that's actually primary.
            if (!comp.IsOperational) return false;
            if (t.IsForbidden(pawn)) return false;
            return pawn.CanReserve(t);
        }
    }
}
