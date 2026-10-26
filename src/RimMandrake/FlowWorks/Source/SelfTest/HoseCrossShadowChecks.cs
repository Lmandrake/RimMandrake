// HOSE_DRAW_FIX_CROSS_SHADOW_QUADRATIC / HOSE_DRAW_FIX_STALLS_WHILE_WORKER_LAYS (live round 6, 2026-10-26: 325 basin map,
// 200 hoses; DrawAll up to 3,094 ms a frame while the lay workers relaid, DrawCrossShadow up to 138 ms for one hose). Every
// landed lay bumped one global poseVersion, so every hose re-scanned every other hose, and every hose above the relaid one
// rebuilt its crossing spans with HoseOverDraw.CrossSpans (every 0.05-cell sample against every lower segment).
//  HX1 on the round's own 200 lays (drawn steady, ranked by HoseMath.Layer): HoseCrossShadows' grid spans equal CrossSpans'
//      for every hose against its lowers, exactly; old and new timings printed.
//  HX2 fuzz: random strands (crossings, NaN points, 0/1-point strands, huge segments, reach above the grid's) equal CrossSpans.
//  HX3 a relay wave on the basin lays: each frame relays k strands and moves some ranks; the index's spans equal a fresh
//      all-pairs oracle for every hose after every frame; it re-collects far fewer strands than all-pairs and its relay frame
//      costs a fraction of the old policy's (all re-scan, every changed upper rebuilt by CrossSpans).
//  HX4 source: the component feeds the index off FrameLegacy (Set at the mesh build, Drop, Clear, RanksMoved, Check).
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using RimMandrake.FlowWorks.Hose;
using RimMandrake.Shared.Slack;

namespace RimMandrake.FlowWorks.SelfTest
{
    internal static class HoseCrossShadowChecks
    {
        private static void Assert(bool ok, string msg)
        {
            if (!ok) throw new Exception(msg);
        }

        private const double Margin = 0.25;   // RM_MapComponent_Hoses.CrossShadowMargin

        /// <summary>Empty = the same spans, bit for bit.</summary>
        internal static string SpanDiff(List<double[]> a, List<double[]> b)
        {
            if (a == null || b == null) return a == b ? "" : "null vs list";
            if (a.Count != b.Count) return $"count {a.Count} vs {b.Count}";
            for (int i = 0; i < a.Count; i++)
            {
                if (a[i].Length != b[i].Length) return $"span {i} length";
                for (int j = 0; j < a[i].Length; j++)
                    if (!a[i][j].Equals(b[i][j])) return $"span {i}[{j}] {a[i][j]:R} vs {b[i][j]:R}";
            }
            return "";
        }

        /// <summary>The round's drawn strands (steady, plump 0.5) and their ranks.</summary>
        private static List<(int id, List<V2> rp)> BasinStrands(out Dictionary<int, int> rank, out double vis)
        {
            List<HoseMath.LayeredHose> hs = HoseLayerChecks.BasinLays(100, out CordWorld _, out var _, out double _);
            vis = HoseMath.VisibleWidth(1, 0.5);
            rank = HoseMath.Layer(hs, vis, new HoseMath.LayerCache()).Rank;
            var r = new List<(int, List<V2>)>();
            foreach (var h in hs)
            {
                if (!h.Lay.Ok) continue;
                List<V2> pts = HoseMath.DrawnPose(h.Lay, 1, int.MaxValue / 2, 1, 0.5, null, default(V2));
                if (pts != null && pts.Count >= 2) r.Add((h.Id, pts));
            }
            return r;
        }

        private static List<IList<V2>> LowersOf(int id, int rk, List<(int id, List<V2> rp)> ss, Func<int, int> rankOf)
        {
            var l = new List<IList<V2>>();
            foreach (var s in ss) if (s.id != id && s.rp.Count >= 2 && rankOf(s.id) < rk) l.Add(s.rp);
            return l;
        }

