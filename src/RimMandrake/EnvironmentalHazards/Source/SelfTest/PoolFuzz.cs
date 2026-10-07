// Approach B for the stranding pools: seeded random grids and ACTION SEQUENCES over RM_PoolKernel, the Verse-free grid
// logic RM_MapComponent_StrandingPools calls (component labelling, main network, pool continuity, the reconnect
// flood-fill, decay target, shoreline-first removal). The registry harness (detect / reconcile / decay in the order the
// component does them) is this file's own; every grid decision comes from the kernel and is also checked against an
// independent oracle. Failures are shrunk and printed as `family seed N: message | actions`.
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;

namespace RimMandrake.EnvironmentalHazards.SelfTest
{
    internal static class PoolFuzz
    {
        public static long Cases, Steps, Comps, PoolsMade, Removed, Reconnects, Detects;
        public static long OverlapObs, UncoveredObs, FragmentObs, GhostObs, EdgeFirstChecks, FallbackLast;
        static readonly int[] DX = { 0, 1, 0, -1 };
        static readonly int[] DZ = { 1, 0, -1, 0 };

        internal struct Act
        {
            public int kind, a, b;
            public override string ToString()
            {
                switch (kind)
                {
                    case 0: return $"Detect(decay={a})";
                    case 1: return $"Tick(+{a})";
                    case 2: return $"Flip({a} cells)";
                    case 3: return $"Fill(rect {a})";
                    default: return $"Dry({a})";
                }
            }
        }

        private static void Check(bool ok, string msg) { if (!ok) throw new Exception(msg); }

        // ---- independent oracles ----------------------------------------------------------------------------------
        private static int[] OracleLabels(int w, int h, bool[] water)
        {
            int n = w * h; int[] lab = new int[n]; for (int i = 0; i < n; i++) lab[i] = -1;
            int next = 0;
            for (int s = 0; s < n; s++)
            {
                if (!water[s] || lab[s] >= 0) continue;
                var stack = new Stack<int>(); stack.Push(s); lab[s] = next;
                while (stack.Count > 0)
                {
                    int c = stack.Pop(); int x = c % w, z = c / w;
                    for (int d = 0; d < 4; d++)
                    {
                        int nx = x + DX[d], nz = z + DZ[d];
                        if (nx < 0 || nz < 0 || nx >= w || nz >= h) continue;
                        int nb = nz * w + nx;
                        if (water[nb] && lab[nb] < 0) { lab[nb] = next; stack.Push(nb); }
                    }
                }
                next++;
            }
            return lab;
        }

        private static bool OracleReconnected(int w, int h, bool[] water, List<int> cells)
        {
            if (cells.Count == 0) return false;
            var seen = new HashSet<int> { cells[0] }; var st = new Stack<int>(); st.Push(cells[0]);
            bool edge = false;
            while (st.Count > 0)
            {
                int c = st.Pop(); int x = c % w, z = c / w;
                if (x == 0 || z == 0 || x == w - 1 || z == h - 1) edge = true;
                for (int d = 0; d < 4; d++)
                {
                    int nx = x + DX[d], nz = z + DZ[d];
                    if (nx < 0 || nz < 0 || nx >= w || nz >= h) continue;
                    int nb = nz * w + nx;
                    if (water[nb] && seen.Add(nb)) st.Push(nb);
                }
            }
            return edge || seen.Count > Math.Max(200, cells.Count * 8);
        }

        private static bool IsEdgeCell(int w, int h, bool[] water, int c)
        {
            int x = c % w, z = c / w;
            for (int d = 0; d < 4; d++)
            {
                int nx = x + DX[d], nz = z + DZ[d];
                if (nx < 0 || nz < 0 || nx >= w || nz >= h || !water[nz * w + nx]) return true;
            }
            return false;
        }

