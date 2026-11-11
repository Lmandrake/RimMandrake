// Seeded fuzz of titan breakthrough clearing (Kernel/RM_TitanClearingKernel.cs, TITAN_BREAKTHROUGH_CLEARING_1), against oracles
// written here from the item and the rulings, never from the kernel:
//   clearing   eligibility: a building only when the crush table allows it at this tier and it is destroyable, not natural rock,
//              not a quest object, not friendly-owned and not a trunk; a giant only for a smasher (T3 by default) with a live
//              owner and no quest tag. Worth: unreachable always; reachable only past factor x AND MinSavingTicks; bad numbers never.
//              Choose: breach first, probe second, none when neither is clearable and worth it. Cadence and give-up bound.
//   line       the straight-line probe's cells: unit orthogonal steps (so a one-cell-thick wall is never stepped over), no repeat,
//              each step closer to the end, ends on the end unless capped, never longer than the cap.
//   lane       the item's own verify, simulated: a lane fully sealed by walls and giant trunks (no detour) is broken through and
//              the titan arrives whenever every seal cell on its way is clearable at its tier; a lane whose straight way meets a
//              protected building is never struck at all; an open gap with a short detour is walked round, never smashed.
//   clearingdeterminism every family replays a seed identically.
using System;
using System.Collections.Generic;

namespace RimMandrake.HugeThings.SelfTest
{
    internal static class ClearingFuzz
    {
        public static long Cases, Checks, Arrived, ProtectedStops, Detoured;

        private static void Check(bool ok, string msg)
        {
            Checks++;
            if (!ok) throw new Exception(msg);
        }

        private static bool OracleSmashes(int tier, int minTier, bool on) => on && tier >= 1 && tier <= 3 && minTier >= 1 && minTier <= 3 && tier >= minTier;

        internal static string CaseClearing(int seed)
        {
            var r = new Random(seed);
            int tier = r.Next(0, 5) - (r.Next(8) == 0 ? 1 : 0);
            bool crush = r.Next(2) == 0, destroyable = r.Next(6) != 0, natural = r.Next(6) == 0, quest = r.Next(6) == 0,
                 friendly = r.Next(5) == 0, trunk = r.Next(6) == 0;
            bool be = TitanClearing.BuildingEligible(tier, crush, destroyable, natural, quest, friendly, trunk);
            bool beWant = tier >= 1 && tier <= 3 && crush && destroyable && !natural && !quest && !friendly && !trunk;
            Check(be == beWant, "BuildingEligible(" + tier + "," + crush + "," + destroyable + "," + natural + "," + quest + "," + friendly + "," + trunk + ") = " + be);

            int minTier = r.Next(10) == 0 ? (r.Next(2) == 0 ? 0 : 4) : r.Next(1, 4);
            bool smash = r.Next(5) != 0, alive = r.Next(6) != 0, tq = r.Next(6) == 0;
            bool te = TitanClearing.TrunkEligible(tier, minTier, smash, alive, tq);
            Check(te == (OracleSmashes(tier, minTier, smash) && alive && !tq), "TrunkEligible wrong at tier " + tier + " min " + minTier);
            if (tier == 1 || tier == 2) Check(!TitanClearing.TrunkEligible(tier, 3, true, true, false), "a T1/T2 titan smashes a giant on the default ladder");

            bool reach = r.Next(3) != 0;
            float by = (float)(r.NextDouble() * 4000), through = (float)(r.NextDouble() * 2000);
            if (r.Next(15) == 0) by = r.Next(2) == 0 ? float.NaN : float.PositiveInfinity;
            if (r.Next(15) == 0) through = -1f;
            float factor = (float)(r.NextDouble() * 8);
            if (r.Next(20) == 0) factor = float.NaN;
            float f = float.IsNaN(factor) ? 2.5f : Math.Min(6f, Math.Max(1.5f, factor));
            bool finite = !float.IsNaN(by) && !float.IsInfinity(by) && by >= 0 && through >= 0;
            bool worthWant = !reach || (finite && by > f * through && by - through >= 240f);
            Check(TitanClearing.Worth(reach, by, through, factor) == worthWant,
                  "Worth(" + reach + "," + by + "," + through + "," + factor + ") wrong");
            Check(Math.Abs(TitanClearing.SaneFactor(factor) - f) < 1e-6, "SaneFactor(" + factor + ") out of its slider range");

            ClearKind bk = (ClearKind)r.Next(0, 3), pk = (ClearKind)r.Next(0, 3);
            float bc = (float)(r.NextDouble() * 2000), pc = (float)(r.NextDouble() * 2000);
            ClearSource want = ClearSource.None;
            bool byOk = !float.IsNaN(by) && !float.IsInfinity(by) && by >= 0;
            if (bk != ClearKind.None && (!reach || (byOk && by > f * bc && by - bc >= 240f))) want = ClearSource.Breach;
            else if (pk != ClearKind.None && (!reach || (byOk && by > f * pc && by - pc >= 240f))) want = ClearSource.Probe;
            ClearSource got = TitanClearing.Choose(reach, by, factor, bk, bc, pk, pc);
            Check(got == want, "Choose picked " + got + ", want " + want);

            int tick = r.Next(-5, 3000);
            Check(TitanClearing.StrikeDue(tick) == (tick >= 0 && tick % 60 == 0), "StrikeDue(" + tick + ")");
            int s = r.Next(0, 80);
            Check(TitanClearing.GiveUp(s) == (s >= 40), "GiveUp(" + s + ")");
            Check(TitanClearing.Active(true, true, true) && !TitanClearing.Active(false, true, true) && !TitanClearing.Active(true, false, true)
                  && !TitanClearing.Active(true, true, false), "clearing is not master AND wake AND its own toggle");
            return (be ? "1" : "0") + (te ? "1" : "0") + (int)got;
        }

