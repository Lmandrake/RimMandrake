using System.Collections.Generic;
using LudeonTK;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.MovingDunes
{
    /// <summary>
    /// Dev-mode handles. The engine's whole visible behaviour is on a multi-day
    /// timescale by design ("extremely slow" is the ruling), so without these the only
    /// way to see whether transport works at all is to wait a season. Every one of them
    /// is a debug action: none is reachable in normal play.
    /// </summary>
    public static class MovingDunesDebugActions
    {
        [DebugAction("Moving Dunes", "Dune field: report",
                     allowedGameStates = AllowedGameStates.PlayingOnMap)]
        private static void ReportField()
        {
            Map map = Find.CurrentMap;
            MapComponent_DuneField field = DuneFieldRegistry.Get(map);
            if (field == null)
            {
                Log.Message(MovingDunesMod.LogPrefix + "this map is not a dune field. Biome "
                            + (map.Biome != null ? map.Biome.defName : "null")
                            + " carries no DuneFieldExtension.");
                return;
            }
            Log.Message(MovingDunesMod.LogPrefix + field.DebugString()
                        + " | patches: canHaveSand=" + MovingDunesMod.CanHaveSandPatchArmed
                        + " decaySuppression=" + MovingDunesMod.DecaySuppressionArmed
                        + " vanillaLayerSuppression=" + MovingDunesMod.VanillaLayerSuppressionArmed);
        }

        [DebugAction("Moving Dunes", "Dune field: shift wind",
                     allowedGameStates = AllowedGameStates.PlayingOnMap)]
        private static void ShiftWind()
        {
            MapComponent_DuneField field = DuneFieldRegistry.Get(Find.CurrentMap);
            if (field == null)
            {
                Log.Warning(MovingDunesMod.LogPrefix + "not a dune field.");
                return;
            }
            field.DebugShiftWind();
            Log.Message(MovingDunesMod.LogPrefix + "wind is now " + field.WindName + ".");
        }

        [DebugAction("Moving Dunes", "Dune field: run 100 batches",
                     allowedGameStates = AllowedGameStates.PlayingOnMap)]
        private static void RunBatches()
        {
            MapComponent_DuneField field = DuneFieldRegistry.Get(Find.CurrentMap);
            if (field == null)
            {
                Log.Warning(MovingDunesMod.LogPrefix + "not a dune field.");
                return;
            }
            field.DebugRunBatches(100);
            Log.Message(MovingDunesMod.LogPrefix + "ran 100 batches (~10 in-game hours of "
                        + "transport). " + field.DebugString());
        }

        [DebugAction("Moving Dunes", "Dune field: seed drift at cell", actionType = DebugActionType.ToolMap,
                     allowedGameStates = AllowedGameStates.PlayingOnMap)]
        private static void SeedDrift()
        {
            Map map = Find.CurrentMap;
            IntVec3 c = UI.MouseCell();
            if (!c.InBounds(map))
            {
                return;
            }
            WeatherBuildupUtility.AddSandRadial(c, map, 6f, 1f);
        }

        [DebugAction("Moving Dunes", "Dune field: bury items here", actionType = DebugActionType.ToolMap,
                     allowedGameStates = AllowedGameStates.PlayingOnMap)]
        private static void BuryHere()
        {
            Map map = Find.CurrentMap;
            IntVec3 c = UI.MouseCell();
            if (!c.InBounds(map))
            {
                return;
            }
            RM_DuneMaterialDef material = DuneFieldRegistry.MaterialOn(map);
            float depth = material != null ? Mathf.Max(material.burialDepth, 0.7f) : 0.7f;
            List<Thing> things = new List<Thing>(map.thingGrid.ThingsListAtFast(c));
            Thing_BuriedCache cache = DuneBurialUtility.BuryThingsAt(c, map, things, depth);
            Log.Message(MovingDunesMod.LogPrefix + (cache == null
                ? "nothing at that cell could be buried."
                : "buried " + cache.ContentsCount + " stack(s) under " + depth.ToStringPercent() + " sand."));
        }
    }
}
