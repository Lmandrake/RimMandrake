// PIPE_POLES_BUILD_SAG_WITH_SUBSTANCE phase 5 (design/RimMandrake/flowworks_pipes_across_pits_design_2026-10-20.md §P3): the
// liquid net's one long-range edge, asserted on the PRODUCTION edge builder (../Machinery/RM_PipeSpanNetMath.cs) and the
// PRODUCTION kernel (../Machinery/RM_LiquidNetKernel.cs) over HoseNetChecks' fake graph, wrapped the way RM_LiquidNet.MapGraph
// wraps the map (cardinal neighbours + RM_PipeSpanEdges.At), plus the production wiring read from source. L1 of the item: an aerial
// edge joins two 60%-cap components and the joined net is refused (two 40% ones accepted); a ring of two pole routes cut in turn
// splits only at the second cut; a cut span rebuilds the net once. Each case has a can-fail. NOT proven here: a pipe across a pit
// on poles carrying liquid in a running game (L2 live row, owed).
using System;
using System.Collections.Generic;
using System.Linq;
using RimMandrake.FlowWorks.Machinery;

namespace RimMandrake.FlowWorks.SelfTest
{
    internal static class PipeSpanNetChecks
    {
        private static void Assert(bool ok, string msg)
        {
            if (!ok) throw new Exception(msg);
        }

        /// <summary>The production adapter's shape: cardinal pipe neighbours, then the span table's extra ones.</summary>
        private sealed class SpanGraph : IRM_NetGraph
        {
            private readonly HoseNetChecks.G g;
            private readonly RM_PipeSpanEdges e;
            public SpanGraph(HoseNetChecks.G g, RM_PipeSpanEdges e) { this.g = g; this.e = e; }
            public RM_NetRole RoleOf(object v) => g.RoleOf(v);
            public IEnumerable<object> OriginTanks(object m) => g.OriginTanks(m);
            public IEnumerable<object> OriginPipeCells(object m) => g.OriginPipeCells(m);
            public IEnumerable<object> PipeTanks(object c) => g.PipeTanks(c);
            public IEnumerable<object> PipeMachines(object c) => g.PipeMachines(c);
            public IEnumerable<object> PipeNeighbours(object c) => g.PipeNeighbours(c).Concat(e.At(c));
            public IList<RM_NetLink> LinksAt(object v) => g.LinksAt(v);
            public bool PipesEnabled => g.PipesEnabled;
            public int Order(object m) => g.Order(m);
        }

        /// <summary>Two straight runs, a (ca0..) and b (cb0..), of n pipe cells each.</summary>
        private static HoseNetChecks.G TwoRuns(int n)
        {
            var g = new HoseNetChecks.G();
            g.Run(Enumerable.Range(0, n).Select(i => "ca" + i).ToArray());
            g.Run(Enumerable.Range(0, n).Select(i => "cb" + i).ToArray());
            return g;
        }

        private static RM_PipeSpanEdges Edges(HoseNetChecks.G g, Dictionary<string, string[]> joins, params string[] spans)
        {
            var pairs = new List<KeyValuePair<object, object>>();
            for (int i = 0; i + 1 < spans.Length; i += 2) pairs.Add(new KeyValuePair<object, object>(spans[i], spans[i + 1]));
            return RM_PipeSpanEdges.Build(pairs, p => joins.TryGetValue(p as string, out string[] j) ? j.Cast<object>().ToList() : new List<object>(),
                (a, b) => g.PipeNeighbours(a).Contains(b));
        }

        private static RM_NetComponents Net(HoseNetChecks.G g, RM_PipeSpanEdges e, int cap) => new RM_NetComponents(new SpanGraph(g, e), cap);

