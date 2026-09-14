using System.Collections.Generic;
using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.EnvironmentalHazards
{
    // GREENTIDE_MECHANICS_2 M6 build, feller 3 ("gnawed from below"). Cribbed
    // structurally from RM_JobDriver_Gnaw (SHIP_VERMIN_MOD_1, same assembly
    // family) — walk to the target, toil a chew-down timer, but end in
    // RM_TreeFallUtility.FellTree instead of TakeDamage-to-destruction: the
    // spec calls for a real fall (damage swath, wood drop, crash), not the
    // vermin job's generic bite-kill.
    public class RM_JobDriver_GnawTreeBase : JobDriver
    {
        private int ticksRemaining = -1;

        public override bool TryMakePreToilReservations(bool errorOnFailed)
        {
            return pawn.Reserve(job.targetA, job, 1, -1, null, errorOnFailed);
        }

        protected override IEnumerable<Toil> MakeNewToils()
        {
            this.FailOnDespawnedNullOrForbidden(TargetIndex.A);
            yield return Toils_Goto.GotoThing(TargetIndex.A, PathEndMode.Touch);

            Toil chew = ToilMaker.MakeToil("MakeNewToils");
            chew.initAction = delegate
            {
                RM_GnawTreeBaseExtension ext = pawn.def?.GetModExtension<RM_GnawTreeBaseExtension>();
                ticksRemaining = ext != null ? ext.chewTicksToFell : 2400;
            };
            chew.tickIntervalAction = delegate(int delta)
            {
                Plant tree = job.targetA.Thing as Plant;
                if (tree == null || tree.Destroyed || !tree.Spawned)
                {
                    ReadyForNextToil();
                    return;
                }

                ticksRemaining -= delta;
                if (ticksRemaining > 0)
                {
                    return;
                }

                RM_TreeFallUtility.FellTree(tree, Rot4.Random, RM_TreeFallUtility.FallCause.Gnawed);
                ReadyForNextToil();
            };
            chew.defaultCompleteMode = ToilCompleteMode.Never;
            chew.WithProgressBar(TargetIndex.A, () =>
            {
                RM_GnawTreeBaseExtension ext = pawn.def?.GetModExtension<RM_GnawTreeBaseExtension>();
                int total = ext != null ? ext.chewTicksToFell : 2400;
                return total <= 0 ? 1f : 1f - (float)ticksRemaining / total;
            });
            chew.FailOnCannotTouch(TargetIndex.A, PathEndMode.Touch);
            yield return chew;
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref ticksRemaining, "ticksRemaining", -1);
        }
    }
}
