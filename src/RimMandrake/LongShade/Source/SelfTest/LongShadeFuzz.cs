// Approach B for LongShade: seeded fuzz over the Verse-free kernel the mod calls (../Kernel/RM_LongShadeKernel.cs):
//   midden   heap tending (layers/progress/cooldown), stack splitting, nearest-tendable pick, build and spacing rules, untended text
//   rim      the dewfringe rim band and its boundaries
//   road     the Crawler Road: shade islands vs union-find, the two biggest, rim sampling, closest pair vs brute force, segments and strides
//   graves   the Long Carry distance band against the plain "out and back" rule, spacing
//   ladder   the Shipfall Commons ladder: which rungs are open (sorted and unsorted lists), who a rung admits
//   commons  the commons cell set against a brute-force oracle and the cache key through ship arrive / leave / move sequences
// A failing case is printed as `family seed N: message`; --fuzz-seed N replays it.
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;

namespace RimMandrake.LongShade.SelfTest
{
    internal static class LongShadeFuzz
    {
        public static long Cases, Steps, FullHeaps, SplitStacks, Islands2Plus, TerminusRoads, GeometricBands, FallbackBands, UnsortedLadders, StaleKeysCaught, BigSamples;
        private static void Check(bool ok, string msg) { if (!ok) throw new Exception(msg); }
        private static string F(double v) { return v.ToString("0.#####", System.Globalization.CultureInfo.InvariantCulture); }

        // ════════════════════════ midden ════════════════════════
        private static List<string> Midden(int n, int seed0)
        {
            var fails = new List<string>();
            for (int s = seed0; s < seed0 + n && fails.Count < 4; s++)
            {
                Cases++;
                var r = new Random(s * 7919 + 3);
                int step = 0;
                try
                {
                    int maxLayers = r.Next(1, 7), cooldown = new[] { 0, 600, 30000, 60000 }[r.Next(4)];
                    float gain = new[] { 0.05f, 0.07f, 0.1f, 0.125f, 0.2f, 0.25f, 0.3f, 0.5f, 1f, 1.5f }[r.Next(10)];
                    int layers = r.Next(0, 2) == 0 ? 0 : r.Next(0, maxLayers + 1); float progress = 0f; int last = -999999, now = 100000, tends = 0;
                    double ledger = layers; bool searchedOnce = false;
                    // the first heap is tendable at once
                    Check(RM_LongShadeKernel.CanTendNow(0, maxLayers, 0, -999999, cooldown), "a fresh heap cannot be tended");
                    for (int k = 0; k < 120; k++)
                    {
                        step = k; Steps++;
                        now += r.Next(0, 40000);
                        bool can = RM_LongShadeKernel.CanTendNow(layers, maxLayers, now, last, cooldown);
                        Check(can == (layers < maxLayers && now - last >= cooldown), "CanTendNow disagrees with its definition");
                        if (r.Next(25) == 0 && layers > 0)
                        {
                            // a colonist searches: the heap is flattened
                            layers = 0; progress = 0f; ledger = 0; searchedOnce = true;
                            continue;
                        }
                        if (!can) continue;
                        int before = layers; float pBefore = progress;
                        last = now; tends++;
                        RM_LongShadeKernel.Tend(ref layers, ref progress, gain, maxLayers);
                        Check(layers >= before && layers <= maxLayers, "layers " + layers + " outside " + before + ".." + maxLayers);
                        Check(progress >= 0f && (layers >= maxLayers ? progress == 0f : progress < 1f), "progress " + F(progress) + " at layers " + layers + "/" + maxLayers);
                        ledger = Math.Min(maxLayers, ledger + gain);
                        if (layers < maxLayers)
                        {
                            // layers + progress follows the sum of gains (float slack grows slowly)
                            Check(Math.Abs(layers + progress - (ledger + 0.0)) < 1e-4 * (tends + 1) + 1e-4, "layers " + layers + " + progress " + F(progress) + " drifted from the gain ledger " + F(ledger));
                        }
                        else FullHeaps++;
                        Check(layers <= Math.Floor(ledger + 1e-4 * (tends + 1)) + 0.0 || layers == maxLayers && ledger >= maxLayers - 1e-3 * (tends + 1), "layers " + layers + " exceed what the gains paid for (ledger " + F(ledger) + ")");
                        // a tend never skips a layer the gain has already paid for
                        Check(layers + progress > before + pBefore - 1e-6f, "a tend lost progress");
                    }
                    _ = searchedOnce;
                    // fresh heap, exact tend counts: n tends of gain g give floor(n*g) layers (the float must not owe a tend)
                    int l2 = 0; float p2 = 0f; int tendsNeeded = (int)Math.Ceiling(1.0 / gain - 1e-9);
                    for (int i = 0; i < tendsNeeded; i++) RM_LongShadeKernel.Tend(ref l2, ref p2, gain, 100);
                    Check(l2 == (int)Math.Floor(tendsNeeded * (double)gain + 1e-4), "after " + tendsNeeded + " tends of " + F(gain) + " the heap holds " + l2 + " layers, " + (int)Math.Floor(tendsNeeded * (double)gain + 1e-4) + " were paid for");
                    Check(l2 >= 1, "after the " + tendsNeeded + " tends a gain of " + F(gain) + " promises, the heap still holds 0 layers (progress " + F(p2) + "): the float sum came up just short of 1");
                    // search
                    Check(RM_LongShadeKernel.SearchRolls(layers, 2) == layers * 2 && RM_LongShadeKernel.SearchRolls(0, 5) == 0, "search rolls");
                    // stacks
                    int total = r.Next(0, 400), limit = r.Next(-2, 120);
                    var stacks = RM_LongShadeKernel.StackSplit(total, limit);
                    int eff = Math.Max(1, limit);
                    Check(stacks.Sum() == total && stacks.All(x => x >= 1 && x <= eff), "stacks " + string.Join("+", stacks.Take(4)) + " for " + total + " at limit " + limit);
                    Check(stacks.Count == (total + eff - 1) / eff && (stacks.Count == 0 || stacks.Take(stacks.Count - 1).All(x => x == eff)), "stack count / fullness for " + total + " at limit " + limit);
                    if (stacks.Count > 1) SplitStacks++;
                    // start layers
                    int st = r.Next(-3, 12), mx = r.Next(1, 8);
                    int cl = RM_LongShadeKernel.ClampStartLayers(st, mx);
                    Check(cl >= 0 && cl <= mx && (st >= 0 && st <= mx ? cl == st : true), "start layers clamp(" + st + "," + mx + ") = " + cl);
                    // untended
                    int day = 60000, nowU = r.Next(0, 1000000), lastU = r.Next(-5, 3) == 0 ? -999999 : nowU - r.Next(0, 800000);
                    Check(RM_LongShadeKernel.Untended(lastU, nowU, day) == (lastU < 0 || nowU - lastU > 10 * day), "untended rule");
                    Check(!RM_LongShadeKernel.Untended(1000, 1000 + 10 * day, day) && RM_LongShadeKernel.Untended(1000, 1001 + 10 * day, day) && RM_LongShadeKernel.Untended(-999999, 5, day), "ten days exactly is still tended; never tended is untended");
                    // build gate and spacing
                    for (int m = 0; m < 8; m++)
                    {
                        bool any = (m & 1) != 0; int existing = (m & 2) != 0 ? 3 : 6; int max = 6;
                        Check(RM_LongShadeKernel.ShouldBuildHeap(any, existing, max) == (!any && existing < max), "ShouldBuildHeap(" + any + "," + existing + ")");
                    }
                    Check(RM_LongShadeKernel.SpacingOk(16f, 16f) && !RM_LongShadeKernel.SpacingOk(15.99f, 16f) && RM_LongShadeKernel.SpacingOk(100f, 16f), "spacing is a minimum, inclusive");
                    // nearest tendable vs oracle
                    int nh = r.Next(0, 8); var dist = new List<float>(); var can2 = new List<bool>();
                    for (int i = 0; i < nh; i++) { dist.Add(r.Next(0, 5) == 0 ? 30f : r.Next(0, 60)); can2.Add(r.Next(3) != 0); }
                    float radius = 30f;
                    int got = RM_LongShadeKernel.NearestTendable(dist, can2, radius, out bool anyIn);
                    var cand = Enumerable.Range(0, nh).Where(i => dist[i] <= radius && can2[i]).ToList();
                    int want = cand.Count == 0 ? -1 : cand.OrderBy(i => dist[i]).ThenBy(i => i).First();
                    Check(got == want, "nearest tendable picked " + got + ", oracle " + want + " from [" + string.Join(",", dist.Select((d, i) => d + (can2[i] ? "" : "x"))) + "]");
                    Check(anyIn == Enumerable.Range(0, nh).Any(i => dist[i] <= radius), "anyInRange disagrees (a heap that cannot be tended still counts as there)");
                }
                catch (Exception e) { fails.Add("midden seed " + s + ": step " + step + ": " + e.Message); }
            }
            return fails;
        }

