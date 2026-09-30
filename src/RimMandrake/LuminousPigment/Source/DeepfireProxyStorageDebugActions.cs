using System.Collections.Generic;
using System.Globalization;
using System.Text;
using LudeonTK;
using RimWorld;
using Verse;

namespace RimMandrake.LuminousPigment
{
    // DEEPFIRE_PROXY_BLOCKS_STORAGE_1: dev-menu tools for
    // src/RimMandrake/bridgetools/prove_deepfire_proxy_storage.py. Same shape
    // as DeepfireFloorDebugActions.cs: each is a ToolMap on the 6x6 rect whose
    // SOUTH-WEST corner is the clicked cell, and each writes exactly one
    // "[DeepfireProxy] {json}" log line. The coat itself goes through the
    // existing "Floor: coat 6x6" action, i.e. the real floor-cluster path.
    public static class DeepfireProxyStorageDebugActions
    {
        private const int Side = 6;
        private const int StackPerCell = 10;
        private const string Tag = "[DeepfireProxy] ";
        private const string StockedDef = "Steel";
        private const string ProbeDef = "WoodLog";

        // Items this proof placed, keyed by the cell each was placed on.
        private static readonly Dictionary<IntVec3, Thing> placed = new Dictionary<IntVec3, Thing>();

        private static CellRect RectFrom(IntVec3 sw) => new CellRect(sw.x, sw.z, Side, Side);

        [DebugAction("Deepfire", "Proxy: stockpile + items 6x6 from cell", actionType = DebugActionType.ToolMap, allowedGameStates = AllowedGameStates.PlayingOnMap)]
        private static void StockpileAndItems()
        {
            Map map = Find.CurrentMap;
            placed.Clear();
            var zone = new Zone_Stockpile(StorageSettingsPreset.DefaultStockpile, map.zoneManager);
            map.zoneManager.RegisterZone(zone);
            int cells = 0, items = 0;
            ThingDef def = ThingDef.Named(StockedDef);
            foreach (IntVec3 c in RectFrom(UI.MouseCell()))
            {
                if (!c.InBounds(map) || map.zoneManager.ZoneAt(c) != null) continue;
                zone.AddCell(c);
                cells++;
                Thing t = ThingMaker.MakeThing(def);
                t.stackCount = StackPerCell;
                if (GenSpawn.Spawn(t, c, map, WipeMode.Vanish) != null && t.Position == c)
                {
                    placed[c] = t;
                    items++;
                }
            }
            Log.Message(Tag + "{\"action\":\"stock\",\"zoneCells\":" + cells + ",\"items\":" + items + "}");
        }

        [DebugAction("Deepfire", "Proxy: clear placed items", actionType = DebugActionType.ToolMap, allowedGameStates = AllowedGameStates.PlayingOnMap)]
        private static void ClearItems()
        {
            int n = 0;
            foreach (Thing t in placed.Values)
            {
                if (t != null && !t.Destroyed)
                {
                    t.Destroy(DestroyMode.Vanish);
                    n++;
                }
            }
            placed.Clear();
            Log.Message(Tag + "{\"action\":\"clear\",\"destroyed\":" + n + "}");
        }

        [DebugAction("Deepfire", "Proxy: storage report 6x6 from cell", actionType = DebugActionType.ToolMap, allowedGameStates = AllowedGameStates.PlayingOnMap)]
        private static void Report()
        {
            Log.Message(Tag + BuildReport(Find.CurrentMap, UI.MouseCell()));
        }

        public static string BuildReport(Map map, IntVec3 sw)
        {
            CultureInfo inv = CultureInfo.InvariantCulture;
            MapComponent_DeepfireLights mc = MapComponent_DeepfireLights.Get(map);
            CellRect rect = RectFrom(sw);

            // Displacement: every item this proof placed must still sit on
            // its own cell with its whole stack.
            int tracked = placed.Count, displaced = 0, lost = 0;
            foreach (KeyValuePair<IntVec3, Thing> kv in placed)
            {
                Thing t = kv.Value;
                if (t == null || t.Destroyed || !t.Spawned) lost++;
                else if (t.Position != kv.Key || t.stackCount != StackPerCell) displaced++;
            }

            List<IntVec3> proxyCells = mc?.FloorLightCells() ?? new List<IntVec3>();
            int proxyCellsInRect = 0, maxItemCountOnProxyCell = 0, proxyCellsValidStorage = 0, proxiesSeenInGrid = 0;
            Thing probe = ThingMaker.MakeThing(ThingDef.Named(ProbeDef));
            foreach (IntVec3 c in proxyCells)
            {
                if (!rect.Contains(c)) continue;
                proxyCellsInRect++;
                int n = c.GetItemCount(map);
                if (n > maxItemCountOnProxyCell) maxItemCountOnProxyCell = n;
                if (c.IsValidStorageFor(map, probe)) proxyCellsValidStorage++;
                foreach (Thing t in c.GetThingList(map))
                {
                    if (t.def == DeepfireDefOf.RM_DeepfireLightProxy) proxiesSeenInGrid++;
                }
            }
            // The probe is never spawned, so it needs no cleanup.
            int emptyCells = 0, emptyValid = 0;
            foreach (IntVec3 c in rect)
            {
                if (!c.InBounds(map) || c.GetItemCount(map) > 0) continue;
                emptyCells++;
                if (c.IsValidStorageFor(map, probe)) emptyValid++;
            }

            var sb = new StringBuilder();
            sb.Append('{');
            sb.AppendFormat(inv, "\"proxyCategory\":\"{0}\",", DeepfireDefOf.RM_DeepfireLightProxy.category);
            sb.AppendFormat(inv, "\"floorLights\":{0},\"coatedInRect\":{1},", mc?.FloorLightCount ?? -1, mc?.CountCoatedFloorCells(rect) ?? -1);
            sb.AppendFormat(inv, "\"tracked\":{0},\"displaced\":{1},\"lost\":{2},", tracked, displaced, lost);
            sb.AppendFormat(inv, "\"proxyCellsInRect\":{0},\"proxiesSeenInGrid\":{1},\"maxItemCountOnProxyCell\":{2},\"proxyCellsValidStorage\":{3},",
                proxyCellsInRect, proxiesSeenInGrid, maxItemCountOnProxyCell, proxyCellsValidStorage);
            sb.AppendFormat(inv, "\"emptyCellsInRect\":{0},\"emptyCellsValidStorage\":{1}", emptyCells, emptyValid);
            sb.Append('}');
            return sb.ToString();
        }
    }
}