        private static List<V2> RandStrand(Random rnd, int kind)
        {
            int n = kind == 0 ? rnd.Next(0, 2) : rnd.Next(2, 30);
            var l = new List<V2>();
            double x = rnd.NextDouble() * 20, z = rnd.NextDouble() * 20;
            for (int i = 0; i < n; i++)
            {
                double step = kind == 2 && i == n / 2 ? 3000 : rnd.NextDouble() * 2.5;
                double a = rnd.NextDouble() * Math.PI * 2;
                x += Math.Cos(a) * step; z += Math.Sin(a) * step;
                if (kind == 3 && rnd.Next(6) == 0) l.Add(new V2(double.NaN, z));
                else if (kind == 4 && rnd.Next(8) == 0) l.Add(l.Count > 0 ? l[l.Count - 1] : new V2(x, z));   // a repeated point
                else l.Add(new V2(x, z));
            }
            return l;
        }

        public static void Run(Action<string, Action> Case)
        {
            Case("HX1 the 325 basin crossing spans (200 real strands) through the segment grids equal CrossSpans exactly", () =>
            {
                var ss = BasinStrands(out var rank, out double vis);
                Assert(ss.Count >= 150, $"the strands lay ({ss.Count}/200): the layout is the live one");
                Func<int, int> rankOf = id => rank.TryGetValue(id, out int k) ? k : -1;
                double oldMs = 0, newMs = 0, oldMax = 0, newMax = 0;
                int crossing = 0;
                var sw = new Stopwatch();
                foreach (var s in ss)
                {
                    List<IList<V2>> lowers = LowersOf(s.id, rankOf(s.id), ss, rankOf);
                    sw.Restart();
                    List<double[]> want = HoseOverDraw.CrossSpans(s.rp, lowers, vis, Margin);
                    double o = sw.Elapsed.TotalMilliseconds;
                    sw.Restart();
                    List<double[]> got = HoseCrossShadows.SpansOf(s.rp, lowers, vis, Margin);
                    double nw = sw.Elapsed.TotalMilliseconds;
                    oldMs += o; newMs += nw; oldMax = Math.Max(oldMax, o); newMax = Math.Max(newMax, nw);
                    string d = SpanDiff(want, got);
                    Assert(d == "", $"hose {s.id}: {d}");
                    if (want.Count > 0) crossing++;
                }
                Assert(crossing >= 10, $"the layout crosses ({crossing} hoses with a crossing shadow): the comparison sees spans");
                Console.WriteLine($"    HX1 {ss.Count} strands, {crossing} with spans; CrossSpans {oldMs:F0} ms total (max {oldMax:F1}), grid {newMs:F0} ms (max {newMax:F1}; grids built per call)");
            });

            Case("HX2 fuzz: random strands (NaN, 0/1 points, huge segments, repeated points, reach above the grid's) equal CrossSpans", () =>
            {
                var rnd = new Random(20261026);
                double[] reaches = { 0.05, 0.3, 0.55, 1.0, 1.4, double.NaN };
                int nonEmpty = 0;
                for (int t = 0; t < 1500; t++)
                {
                    List<V2> upper = RandStrand(rnd, rnd.Next(5));
                    var lowers = new List<IList<V2>>();
                    for (int k = rnd.Next(0, 6); k > 0; k--) lowers.Add(RandStrand(rnd, rnd.Next(5)));
                    if (rnd.Next(10) == 0) lowers.Add(null);
                    double reach = reaches[rnd.Next(reaches.Length)];
                    var clean = lowers.Where(q => q != null && q.Count >= 2).ToList();
                    List<double[]> want = upper.Count < 2 || clean.Count == 0 ? new List<double[]>() : HoseOverDraw.CrossSpans(upper, clean, reach, Margin);
                    List<double[]> got = HoseCrossShadows.SpansOf(upper, lowers, reach, Margin);
                    string d = SpanDiff(want, got);
                    Assert(d == "", $"trial {t} (reach {reach}): {d}");
                    if (want.Count > 0) nonEmpty++;
                }
                Assert(nonEmpty > 200, $"the fuzz crosses ({nonEmpty} trials with spans)");
            });

            Case("HX3 a relay wave on the basin strands: the index equals all-pairs every frame and re-checks only near strands", () =>
            {
                var ss = BasinStrands(out var rank0, out double vis);
                var rank = new Dictionary<int, int>(rank0);
                Func<int, int> rankOf = id => rank.TryGetValue(id, out int k) ? k : -1;
                var cur = ss.ToDictionary(s => s.id, s => s.rp);
                var ids = ss.Select(s => s.id).ToList();
                var idx = new HoseCrossShadows();
                foreach (var s in ss) idx.Set(s.id, s.rp);
                foreach (int id in ids) idx.Check(id, rankOf(id), rankOf, vis, Margin, out _);
                var rnd = new Random(7);
                var sw = new Stopwatch();
                double oldMax = 0, newMax = 0, newTotal = 0, oldTotal = 0;
                long rescans0 = idx.Rescans;
                int frames = 40;
                const int TransitionFrames = 12;
                var trans = new Dictionary<int, int>();
                int maxMoving = 0;
                // the old policy's state: per hose the (serial-sum) key it last built at
                var oldKey = new Dictionary<int, string>();
                var serial = ids.ToDictionary(i => i, i => 0);
                foreach (int id in ids) oldKey[id] = OldKey(id, ids, serial, rankOf, cur);
                for (int f = 0; f < frames; f++)
                {
                    int k = f % 3 == 0 ? 4 : 1;   // the lay queue lands up to 4 a frame
                    // a landed lay starts a transition: its drawn pose is re-keyed every tick until it settles (DrawAll's key
                    // carries TicksGame while unsettled), so it is a new strand every frame for TransitionFrames frames
                    for (int j = 0; j < k; j++) trans[ids[rnd.Next(ids.Count)]] = TransitionFrames;
                    var relaid = trans.Keys.ToList();
                    foreach (int id in relaid) if (--trans[id] <= 0) trans.Remove(id);
                    maxMoving = Math.Max(maxMoving, relaid.Count);
                    foreach (int id in relaid)
                    {
                        // a re-lay: a new strand object, nudged (a re-plan, or the next transition tick's pose)
                        var np = cur[id].Select(p => new V2(p.X + 0.01 * (rnd.NextDouble() - 0.5), p.Z)).ToList();
                        if (rnd.Next(6) == 0) np = np.Take(Math.Max(2, np.Count / 2)).ToList();
                        cur[id] = np;
                        serial[id]++;
                    }
                    var moved = new List<int>();
                    if (f % 4 == 2)
                    {
                        // a rank swap (Layer re-ordered two hoses)
                        int a = ids[rnd.Next(ids.Count)], b = ids[rnd.Next(ids.Count)];
                        if (rank.ContainsKey(a) && rank.ContainsKey(b) && a != b) { int t = rank[a]; rank[a] = rank[b]; rank[b] = t; moved.Add(a); moved.Add(b); }
                    }
                    var curList = ids.Select(i => (i, cur[i])).ToList();
                    // the old policy: every hose re-scans every other; each whose key changed rebuilds with CrossSpans
                    sw.Restart();
                    int oldBuilds = 0;
                    foreach (int id in ids)
                    {
                        string key = OldKey(id, ids, serial, rankOf, cur);
                        if (oldKey[id] == key) continue;
                        oldKey[id] = key;
                        HoseOverDraw.CrossSpans(cur[id], LowersOf(id, rankOf(id), curList, rankOf), vis, Margin);
                        oldBuilds++;
                    }
                    double o = sw.Elapsed.TotalMilliseconds;
                    // the index
                    sw.Restart();
                    foreach (int id in relaid) idx.Set(id, cur[id]);
                    foreach (int id in moved) idx.RankMoved(id);
                    foreach (int id in ids) idx.Check(id, rankOf(id), rankOf, vis, Margin, out _);
                    double nw = sw.Elapsed.TotalMilliseconds;
                    oldMax = Math.Max(oldMax, o); newMax = Math.Max(newMax, nw); oldTotal += o; newTotal += nw;
                    // every hose's spans equal a fresh all-pairs oracle
                    foreach (int id in ids)
                    {
                        Assert(idx.TryGet(id, out HoseCrossShadows.Strand st), $"frame {f}: {id} indexed");
                        List<double[]> want = HoseOverDraw.CrossSpans(cur[id], LowersOf(id, rankOf(id), curList, rankOf), vis, Margin);
                        string d = SpanDiff(want, st.Spans ?? new List<double[]>());
                        Assert(d == "", $"frame {f}, hose {id}: {d}");
                    }
                }
                // a dropped strand leaves its uppers' spans
                int drop = ids[0];
                idx.Drop(drop);
                var rest = ids.Where(i => i != drop).ToList();
                var restList = rest.Select(i => (i, cur[i])).ToList();
                foreach (int id in rest) idx.Check(id, rankOf(id), rankOf, vis, Margin, out _);
                foreach (int id in rest)
                {
                    idx.TryGet(id, out HoseCrossShadows.Strand st);
                    string d = SpanDiff(HoseOverDraw.CrossSpans(cur[id], LowersOf(id, rankOf(id), restList, rankOf), vis, Margin), st.Spans ?? new List<double[]>());
                    Assert(d == "", $"after drop, hose {id}: {d}");
                }
                long rescans = idx.Rescans - rescans0;
                int n = ids.Count;
                Assert(rescans * 4 < (long)frames * n * 3, $"re-collections {rescans} over {frames} frames of {n} hoses (all-pairs: {frames * n})");
                Assert(newMax < 50, $"the index's worst relay frame {newMax:F1} ms");
                Assert(newTotal * 3 < oldTotal, $"the index ({newTotal:F0} ms) well under the old policy ({oldTotal:F0} ms)");
                Console.WriteLine($"    HX3 {n} hoses, {frames} relay frames (up to {maxMoving} strands re-posed a frame): old policy {oldTotal:F0} ms (max {oldMax:F0}/frame), index {newTotal:F0} ms (max {newMax:F1}/frame); re-collections {rescans} vs {frames * n}; span builds {idx.SpanBuilds}, marks {idx.Marked}");
            });

            Case("HX4 source: the component feeds HoseCrossShadows off FrameLegacy and keeps the all-pairs body for FrameLegacy", () =>
            {
                string src = RiverSwitchFlipChecks.Src(System.IO.Path.Combine("Hose", "RM_MapComponent_Hoses.cs"));
                RiverSwitchFlipChecks.Has(src, @"private readonly HoseCrossShadows crossIndex = new HoseCrossShadows\(\);", "one index per component");
                RiverSwitchFlipChecks.Has(src, @"crossIndex\.Set\(r\.parent\.thingIDNumber, rp\);", "a built strand is indexed");
                RiverSwitchFlipChecks.Has(src, @"meshes\.Remove\(r\); crossIndex\.Drop\(r\.parent\.thingIDNumber\);", "a dropped strand leaves the index");
                RiverSwitchFlipChecks.Has(src, @"meshes\.Clear\(\);\s*crossIndex\.Clear\(\);", "a removed map clears it");
                RiverSwitchFlipChecks.Has(src, @"if \(!LegacyFrame\) RanksMoved\(was, layering\);", "a layering rebuild marks only moved ranks");
                RiverSwitchFlipChecks.Has(src, @"crossIndex\.Check\(id, rank, ", "the shadow asks the index");
                Assert(!src.Contains("private int poseVersion") && !src.Contains("poseVersion++;") && !src.Contains("crossVer != poseVersion"), "the global poseVersion is gone");
            });
        }

