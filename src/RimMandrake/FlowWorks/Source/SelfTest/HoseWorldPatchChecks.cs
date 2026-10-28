// HOSE_TICK_REBUILD_ZERO_ALLOC: on map1 every huge-tree trunk blocker spawned or despawned rebuilt the whole hose world
// (388 BuildWorld per window, 21 ms peak own work). HoseWorldPatch rewrites only the changed cells. The oracle: after each of
// thousands of random blocker spawns and removals (kind, tree, cover and band changes, rectangles up to 3x3), the patched
// world reads exactly as a fresh whole-map build, cell by cell (CellSig, BlockAt) and step by step (StepAllowed, every
// cell to its 8 neighbours) -- and a patch allocates nothing.
using System;
using RimMandrake.FlowWorks.Hose;
using RimMandrake.Shared.Slack;

namespace RimMandrake.FlowWorks.SelfTest
{
    internal static class HoseWorldPatchChecks
    {
        private static void Assert(bool ok, string msg)
        {
            if (!ok) throw new Exception(msg);
        }

        /// <summary>A random map: per cell a kind (open, wall, rock, door, water, walk-over building), a tree, a pit cover
        /// and a band; Linked is a fixed hash of the pair's kinds, cells and bands (so a spawn changes its links).</summary>
        private sealed class RandRule : IHoseCellRule
        {
            public readonly int W, H;
            public readonly byte[] Kind;
            public readonly bool[] Tree, Closed;
            public readonly int[] Band;
            public bool Active;
            public int Salt;

            public RandRule(int w, int h)
            {
                W = w; H = h;
                Kind = new byte[w * h]; Tree = new bool[w * h]; Closed = new bool[w * h]; Band = new int[w * h];
            }

            public bool BandsActive => Active;

            public void WriteCell(CordWorld w, Cell c)
            {
                int i = c.Z * W + c.X;
                switch (Kind[i])
                {
                    case 1: w.SetBlocked(c, BlockKind.Wall); break;
                    case 2: w.SetBlocked(c, BlockKind.Rock); break;
                    case 3: w.SetDoor(c); break;
                    case 4: w.SetExtraCost(c, 3f); break;
                    case 5: w.SetExtraCost(c, HoseMath.BuildingCrossCost); break;
                }
                if (Tree[i]) w.SetExtraCost(c, 1.5f);
                if (!Active) return;
                if (Closed[i]) w.SetBlocked(c, BlockKind.Wall);
                if (Band[i] != 0) w.SetBand(c, Band[i]);
            }

            public bool Linked(Cell a, Cell b, int ba, int bb)
            {
                unchecked
                {
                    uint h = (uint)Salt;
                    h = (h ^ (uint)(a.Z * W + a.X)) * 16777619u;
                    h = (h ^ (uint)(b.Z * W + b.X)) * 16777619u;
                    h = (h ^ Kind[a.Z * W + a.X]) * 16777619u;
                    h = (h ^ Kind[b.Z * W + b.X]) * 16777619u;
                    h = (h ^ (uint)ba) * 16777619u;
                    h = (h ^ (uint)bb) * 16777619u;
                    return (h >> 7) % 3 == 0;
                }
            }

            public void Randomize(Random rng, int i, bool blocker)
            {
                Kind[i] = (byte)(blocker ? (rng.Next(2) == 0 ? 1 : 5) : rng.Next(6));
                Tree[i] = !blocker && rng.Next(8) == 0;
                Closed[i] = rng.Next(10) == 0;
                Band[i] = rng.Next(3) == 0 ? -rng.Next(1, 4) : 0;
            }
        }

        private static string Diff(CordWorld a, CordWorld b)
        {
            for (int z = 0; z < a.Height; z++)
                for (int x = 0; x < a.Width; x++)
                {
                    var c = new Cell(x, z);
                    if (CordSig.CellSig(a, c) != CordSig.CellSig(b, c) || a.BlockAt(c) != b.BlockAt(c))
                        return "cell " + x + "," + z + " patched block=" + a.BlockAt(c) + " band=" + a.BandAt(c) + " links=" + a.LinkMask(c)
                            + " extra=" + a.ExtraCost(c) + " full block=" + b.BlockAt(c) + " band=" + b.BandAt(c) + " links=" + b.LinkMask(c)
                            + " extra=" + b.ExtraCost(c);
                    for (int dz = -1; dz <= 1; dz++)
                        for (int dx = -1; dx <= 1; dx++)
                        {
                            var n = new Cell(x + dx, z + dz);
                            if (a.StepAllowed(c, n) != b.StepAllowed(c, n)) return "step " + x + "," + z + " -> " + n.X + "," + n.Z;
                        }
                }
            return null;
        }

