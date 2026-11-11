// PLOT_D_BODY_PRUNE_STALE_SEA: the stage on which the PRODUCTION RM_LiquidStock.ReleaseRect runs offline.
// The selftest has no Verse, so the csproj's ExtractReleaseRect target copies the method, byte for byte and brace-matched,
// out of ..\RM_LiquidStock.cs into obj\...\ReleaseRect.g.cs as a member of StockHarness below. The Verse types it touches
// are stubbed here with only the members it uses; RM_StockMath, RM_BedMath and RM_FlowKernel are the real files. A change
// to ReleaseRect's body is therefore what these cases test, not a copy (a blind check 2026-11-03 found the earlier
// source-text cases stayed green with an early `return 0;`).
using System.Collections.Generic;

namespace RimMandrake.FlowWorks.SelfTest.ReleaseRectHarness
{
    internal struct IntVec3
    {
        public int x, z;
        public IntVec3(int x, int z) { this.x = x; this.z = z; }
    }

    internal struct CellRect
    {
        public int minX, minZ, Width, Height;
        public CellRect(int x, int z, int w, int h) { minX = x; minZ = z; Width = w; Height = h; }
        public bool Contains(IntVec3 c) => c.x >= minX && c.x < minX + Width && c.z >= minZ && c.z < minZ + Height;
    }

    internal sealed class Map
    {
        public IntVec3 Size;
        public Map(int w, int h) { Size = new IntVec3(w, h); }
    }

    internal sealed class RM_MapComponent_Excavation
    {
        public readonly Dictionary<(int, int), int> beds = new Dictionary<(int, int), int>();
        public int BedLevelsAt(IntVec3 c) => beds.TryGetValue((c.x, c.z), out int b) ? b : 1;
    }

    internal sealed class RM_LiquidBody
    {
        public int id;
        public bool limitless;
        public float capacity;
        public float stock;
        public float levelUnit;
        public List<IntVec3> cells = new List<IntVec3>();
        public List<IntVec3> receded = new List<IntVec3>();
        public void AddStock(double fillUnits) { stock += (float)fillUnits; }
    }

    internal sealed partial class StockHarness
    {
        public List<RM_LiquidBody> bodies = new List<RM_LiquidBody>();
        public readonly Dictionary<int, int> cellToBody = new Dictionary<int, int>();
        public readonly Dictionary<int, RM_LiquidBody> byId = new Dictionary<int, RM_LiquidBody>();
        public bool indexDirty;
        public int rebuilds;

        public void RebuildIndex(Map map)
        {
            rebuilds++;
            cellToBody.Clear();
            foreach (RM_LiquidBody body in bodies)
            {
                foreach (IntVec3 c in body.cells)
                {
                    cellToBody[c.z * map.Size.x + c.x] = body.id;
                }
            }
            indexDirty = false;
        }

        public static int BedSum(RM_LiquidBody body, RM_MapComponent_Excavation owner)
        {
            int sum = 0;
            foreach (IntVec3 c in body.cells)
            {
                sum += owner.BedLevelsAt(c);
            }
            return sum;
        }

        public static float LevelUnitOf(RM_LiquidBody body, RM_MapComponent_Excavation owner) =>
            body.levelUnit > 0f ? body.levelUnit : RM_BedMath.LevelUnit(body.capacity, BedSum(body, owner));

        public RM_LiquidBody Add(int id, bool limitless, float levelUnit, IEnumerable<IntVec3> cells, int width)
        {
            var b = new RM_LiquidBody { id = id, limitless = limitless, levelUnit = levelUnit };
            b.cells.AddRange(cells);
            bodies.Add(b);
            byId[id] = b;
            foreach (IntVec3 c in b.cells)
            {
                cellToBody[c.z * width + c.x] = id;
            }
            return b;
        }
    }
}
