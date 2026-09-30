using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.LuminousPigment
{
    // DEEPFIRE_FLOOR_PAINT_1, spec §3.6 / §10 step 6.
    //
    // FLOORS have no comps, so this component owns a per-cell byte grid
    // `floorCoats` (Scribed, DataExposeUtility.LookByteArray). LIGHTS are
    // never saved (RM_DeepfireLightProxy is isSaveable=false): FinalizeInit
    // rebuilds every floor cluster from the grid, and coated Things re-register
    // from CompDeepfire.PostSpawnSetup, exactly as the engine rebuilds glowers.
    //
    // CLUSTERING: the map is tiled into fixed ClusterBlock x ClusterBlock
    // blocks (block = x / 3, z / 3). Inside one block, cells of the same KIND
    // (floor vs. 1x1 building), the same coat count and the same glow colour
    // share ONE proxy, placed on the group cell nearest the group's centroid,
    // radius = coat radius + ClusterRadiusBonus when the group holds 2+ cells.
    // A 6x6 floor whose corner sits on a multiple of 3 is therefore exactly
    // four proxies; an unaligned 6x6 straddles nine blocks and gets nine.
    // Floors and walls never merge (different kinds) so the floor proof's
    // proxy count is not disturbed by a painted wall around the room.
    public partial class MapComponent_DeepfireLights
    {
        private const byte KindFloor = 0;
        private const byte KindBuilding = 1;

        private readonly struct ClusterKey : System.IEquatable<ClusterKey>
        {
            public readonly int Block;
            public readonly byte Kind;
            public readonly int Coats;
            public readonly int Color;

            public ClusterKey(int block, byte kind, int coats, int color)
            {
                Block = block;
                Kind = kind;
                Coats = coats;
                Color = color;
            }

            public bool Equals(ClusterKey o) => Block == o.Block && Kind == o.Kind && Coats == o.Coats && Color == o.Color;
            public override bool Equals(object obj) => obj is ClusterKey k && Equals(k);
            public override int GetHashCode()
            {
                unchecked
                {
                    int h = Block;
                    h = h * 397 ^ Kind;
                    h = h * 397 ^ Coats;
                    h = h * 397 ^ Color;
                    return h;
                }
            }
        }

        private class ClusterGroup
        {
            public Color GlowColor;
            public readonly List<IntVec3> Cells = new List<IntVec3>();
        }

        private byte[] floorCoats;
        private int coatedFloorCells;

        // 1x1 buildings that joined a cluster, and the cell they joined at.
        private readonly Dictionary<Thing, IntVec3> clusteredThings = new Dictionary<Thing, IntVec3>();
        private readonly Dictionary<int, List<Thing>> blockThings = new Dictionary<int, List<Thing>>();
        private readonly Dictionary<int, List<ClusterKey>> blockKeys = new Dictionary<int, List<ClusterKey>>();

        // ---- public floor API (designator, job, dev actions, Harmony hooks) ----

        public int CoatedFloorCellCount => coatedFloorCells;

        public int FloorCoatsAt(IntVec3 c)
        {
            if (floorCoats == null || !c.InBounds(map)) return 0;
            return floorCoats[map.cellIndices.CellToIndex(c)];
        }

        // Spec §3.3: "any floor cell with a floor terrain (TerrainDef.layerable
        // / IsFloor) with fewer than three coats in the floor grid".
        public static bool IsCoatableFloor(Map map, IntVec3 c)
        {
            if (map == null || !c.InBounds(map)) return false;
            TerrainDef top = map.terrainGrid.TopTerrainAt(c);
            return top != null && top.layerable;
        }

        public bool CanAddFloorCoat(IntVec3 c)
        {
            return IsCoatableFloor(map, c) && FloorCoatsAt(c) < CompDeepfire.MaxCoats;
        }

        public bool AddFloorCoat(IntVec3 c)
        {
            if (!CanAddFloorCoat(c)) return false;
            EnsureGrid();
            int i = map.cellIndices.CellToIndex(c);
            bool firstCoat = floorCoats[i] == 0;
            if (firstCoat) coatedFloorCells++;
            floorCoats[i]++;
            AfterFloorChanged(c);
            // DEEPFIRE_GOD_BRIDGE_DELTAS_1, spec §5.2 "first coat on any
            // building/floor/item".
            if (firstCoat) DeepfireGodDeltas.OnFirstFloorCoat(map.terrainGrid.TopTerrainAt(c));
            return true;
        }

        // Spec §3.3 remove ("no refund") and §3.6 floor removed/replaced.
        public bool ClearFloorCoats(IntVec3 c)
        {
            if (floorCoats == null || !c.InBounds(map)) return false;
            int i = map.cellIndices.CellToIndex(c);
            if (floorCoats[i] == 0) return false;
            floorCoats[i] = 0;
            coatedFloorCells--;
            AfterFloorChanged(c);
            return true;
        }

        // SetTerrainColor postfix: recolour -> relight. A null ColorDef keeps
        // the coats; FloorBaseColor then falls back to the floor def's colour.
        public void Notify_FloorColorChanged(IntVec3 c)
        {
            if (FloorCoatsAt(c) <= 0) return;
            RebuildBlockOf(c);
        }

        // Glow colour source for a floor cell (spec §3.1: "Floors read
        // TerrainGrid.ColorAt(c)").
        public Color FloorBaseColor(IntVec3 c)
        {
            ColorDef cd = map.terrainGrid.ColorAt(c);
            if (cd != null) return cd.color;
            return map.terrainGrid.TopTerrainAt(c).DrawColor;
        }

        // Proof/diagnostic counters (dev actions read these).
        public int FloorLightCount => CountLights(KindFloor);
        public int ClusteredBuildingLightCount => CountLights(KindBuilding);
        public int TotalLightCount => entries.Count;

        public int CountCoatedFloorCells(IEnumerable<IntVec3> cells)
        {
            if (floorCoats == null || coatedFloorCells == 0) return 0;
            int n = 0;
            foreach (IntVec3 c in cells)
            {
                if (c.InBounds(map) && floorCoats[map.cellIndices.CellToIndex(c)] > 0) n++;
            }
            return n;
        }

        public List<string> DescribeFloorLights()
        {
            var list = new List<string>();
            foreach (KeyValuePair<object, LightEntry> kv in entries)
            {
                if (!(kv.Key is ClusterKey k) || k.Kind != KindFloor) continue;
                CompGlower g = kv.Value.Proxy?.TryGetComp<CompGlower>();
                list.Add(string.Format("{0},{1} coats={2} radius={3:0.##} color={4}",
                    kv.Value.Cell.x, kv.Value.Cell.z, k.Coats, g?.GlowRadius ?? 0f,
                    g != null ? g.GlowColor.ToString() : "?"));
            }
            return list;
        }

        // DEEPFIRE_PROXY_BLOCKS_STORAGE_1 proof: the cells the floor proxies sit on.
        public List<IntVec3> FloorLightCells()
        {
            var list = new List<IntVec3>();
            foreach (KeyValuePair<object, LightEntry> kv in entries)
            {
                if (kv.Key is ClusterKey k && k.Kind == KindFloor && kv.Value.Proxy != null && !kv.Value.Proxy.Destroyed)
                    list.Add(kv.Value.Proxy.Position);
            }
            return list;
        }

        // ---- building cluster membership ----

        private static bool IsClusterable(Thing t)
        {
            return LuminousPigmentSettings.clusterBlock > 1
                && t.def.category == ThingCategory.Building
                && t.def.size.x == 1 && t.def.size.z == 1;
        }

        private void RegisterClusteredThing(Thing t)
        {
            IntVec3 cell = t.Position;
            if (clusteredThings.TryGetValue(t, out IntVec3 old))
            {
                if (old != cell)
                {
                    RemoveFromBlockList(t, old);
                    AddToBlockList(t, cell);
                    RebuildBlockOf(old);
                }
            }
            else
            {
                AddToBlockList(t, cell);
            }
            clusteredThings[t] = cell;
            RebuildBlockOf(cell);
        }

        private bool DeregisterClusteredThing(Thing t)
        {
            if (!clusteredThings.TryGetValue(t, out IntVec3 cell)) return false;
            clusteredThings.Remove(t);
            RemoveFromBlockList(t, cell);
            RebuildBlockOf(cell);
            return true;
        }

        private void AddToBlockList(Thing t, IntVec3 cell)
        {
            int b = BlockIndex(cell);
            if (!blockThings.TryGetValue(b, out List<Thing> l))
            {
                l = new List<Thing>();
                blockThings[b] = l;
            }
            if (!l.Contains(t)) l.Add(t);
        }

        private void RemoveFromBlockList(Thing t, IntVec3 cell)
        {
            int b = BlockIndex(cell);
            if (blockThings.TryGetValue(b, out List<Thing> l))
            {
                l.Remove(t);
                if (l.Count == 0) blockThings.Remove(b);
            }
        }

        // ---- block rebuild ----

        private static int ClusterBlockSize => System.Math.Max(1, LuminousPigmentSettings.clusterBlock);

        private int BlocksX => (map.Size.x + ClusterBlockSize - 1) / ClusterBlockSize;

        private int BlockIndex(IntVec3 c)
        {
            int b = ClusterBlockSize;
            return (c.z / b) * BlocksX + (c.x / b);
        }

        private void RebuildBlockOf(IntVec3 c)
        {
            if (!c.InBounds(map)) return;
            RebuildBlock(BlockIndex(c));
        }

        private static readonly Dictionary<ClusterKey, ClusterGroup> tmpGroups = new Dictionary<ClusterKey, ClusterGroup>();

        private void RebuildBlock(int block)
        {
            int size = ClusterBlockSize;
            int bx = block % BlocksX;
            int bz = block / BlocksX;
            tmpGroups.Clear();

            // floor cells
            if (floorCoats != null && coatedFloorCells > 0)
            {
                for (int dz = 0; dz < size; dz++)
                {
                    for (int dx = 0; dx < size; dx++)
                    {
                        IntVec3 c = new IntVec3(bx * size + dx, 0, bz * size + dz);
                        if (!c.InBounds(map)) continue;
                        int coats = floorCoats[map.cellIndices.CellToIndex(c)];
                        if (coats <= 0) continue;
                        Color glow = DeepfireColorUtility.GlowColorFor(FloorBaseColor(c), coats);
                        AddToGroup(block, KindFloor, coats, glow, c);
                    }
                }
            }

            // 1x1 coated buildings
            if (blockThings.TryGetValue(block, out List<Thing> things))
            {
                for (int i = 0; i < things.Count; i++)
                {
                    Thing t = things[i];
                    if (t == null || !t.Spawned || t.Map != map) continue;
                    CompDeepfire comp = t.TryGetComp<CompDeepfire>();
                    if (comp == null || comp.coats <= 0) continue;
                    Color glow = DeepfireColorUtility.GlowColorFor(t.DrawColor, comp.coats);
                    AddToGroup(block, KindBuilding, comp.coats, glow, t.Position);
                }
            }

            var produced = new List<ClusterKey>(tmpGroups.Count);
            foreach (KeyValuePair<ClusterKey, ClusterGroup> kv in tmpGroups)
            {
                ClusterGroup g = kv.Value;
                float radius = DeepfireColorUtility.RadiusForCoats(kv.Key.Coats);
                // ClusterRadiusBonus is not a spec §7 key -- internal tuning, stays a constant.
                if (g.Cells.Count > 1) radius += DeepfirePaintDefaults.ClusterRadiusBonus;
                SetLight(kv.Key, AnchorCell(g.Cells), g.GlowColor, radius);
                produced.Add(kv.Key);
            }
            tmpGroups.Clear();

            if (blockKeys.TryGetValue(block, out List<ClusterKey> previous))
            {
                for (int i = 0; i < previous.Count; i++)
                {
                    if (!produced.Contains(previous[i])) RemoveLight(previous[i]);
                }
            }
            if (produced.Count > 0) blockKeys[block] = produced;
            else blockKeys.Remove(block);
        }

        private static void AddToGroup(int block, byte kind, int coats, Color glow, IntVec3 c)
        {
            Color32 c32 = glow;
            int packed = (c32.r << 24) | (c32.g << 16) | (c32.b << 8) | c32.a;
            ClusterKey key = new ClusterKey(block, kind, coats, packed);
            if (!tmpGroups.TryGetValue(key, out ClusterGroup g))
            {
                g = new ClusterGroup { GlowColor = glow };
                tmpGroups[key] = g;
            }
            g.Cells.Add(c);
        }

        private static IntVec3 AnchorCell(List<IntVec3> cells)
        {
            if (cells.Count == 1) return cells[0];
            float sx = 0f, sz = 0f;
            for (int i = 0; i < cells.Count; i++)
            {
                sx += cells[i].x;
                sz += cells[i].z;
            }
            sx /= cells.Count;
            sz /= cells.Count;
            IntVec3 best = cells[0];
            float bestD = float.MaxValue;
            for (int i = 0; i < cells.Count; i++)
            {
                float d = (cells[i].x - sx) * (cells[i].x - sx) + (cells[i].z - sz) * (cells[i].z - sz);
                if (d < bestD)
                {
                    bestD = d;
                    best = cells[i];
                }
            }
            return best;
        }

        private int CountLights(byte kind)
        {
            int n = 0;
            foreach (object key in entries.Keys)
            {
                if (key is ClusterKey k && k.Kind == kind) n++;
            }
            return n;
        }

        private void AfterFloorChanged(IntVec3 c)
        {
            RebuildBlockOf(c);
            // Room.GetStat caches until statsAndRoleDirty; a coat change is
            // not a terrain change, so the room must be told (RimSage:
            // Verse/Room.Notify_TerrainChanged sets statsAndRoleDirty).
            c.GetRoom(map)?.Notify_TerrainChanged();
        }

        private void EnsureGrid()
        {
            int n = map.cellIndices.NumGridCells;
            if (floorCoats == null || floorCoats.Length != n)
            {
                floorCoats = new byte[n];
                coatedFloorCells = 0;
            }
        }

        private void ClearClusterState()
        {
            clusteredThings.Clear();
            blockThings.Clear();
            blockKeys.Clear();
        }

        // DEEPFIRE_MOD_SETTINGS_1, spec §7 clusterBlock: block indices are
        // keyed off the block SIZE (BlocksX/BlockIndex), so a live setting
        // change leaves every existing key stale. Rebuild every cluster from
        // scratch -- the same "floor grid + every coated Thing" FinalizeInit
        // already does on map load -- instead of trying to migrate the old
        // block bookkeeping in place. Called from LuminousPigmentMod.
        // ApplySettings() for every loaded map.
        public void RebuildAllClustering()
        {
            var staleKeys = new List<object>();
            foreach (KeyValuePair<object, LightEntry> kv in entries)
            {
                if (kv.Key is ClusterKey) staleKeys.Add(kv.Key);
            }
            for (int i = 0; i < staleKeys.Count; i++) RemoveLight(staleKeys[i]);
            ClearClusterState();

            if (floorCoats != null && coatedFloorCells > 0)
            {
                var doneBlocks = new HashSet<int>();
                for (int i = 0; i < floorCoats.Length; i++)
                {
                    if (floorCoats[i] == 0) continue;
                    IntVec3 c = map.cellIndices.IndexToCell(i);
                    int b = BlockIndex(c);
                    if (doneBlocks.Add(b)) RebuildBlock(b);
                }
            }

            RegisterCoatedIn(map.listerBuildings.allBuildingsColonist);
            RegisterCoatedIn(map.listerBuildings.allBuildingsNonColonist);
        }

        private void RegisterCoatedIn(List<Building> buildings)
        {
            if (buildings == null) return;
            for (int i = 0; i < buildings.Count; i++)
            {
                Thing t = buildings[i];
                if (!IsClusterable(t)) continue;
                CompDeepfire comp = t.TryGetComp<CompDeepfire>();
                if (comp == null || comp.coats <= 0) continue;
                RegisterClusteredThing(t);
            }
        }

        // ---- persistence ----

        public override void ExposeData()
        {
            base.ExposeData();
            DataExposeUtility.LookByteArray(ref floorCoats, "rmDeepfireFloorCoats");
        }

        public override void FinalizeInit()
        {
            base.FinalizeInit();
            if (floorCoats != null && floorCoats.Length != map.cellIndices.NumGridCells)
            {
                Log.Warning("[LuminousPigment] Deepfire floor grid size does not match the map; coats dropped.");
                floorCoats = null;
            }
            EnsureGrid();

            coatedFloorCells = 0;
            var dirtyBlocks = new HashSet<int>();
            for (int i = 0; i < floorCoats.Length; i++)
            {
                if (floorCoats[i] == 0) continue;
                IntVec3 c = map.cellIndices.IndexToCell(i);
                if (!IsCoatableFloor(map, c))
                {
                    floorCoats[i] = 0; // floor vanished while we were not listening
                    continue;
                }
                if (floorCoats[i] > CompDeepfire.MaxCoats) floorCoats[i] = CompDeepfire.MaxCoats;
                coatedFloorCells++;
                dirtyBlocks.Add(BlockIndex(c));
            }
            foreach (int b in dirtyBlocks) RebuildBlock(b);
        }
    }
}
