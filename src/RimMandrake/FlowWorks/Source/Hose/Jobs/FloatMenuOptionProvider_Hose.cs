using System.Collections.Generic;
using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.FlowWorks.Hose.Jobs
{
    /// <summary>
    /// Design section 2, forced / drafted orders: right-click a reel -> "Carry hose out from ..." (then a cell targeter),
    /// "Pick up hose end of ..." (Laid/Dropped, then a targeter: a new cell, or beside the reel to bring it back) and
    /// "Retract hose at ..."; right-click the free end's cell -> "Pick up hose end". Each places the reel's order through its
    /// MP sync method (OrderDeploy/OrderMove/OrderRetract) and gives this pawn the job forced, so a drafted pawn may run it.
    /// </summary>
    public class FloatMenuOptionProvider_Hose : FloatMenuOptionProvider
    {
        protected override bool Drafted => true;
        protected override bool Undrafted => true;
        protected override bool Multiselect => false;
        protected override bool RequiresManipulation => true;

        protected override bool AppliesInt(FloatMenuContext context) => RM_HoseSettings.enabled;

        public override IEnumerable<FloatMenuOption> GetOptionsFor(Thing clickedThing, FloatMenuContext context)
        {
            Pawn p = context.FirstSelectedPawn;
            CompHoseReel r = clickedThing?.TryGetComp<CompHoseReel>();
            if (p == null || r == null || clickedThing.Faction != Faction.OfPlayer) yield break;
            string label = clickedThing.LabelShort;
            string blocked = Blocked(p, r, clickedThing);
            // C7b-F3: moving a laid end needs a path to the END, not to the reel (the work giver checks the end too)
            string endBlocked = Blocked(p, r, clickedThing, false) ?? EndBlocked(p, r);
            if (r.carry == HoseCarryState.Stored)
                yield return Opt("Carry hose out from " + label, blocked, () => TargetThen(p, r, "Cannot deploy the hose there: ", r.OrderDeploy));
            if (r.carry == HoseCarryState.Laid || r.carry == HoseCarryState.Dropped)
            {
                yield return Opt("Pick up hose end of " + label, endBlocked, () => TargetThen(p, r, "Cannot move the hose end there: ", r.OrderMove));
                yield return Opt("Retract hose at " + label, blocked, () =>
                {
                    HosePendingOrder prevOrder = r.pending;
                    IntVec3 prevAt = r.pendingAt;
                    bool prevFresh = r.pendingFresh;
                    // C7b-F5: a refused forced job puts back what was queued, never leaves the new order for anyone
                    if (r.OrderRetract() == null && !HoseJobs.GiveForced(p, HoseJobs.MakeRetract(r)))
                    {
                        r.pending = prevOrder;
                        r.pendingAt = prevAt;
                        r.pendingFresh = prevFresh;
                    }
                });
            }
        }

        /// <summary>A right-click on a bare cell where a hose end lies (the end is data, not a Thing).</summary>
        public override IEnumerable<FloatMenuOption> GetOptions(FloatMenuContext context)
        {
            Pawn p = context.FirstSelectedPawn;
            RM_MapComponent_Hoses comp = context.map?.GetComponent<RM_MapComponent_Hoses>();
            if (p == null || comp == null) yield break;
            foreach (CompHoseReel r in comp.Reels)
            {
                if (!r.laid || r.far != context.ClickedCell || r.parent.Faction != Faction.OfPlayer) continue;
                string blocked = Blocked(p, r, r.parent, false) ?? EndBlocked(p, r);
                yield return Opt("Pick up hose end (" + r.parent.LabelShort + ")", blocked,
                    () => TargetThen(p, r, "Cannot move the hose end there: ", r.OrderMove));
            }
        }

        private static string Blocked(Pawn p, CompHoseReel r, Thing reel, bool needReelPath = true)
        {
            if (r.carry == HoseCarryState.Carrying || r.carry == HoseCarryState.Retracting) return "someone is handling it";
            if (!p.CanReserve(reel, 1, -1, null, true)) return "reserved";
            if (needReelPath && !p.CanReach(reel, PathEndMode.Touch, Danger.Deadly)) return "no path";
            return null;
        }

        private static string EndBlocked(Pawn p, CompHoseReel r) =>
            r.far.IsValid && !p.CanReach(r.far, PathEndMode.Touch, Danger.Deadly) ? "no path to the hose end" : null;

        private static FloatMenuOption Opt(string label, string blocked, System.Action act) =>
            blocked != null ? new FloatMenuOption(label + " (" + blocked + ")", null) : new FloatMenuOption(label, act);

        /// <summary>Choose the destination cell, place the order (refused with the reel's numbers), give the job forced.</summary>
        private static void TargetThen(Pawn p, CompHoseReel r, string refusal, System.Func<IntVec3, string> order)
        {
            var tp = new TargetingParameters { canTargetLocations = true, canTargetPawns = false, canTargetBuildings = true, canTargetItems = false };
            Find.Targeter.BeginTargeting(tp, t =>
            {
                HosePendingOrder prevOrder = r.pending;
                IntVec3 prevAt = r.pendingAt;
                bool prevFresh = r.pendingFresh;
                string why = order(t.Cell);
                if (why != null)
                {
                    Messages.Message(refusal + r.Explain(why, why == "route too long" ? r.NeedFor(t.Cell) : -1f) + ".", MessageTypeDefOf.RejectInput, false);
                    return;
                }
                Job j = WorkGiver_HoseOrders.JobFor(p, r, true, out string jwhy);
                if (j == null)
                {
                    // GPT source read 2026-10-06 B12: the refused order used to stay queued behind this message; put back what was there
                    r.pending = prevOrder;
                    r.pendingAt = prevAt;
                    r.pendingFresh = prevFresh;
                    Messages.Message("Cannot carry the hose: " + jwhy + ".", MessageTypeDefOf.RejectInput, false);
                    return;
                }
                if (!HoseJobs.GiveForced(p, j))
                {
                    // C7b-F5: the pawn refused the forced job: put back what was queued, as for a refused order above
                    r.pending = prevOrder;
                    r.pendingAt = prevAt;
                    r.pendingFresh = prevFresh;
                }
            }, caster: p);
        }
    }
}
