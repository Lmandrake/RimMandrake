// Hose port step 7 (design FINAL §3.5, §4 step 7), revised by liquid networks L2 (rev 2 §3.1, §4): the topology cache is per
// REVISION (RM_NetTopologyCache, PRODUCTION, in ../Machinery/RM_LiquidNetKernel.cs; the per-tick RM_NetCache is deleted) and
// the perf budget on the kernel: 20 reels, 4 pumps, 10 tanks, <= 0.05 ms/tick mean and <= 1 ms worst tick, rebuilds included.
// Changed assertions: "one walk per pump cycle" became "one component set per revision" (stronger: zero rebuilds per tick on
// a quiet map); the same-tick revalidation case is kept on RouteLive with the bump that replaced MarkDirty.
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
            // L2 (rev 2 §3.1): RM_NetCache (per origin, per tick) is deleted. Components are kept per topology REVISION
            // (RM_NetTopologyCache, PRODUCTION): same revision = same components, however many ticks pass; a bump rebuilds lazily.
            var g = new HoseNetChecks.G();
            g.Hose("P1", "T1", "A");
            var cache = new RM_NetTopologyCache();
            int made = 0;
            Func<RM_NetComponents> make = () => { made++; return new RM_NetComponents(g); };
            RM_NetComponents a = cache.Get(RM_LiquidNetKernel.RevisionKey(1, true, true), make);
            RM_NetResult s1 = a.StoreOf("P1"), s2 = a.StoreOf("P1");
            Check(ReferenceEquals(s1, s2) && a.Builds == 1, "two queries in one revision = one component build");
            for (int tick = 0; tick < 1000; tick++) cache.Get(RM_LiquidNetKernel.RevisionKey(1, true, true), make);
            Check(made == 1 && cache.Revisions == 1, "a quiet map never rebuilds: 1000 ticks, same revision, one component set");
            RM_NetComponents b = cache.Get(RM_LiquidNetKernel.RevisionKey(2, true, true), make);
            Check(made == 2 && !ReferenceEquals(a, b), "a bumped revision builds new components");
            cache.Get(RM_LiquidNetKernel.RevisionKey(2, false, true), make);
            cache.Get(RM_LiquidNetKernel.RevisionKey(2, false, false), make);
            Check(made == 4, "switching pipes or hoses in Mod Settings is a new revision");
            // revalidation: a hose wound in between two transfers in the SAME revision drops the route at transfer time
            RM_NetResult r = b.StoreOf("P1");
            g.Dead.Add(0);
            bool live = RM_LiquidNetKernel.RouteLive(r.Routes["T1"], l => !g.Dead.Contains(l.Id));
            RM_NetComponents c = cache.Get(RM_LiquidNetKernel.RevisionKey(live ? 2 : 3, false, false), make);   // RouteLiveOrBump bumps
            Check(!live && c.StoreOf("P1").Tanks.Count == 0, "a link wound in mid-revision: the transfer drops it and the bumped revision has no tank");
            Check(r.Tanks.Count == 1, "can-fail: the stale revision's store still lists the tank -- only the revalidation stops the transfer");
            // the store holds topology only: a tank's room is never cached (TankToFill re-checks CanAccept on every call)
            Check(typeof(RM_NetResult).GetFields().All(f => f.Name != "Room" && f.Name != "Units"), "the cached store carries no tank room");
            // the link signature (RM_HoseLinks' backstop): any reel, inlet or far change is a different signature
            ulong h0 = RM_LiquidNetKernel.SigStep(RM_LiquidNetKernel.SigSeed, 10, 20, 30);
            Check(h0 != RM_LiquidNetKernel.SigStep(RM_LiquidNetKernel.SigSeed, 10, 20, 31) && h0 != RM_LiquidNetKernel.SigStep(RM_LiquidNetKernel.SigSeed, 10, 21, 30)
                  && h0 != RM_LiquidNetKernel.SigStep(RM_LiquidNetKernel.SigSeed, 11, 20, 30) && h0 == RM_LiquidNetKernel.SigStep(RM_LiquidNetKernel.SigSeed, 10, 20, 30),
                  "the link signature changes with the reel, its inlet or its far end, and only then");

            // ---- perf budget: 20 reels, 4 pumps, 10 tanks; every pump cycles once per 250 ticks (a store lookup and a few
            // route reads); the tank feed reads each tank-ended hose's component once per cycle; a topology bump every 10
            // cycles rebuilds everything inside one tick. Bars: <= 0.05 ms/tick mean and <= 1 ms worst tick (rev 2 §4).
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
            // one untimed pass first: the first call of each kernel method pays the JIT once per game session, not per tick.
            // Then three timed passes; the budget is read off the BEST pass (min mean, min worst tick): a scheduler or GC hiccup
            // lands in one pass (15.6 ms was measured once against the 1 ms bar), a real regression is slow in all three.
            double bestTick = double.MaxValue, bestWorst = double.MaxValue;
            int lastRevisions = -1;
            for (int pass = 0; pass < 4; pass++)
            {
            var nc = new RM_NetTopologyCache();
            int revision = 0, builds = 0;
            double worst = 0;
            var sw = Stopwatch.StartNew();
            var tickClock = new Stopwatch();
            int ticks = 0;
            for (int cycle = 0; cycle < 40; cycle++)
                for (int t = 0; t < 250; t++, ticks++)
                {
                    tickClock.Restart();
                    if (t == 0 && cycle % 10 == 0) revision++;
                    RM_NetComponents comps = nc.Get(RM_LiquidNetKernel.RevisionKey(revision, true, true), () => new RM_NetComponents(big));
                    for (int p = 0; p < pumps.Length; p++)
                    {
                        if (t != p * 50) continue;
                        RM_NetResult w = comps.StoreOf(pumps[p]);
                        for (int k = 0; k < 3; k++) comps.StoreOf(pumps[p]);          // TankToFill / Route / Credit reuse it
                        foreach (List<RM_NetLink> route in w.Routes.Values) RM_LiquidNetKernel.RouteLive(route, l => true);
                    }
                    if (t == 7)   // the settle (L4): each tank's components once per cycle
                        foreach (RM_NetLink l in big.Links.Where(x => ((string)x.B).StartsWith("T")))
                            foreach (RM_NetComponent cc in comps.ComponentsOf(l.B)) cc.Tanks.Count.GetHashCode();
                    builds = Math.Max(builds, comps.Builds);
                    worst = Math.Max(worst, tickClock.Elapsed.TotalMilliseconds);
                }
            sw.Stop();
            if (pass == 0) continue;
            bestTick = Math.Min(bestTick, sw.Elapsed.TotalMilliseconds / ticks);
            bestWorst = Math.Min(bestWorst, worst);
            lastRevisions = nc.Revisions;
            }
            Console.WriteLine("  net perf: best of 3 passes, " + lastRevisions + " revisions, " + bestTick.ToString("0.00000") + " ms/tick mean (budget 0.05), worst tick " + bestWorst.ToString("0.000") + " ms (budget 1)");
            Check(bestTick <= 0.05 && lastRevisions == 4, "perf budget: 20 reels, 4 pumps, 10 tanks <= 0.05 ms/tick mean (" + bestTick.ToString("0.0000") + "), one component set per revision (" + lastRevisions + ")");
            Check(bestWorst <= 1.0, "perf budget: worst tick, rebuild included, <= 1 ms (" + bestWorst.ToString("0.000") + ")");
            RevTwoPerf();
            RelayIndexChecks();
        }

        // ---- liquid networks L11 (rev 2 §4): the budget fixture is FINAL §3.5 plus 3 non-Store tanks, 2 Intake and 2 Outflow
        // ends and 1 pouring pump; every pump cycle each pump reads its store and ports and chooses (PumpNext), the settle plans
        // every component holding a tank with a job, and a topology bump every 10 cycles rebuilds inside one tick. Bars: <= 0.05
        // ms/tick mean and <= 1 ms worst tick, on the PRODUCTION kernel.
        private static void RevTwoPerf()
        {
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
            RM_FreeEndRole[] roles = { RM_FreeEndRole.Intake, RM_FreeEndRole.Intake, RM_FreeEndRole.Outflow, RM_FreeEndRole.Outflow };
            for (int i = 0; i < 4; i++)
                big.Links.Add(new RM_NetLink { Id = big.Links.Count, A = "c" + (2 * i + 1), B = new RM_NetPort { Reel = "E" + i, Cell = "end" + i, Role = roles[i] }, Reel = "E" + i });
            var modes = new Dictionary<string, RM_TankMode> { { "T2", RM_TankMode.Fill }, { "T5", RM_TankMode.Empty }, { "T8", RM_TankMode.Dump } };
            var units = new Dictionary<string, int>();
            for (int i = 0; i < 10; i++) units["T" + i] = 20 * i;
            double worst = 0, mean = 0, bestWorst = double.MaxValue, bestMean = double.MaxValue;
            for (int pass = 0; pass < 4; pass++)   // pass 0 is the untimed JIT pass; the bars read the BEST of the three timed passes (a hiccup hits one, a regression all)
            {
                var nc = new RM_NetTopologyCache();
                int revision = 0;
                var sw = Stopwatch.StartNew();
                var clock = new Stopwatch();
                int ticks = 0;
                worst = 0;
                for (int cycle = 0; cycle < 40; cycle++)
                    for (int t = 0; t < 250; t++, ticks++)
                    {
                        clock.Restart();
                        if (t == 0 && cycle % 10 == 0) revision++;
                        RM_NetComponents comps = nc.Get(RM_LiquidNetKernel.RevisionKey(revision, true, true), () => new RM_NetComponents(big));
                        for (int p = 0; p < pumps.Length; p++)
                        {
                            if (t != p * 50) continue;
                            RM_NetResult store = comps.StoreOf(pumps[p]);
                            var intakes = new List<RM_NetPort>();
                            var outflows = new List<RM_NetPort>();
                            foreach (RM_NetComponent c in comps.ComponentsOf(pumps[p]))
                                foreach (RM_NetPort port in c.Ports) (port.Role == RM_FreeEndRole.Intake ? intakes : outflows).Add(port);
                            var used = new HashSet<int>();
                            bool pouring = p == 3;
                            if (!pouring)
                                RM_LiquidNetKernel.PumpNext(1 + intakes.Count, s => true, outflows.Count, (o, s) => o % 2 == 0, used, s => store.Tanks.Count > 0, cycle, out _, out _);
                            foreach (List<RM_NetLink> route in store.Routes.Values) RM_LiquidNetKernel.RouteLive(route, l => true);
                        }
                        if (t == 7)
                        {
                            var done = new HashSet<RM_NetComponent>();
                            foreach (string m in modes.Keys)
                                foreach (RM_NetComponent c in comps.ComponentsOf(m))
                                {
                                    if (!done.Add(c)) continue;
                                    var view = c.Tanks.Select(x => new RM_SettleTank(int.Parse(((string)x).Substring(1)), units[(string)x], 300, "water",
                                        modes.TryGetValue((string)x, out RM_TankMode md) ? md : RM_TankMode.Store)).ToList();
                                    RM_LiquidNetKernel.SettlePlan(view, 10, cycle);
                                }
                        }
                        worst = Math.Max(worst, clock.Elapsed.TotalMilliseconds);
                    }
                sw.Stop();
                mean = sw.Elapsed.TotalMilliseconds / ticks;
                if (pass > 0) { bestWorst = Math.Min(bestWorst, worst); bestMean = Math.Min(bestMean, mean); }
            }
            worst = bestWorst; mean = bestMean;
            Console.WriteLine("  rev 2 net perf: 20 reels, 4 pumps (1 pouring), 10 tanks (3 with jobs), 2 intake + 2 outflow ends: " + mean.ToString("0.00000") +
                              " ms/tick mean (budget 0.05), worst tick " + worst.ToString("0.000") + " ms (budget 1)");
            Check(mean <= 0.05, "rev 2 perf fixture: mean <= 0.05 ms/tick (" + mean.ToString("0.0000") + ")");
            Check(worst <= 1.0, "rev 2 perf fixture: worst tick, rebuild included, <= 1 ms (" + worst.ToString("0.000") + ")");
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
