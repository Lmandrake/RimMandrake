// Approach B for LeaningScrub: seeded fuzz over the Verse-free kernels the mod calls (../Kernel/*.cs):
//   lean      heading lock, alignment, scent threat, downwind fire pick, step rounding, the Shed V (RM_LeanKernel)
//   smother   the claim clock / maturation gate / yield and stacks (RM_SmotherKernel), as action sequences
//   blaze     the open-fire cluster, stamper dispatch and the one-message-per-blaze rule (RM_BlazeKernel)
//   guardian  the bark-warden disturbance meter, stages, forgiveness and the double-roost rule (RM_GuardianKernel)
//   forms     scratch clocks, lash, rearing, quench, the hoard grow-in clock (RM_FormsKernel), as action sequences
//   walk      the walking stands' march: stands, leading edge, runners, cap, tail dying (RM_FormsKernel.Walk)
//   coat      the coat rub, the felt store and the runway bloom cooldown / delayed answers (RM_CoatKernel)
// A failing action sequence is shrunk (delta debugging) and printed as `family seed N: message | actions`.
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;

namespace RimMandrake.LeaningScrub.SelfTest
{
    internal static partial class LeaningScrubFuzz
    {
        public static long Cases, Steps;
        private static void Check(bool ok, string msg) { if (!ok) throw new Exception(msg); }
        private static bool Near(double a, double b, double eps) { return Math.Abs(a - b) <= eps; }

        internal struct Act
        {
            public int kind, a, b;
            public string[] names;
            public override string ToString() { return (names != null && kind < names.Length ? names[kind] : "k" + kind) + "(" + a + "," + b + ")"; }
        }

        internal static List<T> Shrink<T>(List<T> acts, Func<List<T>, bool> fails)
        {
            var cur = new List<T>(acts);
            for (int chunk = Math.Max(1, cur.Count / 2); chunk >= 1; chunk /= 2)
            {
                bool progress = true;
                while (progress)
                {
                    progress = false;
                    for (int i = 0; i + chunk <= cur.Count; i++)
                    {
                        var trial = new List<T>(cur);
                        trial.RemoveRange(i, chunk);
                        if (fails(trial)) { cur = trial; progress = true; break; }
                    }
                }
            }
            return cur;
        }

        private static string Drive(int seed, Func<Random, List<Act>> gen, Func<int, List<Act>, string> run)
        {
            var acts = gen(new Random(seed));
            string err = run(seed, acts);
            if (err == null) return null;
            var small = Shrink(acts, t => run(seed, t) != null);
            return run(seed, small) + " | " + string.Join(" ", small);
        }

        private static List<string> Family(string name, int n, int baseSeed, Func<int, string> one)
        {
            var fails = new List<string>();
            for (int k = 0; k < n && fails.Count < 5; k++)
            {
                Cases++;
                try { string e = one(baseSeed + k); if (e != null) fails.Add($"{name} seed {baseSeed + k}: {e}"); }
                catch (Exception e) { fails.Add($"{name} seed {baseSeed + k}: {e.Message} {(e is IndexOutOfRangeException || e is ArgumentOutOfRangeException ? e.StackTrace : "")}"); }
            }
            return fails;
        }

        private static List<Act> GenActs(Random r, int minN, int maxN, int[] weights, string[] names)
        {
            int total = weights.Sum(), n = minN + r.Next(maxN - minN + 1);
            var l = new List<Act>();
            for (int i = 0; i < n; i++)
            {
                int w = r.Next(total), kind = 0;
                while (w >= weights[kind]) { w -= weights[kind]; kind++; }
                l.Add(new Act { kind = kind, a = r.Next(1000), b = r.Next(1000), names = names });
            }
            return l;
        }

        // ════════════════════════ lean ════════════════════════
        public static long ScentThreats, FirePicks, ShedCellsMade, LockedHeadings;

