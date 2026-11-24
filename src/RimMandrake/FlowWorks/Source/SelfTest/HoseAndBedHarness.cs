// Engine doubles for the extracted hose order, post-load lay/drain and dry pond bed return.
// The fixtures supply cell contents, saved fields and lay results, as Verse would.
using RimMandrake.FlowWorks.Hose;
using RimMandrake.FlowWorks.Machinery;
using RimMandrake.Shared.Slack;

namespace RimMandrake.FlowWorks.SelfTest.HoseHarness
{
    internal record struct IntVec3(int x, int y, int z)
    {
        public static readonly IntVec3 Invalid = new(-1, 0, -1);
        public bool IsValid => this != Invalid;
        public bool InBounds(Map map) => map.Hoses.World().InBounds(new Cell(x, z));
        public bool Walkable(Map map) => !map.blocked.Contains(this);
        public IEnumerable<Thing> GetThingList(Map map)
        {
            IntVec3 cell = this;
            return map.things.Where(t => t.Position == cell);
        }
    }

    internal record struct CellRect(int minX, int minZ, int maxX, int maxZ)
    {
        public CellRect ExpandedBy(int n) => new(minX - n, minZ - n, maxX + n, maxZ + n);
        public IEnumerable<IntVec3> EdgeCells
        {
            get
            {
                for (int z = minZ; z <= maxZ; z++)
                for (int x = minX; x <= maxX; x++)
                    if (x == minX || x == maxX || z == minZ || z == maxZ) yield return new IntVec3(x, 0, z);
            }
        }
    }

    internal class Thing
    {
        public Map Map;
        public IntVec3 Position;
        public int thingIDNumber;
        public bool Spawned = true;
        public string LabelNoCount => "pump";
        public CellRect OccupiedRect() => new(Position.x, Position.z, Position.x, Position.z);
    }

    internal class Building_LiquidPump : Thing { }

    internal class Map
    {
        public readonly List<Thing> things = new();
        public readonly HashSet<IntVec3> blocked = new();
        public readonly RM_MapComponent_Hoses Hoses;
        public Map() => Hoses = new RM_MapComponent_Hoses(this);
        public T GetComponent<T>() where T : class => Hoses as T;
    }

    internal static class HosePorts
    {
        public static HosePortKind Classify(Thing t) => t is Building_LiquidPump ? HosePortKind.Machine : HosePortKind.None;
        public static Thing FindAt(Map map, IntVec3 end, Thing exclude, out Cell side, out HosePortKind kind)
        {
            side = default;
            kind = HosePortKind.None;
            return map.things.OfType<Building_LiquidPump>().FirstOrDefault(p =>
                RM_PumpPortMath.SideOfPort(p.Position.x, p.Position.z, 1, 1, p.Position.x, p.Position.z, end.x, end.z) >= 0);
        }
    }

    internal enum LoadSaveMode { PostLoadInit }
    internal static class Scribe { public static LoadSaveMode mode = LoadSaveMode.PostLoadInit; }
    internal static class RM_HoseSettings
    {
        public static bool enabled = true, hoseHoldsLiquid = true;
    }

    internal partial class CompHoseReel
    {
        public Thing parent;
        public HoseReelRect Rect = new HoseReelRect(2, 5, 1, 1);
        public IntVec3 far = IntVec3.Invalid, layEnd = IntVec3.Invalid, pendingAt = IntVec3.Invalid;
        public HoseCarryState carry;
        public HosePendingOrder pending;
        public bool laid, pendingFresh, replanPending, restoringLay;
        public List<IntVec3> trail = new();
        public Thing carrier;
        public int heldUnits, flowUntil = RM_LiquidNetKernel.NoLease, spilled;
        public HoseLay lay;
        public string lastLayReason, layKey;
        public ulong corridorHash;
        public long corridorSeenAt;
        public void EndLease() => flowUntil = RM_LiquidNetKernel.NoLease;
    }

    internal static partial class RM_HoseLinks { }
    internal static class RM_LiquidSpill
    {
        public static IntVec3 DrainCell(CompHoseReel reel, Map map) => reel.far;
        public static void DrainHeld(CompHoseReel reel, Map map, IntVec3 cell)
        {
            reel.spilled += reel.heldUnits;
            reel.heldUnits = 0;
        }
    }