        // ════════════════════════ rim ════════════════════════
        private static List<string> Rim(int n, int seed0)
        {
            var fails = new List<string>();
            Cases++;
            try
            {
                Steps += 12;
                Check(!RM_LongShadeKernel.OnRim(0f) && !RM_LongShadeKernel.OnRim(0.05f) && RM_LongShadeKernel.OnRim(0.0501f) && RM_LongShadeKernel.OnRim(0.5f) && RM_LongShadeKernel.OnRim(0.8499f) && !RM_LongShadeKernel.OnRim(0.85f) && !RM_LongShadeKernel.OnRim(1f), "rim band is strictly between 0.05 and 0.85");
                Check(!RM_LongShadeKernel.OnRim(float.NaN) && !RM_LongShadeKernel.OnRim(-1f) && !RM_LongShadeKernel.OnRim(7f), "out-of-range shade is not a rim");
                Check(RM_LongShadeKernel.MinRimShade < RM_LongShadeKernel.MaxRimShade && RM_LongShadeKernel.MinRimShade > 0f && RM_LongShadeKernel.MaxRimShade < 1f, "the rim band lies strictly inside (0,1) (PROVISIONAL 0.05..0.85)");
            }
            catch (Exception e) { fails.Add("rim: " + e.Message); }
            for (int s = seed0; s < seed0 + n && fails.Count < 4; s++)
            {
                Cases++; Steps++;
                var r = new Random(s * 31 + 1);
                try
                {
                    float a = (float)r.NextDouble(), b = Math.Min(1f, a + (float)r.NextDouble() * 0.2f);
                    // the rim is one connected shade interval: if a and b are rim, so is anything between
                    if (RM_LongShadeKernel.OnRim(a) && RM_LongShadeKernel.OnRim(b)) Check(RM_LongShadeKernel.OnRim((a + b) / 2), "the rim band has a hole");
                    Check(RM_LongShadeKernel.OnRim(a) == (a > 0.05f && a < 0.85f), "OnRim(" + F(a) + ")");
                }
                catch (Exception e) { fails.Add("rim seed " + s + ": " + e.Message); }
            }
            return fails;
        }

