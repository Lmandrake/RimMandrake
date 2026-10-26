using System.Collections.Generic;
using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.ColdStorage
{
    [DefOf]
    public static class ColdStorageDefOf
    {
        public static DesignationDef RM_BreakSeal;
        public static JobDef RM_BreakSealJob;

        static ColdStorageDefOf()
        {
            DefOfHelper.EnsureInitializedInCtor(typeof(ColdStorageDefOf));
        }
    }

    /// <summary>
    /// Breaking a seal is a short pawn job (the vanilla "open" pattern): the gizmo marks the stack, a basic worker walks
    /// over, works the seal for a moment and opens it. A drafted or selected pawn can also be ordered to it directly.
    /// </summary>
    public class WorkGiver_BreakSeal : WorkGiver_Scanner
    {
        public override PathEndMode PathEndMode => PathEndMode.ClosestTouch;

        public override IEnumerable<Thing> PotentialWorkThingsGlobal(Pawn pawn)
        {
            foreach (Designation d in pawn.Map.designationManager.SpawnedDesignationsOfDef(ColdStorageDefOf.RM_BreakSeal))
            {
                yield return d.target.Thing;
            }
        }

        public override bool ShouldSkip(Pawn pawn, bool forced = false)
        {
            return !pawn.Map.designationManager.AnySpawnedDesignationOfDef(ColdStorageDefOf.RM_BreakSeal);
        }

        public override bool HasJobOnThing(Pawn pawn, Thing t, bool forced = false)
        {
            if (pawn.Map.designationManager.DesignationOn(t, ColdStorageDefOf.RM_BreakSeal) == null)
            {
                return false;
            }
            CompSealed seal = CompSealed.SealOf(t);
            if (seal == null || seal.opened)
            {
                return false;
            }
            return !t.IsForbidden(pawn) && pawn.CanReserve(t, 1, -1, null, forced);
        }

        public override Job JobOnThing(Pawn pawn, Thing t, bool forced = false)
        {
            return JobMaker.MakeJob(ColdStorageDefOf.RM_BreakSealJob, t);
        }
    }

    public class JobDriver_BreakSeal : JobDriver
    {
        /// <summary>About a second and a half at normal speed: prying a lid, cracking resin, chipping a tar crust.</summary>
        public const int WorkTicks = 90;

        public override bool TryMakePreToilReservations(bool errorOnFailed)
        {
            return pawn.Reserve(job.targetA, job, 1, -1, null, errorOnFailed);
        }

        protected override IEnumerable<Toil> MakeNewToils()
        {
            this.FailOnDespawnedOrNull(TargetIndex.A);
            yield return Toils_Goto.GotoThing(TargetIndex.A, PathEndMode.ClosestTouch);
            yield return Toils_General.Wait(WorkTicks, TargetIndex.A).WithProgressBarToilDelay(TargetIndex.A)
                .FailOnCannotTouch(TargetIndex.A, PathEndMode.ClosestTouch);
            Toil open = ToilMaker.MakeToil("BreakSeal");
            open.initAction = delegate
            {
                Thing t = job.targetA.Thing;
                Map map = t.MapHeld;
                map?.designationManager.DesignationOn(t, ColdStorageDefOf.RM_BreakSeal)?.Delete();
                CompSealed.SealOf(t)?.Open();
            };
            open.defaultCompleteMode = ToilCompleteMode.Instant;
            yield return open;
        }
    }
}
