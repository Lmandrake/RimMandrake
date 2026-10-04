// Messy Conduit core: Verse-free (see CordMath.cs header).
using System;
using System.Collections.Generic;

namespace RimMandrake.MessyConduit.Core
{
    /// <summary>What makes a conduit cell (or any cell) unwalkable; picks the stub look (design §8.7.3).</summary>
    public enum BlockKind : byte { None = 0, Wall = 1, Rock = 2, Water = 3, Device = 4, Hidden = 5 }

    public enum MachineKind { Source, Battery, Consumer, Lamp, Transmitter }

    /// <summary>A powered building: a node of the graph (design §8.2.1).</summary>
    public sealed class MachineInfo
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

        public bool Contains(Cell c) => c.X >= X0 && c.X < X0 + W && c.Z >= Z0 && c.Z < Z0 + H;
    }

    /// <summary>
    /// A plain-array snapshot of everything the cord model reads: which cells hold conduit, which
    /// are walkable, doors, trees, machines. The game adapter copies it from the map's own grids
    /// (linkGrid / thingGrid / pathing.Normal.pathGrid, design §8.1); the SelfTest fills it from the
    /// oracle's scenes. Nothing in the core ever touches the game.
    /// </summary>
    public sealed class CordWorld
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
}