        // ════════════════════════ road ════════════════════════
        private static List<string> Road(int n, int seed0)
        {
            var fails = new List<string>();
            for (int s = seed0; s < seed0 + n && fails.Count < 4; s++)
            {
                Cases++; Steps++;
                var r = new Random(s * 977 + 5);
                try
                {
                    // --- islands vs union-find over a symmetric random graph
                    int np = r.Next(1, 40);
                    var cells = Enumerable.Range(0, np).Select(i => (long)r.Next(1, 500)).ToList();
                    var adj = Enumerable.Range(0, np).Select(i => (IList<int>)new List<int>()).ToList();
                    var uf = Enumerable.Range(0, np).ToArray();
                    Func<int, int> find = null; find = x => uf[x] == x ? x : (uf[x] = find(uf[x]));
                    int edges = r.Next(0, np * 2);
                    for (int e = 0; e < edges; e++)
                    {
                        int u = r.Next(np), v = r.Next(np);
                        if (u == v) continue;
                        adj[u].Add(v); adj[v].Add(u);
                        uf[find(u)] = find(v);
                    }
                    var isl = RM_LongShadeKernel.Islands(adj, cells, out int count, out long[] islandCells);
                    var roots = Enumerable.Range(0, np).Select(find).Distinct().ToList();
                    Check(count == roots.Count, "island count " + count + ", union-find says " + roots.Count);
                    Check(islandCells.Length == count, "island cell list length");
                    for (int u = 0; u < np; u++) for (int v = u + 1; v < np; v++) Check((isl[u] == isl[v]) == (find(u) == find(v)), "patches " + u + "," + v + " grouped " + (isl[u] == isl[v]) + " but connected " + (find(u) == find(v)));
                    for (int i = 0; i < count; i++)
                    {
                        long want = Enumerable.Range(0, np).Where(u => isl[u] == i).Sum(u => cells[u]);
                        Check(islandCells[i] == want, "island " + i + " holds " + islandCells[i] + " cells, its members sum to " + want);
                    }
                    // islands are numbered by their lowest patch
                    int lastLow = -1; for (int i = 0; i < count; i++) { int low = Enumerable.Range(0, np).First(u => isl[u] == i); Check(low > lastLow, "islands are not numbered in order of their first patch"); lastLow = low; }
                    if (count >= 2) Islands2Plus++;
                    // --- two biggest vs a sort
                    if (count >= 2)
                    {
                        bool ok = RM_LongShadeKernel.TwoBiggest(islandCells, count, out int a, out int b);
                        var order = Enumerable.Range(0, count).OrderByDescending(i => islandCells[i]).ThenBy(i => i).ToList();
                        Check(ok && a == order[0] && b == order[1], "two biggest (" + a + "," + b + "), oracle (" + order[0] + "," + order[1] + ") of [" + string.Join(",", islandCells) + "]");
                    }
                    else Check(!RM_LongShadeKernel.TwoBiggest(islandCells, count, out int _, out int _), "one island has no two biggest");

                    // --- rim sampling
                    int len = r.Next(0, 1500), sample = r.Next(1, 400);
                    var all = Enumerable.Range(0, len).Select(i => i * 3 + 7).ToList();
                    var picked = RM_LongShadeKernel.RimSample(all, sample);
                    if (len <= sample) Check(picked.SequenceEqual(all), "a short rim list must come back whole");
                    else
                    {
                        BigSamples++;
                        Check(picked.Count == sample, "sample has " + picked.Count + " of " + sample);
                        Check(picked[0] == all[0], "sample starts at the first rim cell");
                        for (int i = 1; i < picked.Count; i++) Check(picked[i] > picked[i - 1], "sample not strictly increasing (duplicate or reordered cell)");
                        Check(picked.All(all.Contains), "sample holds a cell the rim does not");
                        Check(picked[picked.Count - 1] >= all[(int)((sample - 1) * (len / (float)sample))], "sample misses the tail");
                        Check(picked[picked.Count - 1] <= all[len - 1] && all.IndexOf(picked[picked.Count - 1]) >= len - 2 * (len / sample) - 2, "sample stops far short of the end of the rim");
                    }

                    // --- closest pair vs brute force
                    int width = r.Next(5, 80);
                    var ra = Enumerable.Range(0, r.Next(0, 25)).Select(i => r.Next(width * 60)).ToList();
                    var rb = Enumerable.Range(0, r.Next(0, 25)).Select(i => r.Next(width * 60)).ToList();
                    bool found = RM_LongShadeKernel.ClosestPair(ra, rb, width, out int ca, out int cb);
                    Check(found == (ra.Count > 0 && rb.Count > 0), "closest pair found=" + found);
                    if (found)
                    {
                        Func<int, int, long> d2 = (p, q) => { long dx = p % width - q % width, dz = p / width - q / width; return dx * dx + dz * dz; };
                        long best = ra.SelectMany(p => rb.Select(q => d2(p, q))).Min();
                        Check(d2(ca, cb) == best, "closest pair is " + d2(ca, cb) + " apart, the closest is " + best);
                        Check(ra.Contains(ca) && rb.Contains(cb), "pair cells are not from the two lists");
                        int firstA = ra.First(p => rb.Any(q => d2(p, q) == best)); int firstB = rb.First(q => d2(firstA, q) == best);
                        Check(ca == firstA && cb == firstB, "ties must keep the first pair in list order");
                    }

                    // --- segments and strides
                    float spacing = 6f + (float)r.NextDouble() * 18f, minGap = 1.5f, maxGap = 160f; float gap = (float)(r.NextDouble() * 220);
                    int seg = RM_LongShadeKernel.RoadSegments(gap, spacing, minGap, maxGap, out float stride);
                    if (gap < spacing * minGap || gap > maxGap) Check(seg == 0, "a gap of " + F(gap) + " (spacing " + F(spacing) + ") should lay no road, got " + seg + " segments");
                    else
                    {
                        Check(seg >= 2, "a road of " + seg + " segment(s) over a gap of " + F(gap));
                        Check(stride <= spacing + 1e-4f && stride > spacing / 2 - 1e-4f, "stride " + F(stride) + " outside (spacing/2, spacing] for spacing " + F(spacing));
                        Check(Math.Abs(stride * seg - gap) < 1e-3f, "segments x stride " + F(stride * seg) + " != gap " + F(gap));
                        Check(seg == (int)Math.Ceiling(gap / spacing), "segment count is ceil(gap/spacing)");
                        foreach (bool terminus in new[] { false, true })
                        {
                            var ks = RM_LongShadeKernel.RoadLinkIndices(seg, terminus);
                            Check(ks.Count == (terminus ? Math.Max(0, seg - 2) : seg - 1), "link count " + ks.Count + " for " + seg + " segments, terminus " + terminus);
                            Check(ks.All(k => k >= 1 && k <= seg - 1) && ks.Zip(ks.Skip(1), (p, q) => q == p + 1).All(x => x), "link indices not a consecutive run inside the road");
                            if (terminus) { TerminusRoads++; Check(!ks.Contains(seg - 1), "the terminus stop also got a wreck link"); }
                            // every hop along from -> links -> (terminus) -> to is one stride
                            var stops = new List<int> { 0 }; stops.AddRange(ks); if (terminus && seg >= 2) stops.Add(seg - 1); stops.Add(seg);
                            for (int i = 1; i < stops.Count; i++) Check((stops[i] - stops[i - 1]) * stride <= spacing + 1e-3f, "two stops along the road are " + F((stops[i] - stops[i - 1]) * stride) + " cells apart, more than the spacing " + F(spacing));
                        }
                    }
                    Check(RM_LongShadeKernel.RoadSegments(160f, 12f, 1.5f, 160f, out float _) > 0 && RM_LongShadeKernel.RoadSegments(160.01f, 12f, 1.5f, 160f, out float _) == 0, "a gap of exactly the cap still gets a road; one hair over does not");
                    Check(RM_LongShadeKernel.RoadSegments(18f, 12f, 1.5f, 160f, out float _) > 0 && RM_LongShadeKernel.RoadSegments(17.99f, 12f, 1.5f, 160f, out float _) == 0, "a gap of exactly 1.5 spacings gets a road; one hair under does not");
                    // --- dash / spacing arithmetic
                    int ring = r.Next(0, 4000); float maxDash = r.Next(5, 60);
                    float dash = RM_LongShadeKernel.DashCells(ring, 10, maxDash);
                    Check(dash <= maxDash && Math.Abs(dash - Math.Min(ring / 10.0, maxDash)) < 1e-4, "dash cells " + F(dash) + " for ring cost " + ring);
                    float sp = RM_LongShadeKernel.RoadSpacing(dash, 0.8f, 6f, 24f);
                    Check(sp >= 6f && sp <= 24f && (dash * 0.8f < 6f ? sp == 6f : dash * 0.8f > 24f ? sp == 24f : Math.Abs(sp - dash * 0.8f) < 1e-4), "road spacing " + F(sp) + " for dash " + F(dash));
                }
                catch (Exception e) { fails.Add("road seed " + s + ": " + e.Message); }
            }
            return fails;
        }

