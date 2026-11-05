// CORDPLANNER_ASTAR_SHRINK_TO_ZERO_ALLOC (hose/wire advisory 2026-10-28 §4 #4): CordPlanner's A* moved from a per-call
// Dictionary + SortedSet to a per-thread stamped flat-array scratch and an indexed binary heap ordered (f, g, cell).
//  H1 identical: on a seeded sweep of random worlds (walls/rock/water, costed cells, bands with links, endpoints in blocked
//     cells or off the map, expansion caps, open floors full of ties) AStar and AStarDive return exactly the route the old
//     SortedSet search below returns (kept here verbatim as the reference), so GSS stays identical on load.
//  H2 the stamp wrap (int.MaxValue) and map-size changes between calls change no route.
//  H3 allocation-free: a warmed AStarInto / AStarDiveInto allocates 0 bytes (GC.GetAllocatedBytesForCurrentThread).
using System;
using System.Collections.Generic;
using System.Reflection;
using RimMandrake.Shared.Slack;

namespace RimMandrake.GimmeSomeSlack.SelfTest
{
    internal static class AStarHeapChecks
    {
        private static void Check(bool ok, string msg)
        {
            Program.Check(ok, "astar heap: " + msg);
            Console.WriteLine("astar heap " + (ok ? "PASS " : "FAIL ") + msg);
        }

        // ------------------------------------------------------------------ reference: the pre-change search, verbatim
        private static List<Cell> RefAStar(CordWorld w, Cell start, Cell goal, int maxExpand = 40000)
        {
            if (start == goal) return new List<Cell> { start };
            bool Ok(Cell c) => c == start || c == goal || w.IsWalkable(c);
            double H(Cell c)
            {
                int dx = Math.Abs(c.X - goal.X), dz = Math.Abs(c.Z - goal.Z);
                return Math.Max(dx, dz) + 0.414 * Math.Min(dx, dz);
            }
            var g = new Dictionary<Cell, double> { [start] = 0 };
            var came = new Dictionary<Cell, Cell>();
            var open = new SortedSet<(double f, double g, Cell c)>(Comparer<(double f, double g, Cell c)>.Create((a, b) =>
            {
                int k = a.f.CompareTo(b.f);
                if (k != 0) return k;
                k = a.g.CompareTo(b.g);
                return k != 0 ? k : a.c.CompareTo(b.c);
            }));
            open.Add((H(start), 0, start));
            int expanded = 0;
            while (open.Count > 0)
            {
                var top = open.Min;
                open.Remove(top);
                Cell c = top.c;
                if (c == goal)
                {
                    var path = new List<Cell> { c };
                    while (came.TryGetValue(c, out Cell p)) { c = p; path.Add(c); }
                    path.Reverse();
                    return path;
                }
                if (top.g > g[c] + 1e-12) continue;
                if (++expanded > maxExpand) return null;
                foreach (Cell d in Cell.Dirs8)
                {
                    Cell q = c + d;
                    if (!Ok(q)) continue;
                    if (d.X != 0 && d.Z != 0 && !(Ok(new Cell(c.X + d.X, c.Z)) && Ok(new Cell(c.X, c.Z + d.Z)))) continue;
                    if (!w.StepAllowed(c, q)) continue;
                    double ng = top.g + (d.X != 0 && d.Z != 0 ? 1.414 : 1.0) + w.ExtraCost(q);
                    if (!g.TryGetValue(q, out double old) || ng < old - 1e-12)
                    {
                        if (g.TryGetValue(q, out double o2)) open.Remove((o2 + H(q), o2, q));
                        g[q] = ng;
                        came[q] = c;
                        open.Add((ng + H(q), ng, q));
                    }
                }
            }
            return null;
        }

