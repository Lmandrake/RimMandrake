// LEVELLING_TICK_DIAGNOSE_DRY_GC_SPIKE: the levelling run walk (RM_LevelRunWalk.cs) is the index-space, allocation-free form
// of RM_Levelling.DugBody's old IntVec3 walk. These checks hold it to the old walk's exact answer on random grids: the
// squares it counts, the squares it reaches (a capped walk's queued edge included), the water, the lowest index, the
// deepest square and the depth histogram, across several walks in one cycle (runs are disjoint), with shut sluices,
// two liquids and a small run cap. They also hold the histogram to the old O(sum of depths) loop.
using System;
using System.Collections.Generic;

namespace RimMandrake.FlowWorks.SelfTest
{
    internal static class LevelRunWalkChecks
    {
        private static void Assert(bool ok, string msg)
        {
            if (!ok) throw new Exception(msg);
        }

        /// <summary>A grid as the old walk saw it: depth 0 = undug; water in dL; fluid id; a shut sluice per square.</summary>
        private struct FakeGrid : RM_IRunGrid
        {
            public byte[] depth;
            public long[] water;
            public int[] fluid;
            public bool[] seals;
            public bool Dug(int i) => depth[i] != 0;
            public long Water(int i) => depth[i] == 0 ? 0 : water[i];
            public int Fluid(int i) => fluid[i];
            public bool Seals(int i) => seals[i];
            public int Depth(int i) => depth[i];
        }

        /// <summary>The old DugBody walk, kept literally (N, E, S, W; the cap test on the queue; marks shared in a cycle).</summary>
        private static void OldWalk(FakeGrid g, int w, int h, int start, int[] mark, ref int walkId, int cycleFirst, int maxRun,
            out List<int> processed, out List<int> reached, out long water, out int low, out int maxDepth)
        {
            int[] dx = { 0, 1, 0, -1 }, dz = { 1, 0, -1, 0 };
            int walk = ++walkId;
            mark[start] = walk;
            bool wet = g.Water(start) > 0;
            int fluid = g.Fluid(start);
            var queue = new List<int> { start };
            processed = new List<int>();
            water = 0;
            low = int.MaxValue;
            maxDepth = 0;
            for (int head = 0; head < queue.Count && queue.Count <= maxRun; head++)
            {
                int c = queue[head];
                processed.Add(c);
                maxDepth = Math.Max(maxDepth, g.Depth(c));
                water += g.Water(c);
                low = Math.Min(low, c);
                int x = c % w, z = c / w;
                for (int k = 0; k < 4; k++)
                {
                    int nx = x + dx[k], nz = z + dz[k];
                    if (nx < 0 || nz < 0 || nx >= w || nz >= h) continue;
                    int n = nz * w + nx;
                    if (!g.Dug(n) || mark[n] >= cycleFirst) continue;
                    bool nWet = g.Water(n) > 0;
                    if (nWet != wet || (wet && g.Fluid(n) != fluid) || g.Seals(n)) continue;
                    mark[n] = walk;
                    queue.Add(n);
                }
            }
            reached = queue;
        }

        private static int[] OldHist(List<int> depths, int maxDepth)
        {
            var hist = new int[maxDepth + 1];
            foreach (int d in depths)
                for (int l = 1; l <= d; l++) hist[l]++;
            return hist;
        }

        private static FakeGrid Random(Random r, int w, int h, double dug, double wet, double seal)
        {
            int n = w * h;
            var g = new FakeGrid { depth = new byte[n], water = new long[n], fluid = new int[n], seals = new bool[n] };
            for (int i = 0; i < n; i++)
            {
                if (r.NextDouble() < dug) g.depth[i] = (byte)r.Next(1, r.NextDouble() < 0.05 ? 255 : 12);
                if (r.NextDouble() < wet) g.water[i] = r.Next(1, 4000);
                g.fluid[i] = r.NextDouble() < 0.15 ? 2 : 1;
                g.seals[i] = r.NextDouble() < seal;
            }
            return g;
        }

