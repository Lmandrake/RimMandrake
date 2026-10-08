// Approach B for the Gravship Landing reveal: seeded fuzz over the Verse-free kernel (../Kernel/RM_LandingKernel.cs) against a MODEL of
// the engine's FloodFillerFog.FloodUnfog (decompiled 1.6, RimSage 2026-10-08: 4-connected flood through FOGGED cells whose edifice does
// not make fog, then every fogged fog-making neighbour of an unfogged cell, 8-connected, is unfogged too):
//   world  random walled / roofed / part-unfogged grids and rects (some hanging off the map): final fog compared cell by cell with an
//          independent component spec; one flood per fogged unroofed component; idempotent; cells outside the rect never seed a flood
//   gate   Enabled and IsRoot exhaustively
//   units  edge cases (empty rect, 1x1 map, rect wholly off the map)
// A failing case is printed as `family seed N: message | detail`; --fuzz-seed N replays it.
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;

namespace RimMandrake.GravshipLanding.SelfTest
{
    internal static class GravshipLandingFuzz
    {
        public static long Cases, Steps, Floods, WallsUnfogged, SealedRooms, OpenRoomsLeaked;
        private static void Check(bool ok, string msg) { if (!ok) throw new Exception(msg); }

        private sealed class Grid : IRevealWorld
        {
            public int W, H;
            public bool[,] fog, roof, wall;
            public int floods;
            public Grid(int w, int h) { W = w; H = h; fog = new bool[w, h]; roof = new bool[w, h]; wall = new bool[w, h]; }
            public Grid Clone() { var g = new Grid(W, H); Array.Copy(fog, g.fog, fog.Length); Array.Copy(roof, g.roof, roof.Length); Array.Copy(wall, g.wall, wall.Length); return g; }
            public bool InBounds(int x, int z) { return x >= 0 && z >= 0 && x < W && z < H; }
            public bool IsFogged(int x, int z) { Check(InBounds(x, z), "IsFogged asked out of bounds"); return fog[x, z]; }
            public bool IsRoofed(int x, int z) { Check(InBounds(x, z), "IsRoofed asked out of bounds"); return roof[x, z]; }
            public bool BlocksFog(int x, int z) { Check(InBounds(x, z), "BlocksFog asked out of bounds"); return wall[x, z]; }
            private bool Pass(int x, int z) { return fog[x, z] && !wall[x, z]; }
            // the model of FloodFillerFog.FloodUnfog
            public void FloodUnfog(int x, int z)
            {
                floods++;
                var newly = new List<(int, int)>();
                var stack = new Stack<(int, int)>();
                if (Pass(x, z)) { stack.Push((x, z)); }
                var seen = new HashSet<(int, int)>();
                while (stack.Count > 0)
                {
                    var (cx, cz) = stack.Pop();
                    if (!seen.Add((cx, cz)) || !Pass(cx, cz)) continue;
                    newly.Add((cx, cz));
                    foreach (var (dx, dz) in new[] { (1, 0), (-1, 0), (0, 1), (0, -1) })
                        if (InBounds(cx + dx, cz + dz) && Pass(cx + dx, cz + dz)) stack.Push((cx + dx, cz + dz));
                }
                foreach (var (cx, cz) in newly) fog[cx, cz] = false;
                var border = new HashSet<(int, int)>();
                foreach (var (cx, cz) in newly)
                    for (int dx = -1; dx <= 1; dx++)
                        for (int dz = -1; dz <= 1; dz++)
                        {
                            int nx = cx + dx, nz = cz + dz;
                            if (InBounds(nx, nz) && fog[nx, nz] && !Pass(nx, nz)) border.Add((nx, nz));
                        }
                foreach (var (nx, nz) in border) fog[nx, nz] = false;
            }
        }

        private static string Dump(Grid g)
        {
            var sb = new System.Text.StringBuilder();
            for (int z = g.H - 1; z >= 0; z--) { for (int x = 0; x < g.W; x++) sb.Append(g.wall[x, z] ? (g.fog[x, z] ? 'W' : 'w') : g.roof[x, z] ? (g.fog[x, z] ? 'R' : 'r') : (g.fog[x, z] ? 'O' : 'o')); sb.Append('/'); }
            return sb.ToString();
        }