        internal static string CaseLine(int seed)
        {
            var r = new Random(seed);
            int x0 = r.Next(-40, 40), z0 = r.Next(-40, 40), x1 = r.Next(-40, 40), z1 = r.Next(-40, 40);
            int cap = r.Next(4) == 0 ? r.Next(1, 30) : 400;
            List<int[]> cells = TitanClearing.LineCells(x0, z0, x1, z1, cap);
            int manhattan = Math.Abs(x1 - x0) + Math.Abs(z1 - z0);
            Check(cells.Count <= cap, "line longer than its cap");
            Check(cells.Count == Math.Min(cap, manhattan), "line has " + cells.Count + " cells, want " + Math.Min(cap, manhattan) + " (unit orthogonal steps)");
            int px = x0, pz = z0;
            var seen = new HashSet<long>();
            foreach (int[] c in cells)
            {
                Check(Math.Abs(c[0] - px) + Math.Abs(c[1] - pz) == 1, "a step that is not one orthogonal cell (could jump a wall)");
                Check(Math.Abs(x1 - c[0]) + Math.Abs(z1 - c[1]) == Math.Abs(x1 - px) + Math.Abs(z1 - pz) - 1, "a step away from the end");
                Check(seen.Add(((long)c[0] << 32) ^ (uint)c[1]), "a repeated cell");
                px = c[0];
                pz = c[1];
            }
            if (cap >= manhattan && manhattan > 0) Check(px == x1 && pz == z1, "the line does not end on its end");
            return cells.Count.ToString();
        }

        private const int Open = 0, Wall = 1, Trunk = 2, Protected = 3;

        /// <summary>Shortest 4-connected walk (in steps) through open cells, or -1.</summary>
        private static int Bfs(int[,] g, int sx, int sz, int dx, int dz)
        {
            int w = g.GetLength(0), h = g.GetLength(1);
            var dist = new int[w, h];
            for (int x = 0; x < w; x++) for (int z = 0; z < h; z++) dist[x, z] = -1;
            var q = new Queue<int[]>();
            dist[sx, sz] = 0;
            q.Enqueue(new[] { sx, sz });
            int[] ox = { 1, -1, 0, 0 }, oz = { 0, 0, 1, -1 };
            while (q.Count > 0)
            {
                int[] c = q.Dequeue();
                if (c[0] == dx && c[1] == dz) return dist[dx, dz];
                for (int i = 0; i < 4; i++)
                {
                    int nx = c[0] + ox[i], nz = c[1] + oz[i];
                    if (nx < 0 || nz < 0 || nx >= w || nz >= h || dist[nx, nz] >= 0 || g[nx, nz] != Open) continue;
                    dist[nx, nz] = dist[c[0], c[1]] + 1;
                    q.Enqueue(new[] { nx, nz });
                }
            }
            return -1;
        }