        private static string Lean(int seed)
        {
            var r = new Random(seed);
            // heading lock: the first answer sticks forever
            float first = (float)(r.NextDouble() * 360.0), later = (float)(r.NextDouble() * 360.0);
            float h = RM_LeanKernel.LockHeading(-1f, first);
            Check(h == first, "an unset heading did not take the roll");
            Check(RM_LeanKernel.LockHeading(h, later) == first, "a locked heading changed on a later ask");
            Check(RM_LeanKernel.LockHeading(0f, later) == 0f, "a heading of exactly 0 degrees was treated as unset");
            LockedHeadings++;

            float heading = (float)(r.NextDouble() * 360.0);
            if (r.Next(6) == 0) heading = new[] { 0f, 45f, 90f, 135f, 180f, 225f, 270f, 315f, 360f }[r.Next(9)];
            float dx, dz;
            RM_LeanKernel.Direction(heading, out dx, out dz);
            Check(Near(Math.Sqrt((double)dx * dx + (double)dz * dz), 1.0, 1e-5), $"direction of {heading} is not a unit vector ({dx},{dz})");
            Check(Near(dx, Math.Cos(heading * Math.PI / 180.0), 1e-4) && Near(dz, Math.Sin(heading * Math.PI / 180.0), 1e-4), "direction is not (cos, sin) of the heading");

            // alignment against a double oracle, antisymmetry, scale invariance, zero for a tiny displacement
            for (int t = 0; t < 12; t++)
            {
                int ax = r.Next(-30, 31), az = r.Next(-30, 31);
                float al = RM_LeanKernel.Alignment(ax, az, dx, dz);
                double mag = Math.Sqrt((double)ax * ax + (double)az * az);
                if (ax == 0 && az == 0) Check(al == 0f, "alignment of the zero displacement is not 0");
                else
                {
                    double oracle = (ax * (double)dx + az * (double)dz) / mag;
                    Check(Near(al, oracle, 1e-5), $"alignment ({ax},{az}) = {al}, oracle {oracle}");
                    Check(al >= -1.00001f && al <= 1.00001f, $"alignment {al} outside [-1,1]");
                    Check(Near(RM_LeanKernel.Alignment(-ax, -az, dx, dz), -al, 1e-5), "alignment is not antisymmetric");
                    Check(Near(RM_LeanKernel.Alignment(ax * 2, az * 2, dx, dz), al, 1e-5), "alignment depends on distance");
                }
            }

            // the eight neighbours: 3 or 4 lie within ~72 degrees of the wind, every one passes the double oracle, none opposite
            int[] idx = new int[8];
            int nd = RM_LeanKernel.DownwindNeighbours(dx, dz, idx);
            Check(nd >= 3 && nd <= 4, $"{nd} downwind neighbours at heading {heading} (a 145-degree window over 45-degree spacing must hold 3 or 4)");
            for (int i = 0; i < 8; i++)
            {
                double c = (RM_LeanKernel.NeighbourDx[i] * (double)dx + RM_LeanKernel.NeighbourDz[i] * (double)dz) / Math.Sqrt(RM_LeanKernel.NeighbourDx[i] * RM_LeanKernel.NeighbourDx[i] + RM_LeanKernel.NeighbourDz[i] * RM_LeanKernel.NeighbourDz[i]);
                bool listed = idx.Take(nd).Contains(i);
                if (Math.Abs(c - 0.3) > 1e-4) Check(listed == (c > 0.3), $"neighbour {i} cos {c:F4} listed={listed}");
            }
            Check(idx.Take(nd).Distinct().Count() == nd, "a neighbour was listed twice");

            // fire pick: bias 0 or no lean is vanilla; bias 1 always picks a downwind neighbour; every downwind neighbour is reachable
            Check(RM_LeanKernel.FireSpreadPick(false, 1f, 0f, dx, dz, 0.5f) == -1, "a map without the Lean biased a fire");
            Check(RM_LeanKernel.FireSpreadPick(true, 0f, 0f, dx, dz, 0.5f) == -1, "bias 0 still steered a fire");
            Check(RM_LeanKernel.FireSpreadPick(true, 0.5f, 0.5f, dx, dz, 0.5f) == -1, "a bias roll equal to the bias must fall through to vanilla (Rand.Chance is value < chance)");
            Check(RM_LeanKernel.FireSpreadPick(true, 0.5f, 0.4999f, dx, dz, 0.5f) >= 0, "a bias roll under the bias did not steer");
            var reached = new HashSet<int>();
            for (int k = 0; k <= 20; k++)
            {
                int p = RM_LeanKernel.FireSpreadPick(true, 1f, 0f, dx, dz, k / 20f);
                Check(p >= 0 && idx.Take(nd).Contains(p), $"pick {p} is not a downwind neighbour");
                reached.Add(p); FirePicks++;
            }
            Check(reached.Count == nd, $"only {reached.Count} of {nd} downwind neighbours are reachable by the pick roll");

            // step: banker's rounding, never the origin for k = +-1, antisymmetric
            int sx, sz, tx, tz;
            RM_LeanKernel.Step(0, 0, dx, dz, 1f, out sx, out sz);
            RM_LeanKernel.Step(0, 0, dx, dz, -1f, out tx, out tz);
            Check(sx != 0 || sz != 0, $"Step(1) at heading {heading} is the origin: the leading edge test would read the stand's own cell");
            Check(tx == -sx && tz == -sz, "Step(-1) is not the mirror of Step(1)");
            int k2 = r.Next(1, 6);
            RM_LeanKernel.Step(10, -7, dx, dz, k2, out sx, out sz);
            Check(sx == 10 + (int)Math.Round((double)(dx * k2), MidpointRounding.ToEven) && sz == -7 + (int)Math.Round((double)(dz * k2), MidpointRounding.ToEven), "step does not round like Mathf.RoundToInt");

            // scent: the first threat in order; a threat is alive, within range, upwind (cos >= 0.7) and fleeable
            int np = r.Next(0, 8);
            var pdx = new int[np]; var pdz = new int[np]; var dead = new bool[np]; var canFlee = new bool[np];
            float range = new[] { 5f, 12f, 25f }[r.Next(3)];
            int expect = -1;
            for (int i = 0; i < np; i++)
            {
                pdx[i] = r.Next(-30, 31); pdz[i] = r.Next(-30, 31);
                if (r.Next(3) == 0 && (pdx[i] != 0 || pdz[i] != 0)) { double m = Math.Sqrt(pdx[i] * (double)pdx[i] + pdz[i] * (double)pdz[i]); pdx[i] = (int)Math.Round(dx * Math.Min(range - 1, 3 + r.Next(30)) ); pdz[i] = (int)Math.Round(dz * Math.Min(range - 1, 3 + r.Next(30))); }
                dead[i] = r.Next(5) == 0; canFlee[i] = r.Next(4) != 0;
            }
            int called = 0;
            int got = RM_LeanKernel.FirstScentThreat(np, pdx, pdz, dead, range, dx, dz, i => { called++; return canFlee[i]; });
            for (int i = 0; i < np && expect < 0; i++)
            {
                if (dead[i] || (double)pdx[i] * pdx[i] + (double)pdz[i] * pdz[i] > (double)range * range) continue;
                double mg = Math.Sqrt((double)pdx[i] * pdx[i] + (double)pdz[i] * pdz[i]);
                double c = mg < 0.1 ? 0 : (pdx[i] * (double)dx + pdz[i] * (double)dz) / mg;
                if (Math.Abs(c - 0.7) < 1e-4) { expect = got; break; }   // on the boundary: either answer is acceptable
                if (c >= 0.7 && canFlee[i]) expect = i;
            }
            Check(got == expect, $"scent chose {got}, spec {expect}");
            if (got >= 0) ScentThreats++;

            // the Shed V: counts, downwind, symmetric about the root
            int length = r.Next(1, 14);
            var cx = new List<int>(); var cz = new List<int>();
            RM_LeanKernel.ShedCells(5, 5, dx, dz, length, 1f, () => 0.5f, cx, cz);
            int expectCells = 0; for (int d = 1; d <= length; d++) expectCells += 2 * (d / 3) + 1;
            Check(cx.Count == expectCells, $"shed V of length {length} has {cx.Count} cells, spec {expectCells}");
            for (int i = 0; i < cx.Count; i++)
            {
                int ox = cx[i] - 5, oz = cz[i] - 5;
                Check(ox != 0 || oz != 0, "the shed V put litter on the root cell");
                Check(ox * (double)dx + oz * (double)dz > 0, $"shed cell ({ox},{oz}) lies upwind at heading {heading}");
                Check(Math.Sqrt(ox * (double)ox + oz * (double)oz) <= length + 0.75 + length / 3.0, "shed cell farther than the V allows");
            }
            ShedCellsMade += cx.Count;
            cx.Clear(); cz.Clear();
            RM_LeanKernel.ShedCells(5, 5, dx, dz, length, 0f, () => 0.5f, cx, cz);
            Check(cx.Count == 0, "cellChance 0 still shed litter");
            int rolls = 0;
            RM_LeanKernel.ShedCells(5, 5, dx, dz, length, 0.3f, () => { rolls++; return (float)r.NextDouble(); }, cx, cz);
            Check(rolls == expectCells, $"the V drew {rolls} rolls for {expectCells} cells");
            cx.Clear(); cz.Clear();
            RM_LeanKernel.ShedCells(5, 5, dx, dz, -3, 1f, () => 0f, cx, cz);
            Check(cx.Count == 1, "a non-positive length must still shed one cell");
            return null;
        }

