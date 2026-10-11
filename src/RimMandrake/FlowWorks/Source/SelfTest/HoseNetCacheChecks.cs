// Hose port step 7 (design FINAL §3.5, §4 step 7): the per-tick topology cache (RM_NetCache, PRODUCTION, in
// ../Machinery/RM_LiquidNetKernel.cs) and the perf budget on the kernel: 20 reels, 4 pumps, 10 tanks, <= 0.05 ms/tick mean.
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using RimMandrake.FlowWorks.Hose;
using RimMandrake.FlowWorks.Machinery;
using RimMandrake.Shared.Slack;

namespace RimMandrake.FlowWorks.SelfTest
{
    internal static class HoseNetCacheChecks
    {
        private static void Check(bool ok, string msg) => Program.Check(ok, "hosecache: " + msg);

        public static void Run()
        {
            var g = new HoseNetChecks.G();
            g.Hose("P1", "T1", "A");
            var cache = new RM_NetCache();
            Func<RM_NetResult> walk = () => RM_LiquidNetKernel.Walk(g, "P1");
            RM_NetResult a = cache.Get(1, 100, walk), b = cache.Get(1, 100, walk);
            Check(ReferenceEquals(a, b) && cache.Walks == 1, "two calls in one tick = one walk");
            cache.Get(1, 101, walk);
            Check(cache.Walks == 2 && cache.Cached == 1, "the next tick walks again, and nothing older is kept");
            cache.Get(2, 101, () => RM_LiquidNetKernel.Walk(g, "P2"));
            Check(cache.Walks == 3, "each origin has its own walk");
            // revalidation: a hose wound in between two transfers in the SAME tick drops the route; the origin is walked again
            RM_NetResult r = cache.Get(1, 101, walk);
            g.Dead.Add(0);
            bool live = RM_LiquidNetKernel.RouteLive(r.Routes["T1"], l => !g.Dead.Contains(l.Id));
            if (!live) cache.MarkDirty(1);
            RM_NetResult r2 = cache.Get(1, 101, walk);
            Check(!live && cache.Walks == 4 && r2.Tanks.Count == 0, "a link wound in mid-tick: the transfer drops it and the next call re-walks (no tank)");
            Check(r.Tanks.Count == 1, "can-fail: the stale cached walk still lists the tank -- only the revalidation stops the transfer");
            // the cache holds topology only: a tank's room is never cached (TankToFill re-checks CanAccept on every call)
            Check(typeof(RM_NetResult).GetFields().All(f => f.Name != "Room" && f.Name != "Units"), "the cached result carries no tank room");

            // ---- perf budget: 20 reels, 4 pumps, 10 tanks; every pump cycles once per 250 ticks (one walk, a few credits), the
            // link index is rebuilt on every tick something uses it, and the tank feed walks each tank-ended hose once per cycle
            var big = new HoseNetChecks.G();
            string[] pumps = { "P1", "P2", "P3", "P4" };
            for (int i = 0; i < 10; i++) G2(big, "c" + i, "c" + (i + 1));
            for (int i = 0; i < 10; i++) HoseNetChecks.G.Add(big.PT, "c" + i, "T" + i);
            HoseNetChecks.G.Add(big.PipeOf, "P1", "c0");
            for (int i = 0; i < 20; i++)
            {
                string from = i < 4 ? pumps[i] : (i < 12 ? "R" + (i - 4) : "R" + (i - 12));
                string to = i < 4 ? "R" + i : (i < 12 ? "R" + (i - 3) : "T" + (i - 12) % 10);
                big.Hose(from, to);
            }
            var nc = new RM_NetCache();
            var sw = Stopwatch.StartNew();
            int ticks = 0;
            for (int cycle = 0; cycle < 40; cycle++)
                for (int t = 0; t < 250; t++, ticks++)
                {
                    int now = cycle * 250 + t;
                    for (int p = 0; p < pumps.Length; p++)
                    {
                        if (t != p * 50) continue;
                        var links = big.Links.Select(l => new RM_NetLink { Id = l.Id, A = l.A, B = l.B, Reel = l.Reel }).ToList();   // index rebuild cost
                        RM_NetResult w = nc.Get(p, now, () => RM_LiquidNetKernel.Walk(big, pumps[p]));
                        for (int k = 0; k < 3; k++) nc.Get(p, now, () => RM_LiquidNetKernel.Walk(big, pumps[p]));          // TankToFill / Route / Credit reuse it
                        foreach (List<RM_NetLink> route in w.Routes.Values) RM_LiquidNetKernel.RouteLive(route, l => true);
                        GC.KeepAlive(links);
                    }
                    if (t == 7)
                        foreach (RM_NetLink l in big.Links.Where(x => ((string)x.B).StartsWith("T")))
                            RM_LiquidNetKernel.Across(big, l, l.B);
                }
            sw.Stop();
            double perTick = sw.Elapsed.TotalMilliseconds / ticks;
            Console.WriteLine("  net perf: " + ticks + " ticks, " + nc.Walks + " walks, " + perTick.ToString("0.00000") + " ms/tick mean (budget 0.05)");
            Check(perTick <= 0.05 && nc.Walks == 40 * 4, "perf budget: 20 reels, 4 pumps, 10 tanks <= 0.05 ms/tick mean (" + perTick.ToString("0.0000") + "), one walk per pump cycle");
            RelayIndexChecks();
        }

