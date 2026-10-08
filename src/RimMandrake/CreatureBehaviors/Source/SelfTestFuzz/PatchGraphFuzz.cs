// CreatureBehaviors fuzz, families "patch" and "dash": seeded fuzz over the production RM_ShadePatchGraph / RM_DashMath / RM_WildLeaveMath.
//   patch  random shade / walkable grids against independent oracles: 8-connected components with the minimum-size rule, the rim, the capped
//          multi-source distance field (Bellman-Ford, not Dial's buckets), nearest-shade consistency, edge symmetry and bounds, the
//          reachable-with-return ring against a brute-force scan
//   dash   heat severity floor, tolerated ticks, dash range clamps, the wild-leave precedence table
// A failing case is printed as `family seed N: message | detail`; --fuzz-seed N replays it.
using System;
using System.Collections.Generic;
using System.Linq;

namespace RimMandrake.CreatureBehaviors.FuzzSelfTest
{
    internal static class PatchGraphFuzz
    {
        public static long Patches, Rims, Edges, Capped, Flecks, Rings;
        private static void Check(bool ok, string msg) { if (!ok) throw new Exception(msg); }

        private static List<string> Loop(string name, int n, int seed, Action<Random> one)
        {
            var fails = new List<string>();
            for (int i = 0; i < n; i++)
            {
                CreatureBehaviorsFuzz.Cases++;
                try { one(new Random(seed + i)); } catch (Exception e) { fails.Add($"{name} seed {seed + i}: {e.Message}"); if (fails.Count >= 3) break; }
            }
            return fails;
        }

        private static string Show(int w, int h, bool[] shade, bool[] walk)
        {
            var sb = new System.Text.StringBuilder();
            for (int z = h - 1; z >= 0; z--) { for (int x = 0; x < w; x++) { int i = z * w + x; sb.Append(!walk[i] ? '#' : shade[i] ? 's' : '.'); } sb.Append('/'); }
            return sb.ToString();
        }

