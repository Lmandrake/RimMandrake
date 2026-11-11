// HOSE_DRAW_FIX_CROSS_SHADOW_QUADRATIC / HOSE_DRAW_FIX_STALLS_WHILE_WORKER_LAYS (live round 6, 2026-10-26, 325 basin map,
// 200 hoses). The crossing shadow (RM_MapComponent_Hoses.DrawCrossShadow) was re-checked by EVERY hose whenever ANY strand
// was built or dropped (one global poseVersion), each check walking every other hose; and a re-check whose lower set had
// changed rebuilt its spans with HoseOverDraw.CrossSpans, which tests every 0.05-cell sample of the upper strand against
// every segment of every nearby lower strand (samples x lowers x segments: up to 138 ms for ONE hose in T3). A landed lay
// therefore cost every hose above it a full rebuild in the same frame -- the multi-second DrawAll frames while the worker lays.
//
// This index (Verse-free, so SelfTest runs it): a strand built or dropped, or whose rank moved, marks only the strands whose
// boxes meet its box dirty; only a dirty strand (or one whose own rank moved) re-collects its lowers; a lower set that hashes
// the same keeps its spans; and the spans are computed against a per-strand segment grid (cell 1, built once per strand,
// shared by every upper), giving exactly HoseOverDraw.CrossSpans' spans (same sample walk, same per-segment distance).
using System;
using System.Collections.Generic;
using RimMandrake.Shared.Slack;

namespace RimMandrake.FlowWorks.Hose
{
    internal sealed class HoseCrossShadows
    {
        /// <summary>How far past a strand's points another strand can be and still cross it (cells): the box broad phase's
        /// widening, and the segment grid's padding. A reach above it is answered by the plain CrossSpans.</summary>
        public const double Reach = 1.0;

        /// <summary>A segment whose padded box covers more grid cells than this is tested for every sample instead.</summary>
        private const int MaxCellsPerSegment = 4096;

        public sealed class Strand
        {
            public int Id, Serial;
            public IList<V2> Rp;
            /// <summary>Rp's box widened by <see cref="Reach"/>.</summary>
            public double X0, Z0, X1, Z1;
            public bool Dirty = true;
            public int Rank = -1;
            public bool Keyed;
            public ulong Key;
            public List<double[]> Spans;
            internal Grid grid;
        }

        /// <summary>A strand's segments bucketed by unit cell (each segment in every cell its box padded by Reach meets).</summary>
        internal sealed class Grid
        {
            public readonly IList<V2> Pts;
            public readonly Dictionary<long, List<int>> Cells = new Dictionary<long, List<int>>();
            /// <summary>Segments not bucketed (non-finite or huge): tested for every sample.</summary>
            public readonly List<int> Always = new List<int>();
            public double bx0, bz0, bx1, bz1;   // HoseOverDraw.Bounds of Pts (the oracle's near filter)

            public Grid(IList<V2> pts)
            {
                Pts = pts;
                HoseOverDraw.Bounds(pts, out bx0, out bz0, out bx1, out bz1);
                const double pad = Reach + 1e-6;
                for (int i = 1; i < pts.Count; i++)
                {
                    V2 a = pts[i - 1], b = pts[i];
                    double x0 = Math.Min(a.X, b.X) - pad, x1 = Math.Max(a.X, b.X) + pad, z0 = Math.Min(a.Z, b.Z) - pad, z1 = Math.Max(a.Z, b.Z) + pad;
                    if (!Finite(x0) || !Finite(x1) || !Finite(z0) || !Finite(z1)) { Always.Add(i); continue; }
                    double cx0 = Math.Floor(x0), cx1 = Math.Floor(x1), cz0 = Math.Floor(z0), cz1 = Math.Floor(z1);
                    if ((cx1 - cx0 + 1) * (cz1 - cz0 + 1) > MaxCellsPerSegment || Math.Abs(cx0) > 1e9 || Math.Abs(cz0) > 1e9 || Math.Abs(cx1) > 1e9 || Math.Abs(cz1) > 1e9) { Always.Add(i); continue; }
                    for (long cx = (long)cx0; cx <= (long)cx1; cx++)
                        for (long cz = (long)cz0; cz <= (long)cz1; cz++)
                        {
                            long k = CellKey(cx, cz);
                            if (!Cells.TryGetValue(k, out List<int> l)) Cells[k] = l = new List<int>(4);
                            l.Add(i);
                        }
                }
            }