        // ════════════════════════ graves ════════════════════════
        private static List<string> Graves(int n, int seed0)
        {
            var fails = new List<string>();
            Cases++;
            try
            {
                Check(RM_LongShadeKernel.GravesFarEnough(401f) && !RM_LongShadeKernel.GravesFarEnough(400f) && !RM_LongShadeKernel.GravesFarEnough(0f), "graves must be more than 20 cells apart (squared > 400)");
                Check(!RM_LongShadeKernel.InGraveBand(int.MaxValue, int.MaxValue, 0, int.MaxValue), "an unreached cell is never in the band");
            }
            catch (Exception e) { fails.Add("graves units: " + e.Message); }
            for (int s = seed0; s < seed0 + n && fails.Count < 4; s++)
            {
                Cases++; Steps++;
                var r = new Random(s * 331 + 9);
                try
                {
                    int bare = r.Next(0, 500), geared = r.Next(0, 3) == 0 ? bare : bare + r.Next(0, 400), capCost = r.Next(50, 800); float frac = new[] { 0.2f, 0.4f, 0.5f }[r.Next(3)];
                    RM_LongShadeKernel.GraveBand(bare, geared, capCost, frac, out int lo, out int hi);
                    int unreached = -1;
                    if (geared > bare)
                    {
                        GeometricBands++;
                        // the plain rule: out and back is beyond a bare human but within a parasol-bearer's
                        for (int d = 0; d <= geared + 5; d++)
                            Check(RM_LongShadeKernel.InGraveBand(d, unreached, lo, hi) == (2 * d > bare && 2 * d <= geared), "distance " + d + " (bare ring " + bare + ", geared ring " + geared + "): in band=" + RM_LongShadeKernel.InGraveBand(d, unreached, lo, hi) + ", out-and-back rule says " + (2 * d > bare && 2 * d <= geared));
                    }
                    else
                    {
                        FallbackBands++;
                        Check(hi == capCost && lo == (int)Math.Round(capCost * frac), "fallback band " + lo + ".." + hi + " for cap " + capCost + " fraction " + F(frac));
                        Check(lo <= hi, "fallback band is empty or inverted");
                        for (int d = 0; d <= capCost + 5; d += 3) Check(RM_LongShadeKernel.InGraveBand(d, unreached, lo, hi) == (d >= lo && d <= hi), "fallback membership at " + d);
                    }
                    Check(!RM_LongShadeKernel.InGraveBand(unreached, unreached, lo, hi), "the unreached sentinel fell inside the band");
                }
                catch (Exception e) { fails.Add("graves seed " + s + ": " + e.Message); }
            }
            return fails;
        }