        public static void Run(Action<string, Action> Case)
        {
            var poles = new Dictionary<string, string[]> { { "X1", new[] { "ca59" } }, { "X2", new[] { "cb0" } } };

            Case("PipeSpan_P3_edge_joins_two_60pct_components_cap_after_join_refused", () =>
            {
                const int cap = 100;
                HoseNetChecks.G g = TwoRuns(60);
                RM_NetComponents apart = Net(g, RM_PipeSpanEdges.Empty, cap);
                RM_NetComponent a = apart.ComponentOfNode("ca0"), b = apart.ComponentOfNode("cb0");
                Assert(a != b && !a.Refused && !b.Refused && a.Size == 60 && b.Size == 60, "unjoined, each 60% run operates on its own");
                RM_PipeSpanEdges e = Edges(g, poles, "X1", "X2");
                Assert(e.AerialEdges == 1, "one span, one logical edge (" + e.AerialEdges + ")");
                RM_NetComponents joined = Net(g, e, cap);
                RM_NetComponent ja = joined.ComponentOfNode("ca0"), jb = joined.ComponentOfNode("cb0");
                Assert(ja.Refused && jb.Refused, "the joined net (120% of the cap) is refused whole, both sides (the cap counts AFTER the join)");
                // can fail: without the edge in the walk the cap never sees the join
                Assert(!Net(g, RM_PipeSpanEdges.Empty, cap).ComponentOfNode("ca0").Refused, "CANNOT FAIL: refusal must come from the span edge");
            });

            Case("PipeSpan_P3_edge_joins_two_40pct_components_accepted_as_one", () =>
            {
                const int cap = 100;
                HoseNetChecks.G g = TwoRuns(40);
                var j = new Dictionary<string, string[]> { { "X1", new[] { "ca39" } }, { "X2", new[] { "cb0" } } };
                RM_NetComponents net = Net(g, Edges(g, j, "X1", "X2"), cap);
                RM_NetComponent a = net.ComponentOfNode("ca0");
                Assert(a == net.ComponentOfNode("cb39") && !a.Refused && a.Size == 80, "two 40% runs joined by a span are ONE accepted net of 80 (" + a.Size + ")");
                // members on either side reach each other's tanks over the span
                HoseNetChecks.G.Add(g.PipeOf, "P1", "ca0");
                HoseNetChecks.G.Add(g.PT, "cb39", "T7");
                Assert(Net(g, Edges(g, j, "X1", "X2"), cap).StoreOf("P1").Tanks.Contains("T7"), "a pump on run a stores into run b's tank across the span");
                Assert(!Net(g, RM_PipeSpanEdges.Empty, cap).StoreOf("P1").Tanks.Contains("T7"), "CANNOT FAIL: no span, no reach");
            });

            Case("PipeSpan_P3_one_logical_edge_no_duplicate_cardinal_or_reverse_span", () =>
            {
                HoseNetChecks.G g = TwoRuns(5);
                var j = new Dictionary<string, string[]> { { "X1", new[] { "ca4" } }, { "X2", new[] { "cb0" } }, { "Y1", new[] { "ca3" } } };
                RM_PipeSpanEdges dup = Edges(g, j, "X1", "X2", "X2", "X1");
                Assert(dup.AerialEdges == 1 && dup.At("ca4").Count == 1, "a span listed from both ends is one edge");
                RM_PipeSpanEdges card = Edges(g, j, "X1", "Y1");
                Assert(card.AerialEdges == 0 && card.At("ca4").Count == 0, "two poles whose join cells are already cardinal neighbours add no aerial path");
                var none = new Dictionary<string, string[]> { { "X1", new[] { "ca4" } }, { "X2", new string[0] } };
                Assert(Edges(g, none, "X1", "X2").AerialEdges == 0, "a pole joined to no pipe carries nothing");
                // a pole is a fitting: its under / cardinal / diagonal pipes all join its join cell (the first)
                HoseNetChecks.G f = new HoseNetChecks.G();
                f.Run("cu0", "cu1");
                f.Run("cd0", "cd1");
                var fj = new Dictionary<string, string[]> { { "X1", new[] { "cu1", "cd0" } }, { "X2", new[] { "cb0" } } };
                f.Run("cb0", "cb1");
                RM_PipeSpanEdges fe = Edges(f, fj, "X1", "X2");
                Assert(fe.FittingEdges == 1 && fe.AerialEdges == 1, "fitting 1 + span 1 (" + fe.FittingEdges + "," + fe.AerialEdges + ")");
                RM_NetComponents net = Net(f, fe, RM_NetComponents.MaxConductors);
                Assert(net.ComponentOfNode("cd1") == net.ComponentOfNode("cb1") && net.ComponentOfNode("cu0") == net.ComponentOfNode("cb1"),
                    "both runs at the pole and the far run are one net");
            });

            Case("PipeSpan_P3_ring_of_two_pole_routes_cut_in_turn", () =>
            {
                HoseNetChecks.G g = TwoRuns(20);
                var j = new Dictionary<string, string[]>
                {
                    { "X1", new[] { "ca19" } }, { "X2", new[] { "cb0" } }, { "Y1", new[] { "ca5" } }, { "Y2", new[] { "cb15" } },
                };
                bool One(params string[] spans)
                {
                    RM_NetComponents n = Net(g, Edges(g, j, spans), RM_NetComponents.MaxConductors);
                    return n.ComponentOfNode("ca0") == n.ComponentOfNode("cb0");
                }
                Assert(One("X1", "X2", "Y1", "Y2"), "the ring: both routes up, one net");
                Assert(One("Y1", "Y2"), "route X cut: route Y still joins the net");
                Assert(One("X1", "X2"), "route Y cut instead: route X still joins it");
                Assert(!One(), "both cut: the net splits in two");
            });

            Case("PipeSpan_P3_cut_span_splits_the_net_once", () =>
            {
                HoseNetChecks.G g = TwoRuns(10);
                var j = new Dictionary<string, string[]> { { "X1", new[] { "ca9" } }, { "X2", new[] { "cb0" } }, { "Y1", new[] { "ca2" } }, { "Y2", new[] { "cb7" } } };
                ulong last = 0;
                bool known = false;
                int bumps = 0;
                void Fire(params long[] ids)
                {
                    var sp = new List<KeyValuePair<long, long>>();
                    for (int i = 0; i + 1 < ids.Length; i += 2) sp.Add(new KeyValuePair<long, long>(ids[i], ids[i + 1]));
                    if (RM_PipeSpanNetMath.Changed(ref last, ref known, RM_PipeSpanNetMath.Signature(sp))) bumps++;
                }
                Fire(11, 12);                          // X strung: the first span set on the map is a rebuild
                Assert(bumps == 1, "the first strung span rebuilds (" + bumps + ")");
                Fire(12, 11);                          // GSS fires again for the same set, ends listed the other way
                Fire(11, 12);
                Assert(bumps == 1, "a callback that changed no pipe span rebuilds nothing (" + bumps + ")");
                RM_NetComponents before = Net(g, Edges(g, j, "X1", "X2"), RM_NetComponents.MaxConductors);
                Assert(before.ComponentOfNode("ca0") == before.ComponentOfNode("cb9"), "strung: one net");
                Fire();                                // X cut
                Fire();                                // GSS's second callback for the same cut (fallen halves)
                Assert(bumps == 2, "one cut is one rebuild (" + bumps + ")");
                RM_NetComponents after = Net(g, Edges(g, j), RM_NetComponents.MaxConductors);
                Assert(after.ComponentOfNode("ca0") != after.ComponentOfNode("cb9") && after.Built.Count == 2, "cut: exactly two nets");
                Fire(13, 14, 11, 12);
                Fire(11, 12, 14, 13);
                Assert(bumps == 3, "two spans re-strung in one change: one rebuild, any order (" + bumps + ")");
                // can fail: a signature that ignored the set would never bump
                Assert(RM_PipeSpanNetMath.Signature(new[] { new KeyValuePair<long, long>(1, 2) }) != RM_PipeSpanNetMath.Signature(new KeyValuePair<long, long>[0]),
                    "CANNOT FAIL: a cut must change the signature");
                // a loaded game: the net was built with a span this listener never saw, and the first callback is its cut
                ulong l2 = 0; bool k2 = false;
                Assert(RM_PipeSpanNetMath.Changed(ref l2, ref k2, RM_PipeSpanNetMath.Signature(null)), "the first callback on a map always rebuilds, even to no spans");
                Assert(!RM_PipeSpanNetMath.Changed(ref l2, ref k2, RM_PipeSpanNetMath.Signature(null)), "and the same empty set again rebuilds nothing");
            });

            Case("PipeSpan_P3_production_wiring_adapter_callback_join_order", () =>
            {
                string net = RiverSwitchFlipChecks.Src(System.IO.Path.Combine("Machinery", "RM_LiquidNet.cs"));
                RiverSwitchFlipChecks.Has(net, @"IList<object> extra = SpanEdges\.At\(c\);", "MapGraph.PipeNeighbours walks the span edges");
                RiverSwitchFlipChecks.Has(net, @"PipesEnabled \? RM_PipePoles\.EdgesFor\(map\) : RM_PipeSpanEdges\.Empty", "edges are built per revision, none with pipes off");
                RiverSwitchFlipChecks.Has(net, @"s\.polesOn != RM_MachinerySettings\.pipePolesEnabled\)[\s\S]{0,200}s\.revision\+\+", "the pipe-pole switch is a new revision");
                string poles = RiverSwitchFlipChecks.Src(System.IO.Path.Combine("Machinery", "RM_PipePoles.cs"));
                RiverSwitchFlipChecks.Has(poles, @"RM_PipeSpanNetMath\.Changed\([\s\S]{0,120}\)\)\s*\{\s*NetBumps\+\+;\s*RM_LiquidNet\.Bump\(map\);", "the span callback bumps the net only on a changed set");
                RiverSwitchFlipChecks.Has(poles, @"new Action<Map>\(OnSpansChanged\)", "the callback is registered with GSS");
                int under = poles.IndexOf("pole.OccupiedRect())", StringComparison.Ordinal);
                int dirs = poles.IndexOf("new[] { GenAdj.CardinalDirections, GenAdj.DiagonalDirections }", StringComparison.Ordinal);
                Assert(under > 0 && dirs > under, "JoinCells orders under, then cardinal, then diagonal");
                Assert(!poles.Contains("SpansChangedCount++;\n\t\t}") , "the callback is no longer only a counter");
            });
        }
    }
}
