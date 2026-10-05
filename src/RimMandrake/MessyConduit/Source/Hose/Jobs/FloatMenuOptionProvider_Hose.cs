using System.Collections.Generic;
using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.MessyConduit.Hose.Jobs
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

        protected override bool AppliesInt(FloatMenuContext context) => HoseSettings.enabled;

        public override IEnumerable<FloatMenuOption> GetOptionsFor(Thing clickedThing, FloatMenuContext context)
        {
            Pawn p = context.FirstSelectedPawn;
            CompHoseReel r = clickedThing?.TryGetComp<CompHoseReel>();
            if (p == null || r == null || clickedThing.Faction != Faction.OfPlayer) yield break;
            string label = clickedThing.LabelShort;
            string blocked = Blocked(p, r, clickedThing);
            if (r.carry == HoseCarryState.Stored)
                yield return Opt("Carry hose out from " + label, blocked, () => TargetThen(p, r, "Cannot deploy the hose there: ", r.OrderDeploy));
            if (r.carry == HoseCarryState.Laid || r.carry == HoseCarryState.Dropped)
            {
                yield return Opt("Pick up hose end of " + label, blocked ?? EndBlocked(p, r), () => TargetThen(p, r, "Cannot move the hose end there: ", r.OrderMove));
                yield return Opt("Retract hose at " + label, blocked, () =>
                {
                    if (r.OrderRetract() == null) HoseJobs.GiveForced(p, HoseJobs.MakeRetract(r));
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
                string blocked = Blocked(p, r, r.parent) ?? EndBlocked(p, r);
                yield return Opt("Pick up hose end (reel at " + r.parent.Position + ")", blocked,
                    () => TargetThen(p, r, "Cannot move the hose end there: ", r.OrderMove));
            }
        }

        private static string Blocked(Pawn p, CompHoseReel r, Thing reel)
        {
            if (r.carry == HoseCarryState.Carrying || r.carry == HoseCarryState.Retracting) return "someone is handling it";
            if (!p.CanReserve(reel, 1, -1, null, true)) return "reserved";
            if (!p.CanReach(reel, PathEndMode.Touch, Danger.Deadly)) return "no path";
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
                string why = order(t.Cell);
                if (why != null)
                {
                    Messages.Message(refusal + r.Explain(why, why == "route too long" ? r.NeedFor(t.Cell) : -1f) + ".", MessageTypeDefOf.RejectInput, false);
                    return;
                }
                Job j = WorkGiver_HoseOrders.JobFor(p, r, true, out string jwhy);
                if (j == null) { Messages.Message("Cannot carry the hose: " + jwhy + ".", MessageTypeDefOf.RejectInput, false); return; }
                HoseJobs.GiveForced(p, j);
            }, caster: p);
        }
    }
}