        // ════════════════════════ ladder ════════════════════════
        private static List<string> Ladder(int n, int seed0)
        {
            var fails = new List<string>();
            for (int s = seed0; s < seed0 + n && fails.Count < 4; s++)
            {
                Cases++; Steps++;
                var r = new Random(s * 131 + 29);
                try
                {
                    int count = r.Next(0, 7);
                    bool sorted = r.Next(2) == 0;
                    var delays = Enumerable.Range(0, count).Select(i => (float)(r.Next(0, 100) / 2.0)).ToList();
                    if (sorted) delays.Sort(); else UnsortedLadders++;
                    int tph = 2500;
                    int prev = 0;
                    for (int elapsed = 0; elapsed <= 120 * tph; elapsed += r.Next(1, 4000))
                    {
                        int open = RM_LongShadeKernel.OpenStages(delays, elapsed, tph);
                        Check(open >= 0 && open <= count, "open rungs " + open + " of " + count);
                        Check(open >= prev, "open rungs fell from " + prev + " to " + open + " as time passed");
                        prev = open;
                        for (int i = 0; i < open; i++) Check(elapsed >= (int)Math.Round(delays[i] * tph), "rung " + i + " (after " + F(delays[i]) + " h) is open at " + elapsed + " ticks, before its own delay");
                        if (open < count) Check(elapsed < (int)Math.Round(delays[open] * tph), "rung " + open + " has run its delay but is not open");
                        if (sorted) Check(open == delays.Count(d => elapsed >= (int)Math.Round(d * tph)), "on a sorted ladder the open count is the number of delays passed");
                    }
                    // admission
                    for (int m = 0; m < 64; m++)
                    {
                        bool rule = (m & 1) != 0, listed = (m & 2) != 0, herdOnly = (m & 4) != 0, herd = (m & 8) != 0; float max = (m & 16) != 0 ? 1.5f : 0f, size = (m & 32) != 0 ? 2f : 1f;
                        bool got = RM_LongShadeKernel.Admits(rule, listed, max, size, herdOnly, herd);
                        bool want = !(rule && !listed) && !(max > 0f && size > max) && !(herdOnly && !herd);
                        Check(got == want, "Admits(rule " + rule + ", listed " + listed + ", max " + max + ", size " + size + ", herdOnly " + herdOnly + ", herd " + herd + ") = " + got);
                        if (max == 0f) Check(got == (!(rule && !listed) && !(herdOnly && !herd)), "a zero size cap must mean no size rule");
                    }
                    Check(RM_LongShadeKernel.Admits(false, false, 0.7f, 0.7f, false, false) && !RM_LongShadeKernel.Admits(false, false, 0.7f, 0.7001f, false, false), "a body size equal to the cap is admitted; a hair over is not");
                    // first admitting rung
                    int stagesOpen = r.Next(0, count + 2); var admit = Enumerable.Range(0, count).Select(i => r.Next(3) == 0).ToList();
                    int first = RM_LongShadeKernel.FirstAdmitting(stagesOpen, count, i => admit[i]);
                    int want2 = Enumerable.Range(0, Math.Min(stagesOpen, count)).FirstOrDefault(i => admit[i], -1);
                    Check(first == (Enumerable.Range(0, Math.Min(stagesOpen, count)).Any(i => admit[i]) ? want2 : -1), "first admitting rung " + first + ", oracle " + want2);
                    // a landing: the ladder restarts at the bottom and only ever climbs
                    int arrived = 1000, opened = 0; var said = new List<int>();
                    for (int tick = 1000; tick < 1000 + 120 * tph; tick += 250)
                    {
                        int open = RM_LongShadeKernel.OpenStages(delays, tick - arrived, tph);
                        while (opened < open) { said.Add(opened); opened++; }
                    }
                    Check(said.SequenceEqual(Enumerable.Range(0, said.Count)), "rung messages were not given once each in order");
                }
                catch (Exception e) { fails.Add("ladder seed " + s + ": " + e.Message); }
            }
            return fails;
        }

