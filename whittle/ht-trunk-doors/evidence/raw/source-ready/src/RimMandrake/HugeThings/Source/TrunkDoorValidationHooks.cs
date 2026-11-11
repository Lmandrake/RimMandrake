using System.Linq;
using System.Globalization;
using HarmonyLib;
using Verse.AI;
using RimWorld;
using Verse;

namespace RimMandrake.HugeThings
{
    /// <summary>Fixture work-tab preparation and read-only job observations. Creates no jobs and advances no ticks, growth,
    /// work, damage or destruction. The normal think tree picks up designated cuts.</summary>
    public static class TrunkDoorValidationHooks
    {
        public static string CutState(string pawnId)
        {
            Pawn pawn = Find.CurrentMap?.mapPawns.AllPawnsSpawned.FirstOrDefault(p => p.ThingID == pawnId);
            if (pawn == null) return "FAIL missing pawn";
            var driver = pawn.jobs.curDriver as JobDriver_PlantWork;
            float work = driver == null ? 0f : (float)AccessTools.Field(typeof(JobDriver_PlantWork), "workDone").GetValue(driver);
            return "current=" + pawn.CurJobDef?.defName + " forced=" + pawn.CurJob?.playerForced + " plant=" + pawn.CurJob?.targetA.Thing?.ThingID
                + " contact=" + pawn.CurJob?.targetC.Thing?.ThingID + " work=" + work.ToString("R", CultureInfo.InvariantCulture)
                + " x=" + pawn.Position.x + " z=" + pawn.Position.z + " tick=" + Find.TickManager.TicksGame;
        }

        /// <summary>Only an owned disposable fixture calls this adapter. It changes work-tab/schedule settings,
        /// never creates a job or changes needs, growth, work, time or destruction.</summary>
        public static string PrepareCutter(string pawnId)
        {
            Pawn pawn = Find.CurrentMap?.mapPawns.AllPawnsSpawned.FirstOrDefault(p => p.ThingID == pawnId);
            if (pawn?.workSettings == null || pawn.timetable == null) return "FAIL missing fixture work settings";
            WorkTypeDef cutting = DefDatabase<WorkTypeDef>.GetNamed("PlantCutting");
            if (pawn.WorkTypeIsDisabled(cutting)) return "FAIL fixture cannot cut";
            foreach (WorkTypeDef type in DefDatabase<WorkTypeDef>.AllDefsListForReading)
                pawn.workSettings.SetPriority(type, type == cutting ? 1 : 0);
            for (int hour = 0; hour < 24; hour++) pawn.timetable.SetAssignment(hour, TimeAssignmentDefOf.Work);
            return "pawn=" + pawn.ThingID + " cuttingActive=" + pawn.workSettings.WorkIsActive(cutting)
                + " schedule=Work onlyWorkType=PlantCutting";
        }
    }
}