        /// <summary>The old DrawCrossShadow key: this hose's serial and its lowers' serials (all-pairs scan).</summary>
        private static string OldKey(int id, List<int> ids, Dictionary<int, int> serial, Func<int, int> rankOf, Dictionary<int, List<V2>> cur)
        {
            // round 6's non-legacy body: every other hose's box tested (CrossReach 1), the meeting lower ones keyed
            var sb = new System.Text.StringBuilder();
            sb.Append(id).Append(':').Append(serial[id]).Append('|');
            int rk = rankOf(id);
            Box(cur[id], out double x0, out double z0, out double x1, out double z1);
            foreach (int o in ids)
            {
                if (o == id) continue;
                Box(cur[o], out double a0, out double b0, out double a1, out double b1);
                if (a0 > x1 || a1 < x0 || b0 > z1 || b1 < z0) continue;
                if (rankOf(o) < rk) sb.Append(o).Append(':').Append(serial[o]).Append(',');
            }
            return sb.ToString();
        }

        private static void Box(List<V2> rp, out double x0, out double z0, out double x1, out double z1)
        {
            x0 = z0 = double.MaxValue; x1 = z1 = double.MinValue;
            foreach (V2 p in rp) { x0 = Math.Min(x0, p.X); z0 = Math.Min(z0, p.Z); x1 = Math.Max(x1, p.X); z1 = Math.Max(z1, p.Z); }
            x0 -= 1; z0 -= 1; x1 += 1; z1 += 1;
        }
    }
}