        // ════════════════════════ smother ════════════════════════
        private static readonly string[] SmNames = { "Start", "Tick", "Feature", "Days", "Reload", "Despawn", "Pass" };
        public static long Matured, SecondStarts, SmPasses;

        private sealed class Claim { public int start = -1; public bool spawned = true, matured; public int gone = -1; }

        private static string RunSmother(int seed, List<Act> acts)
        {
            var r = new Random(seed ^ 0x77);
            int now = 100000 + r.Next(5000);
            float days = new[] { 0.05f, 0.1f, 1f, 2.5f, 30f }[r.Next(5)];
            bool feature = true;
            var claims = new List<Claim>();
            for (int i = 0; i < 4; i++) claims.Add(new Claim());
            var registered = new HashSet<Claim>();
            int step = 0;
            foreach (var a in acts)
            {
                step++; Steps++;
                string where = " at step " + step + " " + a;
                Claim c = claims[a.a % claims.Count];
                switch (a.kind)
                {
                    case 0: // Start a smother
                        if (c.matured || !c.spawned) break;
                        int before = c.start;
                        int s = RM_SmotherKernel.Start(c.start, now);
                        if (before >= 0) { Check(s == before, "a second smother moved the start tick" + where); SecondStarts++; }
                        else Check(s == now, "the first smother did not start now" + where);
                        c.start = s; registered.Add(c);
                        break;
                    case 1: // time passes
                        now += 1 + a.b % 4000;
                        break;
                    case 2: feature = !feature; break;
                    case 3: days = new[] { 0.05f, 0.1f, 1f, 2.5f, 30f, 1e9f, float.PositiveInfinity }[a.b % 7]; break;
                    case 4: // reload: Smothered claims re-register, clocks unchanged
                        foreach (var cl in claims) if (cl.spawned && !cl.matured && cl.start >= 0) registered.Add(cl);
                        break;
                    case 5: // the plant is cut or burned: it deregisters and its claim ends
                        if (c.spawned && !c.matured) { c.spawned = false; registered.Remove(c); }
                        break;
                    case 6: // the MapComponentTick of the last interval boundary
                        {
                            int tick = now - now % RM_SmotherKernel.CheckInterval;
                            if (!RM_SmotherKernel.PassRuns(registered.Count, tick, feature))
                            {
                                Check(registered.Count == 0 || !feature, "a pass with claims on file and the feature on did not run" + where);
                                break;
                            }
                            SmPasses++;
                            int claim = RM_SmotherKernel.ClaimTicks(days);
                            var due = new List<Claim>();
                            foreach (var cl in registered)
                            {
                                int rem = RM_SmotherKernel.TicksRemaining(cl.start, claim, tick);
                                if (RM_SmotherKernel.Due(cl.spawned, rem)) due.Add(cl);
                            }
                            foreach (var cl in due)
                            {
                                Check((long)tick - cl.start >= claim, "a claim matured before its time" + where);
                                Check(feature, "a claim matured with the feature off" + where);
                                Check(!cl.matured, "a claim matured twice" + where);
                                cl.matured = true; cl.gone = tick; registered.Remove(cl); Matured++;
                            }
                            foreach (var cl in registered)
                                Check(RM_SmotherKernel.TicksRemaining(cl.start, claim, tick) > 0, "a due claim survived its pass" + where);
                            break;
                        }
                }
                // invariants after every step
                int claimTicks = RM_SmotherKernel.ClaimTicks(days);
                Check(claimTicks >= 1 && claimTicks <= int.MaxValue / 2, "claim ticks left [1, max/2]: " + claimTicks + where);
                foreach (var cl in claims)
                {
                    int rem = RM_SmotherKernel.TicksRemaining(cl.start, claimTicks, now);
                    if (cl.start < 0) { Check(rem == -1 && !RM_SmotherKernel.Smothered(cl.start), "an unsmothered stand reports a claim" + where); }
                    else
                    {
                        Check(RM_SmotherKernel.Smothered(cl.start), "smothered stand reads unsmothered" + where);
                        Check((long)rem == (long)cl.start + claimTicks - now, "remaining is not start + claim - now (overflow?)" + where);
                    }
                }
            }
            return null;
        }

