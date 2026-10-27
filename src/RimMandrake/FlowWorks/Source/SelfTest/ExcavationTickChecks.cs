// EXCAVATION_COMPONENT_DIAGNOSE_TICK_SPIKES (BENCH TPS bisect 2026-10-26: RM_MapComponent_Excavation 0.87 ms/tick on a 325x325
// map, single ticks of 158-172 ms). The excavation tick drives RM_PocketGrid.Tick -> RM_WallReach.Tick. Two whole-map passes ran
// far more often than their inputs changed:
//   1. RM_WallReach: every PathFinderMapData.GatherData (any tick a pawn paths) bumped wallGen, so every labelling (whole-map
//      Kinds() scan + one flood per entry) rebuilt at the 60-tick ceiling even on a map whose walls never moved.
//   2. RM_PocketGrid / RM_WallReach: a ClimbGeneration bump re-flooded every band of every view even when the depth view the
//      floods read came out byte-identical (the spike: plain+stride+floor views x bands x 325x325 in one tick).
// The fix keeps results identical by construction: a delta moves the generation only when its square's kind differs from the
// snapshot the labels were built from (RM_WallReachMath.DeltaMovesKinds), and a rebuild over byte-identical inputs keeps the
// labels (RM_WallReachMath.SameBytes / SameRamps). These checks replay randomized maps against the old full scan.
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;

namespace RimMandrake.FlowWorks.SelfTest
{
    internal static class ExcavationTickChecks
    {
        private static void Assert(bool ok, string msg)
        {
            if (!ok) throw new Exception(msg);
        }

        private static string Src(params string[] rel) => RiverSwitchFlipChecks.Src(Path.Combine(rel));

        private static bool SameLabels(RM_WallReachMath.Labels a, RM_WallReachMath.Labels b)
        {
            if (a == null || b == null) return a == b;
            if (a.count != b.count || a.width != b.width || a.height != b.height || a.label.Length != b.label.Length) return false;
            for (int i = 0; i < a.label.Length; i++) if (a.label[i] != b.label[i]) return false;
            return true;
        }

        private static bool SameLabels(RM_PocketGridMath.Labels a, RM_PocketGridMath.Labels b)
        {
            if (a == null || b == null) return a == b;
            if (a.count != b.count || a.k != b.k || a.label.Length != b.label.Length) return false;
            for (int i = 0; i < a.label.Length; i++) if (a.label[i] != b.label[i]) return false;
            for (int c = 0; c < a.count; c++) if (a.surface[c] != b.surface[c] || a.size[c] != b.size[c]) return false;
            return true;
        }

        private static readonly byte[] KindPool =
        {
            RM_WallReachMath.Open, RM_WallReachMath.Open, RM_WallReachMath.Open, RM_WallReachMath.Open, RM_WallReachMath.Wall,
            RM_WallReachMath.Wall, RM_WallReachMath.Door, RM_WallReachMath.PlayerDoor, RM_WallReachMath.Fence, RM_WallReachMath.DeepWater,
        };

        private static byte[] RandomKinds(Random r, int n)
        {
            var k = new byte[n];
            for (int i = 0; i < n; i++) k[i] = KindPool[r.Next(KindPool.Length)];
            return k;
        }

        private static byte[] RandomDepth(Random r, int n, bool anyDug)
        {
            var d = new byte[n];
            if (anyDug) for (int i = 0; i < n; i++) d[i] = r.Next(4) == 0 ? (byte)r.Next(1, 6) : (byte)0;
            return d;
        }

        /// <summary>One simulated labelling under the new policy: the production rules, minus Verse.</summary>
        private sealed class Sim
        {
            public byte[] snapshot;          // MapState.kinds (kept by reference when its content did not change)
            public long gen;                 // wallGen
            public long builtGen = -1;
            public byte[] builtKinds, builtDepth;
            public RM_WallReachMath.Labels labels;
            public int floods, skips, bumps;

            public void Rebuild(byte[] liveKinds, byte[] depth, int w, int h, int band, int cls)
            {
                byte[] fresh = (byte[])liveKinds.Clone();
                if (!RM_WallReachMath.SameBytes(fresh, snapshot)) snapshot = fresh;      // Kinds()
                if (labels != null && ReferenceEquals(snapshot, builtKinds) && RM_WallReachMath.SameBytes(depth, builtDepth))
                {
                    skips++;
                }
                else
                {
                    labels = RM_WallReachMath.Label(snapshot, depth, w, h, band, cls);
                    floods++;
                }
                builtKinds = snapshot;
                builtDepth = depth;
                builtGen = gen;
            }
        }