        public static void Run(Action<string, Action> Case)
        {
            Case("HOSEPATCH_EQUALS_FULL_REBUILD_RANDOM_SPAWNS", () =>
            {
                var rng = new Random(20261028);
                int scenes = 300, patches = 0;
                for (int s = 0; s < scenes; s++)
                {
                    int w = rng.Next(4, 26), h = rng.Next(4, 26);
                    var rule = new RandRule(w, h) { Active = rng.Next(5) != 0, Salt = rng.Next() };
                    for (int i = 0; i < w * h; i++) rule.Randomize(rng, i, false);
                    var world = new CordWorld(w, h);
                    var fresh = new CordWorld(w, h);
                    HoseWorldPatch.Full(world, rule);
                    var dirty = new HoseWorldDirty(64);
                    dirty.Ensure(w, h);
                    for (int step = 0; step < 15; step++)
                    {
                        // a blocker spawned (a wall or walk-over building, maybe with a cover or band under it) or removed
                        int rects = rng.Next(1, 3);
                        for (int k = 0; k < rects; k++)
                        {
                            int x0 = rng.Next(w), z0 = rng.Next(h), x1 = Math.Min(w - 1, x0 + rng.Next(3)), z1 = Math.Min(h - 1, z0 + rng.Next(3));
                            bool spawn = rng.Next(2) == 0;
                            for (int z = z0; z <= z1; z++)
                                for (int x = x0; x <= x1; x++)
                                    rule.Randomize(rng, z * w + x, spawn);
                            dirty.MarkRect(x0, z0, x1, z1);
                        }
                        Assert(!dirty.Overflow, "scene " + s + ": 2 rects of 3x3 fit 64");
                        HoseWorldPatch.Patch(world, dirty, rule);
                        dirty.Clear();
                        HoseWorldPatch.Full(fresh, rule);
                        string d = Diff(world, fresh);
                        Assert(d == null, "scene " + s + " step " + step + " (" + w + "x" + h + ", bands " + rule.Active + "): " + d);
                        patches++;
                    }
                }
                Assert(patches == scenes * 15, "every patch compared: " + patches);
            });

            Case("HOSEPATCH_DIRTY_LISTS_ONCE_AND_OVERFLOWS", () =>
            {
                var d = new HoseWorldDirty(4);
                d.Ensure(10, 10);
                d.MarkRect(0, 0, 1, 0);
                d.Mark(0, 0);
                d.Mark(-1, 3);
                d.Mark(10, 3);
                Assert(d.Count == 2 && !d.Overflow, "a cell is listed once, out of bounds never: " + d.Count);
                Assert(d.At(1).X == 1 && d.At(1).Z == 0, "At reads the cell back");
                d.MarkRect(5, 5, 7, 5);
                Assert(d.Count == 4 && d.Overflow, "past capacity: overflow, list kept at capacity");
                d.Clear();
                Assert(d.Count == 0 && !d.Overflow, "Clear empties");
                d.Mark(0, 0);
                Assert(d.Count == 1, "a cell listed before Clear lists again after");
            });

            Case("HOSEPATCH_ALLOCATES_NOTHING", () =>
            {
                var rng = new Random(7);
                int w = 250, h = 250;
                var rule = new RandRule(w, h) { Active = true, Salt = 11 };
                for (int i = 0; i < w * h; i++) rule.Randomize(rng, i, false);
                var world = new CordWorld(w, h);
                HoseWorldPatch.Full(world, rule);
                var dirty = new HoseWorldDirty(4096);
                dirty.Ensure(w, h);
                // a trunk blocker spawning and despawning at the same squares: after one round the link set holds its size
                var r2 = new Random(3);
                var at = new int[80];
                for (int k = 0; k < 80; k++) at[k] = r2.Next(w - 2);
                void Round(bool spawn)
                {
                    for (int k = 0; k < 40; k++)
                    {
                        int x0 = at[2 * k], z0 = at[2 * k + 1];
                        for (int z = z0; z <= z0 + 1; z++)
                            for (int x = x0; x <= x0 + 1; x++)
                                rule.Kind[z * w + x] = (byte)(spawn ? 1 : 0);
                        dirty.MarkRect(x0, z0, x0 + 1, z0 + 1);
                        HoseWorldPatch.Patch(world, dirty, rule);
                        dirty.Clear();
                    }
                }
                Round(true); Round(false); Round(true); Round(false);
                long a0 = GC.GetAllocatedBytesForCurrentThread();
                for (int i = 0; i < 5; i++) { Round(true); Round(false); }
                long bytes = GC.GetAllocatedBytesForCurrentThread() - a0;
                Assert(bytes == 0, "400 patches allocated " + bytes + " bytes");
                var fresh = new CordWorld(w, h);
                HoseWorldPatch.Full(fresh, rule);
                Assert(Diff(world, fresh) == null, "and still equal the full build: " + Diff(world, fresh));
            });
        }
    }
}