        public static void Run(Action<string, Action> Case)
        {
            Case("LEVELRUN_walk_matches_old_walk_on_random_grids", () =>
            {
                var r = new Random(1793154265);
                int cases = 0, capped = 0, multi = 0;
                for (int t = 0; t < 400; t++)
                {
                    int w = r.Next(1, 40), h = r.Next(1, 40);
                    FakeGrid g = Random(r, w, h, 0.3 + r.NextDouble() * 0.7, r.NextDouble(), r.NextDouble() * 0.1);
                    int maxRun = r.NextDouble() < 0.3 ? r.Next(1, 30) : 20000;
                    var scratch = new RM_LevelRunScratch();
                    scratch.Prepare(w * h);
                    int[] oldMark = new int[w * h];
                    int oldWalkId = 0;
                    // two cycles: the second must ignore the first cycle's marks
                    for (int cycle = 0; cycle < 2; cycle++)
                    {
                        scratch.BeginCycle();
                        int oldFirst = oldWalkId + 1;
                        int walksThisCycle = 0;
                        for (int s = 0; s < 6; s++)
                        {
                            int start = r.Next(w * h);
                            if (!g.Dug(start) || g.Seals(start)) continue;
                            bool walkedAlready = oldMark[start] >= oldFirst;
                            Assert(walkedAlready == scratch.Reached(start), $"case {t}: reached({start}) {scratch.Reached(start)} vs old {walkedAlready}");
                            if (walkedAlready) continue;
                            OldWalk(g, w, h, start, oldMark, ref oldWalkId, oldFirst, maxRun, out List<int> processed, out List<int> reached,
                                out long water, out int low, out int maxDepth);
                            RM_LevelRun run = RM_LevelRunWalk.Walk(ref g, w, h, start, scratch, maxRun);
                            string tag = $"case {t} cycle {cycle} start {start} ({w}x{h}, cap {maxRun})";
                            Assert(run.Squares == processed.Count, $"{tag}: squares {run.Squares} vs old {processed.Count}");
                            Assert(run.Reached == reached.Count, $"{tag}: reached {run.Reached} vs old {reached.Count}");
                            Assert(run.Water == water, $"{tag}: water {run.Water} vs old {water}");
                            Assert(run.Low == low, $"{tag}: low {run.Low} vs old {low}");
                            Assert(run.MaxDepth == maxDepth, $"{tag}: maxDepth {run.MaxDepth} vs old {maxDepth}");
                            // the queue IS the old walk's, square for square in order (N, E, S, W): a set test let a duplicate
                            // stand in for a missing square, or a reordered walk pass (cs_review 2026-10-28)
                            for (int i = 0; i < reached.Count; i++)
                                Assert(scratch.Queue[i] == reached[i], $"{tag}: queue[{i}] {scratch.Queue[i]} vs old {reached[i]}");
                            var depths = new List<int>();
                            foreach (int c in processed) depths.Add(g.Depth(c));
                            int[] oldHist = OldHist(depths, maxDepth);
                            int[] hist = maxDepth > 0 ? RM_LevelRunWalk.Hist(scratch, maxDepth) : null;
                            if (maxDepth > 0)
                            {
                                Assert(hist.Length == oldHist.Length, $"{tag}: hist length {hist.Length} vs old {oldHist.Length}");
                                for (int l = 0; l < hist.Length; l++)
                                    Assert(hist[l] == oldHist[l], $"{tag}: hist[{l}] {hist[l]} vs old {oldHist[l]}");
                            }
                            if (reached.Count > processed.Count) capped++;
                            walksThisCycle++;
                            cases++;
                        }
                        if (walksThisCycle > 1) multi++;
                    }
                }
                Assert(cases > 300 && capped > 10 && multi > 50, $"too few walks exercised: {cases} walks, {capped} capped, {multi} multi-walk cycles");
                Console.WriteLine($"      {cases} walks, {capped} capped, {multi} cycles with several walks: all equal to the old walk");
            });

            Case("LEVELRUN_walk_allocates_nothing_after_the_first_cycle", () =>
            {
                // the live walk ran on a 325x325 map every 250 ticks; it must not allocate per walk (a GC lands in whoever allocates)
                int w = 325, h = 325;
                var g = new FakeGrid { depth = new byte[w * h], water = new long[w * h], fluid = new int[w * h], seals = new bool[w * h] };
                for (int i = 0; i < w * h; i++) { g.depth[i] = (byte)(1 + i % 9); g.fluid[i] = 1; }
                var scratch = new RM_LevelRunScratch();
                scratch.Prepare(w * h);
                scratch.BeginCycle();
                RM_LevelRunWalk.Walk(ref g, w, h, 0, scratch, 200000);
                long before = GC.GetAllocatedBytesForCurrentThread();
                RM_LevelRun run = default;
                for (int k = 0; k < 5; k++)
                {
                    scratch.BeginCycle();
                    run = RM_LevelRunWalk.Walk(ref g, w, h, 0, scratch, 200000);
                }
                long bytes = GC.GetAllocatedBytesForCurrentThread() - before;
                Assert(run.Squares == w * h, $"walked {run.Squares} of {w * h}");
                Assert(bytes == 0, $"5 full walks of 325x325 allocated {bytes} bytes");
                var sw = System.Diagnostics.Stopwatch.StartNew();
                for (int k = 0; k < 10; k++)
                {
                    scratch.BeginCycle();
                    RM_LevelRunWalk.Walk(ref g, w, h, 0, scratch, 200000);
                }
                Console.WriteLine($"      0 bytes; a 105625-square walk takes {sw.Elapsed.TotalMilliseconds / 10:0.00} ms (CoreCLR)");
            });

            Case("LEVELPOUR_capped_spread_allocates_nothing_and_answers_the_same", () =>
            {
                // live r18: RM_Levelling asks PourRoomDl twice per link per pump cycle; each capped Spread allocated a HashSet and
                // a Queue (2.3 MB per levelling cycle on map1). A capped walk now reuses them, with the same answer every time.
                int w = 325, h = 325;
                Func<int, int, int> nb = (i, d) =>
                {
                    int x = i % w, z = i / w;
                    switch (d)
                    {
                        case 0: return z + 1 < h ? i + w : -1;
                        case 1: return x + 1 < w ? i + 1 : -1;
                        case 2: return z > 0 ? i - w : -1;
                        default: return x > 0 ? i - 1 : -1;
                    }
                };
                Func<int, bool> enter = i => i % 7 != 3;
                Func<int, long> room = i => i % 5 == 0 ? 0 : 1 + i % 3;
                var credits = new List<KeyValuePair<int, long>>(8192);
                long first = RM_LevelPour.Spread(50000, 1L << 40, true, nb, enter, null, room, RM_LevelPour.PourWalkCap, credits, null);
                var firstCredits = new List<KeyValuePair<int, long>>(credits);
                long before = GC.GetAllocatedBytesForCurrentThread();
                long again = 0;
                for (int k = 0; k < 20; k++)
                    again = RM_LevelPour.Spread(50000, 1L << 40, true, nb, enter, null, room, RM_LevelPour.PourWalkCap, credits, null);
                long bytes = GC.GetAllocatedBytesForCurrentThread() - before;
                Assert(first > 0 && again == first, $"placed {first} then {again}");
                Assert(credits.Count == firstCredits.Count, $"credits {firstCredits.Count} then {credits.Count}");
                for (int i = 0; i < credits.Count; i++)
                    Assert(credits[i].Key == firstCredits[i].Key && credits[i].Value == firstCredits[i].Value, $"credit {i} differs");
                Assert(bytes == 0, $"20 capped spreads allocated {bytes} bytes");
                Console.WriteLine($"      20 capped spreads ({credits.Count} credits each): 0 bytes, same answer");
            });
        }
    }
}
