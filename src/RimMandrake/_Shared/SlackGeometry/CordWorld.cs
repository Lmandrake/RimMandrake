// Gimme Some Slack core: Verse-free (see CordMath.cs header).
using System;
using System.Collections.Generic;

// _Shared/SlackGeometry (hose port step 1): linked by GimmeSomeSlack AND FlowWorks; top-level types INTERNAL (see DrawOrder.cs).
namespace RimMandrake.Shared.Slack
{
    /// <summary>What makes a conduit cell (or any cell) unwalkable; picks the stub look (design §8.7.3).</summary>
    internal enum BlockKind : byte { None = 0, Wall = 1, Rock = 2, Water = 3, Device = 4, Hidden = 5 }

    internal enum MachineKind { Source, Battery, Consumer, Lamp, Transmitter }

    /// <summary>A powered building: a node of the graph (design §8.2.1).</summary>
    internal sealed class MachineInfo
    {
        public string Id;
        public MachineKind Kind;
        public int X0, Z0, W = 1, H = 1;
        /// <summary>Conduit cells this machine hooks into (its connectParent cell, or every
        /// conduit cell orthogonally adjacent to a transmitter building's footprint).</summary>
        public List<Cell> Hookups = new List<Cell>();
        /// <summary>Other machines this one connects to directly (a heater on a battery).</summary>
        public List<string> MachineLinks = new List<string>();
        /// <summary>How far (cells) the machine's drawn art stands in from each footprint edge (S = bottom edge): a cord
        /// entering that side runs on this far under the art (owner review 2026-10-04 B10). 0 = art reaches the edge.</summary>
        public double InsetS, InsetN, InsetE, InsetW;

        /// <summary>Round 4 (owner 2026-10-04, station 19: "power cables connected to wall devices should just go up to and
        /// beneath the wall that contains the device, not stop short (such as lights), same rule as other powered devices"):
        /// a wall-mounted device (building.isAttachment: wall lamp, wall bracket) is drawn ON its wall, so its cord ends at
        /// the CENTRE of that wall cell, beneath the wall, instead of the footprint centroid. HasHome false = the centroid.</summary>
        public bool HasHome;
        public int HomeX, HomeZ;

        public bool Contains(Cell c) => c.X >= X0 && c.X < X0 + W && c.Z >= Z0 && c.Z < Z0 + H;
    }

    /// <summary>GPT source read 2026-10-06 B9 (owner decision by question card 2026-10-06: "draw a cord like any other
    /// connection"): a device wired straight to a battery, switch or other non-conduit transmitter building links to that
    /// building's machine node, so the graph lays its lead like any other. The game adapter and the selftest both call this.</summary>
    internal static class CordWorldLinks
    {
        /// <summary>Link device -> transmitter; the transmitter joins the world's machines if it is not there yet (a lone
        /// battery with no conduit beside it still needs its node).</summary>
        public static void LinkToMachine(CordWorld w, MachineInfo device, MachineInfo transmitter)
        {
            if (w == null || device == null || transmitter == null || device == transmitter) return;
            if (!device.MachineLinks.Contains(transmitter.Id)) device.MachineLinks.Add(transmitter.Id);
            if (!w.Machines.Contains(transmitter)) w.Machines.Add(transmitter);
            if (!w.Machines.Contains(device)) w.Machines.Add(device);
        }
    }

    /// <summary>
    /// A plain-array snapshot of everything the cord model reads: which cells hold conduit, which
    /// are walkable, doors, trees, machines. The game adapter copies it from the map's own grids
    /// (linkGrid / thingGrid / pathing.Normal.pathGrid, design §8.1); the SelfTest fills it from the
    /// oracle's scenes. Nothing in the core ever touches the game.
    /// </summary>
    internal sealed class CordWorld
    {
        public readonly int Width, Height;
        private readonly bool[] conduit;
        private readonly byte[] block;     // BlockKind per cell; None = walkable
        private readonly bool[] door;
        private readonly float[] extraCost;
        private readonly bool[] forcedBuried;
        public readonly List<MachineInfo> Machines = new List<MachineInfo>();
        /// <summary>Optional: forbid a conduit link between two cells (Odyssey substructure rule).</summary>
        public Func<Cell, Cell, bool> LinkAllowed;

