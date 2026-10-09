using System.Text;
using LudeonTK;
using Verse;

namespace RimMandrake.LuminousPigment
{
    // DEEPFIRE_HEALTH_CHECK_1: one read-only dev action beside DeepfireStatusDebugActions. It audits the current map's
    // light book (MapComponent_DeepfireLights.Health) and writes exactly one "[DeepfireHealth] {json}" line. It changes
    // nothing. validation.py's health_clean chain reads the three problem counts and expects zero.
    public static class DeepfireHealthDebugActions
    {
        private const string Tag = "[DeepfireHealth] ";

        [DebugAction("Deepfire", "Health: report", actionType = DebugActionType.ToolMap, allowedGameStates = AllowedGameStates.PlayingOnMap)]
        private static void Report()
        {
            Map map = Find.CurrentMap;
            MapComponent_DeepfireLights lights = MapComponent_DeepfireLights.Get(map);
            if (lights == null)
            {
                Log.Message(Tag + "{\"action\":\"health\",\"found\":false}");
                return;
            }
            DeepfireHealthReport h = lights.Health();
            var sb = new StringBuilder();
            sb.Append("{\"action\":\"health\",\"found\":true");
            sb.Append(",\"trackedLights\":").Append(h.TrackedLights);
            sb.Append(",\"proxiesOnMap\":").Append(h.ProxiesOnMap);
            sb.Append(",\"orphanProxies\":").Append(h.OrphanProxies);
            sb.Append(",\"deadEntries\":").Append(h.DeadEntries);
            sb.Append(",\"pawnLights\":").Append(h.PawnLights);
            sb.Append(",\"wrongMapPawnLights\":").Append(h.WrongMapPawnLights);
            sb.Append(",\"coatedFloorCells\":").Append(h.CoatedFloorCells);
            sb.Append(",\"uncoveredFloorCells\":").Append(h.UncoveredFloorCells);
            sb.Append(",\"coatedThings\":").Append(h.CoatedThings);
            sb.Append(",\"uncoveredThings\":").Append(h.UncoveredThings);
            sb.Append(",\"problems\":").Append(h.Problems);
            sb.Append(",\"examples\":[");
            for (int i = 0; i < h.Examples.Count; i++)
            {
                if (i > 0) sb.Append(',');
                sb.Append('"').Append(h.Examples[i].Replace("\\", "/").Replace("\"", "'")).Append('"');
            }
            sb.Append("]}");
            Log.Message(Tag + sb);
        }
    }
}