        private static string SmotherUnits(int seed)
        {
            var r = new Random(seed ^ 0x1234);
            for (int t = 0; t < 40; t++)
            {
                int yieldCount = r.Next(0, 80);
                float g1 = (float)r.NextDouble(), g2 = g1 + (float)r.NextDouble() * (1f - g1);
                float factor = new[] { 0f, 0.5f, 1f, 2f }[r.Next(4)];
                int y1 = RM_SmotherKernel.YieldCount(yieldCount, g1, factor), y2 = RM_SmotherKernel.YieldCount(yieldCount, g2, factor);
                Check(y1 >= 1 && y2 >= 1, "yield below one");
                Check(y2 >= y1, $"yield fell as growth rose ({g1} -> {g2}): {y1} -> {y2}");
                Check(RM_SmotherKernel.YieldCount(yieldCount, 0.05f, factor) == RM_SmotherKernel.YieldCount(yieldCount, 0.3f, factor), "growth under 0.3 should floor at 0.3");
                double spec = yieldCount * Math.Max(0.3, g2) * factor;
                Check(y2 == Math.Max(1, (int)Math.Round(spec)) || Math.Abs(spec - Math.Floor(spec) - 0.5) < 1e-3, $"yield {y2} vs spec {spec}");
                int limit = new[] { 0, 1, 7, 75, 500 }[r.Next(5)];
                var sizes = new List<int>();
                RM_SmotherKernel.Stacks(y2, limit, sizes);
                Check(sizes.Sum() == y2, "stacks do not sum to the yield");
                Check(sizes.All(x => x >= 1 && x <= Math.Max(1, limit)), "a stack is empty or over the limit");
                int el = Math.Max(1, limit);
                Check(sizes.Count == (y2 + el - 1) / el, "wrong number of stacks");
            }
            Check(RM_SmotherKernel.ClaimTicks(1f) == 60000 && RM_SmotherKernel.ClaimTicks(0f) == 6000 && RM_SmotherKernel.ClaimTicks(-5f) == 6000, "claim ticks floor/day wrong");
            Check(RM_SmotherKernel.ClaimTicks(float.NaN) >= 1, "a NaN claim length must not wrap");
            Check(RM_SmotherKernel.ClaimTicks(1e12f) == int.MaxValue / 2, "a huge claim length must saturate");
            Check(!RM_SmotherKernel.PassRuns(0, 2500, true) && !RM_SmotherKernel.PassRuns(3, 2499, true) && !RM_SmotherKernel.PassRuns(3, 2500, false) && RM_SmotherKernel.PassRuns(3, 5000, true), "pass gate truth table");
            Check(RM_SmotherKernel.Due(true, 0) && RM_SmotherKernel.Due(true, -5) && !RM_SmotherKernel.Due(true, 1) && !RM_SmotherKernel.Due(false, -5), "due truth table");
            return null;
        }

