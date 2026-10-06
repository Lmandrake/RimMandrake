using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.RustCathedral
{
    // RUSTCATHEDRAL_BOREHULK_GIANT_BUILD_1 §1: "damaged, it stops, sounds a
    // long grinding horn and backs slowly away from the attacker." The horn
    // is the race's soundWounded (vanilla plays it on damage); this giver is
    // the backing-away. It reads the attacker RM_CompBorehulkDrill recorded,
    // and gives a vanilla Flee job (FleeUtility.FleeJob) at Walk urgency.
    // There is no attack branch anywhere in RM_ThinkTree_Borehulk, so this
    // is the only response to harm it has.
    public class RM_JobGiver_BorehulkBackAway : ThinkNode_JobGiver
    {
        // PROVISIONAL: how long after a hit it keeps backing away, and how far.
        public int harmWindowTicks = 600;

        public int backAwayDistance = 10;

        public override ThinkNode DeepCopy(bool resolve = true)
        {
            RM_JobGiver_BorehulkBackAway obj = (RM_JobGiver_BorehulkBackAway)base.DeepCopy(resolve);
            obj.harmWindowTicks = harmWindowTicks;
            obj.backAwayDistance = backAwayDistance;
            return obj;
        }

        protected override Job TryGiveJob(Pawn pawn)
        {
            RM_CompBorehulkDrill comp = pawn.TryGetComp<RM_CompBorehulkDrill>();
            if (comp == null || comp.lastAttacker == null)
            {
                return null;
            }
            if (Find.TickManager.TicksGame > comp.lastAttackedTick + harmWindowTicks)
            {
                return null;
            }
            Pawn attacker = comp.lastAttacker;
            if (!attacker.Spawned || attacker.Map != pawn.Map || attacker.Dead)
            {
                return null;
            }
            Job job = FleeUtility.FleeJob(pawn, attacker, backAwayDistance);
            if (job != null)
            {
                job.locomotionUrgency = LocomotionUrgency.Walk;
            }
            return job;
        }
    }
}