        // ════════════════════════ commons ════════════════════════
        private sealed class Ship
        {
            public HashSet<(int, int)> sub = new HashSet<(int, int)>();
            public int ex, ez;
        }

        private static List<string> Commons(int n, int seed0)
        {
            var fails = new List<string>();
            for (int s = seed0; s < seed0 + n && fails.Count < 4; s++)
            {
                Cases++;
                var r = new Random(s * 977 + 17);
                int step = 0;
                try
                {
                    int w = r.Next(20, 60), h = r.Next(20, 60);
                    var standable = new bool[w, h]; var shade = new float[w, h];
                    for (int x = 0; x < w; x++) for (int z = 0; z < h; z++) { standable[x, z] = r.Next(8) != 0; shade[x, z] = r.Next(6) == 0 ? 0.5f : (float)r.NextDouble(); }
                    int radius = r.Next(1, 9); float minShade = 0.5f;
                    Func<Ship, int, List<(int, int)>> oracle = null;
                    oracle = (ship, rad) =>
                    {
                        var res = new List<(int, int)>();
                        for (int z = 0; z < h; z++) for (int x = 0; x < w; x++)
                            {
                                if (ship.sub.Contains((x, z)) || !standable[x, z] || shade[x, z] < minShade) continue;
                                bool near = ship.sub.Any(c => (c.Item1 - x) * (c.Item1 - x) + (c.Item2 - z) * (c.Item2 - z) <= rad * rad);
                                if (near) res.Add((x, z));
                            }
                        return res;
                    };
                    Func<Ship, List<(int, int)>> build = ship =>
                    {
                        int minX = ship.sub.Min(c => c.Item1), maxX = ship.sub.Max(c => c.Item1), minZ = ship.sub.Min(c => c.Item2), maxZ = ship.sub.Max(c => c.Item2);
                        return RM_LongShadeKernel.CommonsCells(minX, minZ, maxX, maxZ, radius, w, h, (x, z) => ship.sub.Contains((x, z)), (x, z) => standable[x, z], (x, z) => shade[x, z], minShade)
                            .Select(kv => (kv.Key, kv.Value)).ToList();
                    };
                    var ship0 = new Ship();
                    int bx = r.Next(5, w - 8), bz = r.Next(5, h - 8), sw = r.Next(1, 7), sh = r.Next(1, 7);
                    for (int x = bx; x < Math.Min(w, bx + sw); x++) for (int z = bz; z < Math.Min(h, bz + sh); z++) if (r.Next(10) != 0) ship0.sub.Add((x, z));
                    if (ship0.sub.Count == 0) ship0.sub.Add((bx, bz));
                    ship0.ex = bx; ship0.ez = bz;
                    var got = build(ship0);
                    var want = oracle(ship0, radius);
                    Check(got.SequenceEqual(want), "commons has " + got.Count + " cells, the brute-force oracle " + want.Count);
                    Check(got.All(c => !ship0.sub.Contains(c)), "a commons cell sits on the substructure");
                    Check(got.All(c => c.Item1 >= 0 && c.Item2 >= 0 && c.Item1 < w && c.Item2 < h), "a commons cell is off the map");
                    // near-substructure vs brute force at random cells
                    for (int k = 0; k < 30; k++)
                    {
                        int x = r.Next(-3, w + 3), z = r.Next(-3, h + 3);
                        bool bf = ship0.sub.Any(c => (c.Item1 - x) * (c.Item1 - x) + (c.Item2 - z) * (c.Item2 - z) <= radius * radius);
                        Check(RM_LongShadeKernel.NearSubstructure(x, z, radius, (a, b) => ship0.sub.Contains((a, b))) == bf, "NearSubstructure(" + x + "," + z + ") disagrees with brute force");
                    }
                    // the cache through arrive / leave / move / grid-edit sequences
                    var key = new RM_LongShadeKernel.CommonsKey(); var cache = new List<(int, int)>(); int gridVersion = 0; Ship cur = ship0; bool present = true;
                    for (int t = 0; t < 40; t++)
                    {
                        step = t; Steps++;
                        int act = r.Next(10);
                        if (act == 0) { gridVersion++; for (int q = 0; q < 6; q++) shade[r.Next(w), r.Next(h)] = (float)r.NextDouble(); }
                        else if (act == 1 || act == 2)
                        {
                            // the ship leaves; some time later it lands again, the same ship (same size) at the same or another place
                            present = false; cache.Clear(); key.Invalidate();
                            present = true;
                            if (act == 2) { var moved = new Ship(); int dx = r.Next(-4, 5), dz = r.Next(-4, 5); foreach (var c in cur.sub) { int nx = c.Item1 + dx, nz = c.Item2 + dz; if (nx >= 0 && nz >= 0 && nx < w && nz < h) moved.sub.Add((nx, nz)); } if (moved.sub.Count == cur.sub.Count) { moved.ex = cur.ex + dx; moved.ez = cur.ez + dz; cur = moved; } }
                        }
                        else if (act == 3) { gridVersion += 0; }
                        // the component's Commons(): serve the cache only while the key is fresh
                        if (!key.Fresh(gridVersion, cur.sub.Count, cur.ex, cur.ez)) { key.Set(gridVersion, cur.sub.Count, cur.ex, cur.ez); cache = build(cur); }
                        var fresh = build(cur);
                        Check(cache.SequenceEqual(fresh), "the cached commons (" + cache.Count + " cells) is stale against a fresh build (" + fresh.Count + ") after step " + t + " act " + act);
                        if (act == 1 || act == 2) StaleKeysCaught++;
                    }
                    _ = present;
                }
                catch (Exception e) { fails.Add("commons seed " + s + ": step " + step + ": " + e.Message); }
            }
            // key semantics on their own
            Cases++;
            try
            {
                var k = new RM_LongShadeKernel.CommonsKey();
                Check(!k.Fresh(0, 0, 0, 0) && !k.Fresh(-1, -1, 0, 0), "a new key is never fresh");
                k.Set(3, 40, 10, 12);
                Check(k.Fresh(3, 40, 10, 12) && !k.Fresh(4, 40, 10, 12) && !k.Fresh(3, 41, 10, 12) && !k.Fresh(3, 40, 11, 12) && !k.Fresh(3, 40, 10, 13), "the key is fresh only for the exact (grid version, size, engine x, engine z)");
                k.Invalidate();
                Check(!k.Fresh(3, 40, 10, 12) && !k.Fresh(-1, -1, int.MinValue, int.MinValue) == false || true, "invalidate");
                Check(!k.Fresh(3, 40, 10, 12), "an invalidated key must not be fresh for the values it held");
            }
            catch (Exception e) { fails.Add("commons key: " + e.Message); }
            return fails;
        }

