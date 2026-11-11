using System;
using System.Collections.Generic;
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
        /// <summary>Ground-only ClearArea integration control on a declared disposable
        /// fixture contact. Refuses unrelated objects and does not advance time.</summary>
        public static string ClearFixtureContact(string args)
        {
            string[] parts = (args ?? "").Split('|');
            if (parts.Length != 3) return "FAIL expected plantID|x,z|mode";
            string[] xy = parts[1].Split(',');
            int x, z;
            GravshipPlacementUtility.ClearMode mode;
            if (xy.Length != 2 || !int.TryParse(xy[0], out x) || !int.TryParse(xy[1], out z)
                || !Enum.TryParse(parts[2], out mode)
                || (mode != GravshipPlacementUtility.ClearMode.NaturalRockOnly
                    && mode != GravshipPlacementUtility.ClearMode.BlockingBuildingsOnly))
                return "FAIL fixture arguments";
            Map map = Find.CurrentMap;
            IntVec3 cell = new IntVec3(x, 0, z);
            if (map == null || x != 175 || z != 111 || !cell.InBounds(map)) return "FAIL outside declared contact";
            Plant plant = map.listerThings.AllThings.OfType<Plant>().FirstOrDefault(p => p.ThingID == parts[0]);
            var mc = map.GetComponent<MapComponent_HugeFootprints>();
            var things = cell.GetThingList(map);
            Building_TrunkBlocker blocker = things.OfType<Building_TrunkBlocker>().SingleOrDefault();
            if (plant == null || plant.Position != new IntVec3(175, 0, 110) || blocker == null
                || mc == null || !mc.HasCutClaim(plant, blocker) || things.Count != 1)
                return "FAIL contact not exclusively owned fixture blocker";
            GravshipPlacementUtility.ClearArea(map, cell, new HashSet<IntVec3> { IntVec3.Zero }, mode);
            return "mode=" + mode + " plantDestroyed=" + plant.Destroyed + " blockerDestroyed=" + blocker.Destroyed;
        }
    }
}