        public static List<string> Patch(int n, int seed)
        {
            return Loop("patch", n, seed, r =>
            {
                int w = r.Next(1, 22), h = r.Next(1, 22), N = w * h;
                double pw = r.NextDouble() * 0.35, ps = r.NextDouble();
                var walk = new bool[N]; var shade = new bool[N];
                for (int i = 0; i < N; i++) { walk[i] = r.NextDouble() >= pw; shade[i] = r.NextDouble() < ps * 0.6; }
                int cap = new[] { -7, 0, 10, 14, 30, 60, 140 }[r.Next(7)];
                int minCells = r.Next(-1, 6);
                CreatureBehaviorsFuzz.Steps += N;
                var g = RM_ShadePatchGraph.Build(w, h, shade, walk, cap, minCells);
                string grid = Show(w, h, shade, walk);
                int minEff = Math.Max(1, minCells), capEff = Math.Max(0, cap);
                Func<int, IEnumerable<int>> nbrs = i => Enumerable.Range(0, 9).Where(k => k != 4).Select(k => (x: i % w + k % 3 - 1, z: i / w + k / 3 - 1)).Where(p => p.x >= 0 && p.z >= 0 && p.x < w && p.z < h).Select(p => p.z * w + p.x);

                // ---- labelling oracle: components of shade&walk, scan order ----
                var comp = new int[N]; for (int i = 0; i < N; i++) comp[i] = -1;
                var expectPatch = new int[N]; for (int i = 0; i < N; i++) expectPatch[i] = -1;
                var sizes = new List<int>();
                for (int s = 0; s < N; s++)
                {
                    if (comp[s] >= 0 || !shade[s] || !walk[s]) continue;
                    var q = new Queue<int>(); q.Enqueue(s); comp[s] = sizes.Count; var members = new List<int> { s };
                    while (q.Count > 0) { int u = q.Dequeue(); foreach (int v in nbrs(u)) if (comp[v] < 0 && shade[v] && walk[v]) { comp[v] = sizes.Count; q.Enqueue(v); members.Add(v); } }
                    sizes.Add(members.Count);
                }
                var idOf = new Dictionary<int, int>(); int next = 0;
                for (int s = 0; s < N; s++) if (comp[s] >= 0 && sizes[comp[s]] >= minEff && !idOf.ContainsKey(comp[s])) idOf[comp[s]] = next++;
                for (int i = 0; i < N; i++) if (comp[i] >= 0 && idOf.ContainsKey(comp[i])) expectPatch[i] = idOf[comp[i]];
                Check(g.PatchCount == next, $"{g.PatchCount} patches, oracle {next} | {grid}");
                Patches += g.PatchCount;
                for (int i = 0; i < N; i++) Check(g.patchOf[i] == expectPatch[i], $"patchOf[{i}] = {g.patchOf[i]}, oracle {expectPatch[i]} (cell ({i % w},{i / w}), min {minEff}) | {grid}");
                for (int p = 0; p < g.PatchCount; p++) Check(g.patches[p].cellCount == Enumerable.Range(0, N).Count(i => expectPatch[i] == p), $"patch {p} cellCount");
                int flecks = sizes.Count(s => s < minEff); Flecks += flecks;
                for (int i = 0; i < N; i++) if (shade[i] && walk[i] && g.patchOf[i] == RM_ShadePatchGraph.NoPatch) Check(sizes[comp[i]] < minEff, "a shade cell of a big enough group has no patch");
                for (int i = 0; i < N; i++) if (!walk[i]) Check(g.patchOf[i] == -1 && g.distToShade[i] == RM_ShadePatchGraph.Unreached, $"blocked cell {i} was labelled or reached");

                // ---- rim ----
                for (int p = 0; p < g.PatchCount; p++)
                {
                    var want = Enumerable.Range(0, N).Where(i => expectPatch[i] == p && nbrs(i).Any(v => walk[v] && expectPatch[v] == -1)).ToList();
                    Check(g.patches[p].rim.OrderBy(x => x).SequenceEqual(want), $"patch {p} rim [{string.Join(",", g.patches[p].rim)}] vs oracle [{string.Join(",", want)}] | {grid}");
                    Rims += want.Count;
                    Check(g.patches[p].rim.Distinct().Count() == g.patches[p].rim.Count, "duplicate rim cell");
                }

                // ---- distance field oracle (Bellman-Ford over open walkable cells from every rim) ----
                int INF = int.MaxValue;
                var d = new int[N]; for (int i = 0; i < N; i++) d[i] = INF;
                for (int i = 0; i < N; i++) if (expectPatch[i] >= 0) d[i] = 0;                       // every patch cell is 0, as the graph does
                var seeds = new List<int>(); for (int p = 0; p < g.PatchCount; p++) seeds.AddRange(g.patches[p].rim);
                var dist = new int[N]; for (int i = 0; i < N; i++) dist[i] = INF;
                foreach (int s in seeds) dist[s] = 0;
                bool changed = true;
                while (changed)
                {
                    changed = false;
                    for (int u = 0; u < N; u++)
                    {
                        if (dist[u] == INF) continue;
                        foreach (int v in nbrs(u))
                        {
                            if (!walk[v] || expectPatch[v] != -1) continue;
                            int step = (v % w != u % w && v / w != u / w) ? 14 : 10;
                            int nd = dist[u] + step;
                            if (nd > capEff || nd >= dist[v]) continue;
                            dist[v] = nd; changed = true;
                        }
                    }
                }
                for (int i = 0; i < N; i++)
                {
                    int want = expectPatch[i] >= 0 ? 0 : dist[i];
                    Check(g.distToShade[i] == want, $"distToShade[{i}] ({i % w},{i / w}) = {g.distToShade[i]}, oracle {want} (cap {capEff}) | {grid}");
                    if (want == capEff && capEff > 0) Capped++;
                    if (expectPatch[i] >= 0) Check(g.nearestShade[i] == i, "a patch cell's nearest shade is not itself");
                    else if (want == INF) Check(g.nearestShade[i] == -1, $"unreached cell {i} has a nearest shade");
                    else
                    {
                        int ns = g.nearestShade[i];
                        Check(ns >= 0 && expectPatch[ns] >= 0, $"cell {i}'s nearest shade {ns} is not a patch cell");
                        Check(g.patches[expectPatch[ns]].rim.Contains(ns), $"cell {i}'s nearest shade {ns} is not on a rim");
                        Check(RM_ShadePatchGraph.Octile(i % w, i / w, ns % w, ns / w) <= g.distToShade[i], $"cell {i} is {g.distToShade[i]} from {ns} which is {RM_ShadePatchGraph.Octile(i % w, i / w, ns % w, ns / w)} away in a straight line");
                    }
                }

                // ---- edges ----
                for (int a = 0; a < g.PatchCount; a++)
                {
                    var seenTo = new HashSet<int>();
                    foreach (var e in g.patches[a].edges)
                    {
                        Edges++;
                        Check(e.to != a && e.to >= 0 && e.to < g.PatchCount, "edge to itself or out of range");
                        Check(seenTo.Add(e.to), $"two edges from patch {a} to patch {e.to}");
                        Check(e.cost >= 0 && e.cost <= capEff, $"edge cost {e.cost} outside 0..{capEff}");
                        Check(g.patchOf[e.fromCell] == a && g.patchOf[e.toCell] == e.to, $"edge cells ({e.fromCell},{e.toCell}) are not in patches {a} and {e.to}");
                        Check(e.cost >= RM_ShadePatchGraph.Octile(e.fromCell % w, e.fromCell / w, e.toCell % w, e.toCell / w), "edge cost below the straight-line distance between its cells");
                        var back = g.patches[e.to].edges.FirstOrDefault(x => x.to == a);
                        Check(back.cost == e.cost && back.fromCell == e.toCell && back.toCell == e.fromCell && g.patches[e.to].edges.Any(x => x.to == a), $"edge {a}->{e.to} has no mirror image");
                    }
                }
                Check(g.EdgeCount * 2 == Enumerable.Range(0, g.PatchCount).Sum(p => g.patches[p].edges.Count), "EdgeCount is not half the directed edge count");
                // the edge set is exactly what the fronts say: for every pair of neighbouring cells owned by different patches, dist + dist + step <= cap,
                // the cheapest such sum per pair of patches
                {
                    var oracle = new Dictionary<(int, int), int>();
                    for (int u = 0; u < N; u++)
                    {
                        if (g.distToShade[u] == INF || g.nearestShade[u] < 0) continue;
                        int pa = expectPatch[g.nearestShade[u]];
                        foreach (int v in nbrs(u))
                        {
                            if (!walk[v] || g.distToShade[v] == INF || g.nearestShade[v] < 0) continue;
                            int pb = expectPatch[g.nearestShade[v]];
                            if (pa == pb || pa < 0 || pb < 0) continue;
                            int total = g.distToShade[u] + g.distToShade[v] + ((u % w != v % w && u / w != v / w) ? 14 : 10);
                            if (total > capEff) continue;
                            var key = (Math.Min(pa, pb), Math.Max(pa, pb));
                            if (!oracle.TryGetValue(key, out int best) || total < best) oracle[key] = total;
                        }
                    }
                    var have = new Dictionary<(int, int), int>();
                    for (int a2 = 0; a2 < g.PatchCount; a2++) foreach (var e in g.patches[a2].edges) if (a2 < e.to) have[(a2, e.to)] = e.cost;
                    Check(have.Count == oracle.Count && oracle.All(kv => have.TryGetValue(kv.Key, out int c) && c == kv.Value),
                        $"edges [{string.Join(" ", have.OrderBy(k => k.Key).Select(k => k.Key + "=" + k.Value))}] vs fronts [{string.Join(" ", oracle.OrderBy(k => k.Key).Select(k => k.Key + "=" + k.Value))}] (cap {capEff}) | {grid}");
                }

                // ---- the ring ----
                if (N > 0)
                {
                    int origin = r.Next(N); int range = r.Next(-10, 90);
                    var got = new List<int>();
                    g.ReachableWithReturn(origin, range, got);
                    var wantRing = new List<int>();
                    if (range > 0)
                    {
                        int rr = range / 10; int ox = origin % w, oz = origin / w;
                        for (int z = Math.Max(0, oz - rr); z <= Math.Min(h - 1, oz + rr); z++)
                            for (int x = Math.Max(0, ox - rr); x <= Math.Min(w - 1, ox + rr); x++)
                            {
                                int i = z * w + x;
                                if (g.distToShade[i] == INF) continue;
                                if (RM_ShadePatchGraph.Octile(ox, oz, x, z) + g.distToShade[i] <= range) wantRing.Add(i);
                            }
                    }
                    Check(got.SequenceEqual(wantRing), $"ring from {origin} range {range}: [{string.Join(",", got)}] vs [{string.Join(",", wantRing)}]");
                    Rings += got.Count;
                    var empty = new List<int> { 1 }; g.ReachableWithReturn(-1, 50, empty); Check(empty.Count == 0, "a ring from outside the grid");
                    g.ReachableWithReturn(N, 50, empty); Check(empty.Count == 0, "a ring from index N");
                }
                Check(RM_ShadePatchGraph.Octile(0, 0, 3, 1) == RM_ShadePatchGraph.Octile(3, 1, 0, 0) && RM_ShadePatchGraph.Octile(0, 0, 3, 3) == 42 && RM_ShadePatchGraph.Octile(0, 0, 4, 1) == 14 + 30, "Octile");
                Check(g.PatchAt(-1) == -1 && g.PatchAt(N) == -1, "PatchAt outside the grid");
            });
        }