        public static void Run(Action<string, Action> Case)
        {
            // Randomized maps: every step carries GatherData noise (deltas whose square's kind did not move: a haul, a
            // reservation, a thing spawned on open ground), some steps a real kind edit (wall built/mined, door placed) and
            // some a depth edit (a dig). The new policy's labels must equal a fresh full Label of the live state at every
            // step; the old policy flooded every step.
            Case("WallReach_delta_policy_equals_full_scan", () =>
            {
                int cls = RM_WallReachMath.ClassOf(true, true, false, false, false, false);
                int totalSteps = 0, realSteps = 0, newFloods = 0, oldFloods = 0;
                for (int seed = 1; seed <= 40; seed++)
                {
                    var r = new Random(seed * 7919);
                    int w = r.Next(8, 40), h = r.Next(8, 40), n = w * h;
                    byte[] live = RandomKinds(r, n);
                    byte[] depth = r.Next(3) == 0 ? null : RandomDepth(r, n, true);
                    int band = r.Next(0, 4);
                    var sim = new Sim();
                    sim.Rebuild(live, depth, w, h, band, cls);
                    for (int step = 0; step < 60; step++)
                    {
                        totalSteps++;
                        var deltas = new List<int>();
                        int noise = r.Next(0, 12);
                        for (int j = 0; j < noise; j++) deltas.Add(r.Next(n));
                        bool real = false;
                        int roll = r.Next(10);
                        if (roll == 0)
                        {
                            int c = r.Next(n);
                            byte was = live[c];
                            live[c] = KindPool[r.Next(KindPool.Length)];
                            deltas.Add(c);
                            real = live[c] != was;
                        }
                        else if (roll == 1)
                        {
                            // A -> B -> A inside one gather window: the square ends where the snapshot holds it
                            int c = r.Next(n);
                            byte was = live[c];
                            live[c] = was == RM_WallReachMath.Wall ? RM_WallReachMath.Open : RM_WallReachMath.Wall;
                            live[c] = was;
                            deltas.Add(c);
                        }
                        else if (roll == 2 && depth != null)
                        {
                            depth = (byte[])depth.Clone();
                            int c = r.Next(n);
                            byte was = depth[c];
                            depth[c] = (byte)r.Next(0, 6);
                            real = depth[c] != was;
                        }
                        if (real) realSteps++;
                        // judge the deltas (FlushDeltas) against the snapshot the labels came from
                        byte[] snap = sim.snapshot;
                        if (RM_WallReachMath.DeltaMovesKinds(snap, deltas, i => live[i], false))
                        {
                            sim.gen++;
                            sim.bumps++;
                        }
                        bool depthMoved = !RM_WallReachMath.SameBytes(depth, sim.builtDepth);   // ClimbGeneration's own bump
                        if (sim.gen != sim.builtGen || depthMoved)
                        {
                            sim.Rebuild(live, depth, w, h, band, cls);
                        }
                        oldFloods++;   // the old policy: GatherData bumped every step, every step re-flooded
                        var truth = RM_WallReachMath.Label(live, depth, w, h, band, cls);
                        Assert(SameLabels(sim.labels, truth), "seed " + seed + " step " + step + ": the delta policy's labels differ from a full scan");
                    }
                    newFloods += sim.floods - 1;
                }
                Assert(newFloods <= realSteps, "floods only on a real change: " + newFloods + " floods vs " + realSteps + " real changes");
                Assert(oldFloods == totalSteps && newFloods * 4 < oldFloods, "the old policy flooded every step: old " + oldFloods + " new " + newFloods);
                Console.WriteLine("    [excavation-tick] delta policy: " + totalSteps + " gathers, " + realSteps + " real changes, floods old=" + oldFloods + " new=" + newFloods);
            });

            // Per-tick work is bounded: the judge reads at most MaxQueuedDeltas squares; past the cap it is the old eager stale.
            Case("WallReach_delta_judge_bounded", () =>
            {
                var snap = new byte[RM_WallReachMath.MaxQueuedDeltas * 2];
                int reads = 0;
                var many = new List<int>();
                for (int i = 0; i < RM_WallReachMath.MaxQueuedDeltas; i++) many.Add(i);
                Assert(!RM_WallReachMath.DeltaMovesKinds(snap, many, i => { reads++; return snap[i]; }, false), "unchanged squares do not move the labels");
                Assert(reads == RM_WallReachMath.MaxQueuedDeltas, "one read per queued square, got " + reads);
                reads = 0;
                Assert(RM_WallReachMath.DeltaMovesKinds(snap, many, i => { reads++; return snap[i]; }, true) && reads == 0, "overflowed: stale at once, no reads");
                Assert(RM_WallReachMath.DeltaMovesKinds(null, new List<int> { 3 }, i => 0, false), "no snapshot: any delta is a change");
                Assert(!RM_WallReachMath.DeltaMovesKinds(null, new List<int>(), i => 0, false), "no snapshot, no delta: nothing");
                Assert(!RM_WallReachMath.DeltaMovesKinds(snap, null, i => 0, false), "a null list moves nothing");
                Assert(RM_WallReachMath.DeltaMovesKinds(snap, new List<int> { -1 }, i => 0, false)
                    && RM_WallReachMath.DeltaMovesKinds(snap, new List<int> { snap.Length }, i => 0, false), "an out-of-range delta is a change (never trusted)");
                snap[5] = RM_WallReachMath.Wall;
                Assert(RM_WallReachMath.DeltaMovesKinds(snap, new List<int> { 1, 5 }, i => RM_WallReachMath.Open, false), "a wall gone is a change");

                // the 325x325 bisect map: the judge's cost against the flood it saves
                int w = 325, h = 325, n = w * h;
                var r = new Random(325);
                byte[] kinds = RandomKinds(r, n);
                var noise = new List<int>();
                for (int i = 0; i < 64; i++) noise.Add(r.Next(n));
                int cls = RM_WallReachMath.ClassOf(true, true, false, false, false, false);
                RM_WallReachMath.Label(kinds, null, w, h, 0, cls);   // warm
                var sw = Stopwatch.StartNew();
                for (int t = 0; t < 20; t++) RM_WallReachMath.Label(kinds, null, w, h, 0, cls);
                double floodMs = sw.Elapsed.TotalMilliseconds / 20;
                sw.Restart();
                for (int t = 0; t < 2000; t++) RM_WallReachMath.DeltaMovesKinds(kinds, noise, i => kinds[i], false);
                double judgeMs = sw.Elapsed.TotalMilliseconds / 2000;
                sw.Restart();
                byte[] copy = (byte[])kinds.Clone();
                for (int t = 0; t < 200; t++) RM_WallReachMath.SameBytes(kinds, copy);
                double sameMs = sw.Elapsed.TotalMilliseconds / 200;
                Console.WriteLine("    [excavation-tick] 325x325: flood " + floodMs.ToString("0.000") + " ms, 64-delta judge " + judgeMs.ToString("0.0000")
                    + " ms, SameBytes " + sameMs.ToString("0.000") + " ms");
                Assert(judgeMs * 20 < floodMs, "the judge must cost a small fraction of the flood it saves");
            });

            Case("WallReach_content_skip_equals_rebuild", () =>
            {
                Assert(RM_WallReachMath.SameBytes(null, null) && !RM_WallReachMath.SameBytes(new byte[1], null)
                    && !RM_WallReachMath.SameBytes(new byte[2], new byte[3]) && RM_WallReachMath.SameBytes(new byte[] { 1, 2 }, new byte[] { 1, 2 })
                    && !RM_WallReachMath.SameBytes(new byte[] { 1, 2 }, new byte[] { 1, 3 }), "SameBytes");
                Assert(RM_WallReachMath.SameRamps(null, new Dictionary<int, int>()) && RM_WallReachMath.SameRamps(new Dictionary<int, int> { [1] = 2 }, new Dictionary<int, int> { [1] = 2 })
                    && !RM_WallReachMath.SameRamps(new Dictionary<int, int> { [1] = 2 }, new Dictionary<int, int> { [1] = 3 })
                    && !RM_WallReachMath.SameRamps(new Dictionary<int, int> { [1] = 2 }, new Dictionary<int, int> { [2] = 2 })
                    && !RM_WallReachMath.SameRamps(new Dictionary<int, int> { [1] = 2 }, null), "SameRamps");
                // purity: identical inputs (fresh arrays) give identical labels, ramps included
                int cls = RM_WallReachMath.ClassOf(true, true, false, true, false, false);
                for (int seed = 1; seed <= 25; seed++)
                {
                    var r = new Random(seed);
                    int w = r.Next(6, 30), h = r.Next(6, 30), n = w * h;
                    byte[] kinds = RandomKinds(r, n), depth = RandomDepth(r, n, true);
                    var ramps = new Dictionary<int, int>();
                    for (int j = 0; j < 4; j++) ramps[r.Next(n)] = r.Next(n);
                    Func<int, int, bool> joins = (a, b) => (ramps.TryGetValue(a, out int x) && x == b) || (ramps.TryGetValue(b, out int y) && y == a);
                    var ramps2 = new Dictionary<int, int>(ramps);
                    Func<int, int, bool> joins2 = (a, b) => (ramps2.TryGetValue(a, out int x) && x == b) || (ramps2.TryGetValue(b, out int y) && y == a);
                    for (int band = 0; band < 4; band++)
                    {
                        var first = RM_WallReachMath.Label(kinds, depth, w, h, band, cls, joins);
                        var again = RM_WallReachMath.Label((byte[])kinds.Clone(), (byte[])depth.Clone(), w, h, band, cls, joins2);
                        Assert(RM_WallReachMath.SameRamps(ramps, ramps2) && SameLabels(first, again), "seed " + seed + " band " + band + ": identical inputs, different labels");
                    }
                }
                string wr = Src("Superdeep", "RM_WallReach.cs");
                RiverSwitchFlipChecks.Has(wr, @"if \(e\.labels != null && ReferenceEquals\(kinds, e\.builtKinds\) && RM_WallReachMath\.SameBytes\(depth, e\.builtDepth\) && RM_WallReachMath\.SameRamps\(ramps, e\.builtRamps\)\)",
                    "Build skips only on identical kinds, depth and ramps");
                RiverSwitchFlipChecks.Has(wr, @"if \(!RM_WallReachMath\.SameBytes\(kinds, st\.kinds\)\) \{ st\.kinds = kinds; \}", "Kinds keeps the old array when nothing moved");
                RiverSwitchFlipChecks.Has(wr, @"FlushDeltas\(map, st\); if \(st\.entries\.Count == 0\)", "Tick judges the deltas first");
                RiverSwitchFlipChecks.Has(wr, @"FlushDeltas\(map, st\);.{0,140}bool unthrottled = RM_WallReachMath\.PausedUnthrottled", "a paused write moves the stamp before PausedFrame compares it");
                RiverSwitchFlipChecks.Has(wr, @"if \(unjudged\) \{ Interlocked\.Increment\(ref st\.wallGen\); \} Build\(map, st, e, StampOf\(map, st\), null\);", "a first build never labels from an unjudged snapshot");
                RiverSwitchFlipChecks.Has(wr, @"if \(deltas == null \|\| deltas\.Count == 0\) \{ return; \}", "an empty gather moves nothing");
                RiverSwitchFlipChecks.Has(wr, @"kinds\[idx\] == RM_WallReachMath\.Wall && pg\.WalkableFast\(idx\)\) \{ Interlocked\.Increment\(ref st\.wallGen\); Interlocked\.Exchange\(ref st\.forced, 1\);",
                    "a wall breach still forces at once");
            });

            Case("PocketGrid_content_skip_equals_rebuild", () =>
            {
                // RM_PocketGrid.Build: a ClimbGeneration bump whose depth view and ramps come out identical keeps the bands.
                int skips = 0, floods = 0, oldFloods = 0;
                for (int seed = 1; seed <= 30; seed++)
                {
                    var r = new Random(seed * 31);
                    int w = r.Next(8, 40), h = r.Next(8, 40), n = w * h, bands = 4;
                    byte[] depth = RandomDepth(r, n, true);
                    byte[] lastDepth = null;
                    RM_PocketGridMath.Labels[] kept = null;
                    for (int step = 0; step < 40; step++)
                    {
                        byte[] view = (byte[])depth.Clone();   // ViewDepth: a fresh array every rebuild
                        if (r.Next(5) == 0)
                        {
                            depth[r.Next(n)] = (byte)r.Next(0, 6);   // a real dig (or a no-op write: same value)
                            view = (byte[])depth.Clone();
                        }
                        oldFloods += bands;
                        if (kept != null && RM_WallReachMath.SameBytes(view, lastDepth))
                        {
                            skips++;
                        }
                        else
                        {
                            kept = new RM_PocketGridMath.Labels[bands];
                            for (int k = 1; k <= bands; k++) kept[k - 1] = RM_PocketGridMath.Label(view, w, h, k);
                            floods += bands;
                        }
                        lastDepth = view;
                        for (int k = 1; k <= bands; k++)
                        {
                            Assert(SameLabels(kept[k - 1], RM_PocketGridMath.Label(depth, w, h, k)), "seed " + seed + " step " + step + " k " + k + ": skip differs from rebuild");
                        }
                    }
                }
                Assert(skips > 0 && floods < oldFloods, "the skip must fire on identical views");
                Console.WriteLine("    [excavation-tick] pocket grid: band floods old=" + oldFloods + " new=" + floods + " (" + skips + " rebuilds kept)");
                string pg = Src("Superdeep", "RM_PocketGrid.cs");
                RiverSwitchFlipChecks.Has(pg, @"bool sameInput = old != null && old\.Length == BandCount && RM_WallReachMath\.SameBytes\(depth, lastDepth\) && RM_WallReachMath\.SameRamps\(rampPairs, lastRamps\);",
                    "PocketGrid.Build skips only on an identical view and ramps");
                RiverSwitchFlipChecks.Has(pg, @"if \(!sameInput && notifyFlips", "kept bands flip nothing");
            });
        }
    }
}
