// HOSE_FRAME_FIX_CHOKES_325_BASIN_MAP (live round 5, 2026-10-26: 325 basin map, 100 rigs / 200 hoses, FrameLegacy=0; the lays
// themselves ran on the lay queue's workers, yet DrawAll took ~1 s a frame (5.9 s max) through a 300-tick re-lay wave and
// none of its profiled children accounted for it). RM_MapComponent_Hoses.Layered rebuilds HoseMath.Layer whenever any reel's
// lay object changes -- every frame a lay lands -- and Layer was all pairs, every pair re-summing both strands and testing a
// footprint sample against every segment of the other hose.
//  HL1 on the round's own layout (HoseAllocChecks.BasinWorld, 100 rigs: 200 real lays at maxLength 80) the cached broad-phase
//      Layer gives exactly LayerAllPairs' ranks and joiners, cold and after a re-lay wave; a rebuild after k lays changed tests
//      only pairs with a changed lay; timings printed (old body, cold, one re-lay, a 4-lay wave).
//  HL2 fuzz: random strands (crossings, ends resting on bodies, joiners over others, NaN points, 0/1-point strands, repeated
//      lays, repeated ids) through one long-lived cache with lays replaced between rebuilds, the width changed and some
//      lays edited in place: every rebuild equals LayerAllPairs.
//  HL3 source: Layered passes its cache (FrameLegacy keeps the old body for the live A/B).
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using System.Threading.Tasks;
using RimMandrake.FlowWorks.Hose;
using RimMandrake.Shared.Slack;

namespace RimMandrake.FlowWorks.SelfTest
{
    internal static class HoseLayerChecks
    {
        private static void Assert(bool ok, string msg)
        {
            if (!ok) throw new Exception(msg);
        }

        /// <summary>Empty = the two layerings agree in every rank and every joiner list (order included).</summary>
        internal static string Diff(HoseMath.Layering a, HoseMath.Layering b)
        {
            if (a.Rank.Count != b.Rank.Count) return $"rank count {a.Rank.Count} vs {b.Rank.Count}";
            if (!a.Rank.Keys.SequenceEqual(b.Rank.Keys)) return "rank order differs";
            foreach (var kv in a.Rank) if (b.Rank[kv.Key] != kv.Value) return $"rank of {kv.Key}: {kv.Value} vs {b.Rank[kv.Key]}";
            if (a.Joints.Count != b.Joints.Count) return $"joints count {a.Joints.Count} vs {b.Joints.Count}";
            if (!a.Joints.Keys.SequenceEqual(b.Joints.Keys)) return "joints order differs";
            foreach (var kv in a.Joints)
                if (!kv.Value.SequenceEqual(b.Joints[kv.Key])) return $"joints of {kv.Key}: [{string.Join(",", kv.Value)}] vs [{string.Join(",", b.Joints[kv.Key])}]";
            return "";
        }

        /// <summary>The round's 200 hoses: rigs 0..rigCount-1 of the basin layout, intake and outflow each (parallel, each
        /// worker on its own world copy as the lay queue does).</summary>
        internal static List<HoseMath.LayeredHose> BasinLays(int rigCount, out CordWorld w, out List<(int cx, int z)> rigs, out double ms)
        {
            w = HoseAllocChecks.BasinWorld(out rigs);
            var lays = new HoseLay[rigCount * 2];
            CordWorld src = w;
            var rs = rigs;
            var sw = Stopwatch.StartNew();
            Parallel.For(0, rigCount * 2, () => src.Clone(), (i, _, copy) =>
            {
                var (cx, z) = rs[i / 2];
                lays[i] = HoseLayQueue.Compute(copy, HoseAllocChecks.Inputs(cx, z, i % 2 == 1));
                return copy;
            }, _ => { });
            ms = sw.Elapsed.TotalMilliseconds;
            var hs = new List<HoseMath.LayeredHose>();
            for (int i = 0; i < lays.Length; i++) hs.Add(new HoseMath.LayeredHose { Id = 1000 + i, Lay = lays[i] != null && lays[i].Ok ? lays[i] : new HoseLay() });
            return hs;
        }

        private static HoseLay Relay(CordWorld w, List<(int cx, int z)> rigs, int i, int salt)
        {
            var (cx, z) = rigs[i / 2];
            HoseLayInputs inp = HoseAllocChecks.Inputs(cx, z, i % 2 == 1);
            inp.Seed += (ulong)salt;
            HoseLay l = HoseLayQueue.Compute(w.Clone(), inp);
            return l != null && l.Ok ? l : new HoseLay();
        }

