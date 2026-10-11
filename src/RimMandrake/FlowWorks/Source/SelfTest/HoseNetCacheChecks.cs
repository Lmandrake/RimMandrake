// Hose port step 7 (design FINAL §3.5, §4 step 7): the per-tick topology cache (RM_NetCache, PRODUCTION, in
// ../Machinery/RM_LiquidNetKernel.cs) and the perf budget on the kernel: 20 reels, 4 pumps, 10 tanks, <= 0.05 ms/tick mean.
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using RimMandrake.FlowWorks.Machinery;

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
        }

        private static void G2(HoseNetChecks.G g, string a, string b)
        {
            HoseNetChecks.G.Add(g.Adj, a, b);
            HoseNetChecks.G.Add(g.Adj, b, a);
        }
    }
}
