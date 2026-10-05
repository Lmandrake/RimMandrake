using System.Collections.Generic;
using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.GimmeSomeSlack.Hose.Jobs
{
    /// <summary>
    /// Design sections 2 and 4: any free colonist takes a reel's pending order as Hauling work. The candidates are the map
    /// component's reels with an order (a short list, no map scan). An order whose end lies dropped is picked up again
    /// (autoResumeDroppedHose). Player faction only; enemy use would give the job directly (section 10).
    /// </summary>
    public class WorkGiver_HoseOrders : WorkGiver_Scanner
    {
        public override PathEndMode PathEndMode => PathEndMode.Touch;

        public override Danger MaxPathDanger(Pawn pawn) => Danger.Some;

        private static IEnumerable<CompHoseReel> Ordered(Pawn pawn)
        {
            RM_MapComponent_Hoses comp = pawn.Map?.GetComponent<RM_MapComponent_Hoses>();
            if (comp == null) yield break;
            foreach (CompHoseReel r in comp.Reels)
                if (r.pending != HosePendingOrder.None && r.parent.Spawned && r.parent.Faction == pawn.Faction) yield return r;
        }

        public override IEnumerable<Thing> PotentialWorkThingsGlobal(Pawn pawn)
        {
            foreach (CompHoseReel r in Ordered(pawn)) yield return r.parent;
        }

        public override bool ShouldSkip(Pawn pawn, bool forced = false)
        {
            if (!HoseSettings.enabled) return true;
            foreach (CompHoseReel _ in Ordered(pawn)) return false;
            return true;
        }

        public override Job JobOnThing(Pawn pawn, Thing t, bool forced = false) => JobFor(pawn, t.TryGetComp<CompHoseReel>(), forced, out _);

        /// <summary>The job for this reel's order, or null with the reason (the float menu shows it).</summary>
        public static Job JobFor(Pawn pawn, CompHoseReel r, bool forced, out string why)
        {
            why = null;
            if (r == null || !HoseSettings.enabled) { why = "no hose"; return null; }
            Thing t = r.parent;
            if (t.Faction != pawn.Faction) { why = "not ours"; return null; }
            if (r.pending == HosePendingOrder.None) { why = "no order"; return null; }
            if (r.carry == HoseCarryState.Carrying || r.carry == HoseCarryState.Retracting) { why = "someone is handling it"; return null; }
            if (!forced && t.IsForbidden(pawn)) { why = "forbidden"; return null; }
            if (!pawn.CanReserve(t, 1, -1, null, forced)) { why = "reserved"; return null; }
            Danger d = forced ? Danger.Deadly : Danger.Some;

            if (r.pending == HosePendingOrder.Retract)
            {
                if (r.carry != HoseCarryState.Laid && r.carry != HoseCarryState.Dropped) { why = "nothing to wind in"; return null; }
                if (!pawn.CanReach(t, PathEndMode.Touch, d)) { why = "no path to the reel"; return null; }
                return HoseJobs.MakeRetract(r);
            }

            IntVec3 dest = r.pendingAt;
            if (!dest.IsValid) { why = "no destination"; return null; }
            if (r.carry == HoseCarryState.Stored)
            {
                if (r.pending != HosePendingOrder.Deploy) { why = "nothing to pick up"; return null; }
                if (!pawn.CanReach(t, PathEndMode.Touch, d)) { why = "no path to the reel"; return null; }
            }
            else
            {
                // Laid / Dropped: the end lies out; an interrupted Deploy is a resume
                if (r.pending == HosePendingOrder.Deploy && r.carry == HoseCarryState.Dropped && !forced && !HoseJobTuning.autoResumeDroppedHose)
                { why = "waiting for a new order"; return null; }
                if (!r.far.IsValid) { why = "no hose end"; return null; }
                if (!pawn.CanReach(r.far, PathEndMode.Touch, d)) { why = "no path to the hose end"; return null; }
                if (!forced && !r.far.InAllowedArea(pawn)) { why = "hose end outside allowed area"; return null; }
            }
            if (!r.IsBringBack(dest))
            {
                if (!pawn.CanReach(dest, PathEndMode.Touch, d)) { why = "no path to " + dest; return null; }
                if (!forced && !dest.InAllowedArea(pawn)) { why = "destination outside allowed area"; return null; }
            }
            return HoseJobs.MakeCarry(r);
        }
    }
}