        // ---- grids -----------------------------------------------------------------------------------------------
        private static bool[] RandomGrid(Random r, int w, int h)
        {
            bool[] g = new bool[w * h];
            double p = new[] { 0.1, 0.25, 0.4, 0.55, 0.7 }[r.Next(5)];
            if (r.Next(2) == 0) for (int i = 0; i < g.Length; i++) g[i] = r.NextDouble() < p;
            else
            {
                int blobs = 1 + r.Next(6);
                for (int b = 0; b < blobs; b++)
                {
                    int cx = r.Next(w), cz = r.Next(h), rad = 1 + r.Next(Math.Max(2, Math.Min(w, h) / 2));
                    for (int z = 0; z < h; z++) for (int x = 0; x < w; x++) if ((x - cx) * (x - cx) + (z - cz) * (z - cz) <= rad * rad && r.NextDouble() < 0.9) g[z * w + x] = true;
                }
            }
            if (r.Next(3) == 0) { int row = r.Next(h); for (int x = 0; x < w; x++) g[row * w + x] = true; } // a river to the edge
            return g;
        }

        // ---- primitives vs oracles -------------------------------------------------------------------------------
        public static List<string> Prims(int n, int baseSeed)
        {
            var fails = new List<string>();
            for (int k = 0; k < n && fails.Count < 5; k++)
            {
                int seed = baseSeed + k; var r = new Random(seed); Cases++;
                int w = 1 + r.Next(26), h = 1 + r.Next(26);
                bool[] g = RandomGrid(r, w, h);
                try
                {
                    var comps = RM_PoolKernel.Components(w, h, i => g[i]);
                    Comps += comps.Count; Steps += w * h;
                    int[] lab = OracleLabels(w, h, g);
                    int labelCount = lab.Length == 0 ? 0 : lab.Max() + 1;
                    Check(comps.Count == labelCount, $"{comps.Count} components, oracle {labelCount}");
                    int total = 0;
                    for (int i = 0; i < comps.Count; i++)
                    {
                        var c = comps[i]; total += c.Count;
                        Check(c.Count > 0, "empty component");
                        Check(c.Distinct().Count() == c.Count, "component lists a cell twice");
                        Check(c.All(x => g[x] && lab[x] == lab[c[0]]), "component holds a dry cell or two oracle regions");
                        Check(c[0] == c.Min(), $"component starts at {c[0]} not its lowest cell {c.Min()}");
                        Check(c.Count == lab.Count(l => l == lab[c[0]]), "component is not the whole oracle region");
                        if (i > 0) Check(c[0] > comps[i - 1][0], "components not in scan order");
                    }
                    Check(total == g.Count(x => x), "components do not partition the water");
                    if (comps.Count == 0) continue;
                    int main = RM_PoolKernel.MainIndex(comps);
                    int best = comps.Max(c => c.Count);
                    Check(comps[main].Count == best && comps.FindIndex(c => c.Count == best) == main, "main is not the first largest");

                    // MatchPools vs brute force over random tracked pools (possibly overlapping, stale, empty)
                    var pools = new List<List<int>>();
                    int np = r.Next(5);
                    for (int p = 0; p < np; p++)
                    {
                        var cs = new List<int>(); int m = r.Next(0, 12);
                        for (int q = 0; q < m; q++) cs.Add(r.Next(w * h));
                        pools.Add(cs.Distinct().ToList());
                    }
                    int[] match = RM_PoolKernel.MatchPools(w, h, comps, main, pools);
                    Check(match.Length == comps.Count, "match array wrong length");
                    for (int i = 0; i < comps.Count; i++)
                    {
                        int want = -1;
                        if (i != main)
                            foreach (int cell in comps[i])
                            {
                                int own = -1;
                                for (int p = 0; p < pools.Count; p++) if (pools[p].Contains(cell)) own = p;
                                if (own >= 0) { want = own; break; }
                            }
                        Check(match[i] == want, $"component {i} matched pool {match[i]}, brute force says {want}");
                    }

                    // Reconnected + PickEdgeIndex vs oracles on pools drawn from real components and random junk
                    for (int t = 0; t < 4; t++)
                    {
                        List<int> cells = t < 2 && comps.Count > 0 ? new List<int>(comps[r.Next(comps.Count)]) : Enumerable.Range(0, r.Next(1, Math.Min(w * h, 10) + 1)).Select(_ => r.Next(w * h)).Distinct().ToList();
                        if (r.Next(3) == 0 && cells.Count > 0) { int cut = r.Next(cells.Count); cells = cells.Skip(cut).Concat(cells.Take(cut)).ToList(); }
                        bool rc = RM_PoolKernel.Reconnected(w, h, cells, i => g[i]);
                        Check(rc == OracleReconnected(w, h, g, cells), $"Reconnected={rc} for pool {string.Join(",", cells.Take(6))}.. disagrees with oracle");
                        int pi = RM_PoolKernel.PickEdgeIndex(w, h, cells, i => g[i]);
                        int firstEdge = cells.FindIndex(c => IsEdgeCell(w, h, g, c));
                        Check(pi == (firstEdge >= 0 ? firstEdge : cells.Count - 1), $"PickEdgeIndex {pi}, oracle {(firstEdge >= 0 ? firstEdge : cells.Count - 1)}");
                    }
                    Check(!RM_PoolKernel.Reconnected(w, h, new List<int>(), i => g[i]), "an empty pool counted as reconnected");

                    // decay target: bounds, monotone in elapsed, zero at/after the end, no-ops
                    int orig = r.Next(-1, 200), total2 = r.Next(-1, 300000);
                    int prevT = int.MaxValue; bool all = true;
                    for (int e = -2; e <= (total2 > 0 ? total2 + 5 : 50); e += Math.Max(1, (total2 > 0 ? total2 : 50) / 23))
                    {
                        bool ok = RM_PoolKernel.TryDecayTarget(e, total2, orig, out int tgt);
                        bool should = e > 0 && total2 > 0 && orig > 0;
                        Check(ok == should, $"TryDecayTarget({e},{total2},{orig}) said {ok}");
                        if (!ok) continue;
                        Check(tgt >= 0 && tgt <= orig, $"target {tgt} outside [0,{orig}]");
                        Check(tgt <= prevT, $"target rose {prevT}->{tgt} as time passed");
                        if (e >= total2) Check(tgt == 0, $"target {tgt} at/after the end");
                        prevT = tgt; all = false;
                    }
                    _ = all;
                }
                catch (Exception e) { fails.Add($"prim seed {seed}: {e.Message}"); }
            }
            return fails;
        }