        internal static string CaseLane(int seed)
        {
            var r = new Random(seed);
            int w = r.Next(14, 32), h = r.Next(5, 14);
            int tier = r.Next(1, 4), minTier = r.Next(1, 4);
            bool smash = r.Next(4) != 0;
            int scenario = r.Next(3);   // 0 sealed by walls + trunks, 1 a protected building on the way, 2 an open gap (detour)
            var g = new int[w, h];
            var hp = new int[w, h];
            int seal = r.Next(w / 3 + 1, 2 * w / 3);
            int sx = r.Next(1, w / 3), sz = r.Next(0, h), dx = r.Next(2 * w / 3 + 1, w - 1), dz = r.Next(0, h);
            for (int z = 0; z < h; z++)
            {
                g[seal, z] = r.Next(2) == 0 ? Wall : Trunk;
                hp[seal, z] = r.Next(1, 6);
            }
            int protectedAt = -1, gapAt = -1;
            if (scenario == 1)
            {
                // Put the protected building exactly where the straight way first meets the seal column.
                foreach (int[] c in TitanClearing.LineCells(sx, sz, dx, dz, 400))
                    if (c[0] == seal) { protectedAt = c[1]; break; }
                g[seal, protectedAt] = Protected;
            }
            if (scenario == 2)
            {
                gapAt = r.Next(0, h);
                g[seal, gapAt] = Open;
            }
            bool wallOk = tier >= 2;                         // the crush table's Wall row: crushable from T2
            bool trunkOk = OracleSmashes(tier, minTier, smash);
            float ticks = 13f, factor = (float)(1.5 + r.NextDouble() * 4.5);

            // Judged on the lane as built, before any strike opens more of it.
            int detour0 = Bfs(g, sx, sz, dx, dz);
            float through0 = TitanClearing.StraightCost(dx - sx, dz - sz, ticks);
            bool longDetour = detour0 >= 0 && detour0 * ticks > TitanClearing.SaneFactor(factor) * through0 && detour0 * ticks - through0 >= 240f;
            int px = sx, pz = sz, strikes = 0, protectedStrikes = 0;
            bool arrived = false;
            for (int iter = 0; iter < 2000 && !arrived; iter++)
            {
                int steps = Bfs(g, px, pz, dx, dz);
                bool reach = steps >= 0;
                int ex = px, ez = pz, prevX = px, prevZ = pz;
                ClearKind kind = ClearKind.None;
                foreach (int[] c in TitanClearing.LineCells(px, pz, dx, dz, TitanClearing.ProbeMaxCells))
                {
                    int t = g[c[0], c[1]];
                    if (t != Open)
                    {
                        ex = c[0];
                        ez = c[1];
                        kind = t == Wall ? (TitanClearing.BuildingEligible(tier, wallOk, true, false, false, false, false) ? ClearKind.Building : ClearKind.None)
                             : t == Trunk ? (TitanClearing.TrunkEligible(tier, minTier, smash, true, false) ? ClearKind.Trunk : ClearKind.None)
                             : (TitanClearing.BuildingEligible(tier, false, true, false, false, false, false) ? ClearKind.Building : ClearKind.None);
                        break;
                    }
                    prevX = c[0];
                    prevZ = c[1];
                }
                float straight = TitanClearing.StraightCost(dx - px, dz - pz, ticks);
                ClearSource pick = TitanClearing.Choose(reach, reach ? steps * ticks : -1f, factor, ClearKind.None, -1f, kind, straight);
                if (pick == ClearSource.Probe)
                {
                    Check(kind != ClearKind.None, "a clearing picked an obstacle it may not strike");
                    if (g[ex, ez] == Protected) protectedStrikes++;
                    strikes++;
                    px = prevX;
                    pz = prevZ;
                    if (--hp[ex, ez] <= 0) g[ex, ez] = Open;
                    continue;
                }
                if (reach) { arrived = true; break; }   // walks (round); the sim does not need the route
                break;                                  // sealed and nothing clearable: gives up, vanilla fails
            }

            Check(protectedStrikes == 0, "a protected building was struck " + protectedStrikes + " times");
            if (scenario == 0)
            {
                // Every seal cell the straight way can meet is clearable: it must get through.
                bool allOk = true;
                for (int z = 0; z < h; z++) if (g[seal, z] == Wall && !wallOk || g[seal, z] == Trunk && !trunkOk) allOk = false;
                if (allOk) Check(arrived, "a lane sealed only by clearable walls/trunks was not broken through (tier " + tier + ")");
                if (allOk) Arrived++;
            }
            if (scenario == 1)
            {
                Check(protectedStrikes == 0 && strikes == 0, "the protected lane was struck at all (" + strikes + " strikes)");
                Check(!arrived, "a lane sealed by a protected building on the way was passed");
                ProtectedStops++;
            }
            if (scenario == 2)
            {
                Check(detour0 >= 0, "the gap lane is not reachable (sim bug)");
                if (!longDetour) Check(strikes == 0, "a short detour was smashed through instead of walked (" + strikes + " strikes)");
                Check(arrived, "a reachable lane was not arrived at");
                if (!longDetour) Detoured++;
            }
            return scenario + ":" + strikes + ":" + (arrived ? 1 : 0);
        }