        public CordWorld(int width, int height)
        {
            Width = width;
            Height = height;
            int n = width * height;
            conduit = new bool[n];
            block = new byte[n];
            door = new bool[n];
            extraCost = new float[n];
            forcedBuried = new bool[n];
        }

        public bool InBounds(Cell c) => c.X >= 0 && c.Z >= 0 && c.X < Width && c.Z < Height;
        private int Idx(Cell c) => c.Z * Width + c.X;

        public void SetConduit(Cell c, bool v = true) { if (InBounds(c)) conduit[Idx(c)] = v; }
        public void SetBlocked(Cell c, BlockKind k) { if (InBounds(c)) block[Idx(c)] = (byte)k; }
        public void SetDoor(Cell c) { if (InBounds(c)) door[Idx(c)] = true; }
        public void SetExtraCost(Cell c, float v) { if (InBounds(c)) extraCost[Idx(c)] = v; }
        // ---------------------------------------------------------------- bands (FlowWorks hoses into pits)
        // PIPE_POLES_BUILD_SAG_WITH_SUBSTANCE phase 6 (flowworks_pipes_across_pits_design_2026-10-20.md §P5): a cell's BAND is the
        // height it is walked at (0 = ground; a dug square its step depth). A route may step only between cells of one band,
        // or across a LINKED pair (a ramp or a ladder joining lip and floor). No band ever set (Gimme Some Slack, every world
        // before the hose sets one) = every step allowed and every corridor signature unchanged.
        private int[] band;
        private HashSet<long> bandLinks;

        /// <summary>True once any cell has a non-zero band.</summary>
        public bool HasBands => band != null;
        public void SetBand(Cell c, int b)
        {
            if (!InBounds(c)) return;
            if (band == null) { if (b == 0) return; band = TakeSpare(ref bandSpare) ?? new int[Width * Height]; }
            band[Idx(c)] = b;
        }
        public int BandAt(Cell c) => band != null && InBounds(c) ? band[Idx(c)] : 0;
        private long LinkKey(Cell a, Cell b) => (long)Idx(a) * (Width * (long)Height) + Idx(b);
        /// <summary>Lets a route step between the cardinal neighbours a and b although their bands differ (both directions).</summary>
        public void LinkBands(Cell a, Cell b)
        {
            if (!InBounds(a) || !InBounds(b)) return;
            if (bandLinks == null) { bandLinks = linksSpare ?? new HashSet<long>(); linksSpare = null; }
            bandLinks.Add(LinkKey(a, b));
            bandLinks.Add(LinkKey(b, a));
        }
        public bool BandLinked(Cell a, Cell b) => bandLinks != null && InBounds(a) && InBounds(b) && bandLinks.Contains(LinkKey(a, b));
        /// <summary>HOSE_TICK_REBUILD_ZERO_ALLOC: LinkBands undone (both directions); nothing linked is a no-op.</summary>
        public void UnlinkBands(Cell a, Cell b)
        {
            if (bandLinks == null || !InBounds(a) || !InBounds(b)) return;
            bandLinks.Remove(LinkKey(a, b));
            bandLinks.Remove(LinkKey(b, a));
        }

        /// <summary>HOSE_TICK_REBUILD_ZERO_ALLOC (HoseWorldPatch): one cell back to a new world's state (walkable, no door, no
        /// extra cost, band 0, not buried, no conduit) so the hose world's per-cell rule can be written over it again. Its
        /// band links stay: the patch re-judges every pair it touches (UnlinkBands).</summary>
        public void ClearCell(Cell c)
        {
            if (!InBounds(c)) return;
            int i = Idx(c);
            conduit[i] = false;
            block[i] = 0;
            door[i] = false;
            extraCost[i] = 0f;
            forcedBuried[i] = false;
            if (band != null) band[i] = 0;
        }