        // ---- registry harness ---------------------------------------------------------------------------------------
        private sealed class Pool { public int id, original, birth, decayTotal; public List<int> cells; }

        private sealed class Reg
        {
            public int w, h, now, nextId = 1; public bool[] water; public bool dry;
            public List<Pool> pools = new List<Pool>();
            public HashSet<int> decayedCells = new HashSet<int>();
        }

        private static void Detect(Reg g, int decay)
        {
            Detects++;
            var comps = RM_PoolKernel.Components(g.w, g.h, i => g.water[i]);
            if (comps.Count < 2) return;
            int main = RM_PoolKernel.MainIndex(comps);
            var pc = g.pools.Select(p => new List<int>(p.cells)).ToList();
            int[] match = RM_PoolKernel.MatchPools(g.w, g.h, comps, main, pc);
            int before = g.pools.Count;
            var adopted = new Dictionary<int, int>();
            for (int i = 0; i < comps.Count; i++)
            {
                if (i == main) continue;
                if (match[i] >= 0) { g.pools[match[i]].cells = new List<int>(comps[i]); adopted[match[i]] = i; continue; }
                var pool = new Pool { id = g.nextId++, cells = new List<int>(comps[i]), original = comps[i].Count, birth = g.now, decayTotal = Math.Max(1, decay) };
                g.pools.Add(pool); PoolsMade++;
                if (g.decayedCells.Overlaps(comps[i])) GhostObs++;
            }
            // coverage: each non-main component should now be exactly some pool's cell set
            for (int i = 0; i < comps.Count; i++)
            {
                if (i == main) continue;
                var set = new HashSet<int>(comps[i]);
                bool covered = g.pools.Any(p => p.cells.Count == set.Count && set.SetEquals(p.cells));
                if (!covered) UncoveredObs++;
            }
            Check(g.pools.Count >= before, "a detect pass dropped a tracked pool");
        }

