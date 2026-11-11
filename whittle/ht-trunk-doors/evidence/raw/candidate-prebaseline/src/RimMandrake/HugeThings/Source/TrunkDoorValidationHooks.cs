using System.Linq;
using System.Globalization;
using HarmonyLib;
using Verse.AI;
using RimWorld;
using Verse;

namespace RimMandrake.HugeThings
{
    /// <summary>Bridge fixture adapter for a normal registered workgiver order. Advances no ticks, changes no growth,
    /// geometry, work, damage or destruction. The saved job then runs entirely through vanilla plant work toils.</summary>
    public static class TrunkDoorValidationHooks
    {
        public static string CutState(string pawnId)
        {
            Pawn pawn = Find.CurrentMap?.mapPawns.AllPawnsSpawned.FirstOrDefault(p => p.ThingID == pawnId);
            if (pawn == null) return "FAIL missing pawn";
            var driver = pawn.jobs.curDriver as JobDriver_PlantWork;
            float work = driver == null ? 0f : (float)AccessTools.Field(typeof(JobDriver_PlantWork), "workDone").GetValue(driver);
            return "current=" + pawn.CurJobDef?.defName + " plant=" + pawn.CurJob?.targetA.Thing?.ThingID
                + " contact=" + pawn.CurJob?.targetC.Thing?.ThingID + " work=" + work.ToString("R", CultureInfo.InvariantCulture)
                + " x=" + pawn.Position.x + " z=" + pawn.Position.z + " tick=" + Find.TickManager.TicksGame;
        }

        public static string OrderCut(string ids)
        {
            string[] parts = (ids ?? "").Split('|');
            Map map = Find.CurrentMap;
            if (map == null || parts.Length != 2) return "FAIL expected pawn|blocker on current map";
            Pawn pawn = map.mapPawns.AllPawnsSpawned.FirstOrDefault(p => p.ThingID == parts[0]);
            var blocker = map.listerThings.ThingsOfDef(HugeThingsDefOf.RM_HugeTrunkBlocker)
                .FirstOrDefault(t => t.ThingID == parts[1]) as Building_TrunkBlocker;
            if (pawn == null || blocker == null || !Patch_PlantWork_TrunkContact.Ready) return "FAIL missing subject or inactive patch";
            var giver = DefDatabase<WorkGiverDef>.GetNamed("RM_CutHugePlantFromTrunk").Worker as WorkGiver_CutHugePlantFromTrunk;
            var job = giver?.JobOnThing(pawn, blocker, true);
            if (job == null) return "FAIL registered giver returned no job";
            bool accepted = pawn.jobs.TryTakeOrderedJobPrioritizedWork(job, giver, blocker.Position);
            return "accepted=" + accepted + " current=" + pawn.CurJobDef?.defName + " plant=" + pawn.CurJob?.targetA.Thing?.ThingID
                + " contact=" + pawn.CurJob?.targetC.Thing?.ThingID + " tick=" + Find.TickManager.TicksGame;
        }
    }
}