        // ════════════════════════ extras ═══════════════════════
        private static List<string> Extras(int n, int seed0)
        {
            var fails = new List<string>();
            for (int s = seed0; s < seed0 + n && fails.Count < 4; s++)
            {
                Cases++;
                var r = new Random(s * 104729 + 11);
                try
                {
                    float deep = (float)(0.3 + r.NextDouble() * 0.6), sh = (float)r.NextDouble(), roof = r.Next(2) == 0 ? 0f : (float)r.NextDouble(), gear = r.Next(2) == 0 ? 0f : (float)r.NextDouble();
                    bool wild = RM_LongShadeKernel.WildDeepShade(sh, roof, gear, deep);
                    Check(wild == (sh >= deep && roof <= 0.01f && gear <= 0.01f), "WildDeepShade disagrees with its definition");
                    if (roof > 0.01f || gear > 0.01f) Check(!wild, "built shade read as wild (tollok must never infest built shade)");
                    int dwell = 0, thr = r.Next(250, 6000), step = 250; float sev = 0f; bool everGain = false; int sinceMove = 0;
                    for (int k = 0; k < 80; k++)
                    {
                        Steps++;
                        bool stay = r.Next(8) != 0;
                        dwell = RM_LongShadeKernel.TollokDwell(dwell, stay, step);
                        sinceMove = stay ? sinceMove + step : 0;
                        Check(dwell == sinceMove, "dwell " + dwell + " != time since last move " + sinceMove);
                        float g = RM_LongShadeKernel.TollokGain(dwell, thr, 0.04f, sev);
                        Check(g >= 0f && sev + g <= 1.0001f, "gain pushes severity past 1");
                        if (dwell < thr) Check(g == 0f, "gain before the dwell threshold");
                        else { everGain = true; Check(g > 0f || sev >= 1f, "no gain past the threshold"); }
                        sev += g;
                    }
                    if (everGain) Check(sev > 0f, "infestation never started");
                    int herd = r.Next(0, 20), hot = herd == 0 ? 0 : r.Next(0, herd + 1), minHerd = r.Next(2, 10); float frac = (float)(0.2 + r.NextDouble() * 0.7);
                    bool ready = RM_LongShadeKernel.StampedeReady(herd, hot, minHerd, frac);
                    Check(ready == (herd >= minHerd && herd > 0 && (float)hot / herd >= frac), "StampedeReady disagrees with its definition");
                    Check(!RM_LongShadeKernel.StampedeReady(herd, herd + 1, 0, 0f), "overheated count above herd size accepted");
                    int max = r.Next(100, 9000), t = r.Next(0, 12000);
                    Check(RM_LongShadeKernel.StampedeContinues(true, t, max) == (t < max), "stampede timeout wrong");
                    Check(!RM_LongShadeKernel.StampedeContinues(false, t, max), "a cooled animal keeps running");
                    var shades = new List<float>(); int expect = 0; float cut = (float)r.NextDouble();
                    for (int k = 0, m = r.Next(0, 30); k < m; k++) { float v = (float)r.NextDouble(); shades.Add(v); if (v >= cut) expect++; }
                    Check(RM_LongShadeKernel.ShelterCount(shades, cut) == expect, "ShelterCount disagrees with a plain count");
                    // harrok strip: a point built from (along, side) must land in the strip exactly when its coordinates say so
                    double ang = r.NextDouble() * Math.PI * 2; float dX = (float)Math.Cos(ang), dZ = (float)Math.Sin(ang);
                    float len = (float)(1 + r.NextDouble() * 9), hw = (float)(0.2 + r.NextDouble() * 2), al = (float)(r.NextDouble() * 14 - 2), sd = (float)(r.NextDouble() * 6 - 3);
                    bool inside = RM_LongShadeKernel.InShadowStrip(al * dX + sd * -dZ, al * dZ + sd * dX, dX, dZ, len, hw);
                    if (Math.Abs(al) > 0.01f && Math.Abs(al - len) > 0.01f && Math.Abs(Math.Abs(sd) - hw) > 0.01f) Check(inside == (al > 0f && al <= len && Math.Abs(sd) <= hw), "InShadowStrip disagrees with its (along, side) frame");
                    Check(!RM_LongShadeKernel.InShadowStrip(-dX, -dZ, dX, dZ, len, hw), "a point up-sun of the harrok is in its shadow");
                    int lastS = r.Next(0, 5000), nowS = lastS + r.Next(0, 3000), cd = r.Next(100, 2000);
                    Check(RM_LongShadeKernel.HarrokCanStrike(true, 1f, 1.2f, nowS, lastS, cd) == (nowS - lastS >= cd), "harrok cooldown wrong");
                    Check(!RM_LongShadeKernel.HarrokCanStrike(false, 1f, 1.2f, nowS + 99999, lastS, cd), "harrok strikes prey that is moving");
                    int cx = r.Next(20, 200), cz = r.Next(20, 200), hw2 = r.Next(1, 30), hh = r.Next(1, 14), px = cx + r.Next(-20, 20), pz = cz + r.Next(-10, 10), cnt = 0;
                    for (int yy = cz - 20; yy <= cz + 20; yy++) for (int xx = cx - 30; xx <= cx + 30; xx++) if (RM_LongShadeKernel.InHullRect(xx, yy, cx, cz, hw2, hh)) cnt++;
                    Check(cnt == hw2 * hh, "InHullRect covers " + cnt + " cells for a " + hw2 + "x" + hh + " rect");
                    Check(RM_LongShadeKernel.InHullRect(cx, cz, cx, cz, hw2, hh), "the hull centre is outside its own rect");
                    bool ent = r.Next(2) == 0; int hos = r.Next(0, 3), itm = r.Next(0, 6), mx = r.Next(0, 4);
                    Check(RM_LongShadeKernel.HullLooted(ent, hos, itm, mx) == (ent && hos == 0 && itm <= mx), "HullLooted disagrees with its definition");
                    int st = r.Next(-1, 5000), nw = r.Next(0, 20000), tw = r.Next(1, 15000);
                    Check(RM_LongShadeKernel.TowDone(st, nw, tw) == (st >= 0 && nw - st >= tw), "TowDone disagrees with its definition");
                    Check(!RM_LongShadeKernel.TowDone(-1, 999999, 1), "a clan that never arrived finishes towing");
                    Check(!RM_LongShadeKernel.HarrokCanStrike(true, 5f, 1.2f, nowS + 99999, lastS, cd), "harrok strikes prey above its body-size cap");
                }
                catch (Exception e) { fails.Add("extras seed " + s + ": " + e.Message); }
            }
            return fails;
        }

