// Verse-free (the FlowWorks SelfTest compiles this file): PIPE_POLES_BUILD_SAG_WITH_SUBSTANCE phase 5, the liquid net's one
// long-range edge kind (design/RimMandrake/flowworks_pipes_across_pits_design_2026-10-20.md §P3: "The liquid net gains one
// long-range edge kind (pole to pole). Component caps are applied after the edge joins its components; one logical edge per
// connection, never a duplicate cardinal + aerial path; one-port-per-pump-side still holds; topology is rebuilt on any edge
// change.").
//
//   how a pole joins   a pole is a FITTING, the way every net member is (owner 2026-10-20, a75cd10f5b / 7f876380b2: "A solid
//                      pipe must only be adjacent and is then drawn undernead to the center of the object"): every pipe cell under
//                      it or 8-way around it joins it. Its JOIN CELL (the one the span lands on) is the first of those in a fixed
//                      order -- under, then cardinal, then diagonal -- and the pole's other pipes join that cell (fitting edges).
//                      Reason: a pole stands on solid ground and a pipe beside it is the natural build (the pipe need not share
//                      its square), and the one join cell gives every span exactly one logical edge (join cell to join cell).
//   the edge           extra pipe-neighbour pairs the adapter adds to the cardinal ones (RM_LiquidNet.MapGraph.PipeNeighbours);
//                      the kernel (RM_NetComponents) walks them like any pipe step, so the cap counts the JOINED component.
//                      A pair that is already cardinal neighbours, a pair seen before (two spans, either order) or a span
//                      between two poles sharing one join cell adds nothing.
//   pump ports         a span is pipe to pipe; it never makes a port, so one port per pump side (RM_PumpPortMath) is untouched.
//   rebuild            GSS calls back on every span change; the net bumps its revision only when the strung pipe-span SET
//                      changed (Signature), so one cut is one rebuild however many times the callback fires.
using System;
using System.Collections.Generic;

namespace RimMandrake.FlowWorks.Machinery
{
    public sealed class RM_PipeSpanEdges
    {
        private static readonly List<object> None = new List<object>();
        private readonly Dictionary<object, List<object>> adj = new Dictionary<object, List<object>>();
        private readonly List<KeyValuePair<object, object>> pairs = new List<KeyValuePair<object, object>>();

        /// <summary>State reads: logical span edges (join cell to join cell) and fitting edges (a pole's other pipes to its
        /// join cell) this table holds.</summary>
        public int AerialEdges { get; private set; }
        public int FittingEdges { get; private set; }

        public static readonly RM_PipeSpanEdges Empty = new RM_PipeSpanEdges();

        /// <summary>The extra neighbours of a pipe cell (never its cardinal ones).</summary>
        public IList<object> At(object cell) => cell != null && adj.TryGetValue(cell, out List<object> l) ? l : None;

        public bool Joins(object a, object b) => At(a).Contains(b);

        private bool Seen(object a, object b)
        {
            for (int i = 0; i < pairs.Count; i++)
            {
                KeyValuePair<object, object> p = pairs[i];
                if ((Equals(p.Key, a) && Equals(p.Value, b)) || (Equals(p.Key, b) && Equals(p.Value, a))) return true;
            }
            return false;
        }

        private bool Add(object a, object b, Func<object, object, bool> cardinal)
        {
            if (a == null || b == null || Equals(a, b) || (cardinal != null && cardinal(a, b)) || Seen(a, b)) return false;
            pairs.Add(new KeyValuePair<object, object>(a, b));
            if (!adj.TryGetValue(a, out List<object> la)) adj[a] = la = new List<object>();
            if (!adj.TryGetValue(b, out List<object> lb)) adj[b] = lb = new List<object>();
            la.Add(b);
            lb.Add(a);
            return true;
        }

        /// <summary>The edges for these strung spans (pole, pole). joinCells(pole) lists the pole's pipe cells in join order
        /// (under, cardinal, diagonal; empty = the pole is joined to no pipe and its spans carry nothing); cardinal(a, b) is true
        /// when two pipe cells already conduct as cardinal neighbours.</summary>
        public static RM_PipeSpanEdges Build(IEnumerable<KeyValuePair<object, object>> spans, Func<object, IList<object>> joinCells,
                                             Func<object, object, bool> cardinal)
        {
            var e = new RM_PipeSpanEdges();
            if (spans == null || joinCells == null) return e;
            var fitted = new HashSet<object>();
            var cells = new Dictionary<object, IList<object>>();
            IList<object> Cells(object pole)
            {
                if (!cells.TryGetValue(pole, out IList<object> l)) cells[pole] = l = joinCells(pole) ?? None;
                return l;
            }
            foreach (KeyValuePair<object, object> s in spans)
            {
                if (s.Key == null || s.Value == null || Equals(s.Key, s.Value)) continue;
                IList<object> ja = Cells(s.Key), jb = Cells(s.Value);
                if (ja.Count == 0 || jb.Count == 0) continue;
                foreach (object pole in new[] { s.Key, s.Value })
                {
                    if (!fitted.Add(pole)) continue;
                    IList<object> j = Cells(pole);
                    for (int i = 1; i < j.Count; i++)
                        if (e.Add(j[0], j[i], cardinal)) e.FittingEdges++;
                }
                if (e.Add(ja[0], jb[0], cardinal)) e.AerialEdges++;
            }
            return e;
        }
    }

    public static class RM_PipeSpanNetMath
    {
        /// <summary>The strung pipe-span set as an order-free signature over the two poles' ids (either end first, any listing
        /// order): equal sets, equal signatures.</summary>
        public static ulong Signature(IEnumerable<KeyValuePair<long, long>> spans)
        {
            var keys = new List<KeyValuePair<long, long>>();
            if (spans != null)
                foreach (KeyValuePair<long, long> s in spans)
                    keys.Add(s.Key <= s.Value ? s : new KeyValuePair<long, long>(s.Value, s.Key));
            keys.Sort((x, y) => x.Key != y.Key ? x.Key.CompareTo(y.Key) : x.Value.CompareTo(y.Value));
            ulong h = 14695981039346656037UL;
            h = (h ^ (ulong)keys.Count) * 1099511628211UL;
            foreach (KeyValuePair<long, long> k in keys)
                h = RM_LiquidNetKernel.SigStep(h, k.Key, k.Value, 0x9E37L);
            return h;
        }

        /// <summary>Did the span set change since the last call? Records the new signature. The first call on a map always counts
        /// as a change: the net may already hold edges built from spans this listener never saw (a loaded game whose first
        /// callback is the cut of its only span), and a rebuild is only a revision bump.</summary>
        public static bool Changed(ref ulong last, ref bool known, ulong now)
        {
            if (!known)
            {
                known = true;
                last = now;
                return true;
            }
            if (now == last) return false;
            last = now;
            return true;
        }
    }
}