        // ════════════════════════ blaze ════════════════════════
        public static long Blazes, NoBlazes, Messages, Convs;

        private static string BlazeCase(int seed)
        {
            var r = new Random(seed);
            int n = r.Next(0, 45);
            var xs = new int[n]; var zs = new int[n];
            int cxs = r.Next(-50, 50), czs = r.Next(-50, 50), spread = new[] { 3, 6, 14, 40 }[r.Next(4)];
            for (int i = 0; i < n; i++) { xs[i] = cxs + r.Next(-spread, spread + 1); zs[i] = czs + r.Next(-spread, spread + 1); }
            int min = RM_BlazeKernel.MinOpenFires; float rad = RM_BlazeKernel.ClusterRadius;
            var cnt = new int[n];
            for (int i = 0; i < n; i++) for (int j = 0; j < n; j++) if ((double)(xs[i] - xs[j]) * (xs[i] - xs[j]) + (double)(zs[i] - zs[j]) * (zs[i] - zs[j]) <= (double)rad * rad) cnt[i]++;
            int best = -1, bc = min - 1;
            for (int i = 0; i < n; i++) if (cnt[i] > bc) { bc = cnt[i]; best = i; }
            int got = RM_BlazeKernel.FindBlaze(n, xs, zs, min, rad);
            Check(got == best, $"blaze index {got}, spec {best} ({n} fires)");
            if (got >= 0) { Blazes++; Check(cnt[got] >= min, "blaze cluster smaller than the minimum"); }
            else { NoBlazes++; Check(cnt.All(c => c < min), "no blaze reported though a cluster of the minimum size exists"); }
            // translation and permutation do not change the cluster size
            int dxs = r.Next(-1000, 1000), dzs = r.Next(-1000, 1000);
            var xs2 = xs.Select(x => x + dxs).ToArray(); var zs2 = zs.Select(z => z + dzs).ToArray();
            Check(RM_BlazeKernel.FindBlaze(n, xs2, zs2, min, rad) == got, "translating the fires changed the blaze");
            var perm = Enumerable.Range(0, n).OrderBy(_ => r.Next()).ToArray();
            int gp = RM_BlazeKernel.FindBlaze(n, perm.Select(i => xs[i]).ToArray(), perm.Select(i => zs[i]).ToArray(), min, rad);
            Check((gp >= 0) == (got >= 0), "permuting the fires changed whether there is a blaze");
            if (gp >= 0) Check(cnt[perm[gp]] == cnt[got], "permuting the fires changed the blaze size");
            // dispatch table
            int px = r.Next(-9, 10), pz = r.Next(-9, 10), gx = r.Next(-9, 10), gz = r.Next(-9, 10);
            bool onGoto = r.Next(2) == 0;
            int act = RM_BlazeKernel.ConvergeAction(px, pz, 0, 0, onGoto, gx, gz);
            bool atBlaze = px * px + pz * pz <= RM_BlazeKernel.StampRadius * RM_BlazeKernel.StampRadius;
            bool near = gx * gx + gz * gz <= RM_BlazeKernel.ClusterRadius * RM_BlazeKernel.ClusterRadius;
            int spec = atBlaze ? 0 : (onGoto && near ? 1 : 2);
            Check(act == spec, $"converge action {act}, spec {spec}");
            Convs++;
            // stamping reach: the 2.9-cell disc
            Check(RM_BlazeKernel.Stamps(0, 0, 2, 2) && RM_BlazeKernel.Stamps(0, 0, 1, 2) && !RM_BlazeKernel.Stamps(0, 0, 3, 0) && !RM_BlazeKernel.Stamps(0, 0, 2, 3), "stamp reach table");
            return null;
        }