            /// <summary>True when some segment lies within <paramref name="reach"/> (&lt;= Reach) of <paramref name="p"/>.</summary>
            public bool Near(V2 p, double reach)
            {
                for (int k = 0; k < Always.Count; k++) { int i = Always[k]; if (HoseOverDraw.SegDist(p, Pts[i - 1], Pts[i]) <= reach) return true; }
                if (!Finite(p.X) || !Finite(p.Z)) return false;   // the oracle: every distance NaN, nothing within reach
                double fx = Math.Floor(p.X), fz = Math.Floor(p.Z);
                if (Math.Abs(fx) > 1e9 || Math.Abs(fz) > 1e9) return false;   // no bucketed segment reaches it (they were capped)
                if (!Cells.TryGetValue(CellKey((long)fx, (long)fz), out List<int> l)) return false;
                for (int k = 0; k < l.Count; k++) { int i = l[k]; if (HoseOverDraw.SegDist(p, Pts[i - 1], Pts[i]) <= reach) return true; }
                return false;
            }
        }

        private static bool Finite(double v) => !double.IsNaN(v) && !double.IsInfinity(v);
        private static long CellKey(long x, long z) => (x << 32) ^ (z & 0xffffffffL);

        private readonly Dictionary<int, Strand> strands = new Dictionary<int, Strand>();
        private int serial;

        /// <summary>Counters (census / SelfTest): lower-set re-collections, span rebuilds, strands marked dirty.</summary>
        public long Rescans, SpanBuilds, Marked;
        public int Count => strands.Count;
        public bool TryGet(int id, out Strand s) => strands.TryGetValue(id, out s);

        /// <summary>A strand built (or rebuilt) for <paramref name="id"/>: a fresh serial; strands near its old or new box re-check.</summary>
        public Strand Set(int id, IList<V2> rp)
        {
            if (strands.TryGetValue(id, out Strand old)) MarkNear(old, id);
            var s = new Strand { Id = id, Serial = ++serial, Rp = rp };
            BoxOf(s);
            strands[id] = s;
            MarkNear(s, id);
            return s;
        }

        /// <summary>The strand dropped (wound, carried, deregistered): strands near it re-check.</summary>
        public void Drop(int id)
        {
            if (!strands.TryGetValue(id, out Strand old)) return;
            strands.Remove(id);
            MarkNear(old, id);
        }

        /// <summary>The draw order moved this strand: strands near it re-check (their lower sets may gain or lose it).</summary>
        public void RankMoved(int id)
        {
            if (strands.TryGetValue(id, out Strand s)) { s.Dirty = true; MarkNear(s, id); }
        }

        public void Clear() { strands.Clear(); }

        private void MarkNear(Strand b, int self)
        {
            if (b.Rp == null || b.Rp.Count == 0) return;
            foreach (Strand o in strands.Values)
            {
                if (o.Id == self || o.Dirty) continue;
                if (Meets(o, b)) { o.Dirty = true; Marked++; }
            }
        }

        private static bool Meets(Strand a, Strand b) => !(a.X0 > b.X1 || a.X1 < b.X0 || a.Z0 > b.Z1 || a.Z1 < b.Z0);

        private static void BoxOf(Strand s)
        {
            double x0 = double.MaxValue, z0 = double.MaxValue, x1 = double.MinValue, z1 = double.MinValue;
            if (s.Rp != null) foreach (V2 p in s.Rp) { x0 = Math.Min(x0, p.X); z0 = Math.Min(z0, p.Z); x1 = Math.Max(x1, p.X); z1 = Math.Max(z1, p.Z); }
            s.X0 = x0 - Reach; s.Z0 = z0 - Reach; s.X1 = x1 + Reach; s.Z1 = z1 + Reach;
        }

        private readonly List<Strand> lowersScratch = new List<Strand>();

