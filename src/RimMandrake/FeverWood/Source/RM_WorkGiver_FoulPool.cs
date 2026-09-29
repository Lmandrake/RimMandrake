using System.Collections.Generic;
using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.FeverWood
{
    /// <summary>FEVERWOOD_TENTACLE_SETPIECE_TUNING_1. Scans
    /// RM_Designation_FoulPool cells (same cell-scanning shape as vanilla
    /// WorkGiver_Miner over DesignationDefOf.Mine, read via RimSage this
    /// pass) and finds a reachable RM_RadioactiveSuppressant stack to
    /// carry there. RM_JobDriver_FoulPool does the haul-and-dump.</summary>
    public class RM_WorkGiver_FoulPool : WorkGiver_Scanner
    {
        public override PathEndMode PathEndMode => PathEndMode.Touch;

        public override IEnumerable<IntVec3> PotentialWorkCellsGlobal(Pawn pawn)
        {
            foreach (Designation d in pawn.Map.designationManager.SpawnedDesignationsOfDef(RM_SuppressionDefOf.RM_Designation_FoulPool))
            {
                yield return d.target.Cell;
            }
        }

        public override bool ShouldSkip(Pawn pawn, bool forced = false)
        {
            return !RM_FeverWoodSettings.tentacleUraniumSuppressionEnabled
                || !pawn.Map.designationManager.AnySpawnedDesignationOfDef(RM_SuppressionDefOf.RM_Designation_FoulPool);
        }

        public override bool HasJobOnCell(Pawn pawn, IntVec3 c, bool forced = false)
        {
            if (pawn.Map.designationManager.DesignationAt(c, RM_SuppressionDefOf.RM_Designation_FoulPool) == null)
            {
                return false;
            }
            return FindSuppressant(pawn) != null;
        }

        public override Job JobOnCell(Pawn pawn, IntVec3 c, bool forced = false)
        {
            Thing suppressant = FindSuppressant(pawn);
            if (suppressant == null)
            {
                return null;
            }
            Job job = JobMaker.MakeJob(RM_SuppressionDefOf.RM_FoulPool, suppressant, c);
            int amount = UnityEngine.Mathf.Max(1, RM_FeverWoodSettings.tentacleUraniumSuppressantAmountPerUse);
            job.count = UnityEngine.Mathf.Min(suppressant.stackCount, amount);
            return job;
        }

        private Thing FindSuppressant(Pawn pawn)
        {
            return GenClosest.ClosestThingReachable(pawn.Position, pawn.Map,
                ThingRequest.ForDef(RM_SuppressionDefOf.RM_RadioactiveSuppressant),
                PathEndMode.ClosestTouch, TraverseParms.For(pawn),
                validator: delegate (Thing t)
                {
                    return t.stackCount >= 1 && pawn.CanReserve(t, 1, -1, null);
                });
        }
    }
}