        private static List<V2> Strand(Random rnd, int n, double x, double z)
        {
            var p = new List<V2>();
            double a = rnd.NextDouble() * Math.PI * 2;
            for (int i = 0; i < n; i++)
            {
                p.Add(new V2(x, z));
                a += (rnd.NextDouble() - 0.5) * 0.6;
                double step = 0.05 + rnd.NextDouble() * 0.2;
                x += Math.Cos(a) * step;
                z += Math.Sin(a) * step;
            }
            return p;
        }

        private static HoseLay FuzzLay(Random rnd, List<HoseLay> pool)
        {
            int kind = rnd.Next(12);
            if (kind == 0) return new HoseLay();                                         // never laid
            if (kind == 1 && pool.Count > 0) return pool[rnd.Next(pool.Count)];            // the same lay object twice
            var l = new HoseLay { Ok = true };
            int n = kind == 2 ? rnd.Next(2) : 2 + rnd.Next(60);                           // 0/1-point strands too
            double x = rnd.NextDouble() * 12, z = rnd.NextDouble() * 12;
            // an end started on another strand's body: the end-fitting rule has something to find
            if (kind == 3 && pool.Count > 0 && pool[rnd.Next(pool.Count)].Flat is List<V2> f && f.Count > 4) { V2 on = f[f.Count / 2]; x = on.X; z = on.Z; }
            l.Flat = Strand(rnd, n, x, z);
            l.Plump = rnd.Next(4) == 0 ? new List<V2>() : l.Flat.Select(v => new V2(v.X + 0.01, v.Z - 0.01)).ToList();
            if (kind == 4 && l.Flat.Count > 3) l.Flat[rnd.Next(l.Flat.Count)] = new V2(double.NaN, z);
            for (int k = 0; k < rnd.Next(5); k++) l.Joints.Add(rnd.Next(-1, n + 2));          // out-of-range joiners too
            return l;
        }