        private static void Reconcile(Reg g)
        {
            for (int i = g.pools.Count - 1; i >= 0; i--)
            {
                Pool p = g.pools[i];
                bool oracleRc = OracleReconnected(g.w, g.h, g.water, p.cells);
                bool rc = RM_PoolKernel.Reconnected(g.w, g.h, p.cells, x => g.water[x]);
                Check(rc == oracleRc, $"pool {p.id} Reconnected={rc}, oracle {oracleRc}");
                if (rc) { g.pools.RemoveAt(i); Removed++; Reconnects++; continue; }

                int elapsed = g.now - p.birth;
                if (RM_PoolKernel.TryDecayTarget(elapsed, p.decayTotal, p.original, out int target))
                {
                    int guard = 0;
                    while (p.cells.Count > target && p.cells.Count > 0)
                    {
                        int idx = RM_PoolKernel.PickEdgeIndex(g.w, g.h, p.cells, x => g.water[x]);
                        Check(idx >= 0 && idx < p.cells.Count, "edge pick out of range");
                        int cell = p.cells[idx];
                        int firstEdge = p.cells.FindIndex(c => IsEdgeCell(g.w, g.h, g.water, c));
                        if (firstEdge >= 0) { Check(idx == firstEdge && IsEdgeCell(g.w, g.h, g.water, cell), "removed a non-shoreline cell while a shoreline cell existed"); EdgeFirstChecks++; }
                        else { Check(idx == p.cells.Count - 1, "no shoreline: should remove the last cell"); FallbackLast++; }
                        p.cells.Remove(cell);
                        if (g.dry) g.water[cell] = false; else g.decayedCells.Add(cell); // wet leftover = what a ghost pool is made from
                        Check(++guard < 100000, "decay loop did not terminate");
                    }
                    Check(p.cells.Count <= Math.Max(0, target) || p.cells.Count == 0, $"pool {p.id} left at {p.cells.Count} over target {target}");
                }
                if (p.cells.Count == 0) { g.pools.RemoveAt(i); Removed++; }
            }
            // after the pass: liveness - a pool past its decay window is gone
            foreach (Pool p in g.pools)
                Check(!(g.now - p.birth >= p.decayTotal && p.original > 0), $"pool {p.id} survived past its decay window ({g.now - p.birth} >= {p.decayTotal}) with {p.cells.Count} cells");
        }

        private static void Invariants(Reg g, string what)
        {
            var ids = new HashSet<int>(); int prev = 0;
            foreach (Pool p in g.pools)
            {
                Check(ids.Add(p.id) && p.id > prev, $"pool ids not unique/ascending at {p.id}");
                prev = p.id;
                Check(p.cells.Count == p.cells.Distinct().Count(), $"pool {p.id} lists a cell twice");
                Check(p.cells.All(c => c >= 0 && c < g.w * g.h), $"pool {p.id} holds an out-of-grid cell");
                Check(p.original > 0 && p.decayTotal >= 1, $"pool {p.id} has original {p.original}, decayTotal {p.decayTotal}");
            }
        }