        private static bool Family(string name, int n, int? one, Func<int, string> run)
        {
            int fails = 0, ran = 0;
            for (int i = 0; i < n; i++)
            {
                int seed = one ?? (i * 7919 + name.Length * 104729);
                Cases++;
                ran++;
                try
                {
                    run(seed);
                }
                catch (Exception e)
                {
                    if (fails++ < 5) Console.WriteLine("FAIL " + name + " seed " + seed + ": " + e.Message);
                }
                if (one.HasValue) break;
            }
            Console.WriteLine((fails == 0 && ran > 0 ? "PASS " : "FAIL ") + name + ": " + ran + " cases, " + fails + " failed");
            return fails == 0 && ran > 0;
        }

        public static readonly string[] Families = { "clearing", "line", "lane", "clearingdeterminism" };

        public static bool Run(double scale, int? one, string only)
        {
            int N(int baseN) => Math.Max(scale > 0 ? 1 : 0, (int)(baseN * scale));
            bool ok = true;
            if (only == null || only == "clearing") ok &= Family("clearing", N(8000), one, CaseClearing);
            if (only == null || only == "line") ok &= Family("line", N(4000), one, CaseLine);
            if (only == null || only == "lane") ok &= Family("lane", N(3000), one, CaseLane);
            if (only == null || only == "clearingdeterminism")
                ok &= Family("clearingdeterminism", N(300), one, s =>
                {
                    Check(CaseClearing(s) == CaseClearing(s) && CaseLine(s) == CaseLine(s) && CaseLane(s) == CaseLane(s), "a seed replayed differently");
                    return "";
                });
            // Blindness guard: the lane family must have seen all three outcomes it asserts.
            if (only == null && !one.HasValue && scale >= 1 && (Arrived == 0 || ProtectedStops == 0 || Detoured == 0))
            {
                Console.WriteLine("FAIL lane fuzz is blind: arrived " + Arrived + ", protected stops " + ProtectedStops + ", short detours " + Detoured);
                ok = false;
            }
            Console.WriteLine("titan clearing fuzz: " + Cases + " cases, " + Checks + " checks; lanes broken through " + Arrived
                              + ", protected stops " + ProtectedStops + ", short detours walked " + Detoured);
            return ok;
        }
    }
}