        private static List<Cell> RefAStarDive(CordWorld w, Cell start, Cell goal, Func<Cell, bool> exempt, int maxExpand = 60000)
        {
            if (start == goal) return new List<Cell> { start };
            bool Open(Cell c) => c == start || c == goal || w.IsWalkable(c) || (exempt != null && exempt(c));
            double H(Cell c)
            {
                int dx = Math.Abs(c.X - goal.X), dz = Math.Abs(c.Z - goal.Z);
                return Math.Max(dx, dz) + 0.414 * Math.Min(dx, dz);
            }
            var g = new Dictionary<Cell, double> { [start] = 0 };
            var came = new Dictionary<Cell, Cell>();
            var open = new SortedSet<(double f, double g, Cell c)>(Comparer<(double f, double g, Cell c)>.Create((a, b) =>
            {
                int k = a.f.CompareTo(b.f);
                if (k != 0) return k;
                k = a.g.CompareTo(b.g);
                return k != 0 ? k : a.c.CompareTo(b.c);
            }));
            open.Add((H(start), 0, start));
            int expanded = 0;
            while (open.Count > 0)
            {
                var top = open.Min;
                open.Remove(top);
                Cell c = top.c;
                if (c == goal)
                {
                    var path = new List<Cell> { c };
                    while (came.TryGetValue(c, out Cell p)) { c = p; path.Add(c); }
                    path.Reverse();
                    return path;
                }
                if (top.g > g[c] + 1e-12) continue;
                if (++expanded > maxExpand) return null;
                foreach (Cell d in Cell.Dirs8)
                {
                    Cell q = c + d;
                    if (!w.InBounds(q)) continue;
                    bool diag = d.X != 0 && d.Z != 0;
                    if (diag && !(Open(c) && Open(q) && Open(new Cell(c.X + d.X, c.Z)) && Open(new Cell(c.X, c.Z + d.Z)))) continue;
                    if (!w.StepAllowed(c, q)) continue;
                    double ng = top.g + (diag ? 1.414 : 1.0) + (Open(q) ? w.ExtraCost(q) : CordPlanner.DiveCost);
                    if (!g.TryGetValue(q, out double old) || ng < old - 1e-12)
                    {
                        if (g.TryGetValue(q, out double o2)) open.Remove((o2 + H(q), o2, q));
                        g[q] = ng;
                        came[q] = c;
                        open.Add((ng + H(q), ng, q));
                    }
                }
            }
            return null;
        }

        // ------------------------------------------------------------------ worlds
        private static readonly float[] Costs = { 0.5f, 1f, 1.5f, 0.414f, 2.25f };

        private static CordWorld RandomWorld(Random r, out int width, out int height)
        {
            width = r.Next(3, 64); height = r.Next(3, 64);
            var w = new CordWorld(width, height);
            double block = r.Next(4) == 0 ? 0 : r.NextDouble() * 0.45, cost = r.Next(3) == 0 ? 0 : r.NextDouble() * 0.3;
            bool walls = r.Next(3) == 0;
            for (int x = 0; x < width; x++)
                for (int z = 0; z < height; z++)
                {
                    var c = new Cell(x, z);
                    if (r.NextDouble() < block) w.SetBlocked(c, (BlockKind)(1 + r.Next(4)));
                    else if (r.NextDouble() < cost) w.SetExtraCost(c, Costs[r.Next(Costs.Length)]);
                    if (r.NextDouble() < 0.05) w.SetDoor(c);
                }
            if (walls)   // a few long walls with gaps, the shape that makes routes tie and detour
                for (int k = r.Next(1, 4); k > 0; k--)
                {
                    int x0 = r.Next(width), gap = r.Next(height);
                    for (int z = 0; z < height; z++) if (Math.Abs(z - gap) > 1) w.SetBlocked(new Cell(x0, z), BlockKind.Wall);
                }
            if (r.Next(4) == 0)   // bands: two terraces split at a row, joined by a few links (ramps)
            {
                int split = r.Next(1, height);
                for (int x = 0; x < width; x++)
                    for (int z = split; z < height; z++) w.SetBand(new Cell(x, z), 1);
                for (int k = r.Next(0, 4); k > 0; k--)
                {
                    int x = r.Next(width);
                    w.LinkBands(new Cell(x, split - 1), new Cell(x, split));
                    w.LinkBands(new Cell(x, split), new Cell(x, split - 1));
                }
            }
            return w;
        }

        private static Cell RandomEnd(Random r, int width, int height)
        {
            int k = r.Next(12);
            if (k == 0) return new Cell(-1, r.Next(height));       // off the map (an endpoint on a face beyond the edge)
            if (k == 1) return new Cell(r.Next(width), height);
            return new Cell(r.Next(width), r.Next(height));
        }

        private static bool Same(List<Cell> a, List<Cell> b)
        {
            if (a == null || b == null) return a == null && b == null;
            if (a.Count != b.Count) return false;
            for (int i = 0; i < a.Count; i++) if (a[i] != b[i]) return false;
            return true;
        }

        private static string Show(List<Cell> p) => p == null ? "null" : p.Count + " cells to " + p[p.Count - 1];