        // ---- review S1 (design FINAL §3.1 "Index", G1.17): the shared relay index, measured on the REAL production code
        // (HoseRelayIndex and HoseRelay in ../Hose/HoseRelay.cs), against the per-query shape RM_MapComponent_Hoses used before
        // (RelayOf -> HoseRelay.RelayOf over every footprint, Loops walking the chain with RelayOf at every step).
        private static void Layout(int n, int seed, out List<HoseReelRect> rects, out List<Cell?> far)
        {
            var rnd = new Random(seed);
            rects = new List<HoseReelRect>();
            far = new List<Cell?>();
            for (int i = 0; i < n; i++) rects.Add(new HoseReelRect((i % 10) * 6, (i / 10) * 6, 2, 2));
            for (int i = 0; i < n; i++)
            {
                int roll = rnd.Next(10);
                if (roll < 2) { far.Add(null); continue; }                                   // not laid
                if (roll < 3) { far.Add(new Cell(200 + i, 200)); continue; }                 // a free end
                int to = roll < 8 && i + 1 < n ? i + 1 : rnd.Next(n);                         // chains, plus random edges (loops)
                List<Cell> ic = HoseRelay.IntakeCells(rects[to]);
                far.Add(ic[rnd.Next(ic.Count)]);
            }
        }

        private static int OldNext(List<HoseReelRect> rects, List<Cell?> far, int i) =>
            far[i].HasValue ? HoseRelay.RelayOf(far[i].Value, rects, i) : -1;

        private static List<int> OldFeeders(List<HoseReelRect> rects, List<Cell?> far, int r)
        {
            var o = new List<int>();
            for (int f = 0; f < rects.Count; f++)
                if (f != r && OldNext(rects, far, f) == r && !HoseRelay.WouldLoop(f, r, i => OldNext(rects, far, i))) o.Add(f);
            return o;
        }

