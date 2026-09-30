using System.Collections.Generic;
using System.Globalization;
using System.Text;
using LudeonTK;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.LuminousPigment
{
    // DEEPFIRE_FLOOR_PAINT_1: dev-menu tools for spec §10 step 6's quicktest,
    // driven over the bridge by src/RimMandrake/bridgetools/prove_deepfire_floor.py
    // (rimworld/execute_debug_action with x/z -- every action here is a
    // ToolMap acting on the 6x6 rect whose SOUTH-WEST corner is the clicked
    // cell). Each writes exactly one "[DeepfireFloor] {json}" log line so the
    // script parses a result instead of guessing from the screen.
    // They call the SAME entry points the player path uses (the map
    // component's floor API, vanilla TerrainGrid.SetTerrainColor /
    // RemoveTopLayer), so the Harmony postfixes are what is being proven.
    public static class DeepfireFloorDebugActions
    {
        private const int Side = 6;
        private const string Tag = "[DeepfireFloor] ";

        private static CellRect RectFrom(IntVec3 sw) => new CellRect(sw.x, sw.z, Side, Side);

        [DebugAction("Deepfire", "Floor: coat 6x6 from cell", actionType = DebugActionType.ToolMap, allowedGameStates = AllowedGameStates.PlayingOnMap)]
        private static void Coat6x6()
        {
            Map map = Find.CurrentMap;
            MapComponent_DeepfireLights mc = MapComponent_DeepfireLights.Get(map);
            int added = 0, refused = 0;
            foreach (IntVec3 c in RectFrom(UI.MouseCell()))
            {
                if (mc != null && mc.AddFloorCoat(c)) added++;
                else refused++;
            }
            Log.Message(Tag + "{\"action\":\"coat\",\"added\":" + added + ",\"refused\":" + refused + "}");
        }

        [DebugAction("Deepfire", "Floor: designate 6x6 from cell", actionType = DebugActionType.ToolMap, allowedGameStates = AllowedGameStates.PlayingOnMap)]
        private static void Designate6x6()
        {
            Map map = Find.CurrentMap;
            MapComponent_DeepfireLights mc = MapComponent_DeepfireLights.Get(map);
            int added = 0;
            foreach (IntVec3 c in RectFrom(UI.MouseCell()))
            {
                if (mc == null || !mc.CanAddFloorCoat(c)) continue;
                if (map.designationManager.DesignationAt(c, DeepfireDefOf.RM_ApplyDeepfireFloorDesignation) != null) continue;
                map.designationManager.AddDesignation(new Designation(c, DeepfireDefOf.RM_ApplyDeepfireFloorDesignation));
                added++;
            }
            Log.Message(Tag + "{\"action\":\"designate\",\"added\":" + added + "}");
        }

        [DebugAction("Deepfire", "Floor: vanilla-paint 6x6 red from cell", actionType = DebugActionType.ToolMap, allowedGameStates = AllowedGameStates.PlayingOnMap)]
        private static void PaintRed6x6()
        {
            Map map = Find.CurrentMap;
            ColorDef red = DefDatabase<ColorDef>.GetNamedSilentFail("Structure_Red");
            int painted = 0;
            if (red != null)
            {
                foreach (IntVec3 c in RectFrom(UI.MouseCell()))
                {
                    if (!c.InBounds(map)) continue;
                    map.terrainGrid.SetTerrainColor(c, red);
                    painted++;
                }
            }
            Log.Message(Tag + "{\"action\":\"paintRed\",\"colorDefFound\":" + (red != null ? "true" : "false") + ",\"painted\":" + painted + "}");
        }

        [DebugAction("Deepfire", "Floor: strip coats 6x6 from cell", actionType = DebugActionType.ToolMap, allowedGameStates = AllowedGameStates.PlayingOnMap)]
        private static void Strip6x6()
        {
            Map map = Find.CurrentMap;
            MapComponent_DeepfireLights mc = MapComponent_DeepfireLights.Get(map);
            int stripped = 0;
            foreach (IntVec3 c in RectFrom(UI.MouseCell()))
            {
                if (mc != null && mc.ClearFloorCoats(c)) stripped++;
            }
            Log.Message(Tag + "{\"action\":\"strip\",\"stripped\":" + stripped + "}");
        }

        [DebugAction("Deepfire", "Floor: remove floor 6x6 from cell", actionType = DebugActionType.ToolMap, allowedGameStates = AllowedGameStates.PlayingOnMap)]
        private static void RemoveFloor6x6()
        {
            Map map = Find.CurrentMap;
            int removed = 0;
            foreach (IntVec3 c in RectFrom(UI.MouseCell()))
            {
                if (!c.InBounds(map) || !map.terrainGrid.CanRemoveTopLayerAt(c)) continue;
                map.terrainGrid.RemoveTopLayer(c, doLeavings: false);
                removed++;
            }
            Log.Message(Tag + "{\"action\":\"removeFloor\",\"removed\":" + removed + "}");
        }

        [DebugAction("Deepfire", "Floor: report 6x6 from cell", actionType = DebugActionType.ToolMap, allowedGameStates = AllowedGameStates.PlayingOnMap)]
        private static void Report6x6()
        {
            Log.Message(Tag + BuildReport(Find.CurrentMap, UI.MouseCell()));
        }

        public static string BuildReport(Map map, IntVec3 sw)
        {
            CultureInfo inv = CultureInfo.InvariantCulture;
            MapComponent_DeepfireLights mc = MapComponent_DeepfireLights.Get(map);
            CellRect rect = RectFrom(sw);
            IntVec3 center = new IntVec3(sw.x + Side / 2, 0, sw.z + Side / 2);

            int coated = 0, coatSum = 0, floorCells = 0;
            foreach (IntVec3 c in rect)
            {
                if (!c.InBounds(map)) continue;
                if (MapComponent_DeepfireLights.IsCoatableFloor(map, c)) floorCells++;
                int k = mc?.FloorCoatsAt(c) ?? 0;
                if (k > 0) coated++;
                coatSum += k;
            }

            float ground = center.InBounds(map) ? map.glowGrid.GroundGlowAt(center) : 0f;
            Color32 vis = center.InBounds(map) ? map.glowGrid.VisualGlowAt(map.cellIndices.CellToIndex(center)) : new Color32();
            ColorDef colorDef = center.InBounds(map) ? map.terrainGrid.ColorAt(center) : null;
            TerrainDef top = center.InBounds(map) ? map.terrainGrid.TopTerrainAt(center) : null;

            Room room = center.InBounds(map) ? center.GetRoom(map) : null;
            float roomBeauty = room != null ? room.GetStat(RoomStatDefOf.Beauty) : 0f;
            float roomBonus = RM_RoomStatPart_DeepfireFloor.BonusFor(room);
            int roomCells = room?.CellCount ?? 0;
            int roomCoated = room != null && mc != null ? mc.CountCoatedFloorCells(room.Cells) : 0;
            float cellBeauty = center.InBounds(map) ? BeautyUtility.CellBeauty(center, map) : 0f;

            var sb = new StringBuilder();
            sb.Append('{');
            sb.AppendFormat(inv, "\"rect\":[{0},{1},{2},{3}],", sw.x, sw.z, Side, Side);
            sb.AppendFormat(inv, "\"floorCellsInRect\":{0},\"coatedInRect\":{1},\"coatSumInRect\":{2},", floorCells, coated, coatSum);
            sb.AppendFormat(inv, "\"coatedOnMap\":{0},", mc?.CoatedFloorCellCount ?? -1);
            sb.AppendFormat(inv, "\"floorLights\":{0},\"clusteredBuildingLights\":{1},\"totalLights\":{2},",
                mc?.FloorLightCount ?? -1, mc?.ClusteredBuildingLightCount ?? -1, mc?.TotalLightCount ?? -1);
            sb.Append("\"floorLightList\":[");
            List<string> lights = mc?.DescribeFloorLights() ?? new List<string>();
            for (int i = 0; i < lights.Count; i++)
            {
                if (i > 0) sb.Append(',');
                sb.Append('"').Append(lights[i].Replace("\"", "'")).Append('"');
            }
            sb.Append("],");
            sb.AppendFormat(inv, "\"center\":[{0},{1}],\"centerGroundGlow\":{2:0.####},\"centerVisual\":[{3},{4},{5}],",
                center.x, center.z, ground, vis.r, vis.g, vis.b);
            sb.AppendFormat(inv, "\"centerTerrain\":\"{0}\",\"centerColorDef\":\"{1}\",",
                top?.defName ?? "", colorDef?.defName ?? "");
            sb.AppendFormat(inv, "\"centerCellBeauty\":{0:0.####},", cellBeauty);
            sb.AppendFormat(inv, "\"roomId\":{0},\"roomCells\":{1},\"roomOutdoors\":{2},\"roomCoatedCells\":{3},\"roomBeauty\":{4:0.####},\"roomDeepfireBonus\":{5:0.####}",
                room?.ID ?? -1, roomCells, room != null && room.PsychologicallyOutdoors ? "true" : "false", roomCoated, roomBeauty, roomBonus);
            sb.Append('}');
            return sb.ToString();
        }
    }
}
