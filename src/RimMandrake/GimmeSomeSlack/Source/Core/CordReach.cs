// Gimme Some Slack core: Verse-free (see CordMath.cs header).
// GSS_SNAPSHOT_MEASURE_REBUILD_PER_DIG (live 2026-10-26): a dig anywhere on the map rebuilt every cord. This is the cheap
// spatial answer to "can a terrain or roof change at this cell alter the next Build?".
using System;
using System.Collections.Generic;
using RimMandrake.Shared.Slack;

namespace RimMandrake.GimmeSomeSlack.Core
{
    /// <summary>
    /// The cells where a terrain or roof change can alter what CordBuilder.Build lays, as a coarse block grid built at the
    /// end of each Build. A Build reads the world only (a) through CordGraph at conduit cells (buried kind) and machines,
    /// (b) inside each laid edge's corridor rect, whose hash decides reuse, and (c) the component reads roofs and floor at
    /// each piece's strand points for its static/dynamic split. So the reach is the union of every conduit cell, machine
    /// footprint (and wall home), and every piece's box (corridor, owner, strands, decals, end tips), each grown by
    /// <see cref="Margin"/> cells and rounded out to <see cref="Block"/>-cell blocks. Rounding only ever adds cells, so a
    /// cell outside the reach is certainly outside every input; a piece whose corridor is the whole map (a diving cord:
    /// its route depends on walls anywhere) makes everything reachable.
    /// </summary>
    internal sealed class CordReach
    {
        public const int Block = 8, Margin = 3;
        public readonly int Width, Height;
        private readonly int bw, bh;
        private readonly bool[] hot;
        /// <summary>Every cell reaches (a whole-map corridor).</summary>
        public bool All { get; private set; }
        public int HotBlocks { get; private set; }

        internal CordReach(int width, int height)
        {
            Width = width;
            Height = height;
            bw = Math.Max(1, (width + Block - 1) / Block);
            bh = Math.Max(1, (height + Block - 1) / Block);
            hot = new bool[bw * bh];
        }

        /// <summary>True when a change at c may alter the next Build. Off-map or unknown is conservative: true.</summary>
        public bool Reaches(Cell c)
        {
            if (All) return true;
            if (c.X < 0 || c.Z < 0 || c.X >= Width || c.Z >= Height) return true;
            return hot[(c.Z / Block) * bw + c.X / Block];
        }

        /// <summary>Marks the cell rect [x0..x1] x [z0..z1] grown by the margin.</summary>
        public void Add(int x0, int z0, int x1, int z1)
        {
            if (All) return;
            int bx0 = Math.Max(0, (Math.Min(x0, x1) - Margin)) / Block, bz0 = Math.Max(0, (Math.Min(z0, z1) - Margin)) / Block;
            int bx1 = Math.Min(bw - 1, Math.Max(0, Math.Max(x0, x1) + Margin) / Block), bz1 = Math.Min(bh - 1, Math.Max(0, Math.Max(z0, z1) + Margin) / Block);
            for (int bz = bz0; bz <= bz1; bz++)
                for (int bx = bx0; bx <= bx1; bx++)
                {
                    int i = bz * bw + bx;
                    if (!hot[i]) { hot[i] = true; HotBlocks++; }
                }
        }

        public void AddAll() => All = true;

        internal static CordReach Of(CordWorld w, CordGraph g, List<LaidPiece> pieces)
        {
            var r = new CordReach(w.Width, w.Height);
            foreach (Cell c in g.Cells) r.Add(c.X, c.Z, c.X, c.Z);
            foreach (MachineInfo m in w.Machines)
            {
                r.Add(m.X0, m.Z0, m.X0 + m.W - 1, m.Z0 + m.H - 1);
                if (m.HasHome) r.Add(m.HomeX, m.HomeZ, m.HomeX, m.HomeZ);
                foreach (Cell h in m.Hookups) r.Add(h.X, h.Z, h.X, h.Z);
            }
            foreach (LaidPiece p in pieces)
            {
                if (p.CX0 == 0 && p.CZ0 == 0 && p.CX1 == w.Width - 1 && p.CZ1 == w.Height - 1) { r.AddAll(); return r; }
                int[] b = BoxOf(p);
                r.Add(b[0], b[1], b[2], b[3]);
            }
            return r;
        }

        /// <summary>The cell box of a piece (cached on the piece: a reused piece is the same object with the same geometry).</summary>
        internal static int[] BoxOf(LaidPiece p)
        {
            if (p.ReachBox != null) return p.ReachBox;
            int x0 = p.Owner.X, z0 = p.Owner.Z, x1 = x0, z1 = z0;
            void Grow(double x, double z)
            {
                if (double.IsNaN(x) || double.IsNaN(z) || double.IsInfinity(x) || double.IsInfinity(z)) return;
                int fx = (int)Math.Floor(x), fz = (int)Math.Floor(z);
                if (fx < x0) x0 = fx; if (fx > x1) x1 = fx;
                if (fz < z0) z0 = fz; if (fz > z1) z1 = fz;
            }
            if (p.CX1 > p.CX0 || p.CZ1 > p.CZ0 || p.CX0 != 0 || p.CZ0 != 0) { Grow(p.CX0, p.CZ0); Grow(p.CX1, p.CZ1); }
            foreach (CordStrand s in p.Strands)
                if (s.Pts != null) foreach (V2 q in s.Pts) Grow(q.X, q.Z);
            foreach (CordDecal d in p.Decals) Grow(d.Pos.X, d.Pos.Z);
            foreach (CordEnd e in p.Ends) { Grow(e.Tip.X, e.Tip.Z); Grow(e.NetCell.X, e.NetCell.Z); }
            foreach (Cell c in p.LiveKeys) Grow(c.X, c.Z);
            return p.ReachBox = new[] { x0, z0, x1, z1 };
        }
    }
}