        private static void RelayIndexChecks()
        {
            // equivalence: the index answers exactly what the per-query functions answered, chains and loops included
            bool same = true, sawLoop = false, sawChain = false;
            foreach (int n in new[] { 20, 60 })
                for (int seed = 1; seed <= 12; seed++)
                {
                    Layout(n, seed, out List<HoseReelRect> rects, out List<Cell?> far);
                    var idx = new HoseRelayIndex(rects, far, null);
                    for (int r = 0; r < n; r++)
                    {
                        if (idx.Next(r) != OldNext(rects, far, r)) same = false;
                        bool oldLoop = OldNext(rects, far, r) >= 0 && HoseRelay.WouldLoop(r, OldNext(rects, far, r), i => OldNext(rects, far, i));
                        if (idx.OnLoop(r) != oldLoop) same = false;
                        sawLoop |= oldLoop;
                        if (!idx.Feeders(r).SequenceEqual(OldFeeders(rects, far, r))) same = false;
                        sawChain |= idx.Feeders(r).Count > 0;
                        if (n == 20)
                            for (int t = 0; t < n; t++)
                                if (idx.WouldLoop(r, t) != HoseRelay.WouldLoop(r, t, i => OldNext(rects, far, i))) same = false;
                    }
                }
            Check(same && sawLoop && sawChain, "relay index == the per-query RelayOf/Loops/FeedersOf on 24 layouts (n=20, 60; chains and loops present)");

            // work: one rebuild enumerates each reel's intake cells ONCE (O(reels)); the old per-reel RelayOf + Loops shape is
            // O(n^2) and more. Counted on the real HoseRelay.IntakeCells, so a regression to per-query scans turns this red.
            foreach (int n in new[] { 20, 60 })
            {
                Layout(n, 7, out List<HoseReelRect> rects, out List<Cell?> far);
                HoseRelay.IntakeCellCalls = 0;
                var idx = new HoseRelayIndex(rects, far, null);
                for (int r = 0; r < n; r++) { idx.Feeders(r); idx.Next(r); idx.OnLoop(r); }
                long newCalls = HoseRelay.IntakeCellCalls;
                HoseRelay.IntakeCellCalls = 0;
                for (int r = 0; r < n; r++) { int nx = OldNext(rects, far, r); if (nx >= 0) HoseRelay.WouldLoop(r, nx, i => OldNext(rects, far, i)); }
                long oldCalls = HoseRelay.IntakeCellCalls;
                Console.WriteLine("  relay index n=" + n + ": rebuild + every query = " + newCalls + " intake enumerations (old per-query shape: " + oldCalls + ")");
                Check(newCalls == n, "relay index n=" + n + ": a rebuild plus every reel's Next/Feeders/OnLoop enumerates intakes exactly n times (" + newCalls + ")");
                Check(oldCalls >= (long)n * n / 2, "can-fail: the old per-query shape (RM_HoseLinks.Refresh before S1) costs >= n^2/2 enumerations at n=" + n + " (" + oldCalls + ") -- the counter sees it");
            }

            // time: the real rebuild + every query, n=60, mean over 400 rebuilds
            {
                Layout(60, 3, out List<HoseReelRect> rects, out List<Cell?> far);
                var sw = Stopwatch.StartNew();
                for (int k = 0; k < 400; k++)
                {
                    var idx = new HoseRelayIndex(rects, far, null);
                    for (int r = 0; r < 60; r++) { idx.Feeders(r); idx.OnLoop(r); idx.FedByDebug(r, i => true); }
                }
                sw.Stop();
                double per = sw.Elapsed.TotalMilliseconds / 400;
                var swOld = Stopwatch.StartNew();
                for (int k = 0; k < 20; k++)
                    for (int r = 0; r < 60; r++) { int nx = OldNext(rects, far, r); if (nx >= 0) HoseRelay.WouldLoop(r, nx, i => OldNext(rects, far, i)); OldFeeders(rects, far, r); }
                swOld.Stop();
                double perOld = swOld.Elapsed.TotalMilliseconds / 20;
                Console.WriteLine("  relay index n=60: " + per.ToString("0.0000") + " ms per rebuild + 60 reels' queries (budget 0.25; it runs only when a laid end changes); old per-query shape " + perOld.ToString("0.000") + " ms");
                Check(per <= 0.25, "relay index n=60: rebuild + all queries <= 0.25 ms (" + per.ToString("0.0000") + ")");
                Check(per * 10 <= perOld, "relay index n=60 is >= 10x cheaper than the old per-query shape (" + per.ToString("0.0000") + " vs " + perOld.ToString("0.000") + " ms)");
            }

            // the debug provider on an idle map (no reel flagged) walks nothing; with a flag it still propagates down a chain
            {
                Layout(60, 5, out List<HoseReelRect> rects, out List<Cell?> far);
                var idle = new HoseRelayIndex(rects, far, null);
                HoseRelayIndex.DebugWalkSteps = 0;
                bool any = false;
                for (int r = 0; r < 60; r++) any |= idle.FedByDebug(r, i => true);
                Check(!any && !idle.AnyDebug && HoseRelayIndex.DebugWalkSteps == 0, "debug provider, idle map: 60 hoses read, 0 feeder steps walked");
                var chainRects = new List<HoseReelRect>();
                var chainFar = new List<Cell?>();
                for (int i = 0; i < 4; i++) chainRects.Add(new HoseReelRect(i * 6, 0, 2, 2));
                for (int i = 0; i < 4; i++) chainFar.Add(i < 3 ? HoseRelay.IntakeCells(chainRects[i + 1])[0] : (Cell?)null);
                var flagged = new HoseRelayIndex(chainRects, chainFar, new[] { true, false, false, false });
                Check(flagged.AnyDebug && flagged.FedByDebug(3, i => true) && !flagged.FedByDebug(0, i => true),
                    "debug provider: a flag at the head of a 4-reel chain reaches the last reel, never upstream");
                Check(!flagged.FedByDebug(3, i => i != 1), "can-fail: a feeder with no laid hose stops the debug flag");
            }
        }

        private static void G2(HoseNetChecks.G g, string a, string b)
        {
            HoseNetChecks.G.Add(g.Adj, a, b);
            HoseNetChecks.G.Add(g.Adj, b, a);
        }
    }
}
