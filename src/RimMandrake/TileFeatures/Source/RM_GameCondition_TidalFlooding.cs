using System.Collections.Generic;
using RimWorld;
using Verse;

namespace RimMandrake.TileFeatures
{
    // RM_RisingWaters' permanent condition (VEE_LANDFORMS_BUILD_CRATERS_AND_COMPANY): once a day the sea climbs inland over
    // the flat land next to it as vanilla's temporary shallow floodwater, then falls back. Rebuilt from VEE's description
    // ("the tides push far inland. Large stretches of land are regularly submerged"); no VEE C# was read.
    // The tide band is every unroofed natural land cell without a building within MaxTideReach steps of salt water, reached
    // through such cells only (a wall or a roof keeps the sea out of what lies behind it). The band is rebuilt every in-game
    // hour, so later walls and roofs count. Floodwater is temporary terrain, so the ground underneath is never lost, and the
    // condition removes only the cells it flooded itself (saved with the game), never another flood's water.
    // It acts on the map that owns it (a mutator's condition is that map's own).
    public class RM_GameCondition_TidalFlooding : GameCondition
    {
        public const int TidePeriodTicks = 60000;  // one in-game day per tide cycle; PROVISIONAL
        private const int CheckIntervalTicks = 250;
        private const int ReachRebuildTicks = 2500; // a wall or roof built since keeps the tide out within an in-game hour

        private HashSet<IntVec3> owned = new HashSet<IntVec3>();
        private Dictionary<IntVec3, int> reach;     // not saved: rebuilt on demand and every ReachRebuildTicks
        private int reachBuiltTick = -1;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Collections.Look(ref owned, "ownedFloodCells", LookMode.Value);
            if (Scribe.mode == LoadSaveMode.PostLoadInit && owned == null) owned = new HashSet<IntVec3>();
        }

        public override void GameConditionTick()
        {
            base.GameConditionTick();
            if (Find.TickManager.TicksGame % CheckIntervalTicks != 0) return;
            Map map = SingleMap;
            TerrainDef flood = TerrainDefOf.ShallowFloodwater;
            if (map == null || flood == null) return;
            bool on = RM_TileFeaturesSettings.landformsEnabled && RM_TileFeaturesSettings.tideReach > 0;
            float level = RM_LandformGeometry.TideLevel(Find.TickManager.TicksGame, TidePeriodTicks);
            int now = Find.TickManager.TicksGame;
            if (reach == null || now - reachBuiltTick >= ReachRebuildTicks)
            {
                reach = BuildReach(map);
                reachBuiltTick = now;
            }

            // recede: every owned cell that the tide no longer reaches, or that has become ineligible, dries out
            List<IntVec3> dry = null;
            foreach (IntVec3 c in owned)
            {
                bool keep = on && reach.TryGetValue(c, out int d) && Eligible(c, map)
                            && RM_LandformGeometry.TideFloods(d, RM_TileFeaturesSettings.tideReach, level);
                if (!keep) (dry ?? (dry = new List<IntVec3>())).Add(c);
            }
            if (dry != null)
                foreach (IntVec3 c in dry) Release(c, map, flood);
            if (!on) return;

            // rise: flood every reached, eligible cell the level now covers, unless something else already put water there
            foreach (KeyValuePair<IntVec3, int> kv in reach)
            {
                IntVec3 c = kv.Key;
                if (owned.Contains(c) || !RM_LandformGeometry.TideFloods(kv.Value, RM_TileFeaturesSettings.tideReach, level)) continue;
                if (!Eligible(c, map) || map.terrainGrid.TempTerrainAt(c) != null) continue;
                map.terrainGrid.SetTempTerrain(c, flood);
                owned.Add(c);
            }
        }

        public override void End()
        {
            Map map = SingleMap;
            TerrainDef flood = TerrainDefOf.ShallowFloodwater;
            if (map != null && flood != null)
                foreach (IntVec3 c in new List<IntVec3>(owned)) Release(c, map, flood);
            owned.Clear();
            reach = null;
            base.End();
        }

        private void Release(IntVec3 c, Map map, TerrainDef flood)
        {
            if (c.InBounds(map) && map.terrainGrid.TempTerrainAt(c) == flood) map.terrainGrid.RemoveTempTerrain(c);
            owned.Remove(c);
        }

        // unroofed natural land with no building on it (a floor laid since is not natural and keeps the tide out)
        private static bool Eligible(IntVec3 c, Map map)
        {
            if (!c.InBounds(map) || c.Roofed(map) || c.GetEdifice(map) != null) return false;
            TerrainDef t = map.terrainGrid.TerrainAtIgnoreTemp(map.cellIndices.CellToIndex(c));
            return t != null && t.natural && !t.IsWater && t.categoryType != TerrainDef.TerrainCategoryType.Stone;
        }

        // steps from salt water through eligible cells only, out to the slider's maximum
        private static Dictionary<IntVec3, int> BuildReach(Map map)
        {
            Dictionary<IntVec3, int> r = new Dictionary<IntVec3, int>();
            List<IntVec3> frontier = new List<IntVec3>();
            foreach (IntVec3 c in map.AllCells)
            {
                TerrainDef t = map.terrainGrid.TerrainAtIgnoreTemp(map.cellIndices.CellToIndex(c));
                // open sea only: a sea wall on bridged water, or a roof over it, is a barrier too
                if (t != null && t.IsWater && t.waterBodyType == WaterBodyType.Saltwater && !c.Roofed(map) && c.GetEdifice(map) == null)
                    frontier.Add(c);
            }
            for (int step = 1; step <= RM_TileFeaturesSettings.MaxTideReach && frontier.Count > 0; step++)
            {
                List<IntVec3> next = new List<IntVec3>();
                foreach (IntVec3 c in frontier)
                    foreach (IntVec3 d in GenAdj.CardinalDirections)
                    {
                        IntVec3 n = c + d;
                        if (r.ContainsKey(n) || !Eligible(n, map)) continue;
                        r[n] = step;
                        next.Add(n);
                    }
                frontier = next;
            }
            return r;
        }
    }
}