        /// <summary>The four cardinal links of c as a bit mask (N, E, S, W = bits 0..3): part of the corridor signature, so
        /// building or removing a ramp beside a route re-plans it.</summary>
        public int LinkMask(Cell c)
        {
            if (bandLinks == null) return 0;
            int m = 0;
            for (int r = 0; r < 4; r++) if (BandLinked(c, new Cell(c.X + CardX[r], c.Z + CardZ[r]))) m |= 1 << r;
            return m;
        }
        internal static readonly int[] CardX = { 0, 1, 0, -1 }, CardZ = { 1, 0, -1, 0 };

        /// <summary>May a route step from a to b (the same cell, or one of its 8 neighbours)? Same band, or a linked cardinal
        /// pair; a diagonal step only through one of its two corner cells with both of those steps allowed. Out-of-neighbour
        /// pairs are judged by band alone.</summary>
        public bool StepAllowed(Cell a, Cell b)
        {
            if (band == null) return true;
            int dx = b.X - a.X, dz = b.Z - a.Z;
            if (dx == 0 && dz == 0) return true;
            if (Math.Abs(dx) + Math.Abs(dz) == 1) return BandAt(a) == BandAt(b) || BandLinked(a, b);
            if (Math.Abs(dx) == 1 && Math.Abs(dz) == 1)
            {
                var m1 = new Cell(b.X, a.Z);
                var m2 = new Cell(a.X, b.Z);
                return (StepAllowed(a, m1) && StepAllowed(m1, b)) || (StepAllowed(a, m2) && StepAllowed(m2, b));
            }
            return BandAt(a) == BandAt(b);
        }

        // ---------------------------------------------------------------- busy cells (CORD_LOOP_UNTANGLE_LASSOED_A_PIPE)
        // A walkable cell holding a drawn linear building (a pipe, a conduit, any linked graphic): a canned slack loop or heap
        // never spreads onto one the strand does not already run through, or the cord reads as lassoing it. Nothing set (the
        // hose world, every SelfTest scene before this) = no cell busy and every lay unchanged.
        private bool[] busy;

        public bool HasBusy => busy != null;
        public void SetBusy(Cell c)
        {
            if (!InBounds(c)) return;
            if (busy == null) busy = TakeSpare(ref busySpare) ?? new bool[Width * Height];
            busy[Idx(c)] = true;
        }
        public bool IsBusy(Cell c) => busy != null && InBounds(c) && busy[Idx(c)];

        // ---------------------------------------------------------------- reuse (HOSE_TICK_FIX_SPIKES_AT_SUPERFAST)
        // Live round 9: every whole-map hose snapshot was a new ~1.3 MB world (325 map: five grids, the band grid, the link
        // set) and every lay-pool copy of a dropped snapshot was garbage too, so rebuilds fed the Boehm heap that freezes a
        // frame ~1.3 s per full collection. Reset and CopyFrom refill a retired world in place: afterwards it reads exactly
        // as a new CordWorld (Reset) or as src.Clone() (CopyFrom) through every accessor. The band grid, link set and busy
        // grid keep their "never set" state (null: HasBands, HasBusy, LinkMask's fast path); their storage waits as a spare.
        private int[] bandSpare;
        private HashSet<long> linksSpare;
        private bool[] busySpare;

        private static T[] TakeSpare<T>(ref T[] spare)
        {
            T[] a = spare;
            spare = null;
            if (a != null) Array.Clear(a, 0, a.Length);
            return a;
        }

        /// <summary>Back to a new CordWorld of the same size: every grid cleared, no bands, links, busy cells or machines.</summary>
        public void Reset()
        {
            Array.Clear(conduit, 0, conduit.Length);
            Array.Clear(block, 0, block.Length);
            Array.Clear(door, 0, door.Length);
            Array.Clear(extraCost, 0, extraCost.Length);
            Array.Clear(forcedBuried, 0, forcedBuried.Length);
            if (band != null) { bandSpare = band; band = null; }
            if (bandLinks != null) { bandLinks.Clear(); linksSpare = bandLinks; bandLinks = null; }
            if (busy != null) { busySpare = busy; busy = null; }
            Machines.Clear();
            LinkAllowed = null;
        }