        private static readonly string[] BlNames = { "AddBlaze", "AddFire", "Burn", "Pass", "Drift" };

        private static string RunBlazeSeq(int seed, List<Act> acts)
        {
            var fires = new List<int[]>();
            bool lastValid = false; int lx = 0, lz = 0;
            int msgs = 0;
            int step = 0;
            foreach (var a in acts)
            {
                step++; Steps++;
                string where = " at step " + step + " " + a;
                switch (a.kind)
                {
                    case 0: // a cluster of six
                        for (int i = 0; i < 6; i++) fires.Add(new[] { a.a % 60 - 30 + i % 3, a.b % 60 - 30 + i / 3 });
                        break;
                    case 1: fires.Add(new[] { a.a % 60 - 30, a.b % 60 - 30 }); break;
                    case 2: fires.Clear(); break;
                    case 4: // the whole fire list creeps by a cell
                        foreach (var f in fires) { f[0] += a.a % 3 - 1; f[1] += a.b % 3 - 1; }
                        break;
                    case 3:
                        {
                            int[] xs = fires.Select(f => f[0]).ToArray(), zs = fires.Select(f => f[1]).ToArray();
                            int idx = RM_BlazeKernel.FindBlaze(fires.Count, xs, zs, RM_BlazeKernel.MinOpenFires, RM_BlazeKernel.ClusterRadius);
                            if (idx < 0) { lastValid = false; break; }
                            bool isNew = RM_BlazeKernel.NewBlaze(lastValid, lx, lz, xs[idx], zs[idx]);
                            double d = Math.Sqrt((double)(xs[idx] - lx) * (xs[idx] - lx) + (double)(zs[idx] - lz) * (zs[idx] - lz));
                            bool specNew = !lastValid || d > 12.0;
                            if (Math.Abs(d - 12.0) > 1e-9) Check(isNew == specNew, "new-blaze verdict wrong" + where);
                            if (isNew) { msgs++; Messages++; }
                            lastValid = true; lx = xs[idx]; lz = zs[idx];
                            break;
                        }
                }
                Steps++;
            }
            return null;
        }
    }
}