        public static void Run()
        {
            // H1: seeded sweep
            int cases = 0, routed = 0, capped = 0, diverged = 0;
            long newTicks = 0, refTicks = 0;
            string first = null;
            int[] caps = { 3, 40, 400, 40000 };
            for (int seed = 1; seed <= 1500; seed++)
            {
                var r = new Random(seed);
                CordWorld w = RandomWorld(r, out int width, out int height);
                for (int t = 0; t < 4; t++)
                {
                    Cell s = RandomEnd(r, width, height), g = RandomEnd(r, width, height);
                    int cap = r.Next(5) == 0 ? caps[r.Next(caps.Length)] : 40000;
                    Func<Cell, bool> exempt = r.Next(3) == 0 ? null : c => Math.Max(Math.Abs(c.X - s.X), Math.Abs(c.Z - s.Z)) <= 1
                                                                           || Math.Max(Math.Abs(c.X - g.X), Math.Abs(c.Z - g.Z)) <= 1;
                    long t0 = System.Diagnostics.Stopwatch.GetTimestamp();
                    List<Cell> a = CordPlanner.AStar(w, s, g, cap);
                    List<Cell> d = CordPlanner.AStarDive(w, s, g, exempt, cap + 20000);
                    long t1 = System.Diagnostics.Stopwatch.GetTimestamp();
                    List<Cell> ra = RefAStar(w, s, g, cap), rd = RefAStarDive(w, s, g, exempt, cap + 20000);
                    newTicks += t1 - t0; refTicks += System.Diagnostics.Stopwatch.GetTimestamp() - t1;
                    cases += 2;
                    if (ra != null) routed++;
                    if (ra == null && RefAStar(w, s, g) != null) capped++;
                    if (!Same(a, ra)) { diverged++; first = first ?? $"seed {seed} walk {s}->{g} cap {cap}: new {Show(a)}, ref {Show(ra)}"; }
                    if (!Same(d, rd)) { diverged++; first = first ?? $"seed {seed} dive {s}->{g}: new {Show(d)}, ref {Show(rd)}"; }
                }
            }
            Check(diverged == 0 && routed > 1000 && capped > 20,
                  $"H1 {cases} searches identical to the SortedSet reference ({routed} walk routes, {capped} cut by a cap; diverged {diverged}" +
                  (first != null ? ", first: " + first : "") + $"); time new {newTicks * 1000.0 / System.Diagnostics.Stopwatch.Frequency:F0} ms, " +
                  $"reference {refTicks * 1000.0 / System.Diagnostics.Stopwatch.Frequency:F0} ms");

            // H2: the stamp wraps at int.MaxValue; sizes change between calls
            FieldInfo fs = typeof(CordPlanner).GetField("scratch", BindingFlags.NonPublic | BindingFlags.Static);
            object sc = fs?.GetValue(null);
            FieldInfo cur = sc?.GetType().GetField("Cur");
            bool wrapOk = cur != null;
            if (wrapOk)
            {
                cur.SetValue(sc, int.MaxValue - 3);
                for (int seed = 2001; seed <= 2012; seed++)
                {
                    var r = new Random(seed);
                    CordWorld w = RandomWorld(r, out int width, out int height);
                    Cell s = RandomEnd(r, width, height), g = RandomEnd(r, width, height);
                    wrapOk &= Same(CordPlanner.AStar(w, s, g), RefAStar(w, s, g)) && Same(CordPlanner.AStarDive(w, s, g, null), RefAStarDive(w, s, g, null));
                }
                wrapOk &= (int)cur.GetValue(sc) < 1000;
            }
            Check(wrapOk, "H2 routes unchanged across the stamp wrap and map-size changes (scratch field " + (cur != null ? "found" : "MISSING") + ")");

            // H3: allocation-free once warm
            var big = new CordWorld(120, 120);
            var rb = new Random(77);
            for (int x = 0; x < 120; x++)
                for (int z = 0; z < 120; z++)
                    if (rb.NextDouble() < 0.25) big.SetBlocked(new Cell(x, z), BlockKind.Rock);
                    else if (rb.NextDouble() < 0.1) big.SetExtraCost(new Cell(x, z), 1.5f);
            Cell bs = new Cell(1, 1), bg = new Cell(118, 117);
            Func<Cell, bool> bex = c => c == bs || c == bg;
            var into = new List<Cell>(1024);
            bool w1 = CordPlanner.AStarInto(big, bs, bg, into), w2 = CordPlanner.AStarDiveInto(big, bs, bg, bex, into);
            int walkLen = 0;
            long before = GC.GetAllocatedBytesForCurrentThread();
            for (int i = 0; i < 20; i++)
            {
                CordPlanner.AStarInto(big, bs, bg, into);
                walkLen = into.Count;
                CordPlanner.AStarDiveInto(big, bs, bg, bex, into);
            }
            long bytes = GC.GetAllocatedBytesForCurrentThread() - before;
            Check(w2 && bytes == 0, $"H3 40 warmed searches on a 120x120 rock field allocate {bytes} bytes (bar 0; walk routed {w1}, {walkLen} cells; dive {into.Count} cells)");
        }
    }
}