        /// <summary>This world made a copy of <paramref name="src"/> (same size), in place: what <see cref="Clone"/> returns.</summary>
        public void CopyFrom(CordWorld src)
        {
            if (src.Width != Width || src.Height != Height) throw new ArgumentException("CordWorld.CopyFrom: size differs");
            Array.Copy(src.conduit, conduit, conduit.Length);
            Array.Copy(src.block, block, block.Length);
            Array.Copy(src.door, door, door.Length);
            Array.Copy(src.extraCost, extraCost, extraCost.Length);
            Array.Copy(src.forcedBuried, forcedBuried, forcedBuried.Length);
            if (src.band == null) { if (band != null) { bandSpare = band; band = null; } }
            else
            {
                if (band == null) { band = bandSpare ?? new int[Width * Height]; bandSpare = null; }
                Array.Copy(src.band, band, band.Length);
            }
            if (src.bandLinks == null) { if (bandLinks != null) { bandLinks.Clear(); linksSpare = bandLinks; bandLinks = null; } }
            else
            {
                if (bandLinks == null) { bandLinks = linksSpare ?? new HashSet<long>(); linksSpare = null; }
                bandLinks.Clear();
                bandLinks.UnionWith(src.bandLinks);
            }
            if (src.busy == null) { if (busy != null) { busySpare = busy; busy = null; } }
            else
            {
                if (busy == null) { busy = busySpare ?? new bool[Width * Height]; busySpare = null; }
                Array.Copy(src.busy, busy, busy.Length);
            }
            Machines.Clear();
            Machines.AddRange(src.Machines);
            LinkAllowed = src.LinkAllowed;
        }

        /// <summary>HOSE_LAY_FIX_SYNC_RELAY_IN_DRAW: an independent copy (every grid copied; Machines a new list of the same
        /// infos; LinkAllowed shared). A FlowWorks hose lay runs on a worker thread against its own copy, because the lay
        /// marks the reel's footprint solid for its duration (RM_MapComponent_Hoses.LayFrom) and the main thread keeps
        /// using the snapshot it was copied from.</summary>
        public CordWorld Clone()
        {
            var o = new CordWorld(Width, Height);
            Array.Copy(conduit, o.conduit, conduit.Length);
            Array.Copy(block, o.block, block.Length);
            Array.Copy(door, o.door, door.Length);
            Array.Copy(extraCost, o.extraCost, extraCost.Length);
            Array.Copy(forcedBuried, o.forcedBuried, forcedBuried.Length);
            if (band != null) o.band = (int[])band.Clone();
            if (bandLinks != null) o.bandLinks = new HashSet<long>(bandLinks);
            if (busy != null) o.busy = (bool[])busy.Clone();
            o.Machines.AddRange(Machines);
            o.LinkAllowed = LinkAllowed;
            return o;
        }

        /// <summary>A walkable conduit cell that must still count as buried (an untagged or Hidden
        /// conduit def): it carries connectivity but is never drawn (design §8.7.6 last rows).</summary>
        public void SetForcedBuried(Cell c) { if (InBounds(c)) forcedBuried[Idx(c)] = true; }

        public bool IsConduit(Cell c) => InBounds(c) && conduit[Idx(c)];
        public bool IsWalkable(Cell c) => InBounds(c) && block[Idx(c)] == 0;
        public BlockKind BlockAt(Cell c) => InBounds(c) ? (BlockKind)block[Idx(c)] : BlockKind.Wall;
        public bool IsDoor(Cell c) => InBounds(c) && door[Idx(c)];
        public float ExtraCost(Cell c) => InBounds(c) ? extraCost[Idx(c)] : 0f;