        public static void Run(Action<string, Action> Case)
        {
            Case("HL1 the 325 basin layering (200 real lays) equals the old body, cold and after re-lays, and re-tests only changed pairs", () =>
            {
                List<HoseMath.LayeredHose> hs = BasinLays(100, out CordWorld w, out var rigs, out double layMs);
                int laid = hs.Count(h => h.Lay.Ok);
                Assert(laid >= 150, $"the lays lay ({laid}/200): the layout is the live one");
                double vis = HoseMath.VisibleWidth(1, 0.5);
                long o0 = GC.GetAllocatedBytesForCurrentThread();
                var sw = Stopwatch.StartNew();
                HoseMath.Layering old = HoseMath.LayerAllPairs(hs, vis);
                double oldMs = sw.Elapsed.TotalMilliseconds;
                long oldBytes = GC.GetAllocatedBytesForCurrentThread() - o0;
                var cache = new HoseMath.LayerCache();
                long a0 = GC.GetAllocatedBytesForCurrentThread();
                sw.Restart();
                HoseMath.Layering cold = HoseMath.Layer(hs, vis, cache);
                double coldMs = sw.Elapsed.TotalMilliseconds;
                long coldBytes = GC.GetAllocatedBytesForCurrentThread() - a0;
                string d = Diff(old, cold);
                Assert(d == "", "cold: " + d);
                long tested0 = cache.PairsTested;
                int n = hs.Count;
                Assert(tested0 < n * (n - 1) / 4, $"broad phase: {tested0} of {n * (n - 1)} pairs tested cold");
                // a re-lay wave: one lay, then four (the lay queue's per-frame start budget), each a new lay object
                double[] waveMs = new double[2];
                int[] waveK = { 1, 4 };
                for (int wv = 0; wv < 2; wv++)
                {
                    int k = waveK[wv];
                    var changed = new List<int>();
                    for (int c = 0; c < k; c++) { int i = (37 + 53 * c + 11 * wv) % n; changed.Add(i); hs[i] = new HoseMath.LayeredHose { Id = hs[i].Id, Lay = Relay(w, rigs, i, 7 + wv) }; }
                    long t0 = cache.PairsTested;
                    a0 = GC.GetAllocatedBytesForCurrentThread();
                    sw.Restart();
                    HoseMath.Layering warm = HoseMath.Layer(hs, vis, cache);
                    waveMs[wv] = sw.Elapsed.TotalMilliseconds;
                    long warmBytes = GC.GetAllocatedBytesForCurrentThread() - a0;
                    long tested = cache.PairsTested - t0;
                    d = Diff(HoseMath.LayerAllPairs(hs, vis), warm);
                    Assert(d == "", $"after {k} re-lay(s): " + d);
                    Assert(tested <= 2L * k * (n - 1), $"{k} re-lay(s) re-tested {tested} pairs (bound {2 * k * (n - 1)}: only pairs with a changed lay)");
                    Console.WriteLine($"    HL1 wave {k}: {waveMs[wv]:0.00} ms, {tested} pairs re-tested, {warmBytes / 1024} KB");
                }
                Console.WriteLine($"    HL1: {laid}/200 laid in {layMs / 1000:0.0} s; LayerAllPairs {oldMs:0.0} ms ({oldBytes / (1024 * 1024)} MB); cached cold {coldMs:0.0} ms ({tested0} pairs, {coldBytes / 1024} KB); geoms {cache.GeomCount}, pairs kept {cache.PairCount}; ends on another {cache.EndsOn}, joiners over another {cache.JointsOver}");
                Assert(cache.EndsOn > 0, "the basin has ends resting on other hoses (the rule the order serves is exercised)");
                Assert(waveMs[1] < 100, $"a 4-lay wave rebuild took {waveMs[1]:0.0} ms (bound 100 ms; the frame bar)");
            });
            Case("HL2 fuzz: a long-lived layering cache equals the old body through lay swaps and width changes", () =>
            {
                var rnd = new Random(20261026);
                var cache = new HoseMath.LayerCache();
                var pool = new List<HoseLay>();
                var hs = new List<HoseMath.LayeredHose>();
                for (int i = 0; i < 40; i++) { HoseLay l = FuzzLay(rnd, pool); pool.Add(l); hs.Add(new HoseMath.LayeredHose { Id = rnd.Next(4) == 0 ? rnd.Next(100) : 100 + i, Lay = l }); }
                int rounds = 0, edited = 0;
                double vis = HoseMath.VisibleWidth(1, 0.5);
                for (int round = 0; round < 300; round++)
                {
                    int swaps = rnd.Next(4);
                    for (int s = 0; s < swaps; s++) { HoseLay l = FuzzLay(rnd, pool); pool.Add(l); hs[rnd.Next(hs.Count)].Lay = l; }
                    if (round % 7 == 3 && hs.Count > 5) hs.RemoveAt(rnd.Next(hs.Count));
                    if (round % 9 == 4) { HoseLay l = FuzzLay(rnd, pool); pool.Add(l); hs.Add(new HoseMath.LayeredHose { Id = 500 + round, Lay = l }); }
                    // a lay edited in place (landed lays never are; the cache must notice rather than trust it)
                    if (round % 11 == 5) { HoseLay e = hs[rnd.Next(hs.Count)].Lay; if (e.Flat.Count > 3) { e.Flat = Strand(rnd, e.Flat.Count, e.Flat[0].X + 0.3, e.Flat[0].Z); edited++; } }
                    if (round % 50 == 25) vis = HoseMath.VisibleWidth(1, rnd.NextDouble());
                    HoseMath.Layering a = HoseMath.LayerAllPairs(hs, vis), b = HoseMath.Layer(hs, vis, cache);
                    string d = Diff(a, b);
                    Assert(d == "", $"round {round}: " + d);
                    rounds++;
                }
                Console.WriteLine($"    HL2: {rounds} rebuilds equal ({edited} lays edited in place); ends on another {cache.EndsOn}, joiners over another {cache.JointsOver}; tested {cache.PairsTested}, reused {cache.PairsReused}");
                Assert(cache.EndsOn > 20 && cache.JointsOver > 20 && edited > 5, $"the fuzz reaches both rules and the edit guard (ends {cache.EndsOn}, joiners {cache.JointsOver}, edits {edited})");
                Assert(cache.PairsReused > cache.PairsTested, "pairs are reused between rebuilds");
            });
            Case("HL3 source: Layered passes its cache; FrameLegacy keeps the old body", () =>
            {
                string src = RiverSwitchFlipChecks.Src(System.IO.Path.Combine("Hose", "RM_MapComponent_Hoses.cs"));
                RiverSwitchFlipChecks.Has(src, @"layering = LegacyFrame \? HoseMath\.LayerAllPairs\(hs, layVis\) : HoseMath\.Layer\(hs, layVis, layerCache\);", "Layered uses the cache off FrameLegacy");
                RiverSwitchFlipChecks.Has(src, @"private readonly HoseMath\.LayerCache layerCache = new HoseMath\.LayerCache\(\);", "one cache per component");
            });
        }
    }
}