        private static void Case(int seed)
        {
            var r = new Random(seed);
            int W = r.Next(1, 25), H = r.Next(1, 25);
            var g = new Grid(W, H);
            double pw = r.NextDouble() * 0.45, pr = r.NextDouble(), pu = r.Next(3) == 0 ? r.NextDouble() * 0.3 : 0;
            // a roofed block (a building) so sealed rooms exist
            int bx = r.Next(0, W), bz = r.Next(0, H), bw = r.Next(1, 8), bh = r.Next(1, 8);
            for (int x = 0; x < W; x++)
                for (int z = 0; z < H; z++)
                {
                    g.wall[x, z] = r.NextDouble() < pw;
                    g.roof[x, z] = (x >= bx && x < bx + bw && z >= bz && z < bz + bh) ? r.NextDouble() < 0.85 : r.NextDouble() < pr * 0.2;
                    g.fog[x, z] = r.NextDouble() >= pu;
                }
            // the rect: the whole map, or a sub-rect, possibly hanging off the edges
            int rx = r.Next(2) == 0 ? 0 : r.Next(-3, W), rz = r.Next(2) == 0 ? 0 : r.Next(-3, H);
            int rw = r.Next(2) == 0 ? W + 3 : r.Next(0, W + 4), rh = r.Next(2) == 0 ? H + 3 : r.Next(0, H + 4);
            Steps += W * H;
            var before = g.Clone();
            var after = g.Clone();
            int roots = RM_LandingKernel.Reveal(after, rx, rz, rw, rh);

            // ---- spec ----
            var comp = new int[W, H];
            int nc = 0;
            var members = new List<List<(int, int)>>();
            for (int x = 0; x < W; x++)
                for (int z = 0; z < H; z++)
                {
                    if (comp[x, z] != 0 || !before.fog[x, z] || before.wall[x, z]) continue;
                    nc++;
                    var list = new List<(int, int)>();
                    var q = new Queue<(int, int)>(); q.Enqueue((x, z)); comp[x, z] = nc;
                    while (q.Count > 0)
                    {
                        var (cx, cz) = q.Dequeue(); list.Add((cx, cz));
                        foreach (var (dx, dz) in new[] { (1, 0), (-1, 0), (0, 1), (0, -1) })
                        {
                            int nx = cx + dx, nz = cz + dz;
                            if (nx >= 0 && nz >= 0 && nx < W && nz < H && comp[nx, nz] == 0 && before.fog[nx, nz] && !before.wall[nx, nz]) { comp[nx, nz] = nc; q.Enqueue((nx, nz)); }
                        }
                    }
                    members.Add(list);
                }
            var open = new bool[nc + 1];
            for (int x = Math.Max(0, rx); x < Math.Min(W, rx + rw); x++)
                for (int z = Math.Max(0, rz); z < Math.Min(H, rz + rh); z++)
                    if (comp[x, z] != 0 && !before.roof[x, z]) open[comp[x, z]] = true;
            int wantRoots = open.Count(b => b);
            Check(roots == wantRoots, $"{roots} floods started, one per fogged unroofed component = {wantRoots}");
            Check(after.floods == roots, "the kernel reported " + roots + " roots but the world saw " + after.floods + " floods");
            Floods += roots;
            var want = before.Clone();
            for (int c = 1; c <= nc; c++) if (open[c]) foreach (var (x, z) in members[c - 1]) want.fog[x, z] = false;
            for (int x = 0; x < W; x++)
                for (int z = 0; z < H; z++)
                {
                    if (!before.fog[x, z] || !before.wall[x, z]) continue;
                    for (int dx = -1; dx <= 1; dx++)
                        for (int dz = -1; dz <= 1; dz++)
                        {
                            int nx = x + dx, nz = z + dz;
                            if (nx >= 0 && nz >= 0 && nx < W && nz < H && comp[nx, nz] != 0 && open[comp[nx, nz]] && want.fog[x, z]) { want.fog[x, z] = false; WallsUnfogged++; }
                        }
                }
            for (int x = 0; x < W; x++)
                for (int z = 0; z < H; z++)
                    Check(after.fog[x, z] == want.fog[x, z], $"cell ({x},{z}) fog is {after.fog[x, z]}, spec says {want.fog[x, z]}");
            // properties the item promises
            for (int c = 1; c <= nc; c++)
            {
                bool anyUnroofed = members[c - 1].Any(p => !before.roof[p.Item1, p.Item2]);
                if (!anyUnroofed) { SealedRooms++; foreach (var (x, z) in members[c - 1]) Check(after.fog[x, z], $"a fully roofed sealed component was unfogged at ({x},{z})"); }
                else if (members[c - 1].Any(p => before.roof[p.Item1, p.Item2]) && open[c]) OpenRoomsLeaked++;
            }
            // idempotent
            var again = after.Clone();
            Check(RM_LandingKernel.Reveal(again, rx, rz, rw, rh) == 0, "a second reveal started floods again");
            Check(Dump(again) == Dump(after), "a second reveal changed the fog");
            // unrelated cells are never refogged
            for (int x = 0; x < W; x++) for (int z = 0; z < H; z++) Check(!(after.fog[x, z] && !before.fog[x, z]), "a reveal REFOGGED a cell");
        }