        /// <summary>A conduit cell drawn as buried: unwalkable, or forced (hidden/untagged conduit).</summary>
        public bool IsBuried(Cell c) => !IsWalkable(c) || (InBounds(c) && forcedBuried[Idx(c)]);
        public BlockKind BuriedKind(Cell c)
        {
            BlockKind k = BlockAt(c);
            if (k != BlockKind.None) return k;
            return InBounds(c) && forcedBuried[Idx(c)] ? BlockKind.Hidden : BlockKind.None;
        }

        public IEnumerable<Cell> ConduitCells()
        {
            for (int z = 0; z < Height; z++)
                for (int x = 0; x < Width; x++)
                    if (conduit[z * Width + x]) yield return new Cell(x, z);
        }

        /// <summary>
        /// Signed distance (cells) from p to the nearest unwalkable cell or the map edge: positive
        /// outside, negative inside. Exact against the axis-aligned cell boxes within 2 cells, which
        /// is all the planner and the slack ever ask about (clearances of 0.07-0.3 cell). Replaces the
        /// oracle's sampled SDF (rope.sdf_grid).
        /// </summary>
        public double Clearance(V2 p)
        {
            Cell c = p.Floor;
            if (!IsWalkable(c))
            {
                // inside: distance to the nearest walkable cell box, negated
                double best = 2.5;
                for (int dz = -2; dz <= 2; dz++)
                    for (int dx = -2; dx <= 2; dx++)
                    {
                        var q = new Cell(c.X + dx, c.Z + dz);
                        if (IsWalkable(q)) best = Math.Min(best, BoxDist(p, q));
                    }
                return -best;
            }
            double d = 2.5;
            for (int dz = -2; dz <= 2; dz++)
                for (int dx = -2; dx <= 2; dx++)
                {
                    if (dx == 0 && dz == 0) continue;
                    var q = new Cell(c.X + dx, c.Z + dz);
                    if (!IsWalkable(q)) d = Math.Min(d, BoxDist(p, q));
                }
            return d;
        }

        /// <summary>Unit direction of increasing clearance at p (central differences).</summary>
        public V2 ClearanceGradient(V2 p)
        {
            const double h = 0.03;
            double gx = Clearance(new V2(p.X + h, p.Z)) - Clearance(new V2(p.X - h, p.Z));
            double gz = Clearance(new V2(p.X, p.Z + h)) - Clearance(new V2(p.X, p.Z - h));
            var g = new V2(gx, gz);
            return g.Len < 1e-9 ? new V2(0, 0) : g.Norm();
        }

        private static double BoxDist(V2 p, Cell q)
        {
            double dx = Math.Max(Math.Max(q.X - p.X, 0), p.X - (q.X + 1));
            double dz = Math.Max(Math.Max(q.Z - p.Z, 0), p.Z - (q.Z + 1));
            return Math.Sqrt(dx * dx + dz * dz);
        }
    }

    /// <summary>One cell's part of a corridor hash (lifted from CordBuilder, hose port step 1, so the hose needs no builder):
    /// walkable, door, and (GPT source read 2026-10-06 B7/A13) the route cost (trees 1.5, water 3), so a tree cut or planted
    /// re-plans the cords and hoses through it instead of leaving the old route standing until a reload.</summary>
    internal static class CordSig
    {
        public static ulong CellSig(CordWorld w, Cell c) => Of(w.IsWalkable(c), w.IsDoor(c), w.ExtraCost(c), w.BandAt(c), w.LinkMask(c));

        /// <summary>The signature formula itself, shared with the hose's live per-cell read (RM_MapComponent_Hoses.LiveCellSig) so
        /// the two can never drift. Phase 6: the band and the cardinal link mask are folded in; both are 0 in a world with no
        /// bands, which leaves the value exactly the pre-band formula.</summary>
        public static ulong Of(bool walkable, bool door, float extra, int band, int linkMask) =>
            (ulong)(walkable ? 1 : 2) ^ (door ? 4UL : 0UL) ^ ((ulong)Math.Round(extra * 16) << 3)
            ^ ((ulong)(uint)band << 24) ^ ((ulong)(linkMask & 15) << 56);
    }
}