        private static string RunSeq(int seed, List<Act> acts)
        {
            var r = new Random(seed);
            var g = new Reg { w = 6 + r.Next(24), h = 6 + r.Next(24), dry = r.Next(4) != 0 };
            g.water = RandomGrid(r, g.w, g.h);
            try
            {
                foreach (var a in acts)
                {
                    Steps++;
                    switch (a.kind)
                    {
                        case 0: Detect(g, a.a); break;
                        case 1:
                        {
                            var counts = g.pools.ToDictionary(p => p.id, p => p.cells.Count);
                            g.now += a.a; Reconcile(g);
                            foreach (Pool p in g.pools) if (counts.TryGetValue(p.id, out int was)) Check(p.cells.Count <= was, $"pool {p.id} grew {was}->{p.cells.Count} with no detect pass");
                            break;
                        }
                        case 2:
                            for (int i = 0; i < a.a; i++) { int c = new Random(seed * 31 + a.b + i).Next(g.w * g.h); g.water[c] = !g.water[c]; }
                            break;
                        case 3:
                        {
                            var rr = new Random(seed * 17 + a.b); int x0 = rr.Next(g.w), z0 = rr.Next(g.h), ww = 1 + rr.Next(6), hh = 1 + rr.Next(6);
                            for (int z = z0; z < Math.Min(g.h, z0 + hh); z++) for (int x = x0; x < Math.Min(g.w, x0 + ww); x++) g.water[z * g.w + x] = a.a != 0;
                            break;
                        }
                        default: g.dry = a.a != 0; break;
                    }
                    Invariants(g, a.ToString());
                    // observation tallies
                    for (int i = 0; i < g.pools.Count; i++)
                    {
                        for (int j = i + 1; j < g.pools.Count; j++) if (g.pools[i].cells.Intersect(g.pools[j].cells).Any()) { OverlapObs++; i = g.pools.Count; break; }
                    }
                    foreach (Pool p in g.pools)
                        if (p.cells.Count > 1) { var set = new HashSet<int>(p.cells); int[] lab = OracleLabels(g.w, g.h, Enumerable.Range(0, g.w * g.h).Select(c => set.Contains(c)).ToArray()); if (lab.Max() > 0) FragmentObs++; }
                }
            }
            catch (Exception e) { return e.Message; }
            return null;
        }

        private static List<Act> Gen(Random r, int len)
        {
            var l = new List<Act>();
            for (int i = 0; i < len; i++)
            {
                int k = r.Next(100);
                int[] dec = { 250, 2500, 20000, 60000, 240000 };
                if (k < 22) l.Add(new Act { kind = 0, a = dec[r.Next(dec.Length)] });
                else if (k < 62) l.Add(new Act { kind = 1, a = new[] { 1, 250, 250, 2500, 15000, 60000 }[r.Next(6)] });
                else if (k < 78) l.Add(new Act { kind = 2, a = 1 + r.Next(30), b = r.Next(1000) });
                else if (k < 92) l.Add(new Act { kind = 3, a = r.Next(2), b = r.Next(1000) });
                else l.Add(new Act { kind = 4, a = r.Next(2) });
            }
            return l;
        }

        public static List<string> Sequences(int n, int baseSeed)
        {
            var fails = new List<string>();
            for (int k = 0; k < n && fails.Count < 5; k++)
            {
                int seed = baseSeed + k; var r = new Random(seed);
                var acts = Gen(r, 8 + r.Next(60)); Cases++;
                if (RunSeq(seed, acts) == null) continue;
                var min = AxisFuzz.Shrink(acts, t => RunSeq(seed, t) != null);
                fails.Add($"pool seed {seed}: {RunSeq(seed, min)} | {string.Join(" ", min)}");
            }
            return fails;
        }

        public static void Report(Func<int, int> N, Func<int, int> S, string only, ref bool ok)
        {
            var fam = new (string name, Func<List<string>> run)[]
            {
                ("prim", () => Prims(N(20000), S(1))),
                ("pool", () => Sequences(N(5000), S(1))),
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
            Console.WriteLine($"pool coverage: components {Comps}, pools made {PoolsMade}, removed {Removed} (reconnected {Reconnects}), detect passes {Detects}, shoreline-first picks {EdgeFirstChecks}, last-cell fallbacks {FallbackLast}");
            Console.WriteLine($"pool observations (design, not failure): overlapping tracked pools {OverlapObs} steps, components left uncovered by a pool {UncoveredObs}, pools fragmented by decay {FragmentObs}, ghost pools re-made from decayed wet cells {GhostObs}");
        }

        public static bool Run(double scale, int? oneSeed, string only)
        {
            bool ok = true;
            Report(n => oneSeed.HasValue ? 1 : (int)(n * scale), s => oneSeed ?? s, only, ref ok);
            return ok;
        }
    }
}
