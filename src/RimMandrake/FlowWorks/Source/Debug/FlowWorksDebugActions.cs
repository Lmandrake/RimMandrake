using System.Collections.Generic;
using System.Text;
using LudeonTK;
using Verse;

// Owner ruling 24 (2026-09-16): a source is not a building. CompFluidReservoir
// and RM_FluidSpring_Test are DELETED, and with them every reservoir reading
// this surface used to take. RM_MapComponent_Excavation's depth/fill grid is
// the core now, and it is what these actions report.

namespace RimMandrake.FlowWorks
{
    // Bridge-reachable test surface, same pattern as RimMandrakePits'
    // PitDebugActions: gizmo/labor-only actions get a ToolMap hook so a
    // live proof does not depend on a colonist actually walking over and
    // finishing a multi-thousand-work-unit dig job.
    public static class FlowWorksDebugActions
    {
        private const string CAT = "RMFlowWorks";

        [DebugAction(CAT, "Instant-dig canal at cell",
            allowedGameStates = AllowedGameStates.PlayingOnMap,
            actionType = DebugActionType.ToolMap)]
        private static void InstantDig()
        {
            IntVec3 c = UI.MouseCell();
            Map map = Find.CurrentMap;
            if (map == null) return;
            // Fixed 2026-09-02 (opus code review): UI.MouseCell() returns off-map
            // cells freely when zoomed out; c.GetTerrain(map) below has no bounds
            // check and throws IndexOutOfRangeException on one, in the primary
            // verification tool for this whole mod.
            if (!c.InBounds(map)) { Log.Message("[RMFlowWorksDebug] " + c + " is off-map."); return; }
            RM_MapComponent_Excavation ex = map.GetComponent<RM_MapComponent_Excavation>();
            byte newDepth = (ex != null) ? ex.Deepen(c) : (byte)0;
            Log.Message("[RMFlowWorksDebug] INSTANT_DIG at " + c
                + " D=" + newDepth + " (" + RM_ExcavationDepth.LabelOf(newDepth) + ")"
                + " terrainNow=" + c.GetTerrain(map).defName);
        }

        [DebugAction(CAT, "Report depth grid (RAW)",
            allowedGameStates = AllowedGameStates.PlayingOnMap,
            actionType = DebugActionType.ToolMap)]
        private static void ReportDepthGrid()
        {
            IntVec3 c = UI.MouseCell();
            Map map = Find.CurrentMap;
            if (map == null) return;
            if (!c.InBounds(map)) { Log.Message("[RMFlowWorksDebug] " + c + " is off-map."); return; }
            RM_MapComponent_Excavation ex = map.GetComponent<RM_MapComponent_Excavation>();
            if (ex == null) { Log.Error("[RMFlowWorksDebug] no RM_MapComponent_Excavation on this map."); return; }
            byte d = ex.DepthAt(c);
            byte f = ex.FillAt(c);
            Log.Message("[RMFlowWorksDebug] DEPTH_GRID pos=" + c
                + " D=" + d + " (" + RM_ExcavationDepth.LabelOf(d) + ")"
                + " F=" + f
                + " tier=" + RM_ExcavationDepth.FillTier(f, d)
                + " excavated=" + ex.IsExcavated(c)
                + " source=" + ex.IsSourceCell(c)
                + " canLiquidEnter=" + ex.CanLiquidEnter(c)
                + " baseTerrain=" + map.terrainGrid.BaseTerrainAt(c).defName
                + " tempTerrain=" + (map.terrainGrid.TempTerrainAt(c)?.defName ?? "none")
                + " | MAP excavatedCells=" + ex.ExcavatedCellCount
                + " overflowDestroyedTotal=" + ex.OverflowDestroyedTotal.ToString("F1")
                + " activeFluid=" + (ex.ActiveFluid?.defName ?? "NULL"));
        }

        [DebugAction(CAT, "Report cell (RAW)",
            allowedGameStates = AllowedGameStates.PlayingOnMap,
            actionType = DebugActionType.ToolMap)]
        private static void ReportCell()
        {
            IntVec3 c = UI.MouseCell();
            Map map = Find.CurrentMap;
            if (map == null) return;
            // Same guard as InstantDig and ReportDepthGrid, and the same reason
            // (fixed there 2026-09-02, opus code review): UI.MouseCell() returns
            // off-map cells freely when zoomed out, and c.GetTerrain(map) below
            // has no bounds check and throws IndexOutOfRangeException on one --
            // in the primary verification tool for this whole mod. This sibling
            // method was missed when the other two were fixed.
            if (!c.InBounds(map)) { Log.Message("[RMFlowWorksDebug] " + c + " is off-map."); return; }
            StringBuilder sb = new StringBuilder();
            sb.Append("[RMFlowWorksDebug] REPORT_CELL pos=").Append(c);
            sb.Append(" terrain=").Append(c.GetTerrain(map).defName);
            sb.Append(" isWater=").Append(c.GetTerrain(map).IsWater);
            // A flood now writes the TEMPORARY terrain layer (owner ruling
            // 2026-09-02: recoverable, per vanilla SeasonalFlood), so the one
            // question live verification has to answer about a flooded cell is
            // "what comes back when it drains" -- which GetTerrain, returning
            // the temp layer first, cannot show on its own.
            sb.Append(" tempTerrain=").Append(map.terrainGrid.TempTerrainAt(c)?.defName ?? "none");
            sb.Append(" underneath=").Append(map.terrainGrid.TopTerrainAt(c).defName);

            List<Thing> here = c.GetThingList(map);
            for (int i = 0; i < here.Count; i++)
            {
                Thing t = here[i];
                sb.Append("\n  THING ").Append(t.def.defName).Append(" id=").Append(t.ThingID);
                if (t is Flood_FlowWorks flood)
                {
                    sb.Append(" [flood spawned=").Append(flood.Spawned)
                      .Append(" floodedTileCount=").Append(flood.FloodedTileCount)
                      .Append(" remainingVolume=").Append(flood.RemainingVolume.ToString("F1"))
                      .Append(" expiresAtTick=").Append(flood.ExpiresAtTick)
                      .Append(" nowTick=").Append(Find.TickManager.TicksGame).Append(']');
                }
            }
            Log.Message(sb.ToString());
        }
    }
}