        private static List<string> World(int n, int seed)
        {
            var fails = new List<string>();
            for (int i = 0; i < n; i++)
            {
                Cases++;
                try { Case(seed + i); } catch (Exception e) { fails.Add($"world seed {seed + i}: {e.Message}"); if (fails.Count >= 3) break; }
            }
            return fails;
        }

        private static List<string> Gate()
        {
            var fails = new List<string>();
            try
            {
                for (int m = 0; m < 8; m++) { Cases++; Steps++; bool o = (m & 1) != 0, a = (m & 2) != 0, s = (m & 4) != 0; Check(RM_LandingKernel.Enabled(o, a, s) == (o && a && s), $"Enabled({o},{a},{s})"); }
                for (int m = 0; m < 16; m++)
                {
                    Cases++; Steps++;
                    bool ib = (m & 1) != 0, f = (m & 2) != 0, ro = (m & 4) != 0, bl = (m & 8) != 0;
                    Check(RM_LandingKernel.IsRoot(ib, f, ro, bl) == (ib && f && !ro && !bl), $"IsRoot({ib},{f},{ro},{bl})");
                }
            }
            catch (Exception e) { fails.Add("gate seed 0: " + e.Message); }
            return fails;
        }

        private static List<string> Units()
        {
            var fails = new List<string>();
            Action<string, Action> t = (name, a) => { Cases++; Steps++; try { a(); } catch (Exception e) { fails.Add("units seed 0: " + name + ": " + e.Message); } };
            t("empty rect", () => { var g = new Grid(5, 5); for (int x = 0; x < 5; x++) for (int z = 0; z < 5; z++) g.fog[x, z] = true; Check(RM_LandingKernel.Reveal(g, 2, 2, 0, 3) == 0 && RM_LandingKernel.Reveal(g, 2, 2, 3, 0) == 0, "an empty rect started a flood"); });
            t("rect wholly off the map", () => { var g = new Grid(5, 5); for (int x = 0; x < 5; x++) for (int z = 0; z < 5; z++) g.fog[x, z] = true; Check(RM_LandingKernel.Reveal(g, 10, 10, 4, 4) == 0 && RM_LandingKernel.Reveal(g, -9, -9, 4, 4) == 0, "an off-map rect started a flood"); });
            t("1x1 map", () => { var g = new Grid(1, 1); g.fog[0, 0] = true; Check(RM_LandingKernel.Reveal(g, 0, 0, 1, 1) == 1 && !g.fog[0, 0], "a 1x1 open fogged map was not revealed"); });
            t("a walled-in unroofed cell is a root only for itself", () =>
            {
                var g = new Grid(3, 3);
                for (int x = 0; x < 3; x++) for (int z = 0; z < 3; z++) { g.fog[x, z] = true; g.wall[x, z] = !(x == 1 && z == 1); }
                Check(RM_LandingKernel.Reveal(g, 0, 0, 3, 3) == 1, "walled cell not revealed exactly once");
                Check(!g.fog[1, 1] && !g.fog[0, 0] && !g.fog[2, 2], "the ring of walls around an opened cell stays fogged (vanilla unfogs the border)");
            });
            t("an open door lets the flood into a roofed room (vanilla behaviour, recorded)", () =>
            {
                var g = new Grid(5, 1);
                for (int x = 0; x < 5; x++) { g.fog[x, 0] = true; g.roof[x, 0] = x >= 2; }
                RM_LandingKernel.Reveal(g, 0, 0, 5, 1);
                Check(g.fog.Cast<bool>().All(f => !f), "a roofed room joined to open ground by an unwalled gap stayed fogged; the mod text says roofed interiors stay hidden, the engine flood reveals them when they are connected");
            });
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
                ("gate", () => Gate()),
                ("world", () => World(N(8000), S(1))),
                ("units", () => Units()),
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
            if ((only == null || only == "world") && !oneSeed.HasValue && scale >= 1)
            {
                Console.WriteLine($"world reached: floods {Floods}, walls unfogged {WallsUnfogged}, sealed roofed components {SealedRooms}, open-connected roofed components {OpenRoomsLeaked}");
                if (Floods == 0 || WallsUnfogged == 0 || SealedRooms == 0 || OpenRoomsLeaked == 0) { Console.WriteLine("FAIL world fuzz never reached a flood / border wall / sealed room / connected room (blind)"); ok = false; }
            }
            Console.WriteLine($"gravshiplanding fuzz: {Cases} cases, {Steps} steps, {sw.Elapsed.TotalSeconds:F2}s total -> {(ok ? "OK" : "FAILED")}");
            return ok;
        }
    }
}