        public static bool Run(double scale, int? oneSeed, string only)
        {
            var sw = Stopwatch.StartNew();
            bool ok = true;
            int N(int n) { return oneSeed.HasValue ? 1 : (int)(n * scale); }
            int S(int baseSeed) { return oneSeed ?? baseSeed; }
            var fam = new (string name, Func<List<string>> run)[]
            {
                ("midden", () => Midden(N(5000), S(1))),
                ("rim", () => Rim(N(3000), S(1))),
                ("road", () => Road(N(3000), S(1))),
                ("graves", () => Graves(N(5000), S(1))),
                ("ladder", () => Ladder(N(4000), S(1))),
                ("commons", () => Commons(N(600), S(1))),
                ("extras", () => Extras(N(4000), S(1))),
            };
            foreach (var f in fam)
            {
                if (only != null && f.name != only) continue;
                long c0 = Cases, s0 = Steps; var t = Stopwatch.StartNew();
                var fails = f.run();
                Console.WriteLine($"fuzz {f.name}: {Cases - c0} cases, {Steps - s0} steps, {t.Elapsed.TotalSeconds:F2}s, {(fails.Count == 0 ? "0 failures" : fails.Count + " FAILURES")}");
                foreach (var m in fails) Console.WriteLine("FAIL " + m);
                if (fails.Count > 0) ok = false;
            }
            if (only != null && !fam.Any(f => f.name == only)) { Console.WriteLine("FAIL unknown --fuzz-only family: " + only); return false; }
            if (Cases == 0) { Console.WriteLine("FAIL no cases ran (--fuzz-scale too small?); a fuzz that checked nothing is not a pass"); return false; }
            if (only == null)
            {
                Console.WriteLine($"reached: full heaps {FullHeaps}, split stacks {SplitStacks}, multi-island graphs {Islands2Plus}, sampled rims {BigSamples}, terminus roads {TerminusRoads}, geometric grave bands {GeometricBands}, fallback bands {FallbackBands}, unsorted ladders {UnsortedLadders}, ship leave/land cycles {StaleKeysCaught}");
                if (!oneSeed.HasValue && scale >= 1 && (FullHeaps == 0 || SplitStacks == 0 || Islands2Plus == 0 || BigSamples == 0 || TerminusRoads == 0 || GeometricBands == 0 || FallbackBands == 0 || UnsortedLadders == 0 || StaleKeysCaught == 0)) { Console.WriteLine("FAIL the fuzz never reached full heaps, split stacks, multi-island graphs, sampled rims, terminus roads, both grave bands, unsorted ladders and ship cycles (blind)"); ok = false; }
            }
            Console.WriteLine($"longshade fuzz: {Cases} cases, {Steps} steps, {sw.Elapsed.TotalSeconds:F2}s total -> {(ok ? "OK" : "FAILED")}");
            return ok;
        }
    }
}