    internal partial class RM_MapComponent_Hoses
    {
        private readonly Map map;
        private readonly CordWorld world = new(25, 15);
        private readonly HoseReplanQueue replanQueue = new();
        public readonly List<CompHoseReel> reels = new();
        private static int LeaseVersion;
        private int LastLayMs, Relays;
        public RM_MapComponent_Hoses(Map map) => this.map = map;
        public CordWorld World() => world;
        public CompHoseReel ReelCovering(CompHoseReel reel, IntVec3 target) => null;
        public CompHoseReel RelayAt(CompHoseReel reel, Cell cell) =>
            reels.FirstOrDefault(r => r != reel && HoseRelay.IsIntakeOf(r.Rect, cell));
        public bool Loops(CompHoseReel reel, CompHoseReel relay, bool order) => false;
        public IEnumerable<CompHoseReel> FeedersOf(CompHoseReel relay) =>
            reels.Where(r => r.laid && RelayAt(r, new Cell(r.far.x, r.far.z)) == relay);
        public string CheckInstall(CompHoseReel reel, IntVec3 target) => HoseMath.CheckInstall(world, reel.Rect, new Cell(target.x, target.z), 20);
        private ulong CorridorHash(CordWorld w, HoseLay lay) => 0;
        private void DropMeshes(CompHoseReel r) { }
    }
}

namespace RimMandrake.FlowWorks.SelfTest.BedHarness
{
    internal record struct IntVec3(int x, int z)
    {
        public static IntVec3 operator +(IntVec3 a, IntVec3 b) => new(a.x + b.x, a.z + b.z);
        public bool InBounds(Map map) => x >= 0 && x <= 2 && z == 0;
    }
    internal static class GenAdj
    {
        public static readonly IntVec3[] CardinalDirections = { new(1, 0), new(0, 1), new(-1, 0), new(0, -1) };
    }
    internal class Map
    {
        public readonly Map cellIndices;
        public readonly Dictionary<IntVec3, bool> edificeGrid = new() { [new(0, 0)] = false, [new(1, 0)] = false, [new(2, 0)] = false };
        public Map() => cellIndices = this;
        public int CellToIndex(IntVec3 c) => c.x;
    }
    internal static class RM_FlowDoorRules { public static bool SealsLiquid(bool edifice) => edifice; }
    internal static class RimMandrakeFlowWorksSettings
    {
        public static bool pondBedHollowEnabled = true, pondReturnLegEnabled = true;
    }
    internal class FluidDef { }

    internal partial class Excavation
    {
        private readonly Map map = new();
        private const int bedCellCount = 1;
        private readonly List<IntVec3> excavatedCells = new() { new(1, 0), new(2, 0) };
        private readonly int[] depthGrid = { 0, 4, 4 };
        public readonly long[] water = { 0, 25000, 25000 };
        public long pondStock, pondCapacity = 20000;
        private readonly FluidDef ActiveFluid = new();
        private FluidDef FluidAt(IntVec3 c) => ActiveFluid;
        private int NaturalBedDepthAt(IntVec3 c) => c.x == 0 ? 2 : 0;
        private long WaterDl(int i) => water[i];
        private long WaterDlAt(IntVec3 c) => WaterDl(c.x);
        private long ReturnRoomDl(IntVec3 c, FluidDef fluid, long want) => Math.Min(want, pondCapacity - pondStock);
        private long TakeDlCore(IntVec3 c, long want, out FluidDef fluid)
        {
            fluid = ActiveFluid;
            long took = Math.Min(want, water[c.x]);
            water[c.x] -= took;
            return took;
        }
        private bool TryReturnDl(IntVec3 c, FluidDef fluid, long dl)
        {
            if (ReturnRoomDl(c, fluid, dl) != dl) return false;
            pondStock += dl;
            return true;
        }
        private bool TryPourDl(IntVec3 c, FluidDef fluid, long dl) { water[c.x] += dl; return true; }
        private void ReportLiquidLost(IntVec3 c, long dl, string reason) => throw new Exception(reason);
        public void ReturnAtShore() => RunIntoBeds();
    }
}