        /// <summary>
        /// The crossing spans of <paramref name="id"/>'s strand at <paramref name="rank"/>: re-collected only when it is dirty or
        /// its rank moved, rebuilt only when the lower set (by build serial) changed. True = <paramref name="spans"/> is new (the
        /// caller rebuilds its mesh); false = keep what was built (spans is the kept list). Lowers are strands whose boxes meet
        /// this one's and whose rank (<paramref name="rankOf"/>) is lower -- the set the all-pairs scan found.
        /// </summary>
        /// <summary>Would Check rescan this strand now (dirty, rank moved or never keyed)? Asks without consuming the dirt
        /// (HOSE_RELAY_FIX_WAVE_FRAME_OVER_BUDGET: a frame past its budget leaves a pending strand for the next).</summary>
        public bool Pending(int id, int rank)
        {
            if (!strands.TryGetValue(id, out Strand s) || s.Rp == null || s.Rp.Count < 2) return false;
            return s.Dirty || s.Rank != rank || !s.Keyed;
        }

        public bool Check(int id, int rank, Func<int, int> rankOf, double reach, double margin, out List<double[]> spans)
        {
            spans = null;
            if (!strands.TryGetValue(id, out Strand s)) return false;
            spans = s.Spans;
            if (s.Rp == null || s.Rp.Count < 2) return false;
            if (!s.Dirty && s.Rank == rank && s.Keyed) return false;
            s.Dirty = false;
            s.Rank = rank;
            Rescans++;
            // the key: this strand's serial and an order-free sum over its lowers' serials (the scan order is the dictionary's)
            ulong sum = 0;
            lowersScratch.Clear();
            foreach (Strand o in strands.Values)
            {
                if (o.Id == id || o.Rp == null || o.Rp.Count < 2 || !Meets(o, s)) continue;
                if (rankOf(o.Id) >= rank) continue;
                sum += Mix((ulong)(uint)o.Serial);
                lowersScratch.Add(o);
            }
            ulong key = Mix((ulong)(uint)s.Serial ^ 0xC2B2AE3D27D4EB4FUL) ^ (sum * 0x9E3779B97F4A7C15UL) ^ (ulong)lowersScratch.Count;
            if (s.Keyed && s.Key == key) return false;
            s.Keyed = true;
            s.Key = key;
            s.Spans = spans = Spans(s.Rp, lowersScratch, reach, margin);
            SpanBuilds++;
            return true;
        }

        /// <summary>HoseOverDraw.CrossSpans over these lowers, through their segment grids (built once per strand).</summary>
        internal static List<double[]> Spans(IList<V2> upper, List<Strand> lowers, double reach, double margin)
        {
            if (upper == null || upper.Count < 2 || lowers.Count == 0) return new List<double[]>();
            if (!(reach <= Reach))
            {
                var plain = new List<IList<V2>>(lowers.Count);
                foreach (Strand o in lowers) plain.Add(o.Rp);
                return HoseOverDraw.CrossSpans(upper, plain, reach, margin);
            }
            HoseOverDraw.Bounds(upper, out double ux0, out double uz0, out double ux1, out double uz1);
            var near = new List<Grid>();
            foreach (Strand o in lowers)
            {
                Grid g = o.grid ?? (o.grid = new Grid(o.Rp));
                // the oracle's near filter, the same expression
                if (g.bx0 - reach > ux1 || g.bx1 + reach < ux0 || g.bz0 - reach > uz1 || g.bz1 + reach < uz0) continue;
                near.Add(g);
            }
            if (near.Count == 0) return new List<double[]>();
            return HoseOverDraw.SpansWhere(upper, p =>
            {
                for (int i = 0; i < near.Count; i++) if (near[i].Near(p, reach)) return true;
                return false;
            }, margin);
        }

        /// <summary>The same spans for plain point lists (SelfTest: the indexed path against the oracle on any input).</summary>
        internal static List<double[]> SpansOf(IList<V2> upper, IList<IList<V2>> lowers, double reach, double margin)
        {
            var ls = new List<Strand>();
            foreach (IList<V2> q in lowers) if (q != null && q.Count >= 2) ls.Add(new Strand { Rp = q });
            return Spans(upper, ls, reach, margin);
        }

        private static ulong Mix(ulong z)
        {
            z += 0x9E3779B97F4A7C15UL;
            z = (z ^ (z >> 30)) * 0xBF58476D1CE4E5B9UL;
            z = (z ^ (z >> 27)) * 0x94D049BB133111EBUL;
            return z ^ (z >> 31);
        }
    }
}
