// HOSE_TICK_REBUILD_ZERO_ALLOC: the hose world patched cell by cell instead of rebuilt whole. Verse-free (compiled into the
// SelfTest, whose HoseWorldPatchChecks hold Patch == Full over thousands of random spawns and removals). The game adapter is
// RM_MapComponent_Hoses (its LiveRule writes one cell by World()'s rule; ProofPatch holds a patched world to BuildWorld live).
using System;
using RimMandrake.Shared.Slack;

namespace RimMandrake.FlowWorks.Hose
{
    /// <summary>The hose world's rule for one cell, as the whole-map build applies it.</summary>
    internal interface IHoseCellRule
    {
        /// <summary>Writes cell c of a cleared world (CordWorld.ClearCell): base (fog, door, walkable, water, rig, blocked),
        /// tree, and when <see cref="BandsActive"/> the band pass's closed verdict and band.</summary>
        void WriteCell(CordWorld w, Cell c);
        /// <summary>Does the band pass run at all (RM_HoseBands.Apply's early returns)?</summary>
        bool BandsActive { get; }
        /// <summary>RM_HoseBands.Linked: may a route step from a (band ba) to its cardinal neighbour b (band bb)?</summary>
        bool Linked(Cell a, Cell b, int ba, int bb);
    }

    /// <summary>The cells changed since the hose world was built: a stamp grid (each cell listed once) and a list, both reused.
    /// Past <see cref="Capacity"/> cells it only says <see cref="Overflow"/> and the caller rebuilds whole.</summary>
    internal sealed class HoseWorldDirty
    {
        public readonly int Capacity;
        private int[] stamp = new int[0];
        private readonly int[] list;
        private int gen = 1, width, height;
        public int Count { get; private set; }
        public bool Overflow { get; private set; }

        public HoseWorldDirty(int capacity)
        {
            Capacity = capacity;
            list = new int[capacity];
        }

        /// <summary>Sized for a w x h world; a new size (a different map) starts empty.</summary>
        public void Ensure(int w, int h)
        {
            if (w == width && h == height) return;
            width = w;
            height = h;
            stamp = new int[w * h];
            gen = 1;
            Count = 0;
            Overflow = false;
        }

        public void Mark(int x, int z)
        {
            if (x < 0 || z < 0 || x >= width || z >= height) return;
            int i = z * width + x;
            if (stamp[i] == gen) return;
            if (Count == Capacity) { Overflow = true; return; }
            stamp[i] = gen;
            list[Count++] = i;
        }

        /// <summary>Marks every cell of the inclusive rectangle (clipped to the world).</summary>
        public void MarkRect(int x0, int z0, int x1, int z1)
        {
            for (int z = z0; z <= z1; z++)
                for (int x = x0; x <= x1; x++)
                    Mark(x, z);
        }

        public Cell At(int k) => new Cell(list[k] % width, list[k] / width);

        public void Clear()
        {
            Count = 0;
            Overflow = false;
            if (++gen == int.MaxValue) { Array.Clear(stamp, 0, stamp.Length); gen = 1; }
        }
    }

    internal static class HoseWorldPatch
    {
        /// <summary>Brings a world built by <see cref="Full"/> (or the game's BuildWorld) up to date after the cells in
        /// <paramref name="dirty"/> changed: each is cleared and rewritten, and every band link with an end in one is judged
        /// again (Apply's rule: a pair of differing bands is linked when either end, on a non-zero band, says Linked). Only
        /// the dirty cells' own state may have changed, and Linked must read only its pair. Allocates nothing once the link
        /// set has grown to its size.</summary>
        public static void Patch(CordWorld w, HoseWorldDirty dirty, IHoseCellRule rule)
        {
            int n = dirty.Count;
            for (int k = 0; k < n; k++)
            {
                Cell c = dirty.At(k);
                w.ClearCell(c);
                rule.WriteCell(w, c);
            }
            // bands off: the world was built with none (switching them is a whole rebuild) and none was written above
            if (!rule.BandsActive || !w.HasBands) return;
            for (int k = 0; k < n; k++)
            {
                Cell c = dirty.At(k);
                int b = w.BandAt(c);
                for (int r = 0; r < 4; r++)
                {
                    var nc = new Cell(c.X + CordWorld.CardX[r], c.Z + CordWorld.CardZ[r]);
                    if (!w.InBounds(nc)) continue;
                    w.UnlinkBands(c, nc);
                    int nb = w.BandAt(nc);
                    if (nb != b && ((b != 0 && rule.Linked(c, nc, b, nb)) || (nb != 0 && rule.Linked(nc, c, nb, b)))) w.LinkBands(c, nc);
                }
            }
        }

        /// <summary>The whole-map build Patch must equal: every cell written, then (bands active and any band set) every
        /// non-zero-band cell linked to each differing cardinal neighbour it says Linked (RM_HoseBands.Apply's second pass).</summary>
        public static void Full(CordWorld w, IHoseCellRule rule)
        {
            w.Reset();
            for (int z = 0; z < w.Height; z++)
                for (int x = 0; x < w.Width; x++)
                    rule.WriteCell(w, new Cell(x, z));
            if (!rule.BandsActive || !w.HasBands) return;
            for (int z = 0; z < w.Height; z++)
                for (int x = 0; x < w.Width; x++)
                {
                    var c = new Cell(x, z);
                    int b = w.BandAt(c);
                    if (b == 0) continue;
                    for (int r = 0; r < 4; r++)
                    {
                        var n = new Cell(x + CordWorld.CardX[r], z + CordWorld.CardZ[r]);
                        if (!w.InBounds(n)) continue;
                        int nb = w.BandAt(n);
                        if (nb != b && rule.Linked(c, n, b, nb)) w.LinkBands(c, n);
                    }
                }
        }
    }
}