        public static List<string> Dash(int n, int seed)
        {
            return Loop("dash", n, seed, r =>
            {
                CreatureBehaviorsFuzz.Steps++;
                // severity floor: max(curve * 6.45e-5, 0.000375)
                Check(RM_DashMath.SeverityPerInterval(0f) == 0.000375f && RM_DashMath.SeverityPerInterval(-4f) == 0.000375f, "severity floor");
                float over = (float)(r.NextDouble() * 80);
                float sev = RM_DashMath.SeverityPerInterval(over);
                Check(sev >= 0.000375f && Math.Abs(sev - Math.Max(over * 6.45E-05f, 0.000375f)) < 1e-9f, "severity formula");
                Check(RM_DashMath.SeverityPerInterval(over + 5f) >= sev, "severity fell as the overage rose");
                float safe = (float)(r.NextDouble() * 40 + 10), felt = safe + (float)(r.NextDouble() * 30 - 10), budget = r.Next(5) == 0 ? (float)(r.NextDouble() * 2 - 1) : r.Next(7) == 0 ? 50000f : (float)(r.NextDouble() * 0.8);
                int tol = RM_DashMath.ToleratedTicks(felt, safe, over, budget);
                if (budget <= 0f) Check(tol == 0, "tolerated ticks with no budget");
                else if (felt <= safe) Check(tol == int.MaxValue, "a creature not pushed past its safe max has a tolerance limit");
                else
                {
                    Check(tol > 0, "tolerated ticks not positive");
                    Check(RM_DashMath.ToleratedTicks(felt, safe, over, budget * 1.5f) >= tol, "a bigger budget tolerated less");
                    Check(RM_DashMath.ToleratedTicks(felt, safe, over + 5f, budget) <= tol, "a hotter sun tolerated more");
                    double ideal = budget / (double)sev * RM_DashMath.HeatIntervalTicks;
                    Check(ideal >= int.MaxValue ? tol == int.MaxValue : Math.Abs(tol - ideal) <= 1.0 + ideal * 1e-6, $"tolerated {tol}, ideal {ideal} (float arithmetic: relative error under 1e-6 is expected)");
                }
                float tpc = RM_DashMath.TicksPerCell((float)(r.NextDouble() * 20), new[] { 0.75f, 1f, 0f }[r.Next(3)]);
                Check(tpc >= 1f, "ticks per cell under 1");
                float strict = new[] { 0f, 0.5f, 1f, 2f }[r.Next(4)], min = r.Next(0, 4), max = min + r.Next(0, 30);
                int cost = RM_DashMath.DashRangeCost(tol, tpc, strict, min, max);
                if (tol <= 0 || strict <= 0f) Check(cost == 0, "dash range with no tolerance / strictness");
                else
                {
                    Check(cost >= (int)Math.Round(min * 10) && cost <= (int)Math.Round(max * 10), $"dash range {cost} outside [{min * 10},{max * 10}]");
                    Check(RM_DashMath.DashRangeCost(tol, tpc, strict * 1.5f, min, max) >= cost, "a stricter dial shortened the range");
                    if (tol == int.MaxValue) Check(cost == (int)Math.Round(Math.Min(max, Math.Max(min, max * strict)) * 10), "an unlimited tolerance does not give the max range");
                }
                // wild leave precedence: too warm (season) > too cold (season) > warm (ambient) > cold (ambient) > starving > none
                float cmin = r.Next(-20, 10), cmax = cmin + r.Next(5, 40), smin = r.Next(-30, 10), smax = smin + r.Next(10, 70);
                float season = r.Next(-40, 60), amb = r.Next(-40, 90); bool starving = r.Next(2) == 0;
                var got = RM_WildLeaveMath.Classify(season, cmin, cmax, amb, smin, smax, starving);
                var want = season >= cmax ? RM_WildLeaveReason.TooWarm : season <= cmin ? RM_WildLeaveReason.TooCold : amb > smax ? RM_WildLeaveReason.TooWarm : amb < smin ? RM_WildLeaveReason.TooCold : starving ? RM_WildLeaveReason.Starving : RM_WildLeaveReason.None;
                Check(got == want, $"Classify(season {season} [{cmin},{cmax}], ambient {amb} [{smin},{smax}], starving {starving}) = {got}, want {want}");
                Check(RM_WildLeaveMath.ShouldNotify(1000, -1, 600) && RM_WildLeaveMath.ShouldNotify(10, -1, 600) && !RM_WildLeaveMath.ShouldNotify(1000, 500, 600) && RM_WildLeaveMath.ShouldNotify(1100, 500, 600) && RM_WildLeaveMath.ShouldNotify(0, 0, 0), "ShouldNotify window");
            });
        }
    }
}
