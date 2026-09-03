using System.Collections.Generic;
using System.Text;
using LudeonTK;
using Verse;

namespace RimMandrake.FluidCanals
{
    // Bridge-reachable test surface, same pattern as RimMandrakePits'
    // PitDebugActions: gizmo/labor-only actions get a ToolMap hook so a
    // live proof does not depend on a colonist actually walking over and
    // finishing a multi-thousand-work-unit dig job.
    public static class FluidCanalsDebugActions
    {
        private const string CAT = "RMFluidCanals";

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
            if (!c.InBounds(map)) { Log.Message("[RMFluidCanalsDebug] " + c + " is off-map."); return; }
            map.terrainGrid.SetTerrain(c, RimMandrakeFluidCanals_DefOf.RM_Channel_Empty);
            CompFluidReservoir.Notify_CanalCellOpened(map, c);
            Log.Message("[RMFluidCanalsDebug] INSTANT_DIG at " + c
                + " terrainNow=" + c.GetTerrain(map).defName);
        }

        [DebugAction(CAT, "Report cell (RAW)",
            allowedGameStates = AllowedGameStates.PlayingOnMap,
            actionType = DebugActionType.ToolMap)]
        private static void ReportCell()
        {
            IntVec3 c = UI.MouseCell();
            Map map = Find.CurrentMap;
            if (map == null) return;
            StringBuilder sb = new StringBuilder();
            sb.Append("[RMFluidCanalsDebug] REPORT_CELL pos=").Append(c);
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
                CompFluidReservoir res = t.TryGetComp<CompFluidReservoir>();
                if (res != null)
                {
                    // Fixed 2026-09-02 (opus code review): fluidDef/volume are
                    // static Props config that never change - printed next to
                    // nothing live, they read like live state and aren't. spent
                    // is the one real runtime field; without it, re-triggering an
                    // already-spent reservoir reported identically to a fresh
                    // one, in the tool meant to verify exactly that distinction.
                    sb.Append(" [reservoir spent=").Append(res.Spent)
                      .Append(" fluid=").Append(res.Props.fluidDef?.defName ?? "NULL")
                      .Append(" volume=").Append(res.Props.volume.ToString("F1")).Append(']');
                }
                if (t is Flood_FluidCanal flood)
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
