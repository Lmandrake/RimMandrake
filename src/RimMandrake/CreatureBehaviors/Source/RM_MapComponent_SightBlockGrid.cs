using Verse;

namespace RimMandrake.CreatureBehaviors
{
    // ════════════════════════════════════════════════════════════════════
    // GREENTIDE_PLANT_SIGHT_BLOCK_ENGINE_1 — per-map sight-blocker grid.
    //
    // Mirrors how CoverGrid/FogGrid are kept: a flat per-cell array updated
    // incrementally (RM_CompSightBlocker registers on spawn / growth crossing
    // its threshold, deregisters on despawn / falling below it), so the LOS
    // postfix does one array read per cell and never touches thing lists.
    // A count, not a bool, so two overlapping blockers on one cell cannot
    // clear each other. Nothing is saved: comps re-register on load.
    // ════════════════════════════════════════════════════════════════════
    public class RM_MapComponent_SightBlockGrid : MapComponent
    {
        private byte[] counts;
        private int sizeX;
        private int blockedCells;

        // Main-thread cache for the hot path: Map.GetComponent is a list scan.
        private static Map cachedMap;
        private static RM_MapComponent_SightBlockGrid cachedGrid;

        public RM_MapComponent_SightBlockGrid(Map map) : base(map)
        {
        }

        /// <summary>How many cells currently hold at least one qualifying blocker.</summary>
        public int BlockedCellCount => blockedCells;

        public static RM_MapComponent_SightBlockGrid For(Map map)
        {
            if (map == null)
            {
                return null;
            }
            if (map == cachedMap)
            {
                return cachedGrid;
            }
            RM_MapComponent_SightBlockGrid grid = map.GetComponent<RM_MapComponent_SightBlockGrid>();
            cachedMap = map;
            cachedGrid = grid;
            return grid;
        }

        private void EnsureArray()
        {
            if (counts == null)
            {
                sizeX = map.Size.x;
                counts = new byte[map.cellIndices.NumGridCells];
            }
        }

        public void Register(CellRect rect)
        {
            EnsureArray();
            foreach (IntVec3 c in rect)
            {
                if (!c.InBounds(map))
                {
                    continue;
                }
                int i = c.z * sizeX + c.x;
                if (counts[i] == 0)
                {
                    blockedCells++;
                }
                if (counts[i] < byte.MaxValue)
                {
                    counts[i]++;
                }
            }
        }

        public void Deregister(CellRect rect)
        {
            if (counts == null)
            {
                return;
            }
            foreach (IntVec3 c in rect)
            {
                if (!c.InBounds(map))
                {
                    continue;
                }
                int i = c.z * sizeX + c.x;
                if (counts[i] == 0)
                {
                    continue;
                }
                counts[i]--;
                if (counts[i] == 0)
                {
                    blockedCells--;
                }
            }
        }

        public bool IsBlocked(IntVec3 c)
        {
            return counts != null && c.x >= 0 && c.z >= 0 && c.x < sizeX && c.z * sizeX + c.x < counts.Length
                && counts[c.z * sizeX + c.x] != 0;
        }

        /// <summary>
        /// Exact replica of GenSight.LineOfSight(start, end, map, skipFirstCell, validator, halfXOffset, halfZOffset)'s
        /// cell walk (1.6 decompile). The start cell is ALWAYS skipped (a pawn standing in a thicket sees out of it) and
        /// the end cell is never visited by the vanilla walk either (you can see a pawn standing IN one thicket cell;
        /// what hides them is thicket BETWEEN). True when at least <paramref name="needed"/> blocked cells lie between.
        /// </summary>
        public bool WalkBlocks(IntVec3 start, IntVec3 end, int halfXOffset, int halfZOffset, int needed)
        {
            if (counts == null || blockedCells == 0)
            {
                return false;
            }
            bool flag = (start.x != end.x) ? (start.x < end.x) : (start.z < end.z);
            int num = System.Math.Abs(end.x - start.x);
            int num2 = System.Math.Abs(end.z - start.z);
            int x = start.x;
            int z = start.z;
            int n = 1 + num + num2;
            int ix = (end.x > start.x) ? 1 : -1;
            int iz = (end.z > start.z) ? 1 : -1;
            num *= 4;
            num2 *= 4;
            num += halfXOffset * 2;
            num2 += halfZOffset * 2;
            int err = num / 2 - num2 / 2;
            int hits = 0;
            int len = counts.Length;
            while (n > 1)
            {
                if ((x != start.x || z != start.z) && (x != end.x || z != end.z))
                {
                    int i = z * sizeX + x;
                    if (x >= 0 && x < sizeX && i >= 0 && i < len && counts[i] != 0 && ++hits >= needed)
                    {
                        return true;
                    }
                }
                if (err > 0 || (err == 0 && flag))
                {
                    x += ix;
                    err -= num2;
                }
                else
                {
                    z += iz;
                    err += num;
                }
                n--;
            }
            return false;
        }

        /// <summary>
        /// Exact replica of GenSight.LineOfSight(start, end, map, startRect, endRect, validator, forLeaning)'s cell walk:
        /// stops (clear) on reaching endRect, never counts cells inside startRect.
        /// </summary>
        public bool WalkBlocks(IntVec3 start, IntVec3 end, CellRect startRect, CellRect endRect, int needed)
        {
            if (counts == null || blockedCells == 0)
            {
                return false;
            }
            bool flag = (start.x != end.x) ? (start.x < end.x) : (start.z < end.z);
            int num = System.Math.Abs(end.x - start.x);
            int num2 = System.Math.Abs(end.z - start.z);
            int x = start.x;
            int z = start.z;
            int n = 1 + num + num2;
            int ix = (end.x > start.x) ? 1 : -1;
            int iz = (end.z > start.z) ? 1 : -1;
            int err = num - num2;
            num *= 2;
            num2 *= 2;
            int hits = 0;
            int len = counts.Length;
            IntVec3 c = default(IntVec3);
            while (n > 1)
            {
                c.x = x;
                c.z = z;
                if (endRect.Contains(c))
                {
                    return false;
                }
                if (!startRect.Contains(c))
                {
                    int i = z * sizeX + x;
                    if (x >= 0 && x < sizeX && i >= 0 && i < len && counts[i] != 0 && ++hits >= needed)
                    {
                        return true;
                    }
                }
                if (err > 0 || (err == 0 && flag))
                {
                    x += ix;
                    err -= num2;
                }
                else
                {
                    z += iz;
                    err += num;
                }
                n--;
            }
            return false;
        }

        public override void MapRemoved()
        {
            base.MapRemoved();
            if (cachedMap == map)
            {
                cachedMap = null;
                cachedGrid = null;
            }
        }
    }
}
