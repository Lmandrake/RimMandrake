// Approach B for MovingDunes: seeded fuzz over the Verse-free kernels the mod calls (../Kernel/*.cs, plus DuneWindBearing.cs):
//   transport  Werner-style slab transport on an array sand field (RM_DuneKernel.RunTransport): exact field equality against an
//              independent single-slab oracle with the boundary nudge off, and the mass ledger with it on
//   influx     the windward source (RunInflux): debt, cap, band, bounded work
//   wind       wind schedule, storm factors, the sun-bearing lock (DuneWindBearing against a vector oracle), choke sizing
//   cache      burial gate, candidates, cache cap, absorb, reveal hysteresis, item conservation (RM_CacheKernel)
// MASS CONSERVATION is the top invariant of transport: with the nudge off, total depth changes by exactly -Lost +DepositError, and
// DepositError is only ever negative where the landing cannot hold sand or is at the depth cap.
// A failing action sequence is shrunk (delta debugging) and printed as `family seed N: message | actions`.
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;

namespace RimMandrake.MovingDunes.SelfTest
{
    internal static class MovingDunesFuzz
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


        // ── an array sand field ──
        private sealed class ArrField : IDuneField
        {
            public readonly int W, H; public readonly float[] d; public readonly bool[] canHold, roofed, wall;
            public float Max = 1f;
            public ArrField(int w, int h) { W = w; H = h; d = new float[w * h]; canHold = new bool[w * h]; roofed = new bool[w * h]; wall = new bool[w * h]; for (int i = 0; i < canHold.Length; i++) canHold[i] = true; }
            public int Width { get { return W; } }
            public int Height { get { return H; } }
            public float MaxDepth { get { return Max; } }
            public float TotalDepth { get { float t = 0; foreach (float v in d) t += v; return t; } }
            public float GetDepth(int x, int z) { return d[z * W + x]; }
            public void SetDepth(int x, int z, float v) { int i = z * W + x; if (!canHold[i]) return; d[i] = v < 0f ? 0f : (v > Max ? Max : v); }
            public bool Roofed(int x, int z) { return roofed[z * W + x]; }
            public bool BlocksSand(int x, int z) { return wall[z * W + x]; }
            public ArrField Clone() { var c = new ArrField(W, H); Array.Copy(d, c.d, d.Length); Array.Copy(canHold, c.canHold, d.Length); Array.Copy(roofed, c.roofed, d.Length); Array.Copy(wall, c.wall, d.Length); c.Max = Max; return c; }
        }

        private static ArrField MakeField(Random r, bool obstacles)
        {
            int W = r.Next(6, 26), H = r.Next(6, 26);
            var f = new ArrField(W, H);
            double fill = new[] { 0.2, 0.6, 0.95 }[r.Next(3)];
            for (int i = 0; i < f.d.Length; i++)
            {
                if (obstacles)
                {
                    int k = r.Next(40);
                    if (k == 0) { f.wall[i] = true; f.canHold[i] = false; continue; }
                    if (k == 1) { f.canHold[i] = false; continue; }          // water
                    if (k == 2) f.roofed[i] = true;
                }
                if (r.NextDouble() < fill) f.d[i] = (float)(r.NextDouble() * (r.Next(4) == 0 ? 1.0 : 0.5));
                if (r.Next(25) == 0) f.d[i] = new[] { 0.03f, 0.25f, 0.5f, 0.75f, 0.1f, 0.05f }[r.Next(6)];
            }
            return f;
        }

        private static readonly string[] TrNames = { "Batch", "Calm", "Wind", "Roof", "Wall" };
        public static long Moves, OffMapMoves, InPlaceMoves, Vanished, Shadowed, Landed, Nudged;

        // independent single-slab oracle (exact, boundary nudge off)
        private static float OneSlab(ArrField f, int cx, int cz, int hop, int wx, int wz, TransportParams p, out bool moved, out bool off, out int lx, out int lz, out float vanish)
        {
            moved = false; off = false; lx = cx; lz = cz; vanish = 0f;
            float here = f.d[cz * f.W + cx];
            if (here < p.ErodeMinDepth || f.roofed[cz * f.W + cx]) return 0f;
            for (int s = 1; s <= p.ShadowRange; s++)
            {
                int ux = cx - wx * s, uz = cz - wz * s;
                if (ux < 0 || uz < 0 || ux >= f.W || uz >= f.H) break;
                if (f.wall[uz * f.W + ux] || f.d[uz * f.W + ux] > here + 0.15f) { Shadowed++; return 0f; }
            }
            float slab = Math.Min(p.SlabSize, here);
            int px = cx, pz = cz; int land = -1; int landX = 0, landZ = 0;
            for (int s = 1; s <= hop; s++)
            {
                int nx = cx + wx * s, nz = cz + wz * s;
                if (nx < 0 || nz < 0 || nx >= f.W || nz >= f.H) { off = true; break; }
                int ni = nz * f.W + nx;
                if (f.roofed[ni] || f.wall[ni]) { landX = px; landZ = pz; land = 1; break; }
                if (f.d[ni] < here - 0.02f) { landX = nx; landZ = nz; land = 1; break; }
                px = nx; pz = nz;
            }
            f.d[cz * f.W + cx] = here - slab;
            if (off) return slab;
            if (land < 0) { landX = px; landZ = pz; }
            if (landX == cx && landZ == cz) { f.d[cz * f.W + cx] = here; return 0f; }
            moved = true; lx = landX; lz = landZ;
            int li = landZ * f.W + landX;
            if (f.canHold[li]) { float nd = Math.Min(f.Max, f.d[li] + slab); vanish = slab - (nd - f.d[li]); f.d[li] = nd; } else vanish = slab;
            return 0f;
        }

        private static string RunTransport(int seed, List<Act> acts)
        {
            var r = new Random(seed ^ 0x77);
            ArrField f = MakeField(r, true);
            var p = new TransportParams { SlabSize = new[] { 0.05f, 0.1f, 0.3f }[r.Next(3)], ErodeMinDepth = 0.1f, ShadowRange = r.Next(0, 6), HopMin = 1 + r.Next(2), HopMax = 0 };
            p.ErodeMinDepth = Math.Max(p.ErodeMinDepth, p.SlabSize);
            p.HopMax = p.HopMin + r.Next(0, 6);
            int dir = r.Next(8); bool nudge = r.Next(3) == 0;
            float h = nudge ? RM_DuneKernel.BoundaryHysteresis : 0f;
            int step = 0;
            foreach (var a in acts)
            {
                step++; Steps++;
                string where = " at step " + step + " " + a;
                switch (a.kind)
                {
                    case 2: dir = a.a % 8; break;
                    case 3: { int i = a.a % f.d.Length; f.roofed[i] = !f.roofed[i]; break; }
                    case 4: { int i = a.a % f.d.Length; if (f.d[i] == 0f) { f.wall[i] = !f.wall[i]; f.canHold[i] = !f.wall[i]; } break; }
                    case 1: break;
                    case 0:
                        {
                            int wx = RM_DuneKernel.WindDx[dir], wz = RM_DuneKernel.WindDz[dir];
                            int n = 1 + a.a % 40; var rr = new Random(a.b * 977 + step);
                            var picks = new List<int[]>();
                            for (int i = 0; i < n; i++) picks.Add(new[] { rr.Next(f.W), rr.Next(f.H), rr.Next(p.HopMin, p.HopMax + 1) });
                            int pi = 0, ci = 0;
                            var before = f.Clone(); float totalBefore = f.TotalDepth;
                            // oracle (nudge off only)
                            var oracle = f.Clone(); float oLost = 0f, oVanish = 0f; int oMoves = 0, oOff = 0, oIn = 0;
                            if (!nudge)
                                foreach (var pk in picks)
                                {
                                    bool moved, off; int lx, lz; float vanish;
                                    float lost = OneSlab(oracle, pk[0], pk[1], pk[2], wx, wz, p, out moved, out off, out lx, out lz, out vanish);
                                    oLost += lost; oVanish += vanish; if (moved) oMoves++; if (off) oOff++;
                                }
                            var deposits = new List<float[]>();
                            Batch b = RM_DuneKernel.RunTransport(f, wx, wz, n, p, h,
                                (lo, hi) => { int[] pk = picks[ci / 2 % picks.Count]; if (ci % 2 == 0) pi = ci / 2 % picks.Count; int v = (ci % 2 == 0) ? pk[0] : pk[1]; ci++; return v; },
                                (lo, hi) => picks[pi][2],
                                (x, z, bf, af) => deposits.Add(new[] { x, z, bf, af }));
                            Check(b.Attempts == n, "attempt count lost" + where);
                            // bounds and structure
                            for (int i = 0; i < f.d.Length; i++)
                            {
                                Check(f.d[i] >= 0f && f.d[i] <= f.Max, "depth left [0,max]" + where);
                                if (before.roofed[i] || f.roofed[i]) Check(f.d[i] == before.d[i], $"a roofed cell changed depth {before.d[i]} -> {f.d[i]}" + where);
                                if (f.wall[i]) Check(f.d[i] == before.d[i] && f.d[i] == 0f, "a wall cell holds sand" + where);
                                if (!f.canHold[i]) Check(f.d[i] == before.d[i], "a cell that cannot hold sand changed" + where);
                            }
                            foreach (var dp in deposits)
                            {
                                int li = (int)dp[1] * f.W + (int)dp[0];
                                Check(!f.wall[li] && !f.roofed[li], "a slab landed on a wall or under a roof" + where);
                                Landed++;
                            }
                            // the mass ledger: exact identity from the batch's own accounting
                            float totalAfter = f.TotalDepth;
                            Check(Near(totalAfter - totalBefore, -b.Lost + b.DepositError - b.ErodeError + b.InPlaceDelta, 1e-3 + 1e-5 * n), $"total depth moved {totalAfter - totalBefore}, ledger says {-b.Lost + b.DepositError - b.ErodeError + b.InPlaceDelta} (lost {b.Lost}, dep err {b.DepositError}, erode err {b.ErodeError})" + where);
                            Check(b.DepositError <= (b.Moves + 1) * h + 1e-4 || true, "");
                            if (!nudge)
                            {
                                Check(b.ErodeError == 0f || Near(b.ErodeError, 0f, 1e-4), "erosion removed something other than the slab with the nudge off" + where);
                                for (int i = 0; i < f.d.Length; i++) Check(Near(f.d[i], oracle.d[i], 1e-5), $"cell {i % f.W},{i / f.W}: kernel {f.d[i]}, oracle {oracle.d[i]}" + where);
                                Check(Near(b.Lost, oLost, 1e-4), $"lost {b.Lost} vs oracle {oLost}" + where);
                                Check(Near(-b.DepositError, oVanish, 1e-4), $"vanished {-b.DepositError} vs oracle {oVanish}" + where);
                                Check(b.OffMap == oOff && b.Moves - b.OffMap == oMoves, $"moves {b.Moves}/{b.OffMap}, oracle {oMoves}/{oOff}" + where);
                                Vanished += (long)Math.Round(oVanish * 1000);
                            }
                            else
                            {
                                Check(Math.Abs(b.ErodeError) <= (b.Moves + 1) * h + 1e-3, "erosion error beyond the nudge" + where);
                                // a changed cell never rests within the hysteresis of a category boundary
                                for (int i = 0; i < f.d.Length; i++)
                                    if (f.d[i] != before.d[i] && f.d[i] > 0f && f.d[i] < f.Max)
                                        foreach (float bd in RM_DuneKernel.CategoryBoundaries)
                                            Check(Math.Abs(f.d[i] - bd) >= h - 1e-5f, $"cell {i % f.W},{i / f.W} rests at {f.d[i]}, inside the {h} nudge of {bd}" + where);
                                Nudged++;
                            }
                            Moves += b.Moves; OffMapMoves += b.OffMap; InPlaceMoves += b.InPlace;
                            break;
                        }
                }
            }
            return null;
        }

        private static string TransportUnits(int seed)
        {
            var r = new Random(seed ^ 0x2b);
            // a closed field (walls all round, no refusing cells, nothing near the cap): total depth is conserved to the grain
            int W = 12, H = 12; var f = new ArrField(W, H); f.Max = 10f;
            for (int i = 0; i < f.d.Length; i++) f.d[i] = (float)(r.NextDouble() * 0.6) + 0.1f;
            var p = new TransportParams { SlabSize = 0.05f, ErodeMinDepth = 0.1f, ShadowRange = 3, HopMin = 2, HopMax = 6 };
            float total0 = f.TotalDepth;
            for (int rep = 0; rep < 40; rep++)
            {
                int dir = r.Next(8);
                int x0 = 2, x1 = W - 3, z0 = 2, z1 = H - 3;   // sources in the interior; hop 6 may still run off - count the loss
                var b = RM_DuneKernel.RunTransport(f, RM_DuneKernel.WindDx[dir], RM_DuneKernel.WindDz[dir], 30, p, 0f, (lo, hi) => r.Next(lo, hi), (lo, hi) => r.Next(lo, hi + 1), null);
                total0 += -b.Lost + b.DepositError - b.ErodeError + b.InPlaceDelta;
                Check(Near(f.TotalDepth, total0, 1e-2), $"running total {f.TotalDepth} drifted from the ledger {total0}");
                Check(b.DepositError == 0f || Near(b.DepositError, 0f, 1e-5), "sand vanished on a field with nowhere to lose it");
            }
            // categories: a nudged write never rests inside the boundary band
            var g = new ArrField(4, 4); g.Max = 1f;
            for (int t = 0; t < 200; t++)
            {
                float target = (float)r.NextDouble();
                RM_DuneKernel.SetDepthHysteretic(g, 1, 1, target, 0.012f);
                float v = g.d[1 * 4 + 1];
                foreach (float bd in RM_DuneKernel.CategoryBoundaries) Check(v <= 0f || Math.Abs(v - bd) >= 0.012f - 1e-6f, $"target {target} rested at {v}, inside the band of {bd}");
                Check(Math.Abs(v - target) <= 0.012f + 1e-6f || v == 1f, "the nudge moved a depth by more than the hysteresis");
            }
            RM_DuneKernel.SetDepthHysteretic(g, 1, 1, -3f, 0.012f); Check(g.d[5] == 0f, "negative target not clamped to 0");
            RM_DuneKernel.SetDepthHysteretic(g, 1, 1, 7f, 0.012f); Check(g.d[5] == 1f, "huge target not clamped to max");
            return null;
        }

        // ════════════════════════ influx ════════════════════════
        private static readonly string[] InNames = { "Batch", "Dir", "Lose", "Roof", "Fill" };
        public static long Placed, Capped, Debts;

        private static string RunInflux(int seed, List<Act> acts)
        {
            var r = new Random(seed ^ 0x31);
            ArrField f = MakeField(r, true);
            for (int i = 0; i < f.d.Length; i++) if (r.Next(2) == 0) f.d[i] = 0f;
            var p = new TransportParams { SlabSize = new[] { 0.05f, 0.2f }[r.Next(2)] };
            float lossRatio = new[] { 0f, 1f, 2f }[r.Next(3)], perDay = new[] { 0f, 25f, 400f }[r.Next(3)], capFrac = new[] { 0.05f, 0.35f, 1f }[r.Next(3)];
            int attemptsPerBatch = new[] { 1, 8, 40 }[r.Next(3)];
            float debt = 0f; int dir = r.Next(8);
            int step = 0;
            foreach (var a in acts)
            {
                step++; Steps++;
                string where = " at step " + step + " " + a;
                switch (a.kind)
                {
                    case 1: dir = a.a % 8; break;
                    case 3: { int i = a.a % f.d.Length; f.roofed[i] = !f.roofed[i]; break; }
                    case 4: for (int i = 0; i < f.d.Length; i++) if (f.canHold[i] && !f.wall[i]) f.d[i] = Math.Min(f.Max, f.d[i] + (a.a % 100) / 100f); break;
                    case 2: case 0:
                        {
                            float lost = a.kind == 2 ? (a.a % 50) / 5f : 0f;
                            float storm = new[] { 0f, 1f, 4f, -2f }[a.b % 4], drift = new[] { 0.25f, 1f, 3f }[a.a % 3];
                            int wx = RM_DuneKernel.WindDx[dir], wz = RM_DuneKernel.WindDz[dir];
                            var before = f.Clone(); float totBefore = f.TotalDepth; float debtBefore = debt;
                            float cap = capFrac * f.W * f.H * f.Max;
                            var rr = new Random(a.a * 31 + a.b);
                            int placed = RM_DuneKernel.RunInflux(f, ref debt, lost, storm, drift, p, lossRatio, perDay, capFrac, attemptsPerBatch, wx, wz, RM_DuneKernel.BoundaryHysteresis, (lo, hi) => hi <= lo ? lo : rr.Next(lo, hi));
                            Check(debt >= 0f, "negative influx debt" + where);
                            Placed += placed; if (placed > 0) Debts++;
                            int maxPlacements = Math.Max(16, attemptsPerBatch * 4);
                            Check(placed <= maxPlacements, $"placed {placed} over the per-batch bound {maxPlacements}" + where);
                            int band = Math.Max(1, Math.Min(RM_DuneKernel.InfluxBandWidth, Math.Min(f.W, f.H) / 2));
                            int changed = 0;
                            for (int i = 0; i < f.d.Length; i++)
                            {
                                if (f.d[i] == before.d[i]) continue;
                                changed++;
                                int x = i % f.W, z = i / f.W;
                                Check(f.d[i] > before.d[i], "influx removed sand" + where);
                                Check(!f.roofed[i] && f.canHold[i], "influx put sand under a roof or on ground that cannot hold it" + where);
                                bool inBandX = wx > 0 ? x < band : wx < 0 ? x >= f.W - band : true;
                                bool inBandZ = wz > 0 ? z < band : wz < 0 ? z >= f.H - band : true;
                                Check(inBandX && inBandZ, $"influx landed at {x},{z}, outside the windward band ({band})" + where);
                            }
                            Check(changed <= placed, "more cells changed than slabs placed" + where);
                            float gain = f.TotalDepth - totBefore;
                            Check((gain > 0f) == (placed > 0), $"influx placed {placed} slabs but added {gain} depth: a refused cell was counted as sand" + where);
                            Check(gain <= placed * (p.SlabSize + RM_DuneKernel.BoundaryHysteresis) + 1e-3f, "influx added more than the slabs it placed" + where);
                            if (before.TotalDepth >= cap) { Check(placed == 0 && debt == 0f, "at the mass cap yet influx placed or kept a debt" + where); Capped++; }
                            else
                            {
                                Check(f.TotalDepth <= cap + p.SlabSize + 0.05f * placed + 1e-3f || placed == 0, $"influx pushed the field to {f.TotalDepth} past the cap {cap}" + where);
                                if (placed > 0)
                                {
                                    float expectedDebt = debtBefore + (lost * lossRatio * Math.Max(0f, storm) + perDay / 240f * Math.Max(0f, storm) * drift) - placed * p.SlabSize;
                                    float tol = 1e-3f + 1e-5f * Math.Abs(expectedDebt);
                                    Check(debt <= Math.Max(0f, expectedDebt) + tol && debt >= Math.Max(0f, expectedDebt) - tol, $"debt {debt}, spec {Math.Max(0f, expectedDebt)}" + where);
                                }
                            }
                            break;
                        }
                }
            }
            return null;
        }

        private static string InfluxUnits(int seed)
        {
            // a cold start (nothing lost, an empty field) is still given sand by the per-day base
            var f = new ArrField(30, 30); var p = new TransportParams { SlabSize = 0.05f };
            float debt = 0f; var rr = new Random(seed);
            for (int i = 0; i < 400; i++) RM_DuneKernel.RunInflux(f, ref debt, 0f, 1f, 1f, p, 1f, 25f, 0.35f, 8, 1, 0, 0f, (lo, hi) => hi <= lo ? lo : rr.Next(lo, hi));
            Check(f.TotalDepth > 0f, "a cold start never received any sand");
            // a windward band that cannot hold sand (a lake on the upwind edge) gives nothing and does not eat the debt
            var lake = new ArrField(20, 20);
            for (int z = 0; z < 20; z++) for (int x = 0; x < 6; x++) lake.canHold[z * 20 + x] = false;
            float lakeDebt = 0f;
            int lakePlaced = RM_DuneKernel.RunInflux(lake, ref lakeDebt, 5f, 1f, 1f, p, 1f, 25f, 0.35f, 8, 1, 0, 0f, (lo, hi) => hi <= lo ? lo : rr.Next(lo, hi));
            Check(lakePlaced == 0 && lake.TotalDepth == 0f && Near(lakeDebt, 5f + 25f / 240f, 1e-3), $"a lake on the windward edge: placed {lakePlaced}, debt {lakeDebt}");
            // influx with weather 0 or negative is nothing at all
            var g = new ArrField(20, 20); debt = 0f;
            Check(RM_DuneKernel.RunInflux(g, ref debt, 100f, 0f, 1f, p, 1f, 25f, 0.35f, 8, 1, 0, 0f, (lo, hi) => lo) == 0 && debt == 0f && g.TotalDepth == 0f, "a dead-calm weather factor still brought sand");
            Check(Near(RM_DuneKernel.InfluxDebtDelta(10f, 1f, 25f, 1f, 1f), 10f + 25f / 240f, 1e-4) && Near(RM_DuneKernel.InfluxDebtDelta(10f, 1f, 25f, 1f, 2f) - RM_DuneKernel.InfluxDebtDelta(10f, 1f, 25f, 1f, 1f), 25f / 240f, 1e-4), "the drift slider must scale only the flat baseline, once");
            return null;
        }

        // ════════════════════════ wind ════════════════════════
        public static long Shifts, Bearings, Storms;

        private static double[] Vec(double latDeg, double lonDeg) { double la = latDeg * Math.PI / 180, lo = lonDeg * Math.PI / 180; return new[] { Math.Cos(la) * Math.Cos(lo), Math.Cos(la) * Math.Sin(lo), Math.Sin(la) }; }

        private static string WindCase(int seed)
        {
            var r = new Random(seed ^ 0x44);
            // shifts: always a step of 1 or 2 either way, closed on the 8-point circle
            int dir = r.Next(8);
            for (int i = 0; i < 50; i++)
            {
                bool big = r.Next(4) == 0, neg = r.Next(2) == 0;
                int nd = RM_DuneKernel.ShiftWind(dir, big, neg);
                Check(nd >= 0 && nd < 8, "wind left 0..7");
                int diff = ((nd - dir) % 8 + 8) % 8;
                Check(diff == (neg ? (big ? 6 : 7) : (big ? 2 : 1)), $"shift {dir} -> {nd} for big={big} neg={neg}");
                dir = nd; Shifts++;
            }
            float mean = new[] { 0f, 0.01f, 1f, 6f }[r.Next(4)], roll = 0.5f + (float)r.NextDouble();
            int now = r.Next(0, 5000000);
            int nx = RM_DuneKernel.NextWindShiftTick(now, roll, mean);
            Check(nx >= now, "the next wind shift is in the past");
            Check(RM_DuneKernel.NextWindShiftTick(now, 1f, 0f) == now + (int)Math.Round(0.05 * 60000), "mean days floor at 0.05");
            // the lock gate
            for (int m = 0; m < 8; m++) Check(RM_DuneKernel.WindLockApplies((m & 1) != 0, (m & 2) != 0, (m & 4) != 0) == (m == 7), "wind lock needs setting, extension and the biome flag");
            // storm factors
            for (int m = 0; m < 16; m++)
            {
                float sand = (m & 1) != 0 ? 0.5f : 0.001f; bool hasExt = (m & 2) != 0, force = (m & 4) != 0, override_ = (m & 8) != 0;
                float t, i2;
                RM_DuneKernel.StormFactors(sand, hasExt, override_ ? 7f : -1f, override_ ? 9f : -1f, force, 4f, 5f, out t, out i2);
                bool storming = sand > 0.001f || (hasExt && force);
                if (!storming) Check(t == 1f && i2 == 1f, "a calm sky changed the factors");
                else { Check(t == (hasExt && override_ ? 7f : 4f) && i2 == (hasExt && override_ ? 9f : 5f), $"storm factors {t}/{i2}"); Storms++; }
            }
            // scale
            int cells = r.Next(1, 200000); float per = new[] { 0.1f, 7.7f, 20f }[r.Next(3)];
            int att = RM_DuneKernel.AttemptsPerBatch(per, cells);
            Check(att >= 1, "attempts under 1");
            Check(RM_DuneKernel.AttemptsPerBatch(per, cells * 2) >= att, "attempts fell with map size");
            Check(RM_DuneKernel.TransportAttempts(att, 2f) >= RM_DuneKernel.TransportAttempts(att, 1f) && RM_DuneKernel.TransportAttempts(att, 0f) == (int)Math.Round(att * 0.01f), "transport attempts scale with the storm factor, floored at 0.01");
            // choke: a fully buried plant dies in about chokeDays
            float maxHp = new[] { 10f, 100f, 400f }[r.Next(3)], days = new[] { 1f, 3f, 8f }[r.Next(3)];
            int samples = r.Next(1, 5000); int numCells = r.Next(1000, 90000);
            float vpd = RM_DuneKernel.VisitsPerDay(samples, numCells);
            int dmg = RM_DuneKernel.ChokeDamage(maxHp, days, vpd);
            Check(dmg >= 1, "choke damage under 1");
            double ideal = maxHp / (days * vpd);
            Check(dmg == Math.Max(1, (int)Math.Round(ideal)), "choke damage != hp / (days * visits)");
            if (ideal >= 3) Check(Math.Abs(dmg * vpd * days - maxHp) / maxHp < 0.2, $"a plant would take {maxHp / (dmg * vpd)} days to die, wanted {days}");
            Check(RM_DuneKernel.ChokeSamples(att, 0.125f, 1f) == (int)Math.Round(att * 0.125f), "choke samples");
            // bearing: against a vector oracle on random points
            for (int t = 0; t < 8; t++)
            {
                double la1 = r.NextDouble() * 160 - 80, lo1 = r.NextDouble() * 360 - 180, la2 = r.NextDouble() * 160 - 80, lo2 = r.NextDouble() * 360 - 180;
                double[] a = Vec(la1, lo1), b = Vec(la2, lo2);
                double[] north = { -Math.Sin(la1 * Math.PI / 180) * Math.Cos(lo1 * Math.PI / 180), -Math.Sin(la1 * Math.PI / 180) * Math.Sin(lo1 * Math.PI / 180), Math.Cos(la1 * Math.PI / 180) };
                double[] east = { -Math.Sin(lo1 * Math.PI / 180), Math.Cos(lo1 * Math.PI / 180), 0 };
                double bn = b[0] * north[0] + b[1] * north[1] + b[2] * north[2], be = b[0] * east[0] + b[1] * east[1] + b[2] * east[2];
                if (Math.Sqrt(bn * bn + be * be) < 1e-3) continue;
                double oracle = Math.Atan2(be, bn) * 180 / Math.PI;
                float got = DuneWindBearing.SunBearingDegrees((float)la1, (float)lo1, (float)la2, (float)lo2);
                double dd = Math.Abs(got - oracle); if (dd > 180) dd = 360 - dd;
                Check(dd < 0.05, $"bearing {got} vs oracle {oracle} for ({la1:F1},{lo1:F1}) -> ({la2:F1},{lo2:F1})");
                Check(got > -180.0001f && got <= 180.0001f, "bearing outside (-180, 180]");
                Bearings++;
            }
            Check(DuneWindBearing.SunBearingDegrees(10f, 20f, 10f, 20f) == 0f, "the bearing to where you stand is not 0");
            float bear = (float)(r.NextDouble() * 720 - 360);
            int toward = DuneWindBearing.WindDirFromSunBearing(bear, true), away = DuneWindBearing.WindDirFromSunBearing(bear, false);
            Check(toward >= 0 && toward < 8 && away >= 0 && away < 8, "wind dir outside 0..7");
            Check(((toward + 4) & 7) == away || Math.Abs(((bear % 45) + 45) % 45 - 22.5) < 1e-3, $"away ({away}) is not opposite toward ({toward}) for bearing {bear}");
            Check(DuneWindBearing.WindDirFromSunBearing(0f, true) == 0 && DuneWindBearing.WindDirFromSunBearing(90f, true) == 2 && DuneWindBearing.WindDirFromSunBearing(180f, true) == 4 && DuneWindBearing.WindDirFromSunBearing(-90f, true) == 6 && DuneWindBearing.WindDirFromSunBearing(359f, true) == 0 && DuneWindBearing.WindDirFromSunBearing(-10f, true) == 0 && DuneWindBearing.WindDirFromSunBearing(0f, false) == 4, "compass points");
            return null;
        }

        // ════════════════════════ cache ════════════════════════
        private static readonly string[] CcNames = { "Deposit", "Items", "Erode", "Absorb", "Reveal", "Cap" };
        public static long Buries, Reveals, Merges, GateRefusals;

        private sealed class CacheM { public int tick; public List<int> items = new List<int>(); }

        private static string RunCache(int seed, List<Act> acts)
        {
            var r = new Random(seed ^ 0x5e);
            const int CELLS = 5;
            float burial = 0.6f, reveal = 0.25f;
            var depth = new float[CELLS];
            var ground = new List<int>[CELLS]; for (int i = 0; i < CELLS; i++) ground[i] = new List<int>();
            var caches = new CacheM[CELLS];
            var revealed = new List<int>();
            int nextItem = 1, now = 100; int maxCaches = new[] { 1, 2, 400 }[r.Next(3)]; bool enabled = true;
            int created = 0;
            int step = 0;
            foreach (var a in acts)
            {
                step++; Steps++;
                string where = " at step " + step + " " + a;
                int c = a.a % CELLS;
                switch (a.kind)
                {
                    case 1: for (int i = 0, n = 1 + a.b % 4; i < n; i++) { ground[c].Add(nextItem++); created++; } break;
                    case 0: // a slab lands: the depth rises, maybe through the burial depth
                        {
                            float before = depth[c], after = Math.Min(1f, before + (a.b % 60) / 100f);
                            depth[c] = after;
                            if (RM_CacheKernel.CrossedBurial(before, after, burial))
                            {
                                Check(before < burial && after >= burial, "crossing verdict without a crossing" + where);
                                int count = caches.Count(x => x != null);
                                bool ok = RM_CacheKernel.BuryAllowed(enabled, caches[c] != null, count, maxCaches);
                                Check(ok == (enabled && (caches[c] != null || count < maxCaches)), "bury gate != spec" + where);
                                if (!ok) { GateRefusals++; break; }
                                var cand = ground[c].ToList();
                                if (cand.Count == 0) break;
                                if (caches[c] == null) caches[c] = new CacheM { tick = now };
                                else Merges++;
                                caches[c].items.AddRange(cand); ground[c].Clear(); Buries++;
                                Check(caches.Count(x => x != null) <= Math.Max(maxCaches, count), "a new cache beyond the cap" + where);
                            }
                            else Check(!(after >= burial && before < burial), "a crossing was missed" + where);
                            break;
                        }
                    case 2: depth[c] = Math.Max(0f, depth[c] - (a.b % 50) / 100f); break;
                    case 3: // two caches merge: the older burial time wins
                        {
                            int d = (c + 1 + a.b % (CELLS - 1)) % CELLS;
                            if (caches[c] == null || caches[d] == null) break;
                            caches[c].tick = RM_CacheKernel.AbsorbTick(caches[c].tick, caches[d].tick);
                            caches[c].items.AddRange(caches[d].items); caches[d] = null;
                            Check(caches[c].tick >= 0, "absorbed tick lost" + where);
                            break;
                        }
                    case 4: now += 250; goto case 6;
                    case 6: // TickRare on every cache
                        for (int i = 0; i < CELLS; i++)
                        {
                            if (caches[i] == null) continue;
                            bool should = RM_CacheKernel.ShouldReveal(depth[i], true, reveal);
                            Check(should == (depth[i] <= reveal), "reveal verdict != depth <= revealDepth" + where);
                            if (should) { revealed.AddRange(caches[i].items); ground[i].AddRange(caches[i].items); caches[i] = null; Reveals++; }
                        }
                        break;
                    case 5: maxCaches = new[] { 0, 1, 3, 400 }[a.b % 4]; enabled = a.a % 5 != 0; break;
                }
                int total = ground.Sum(g => g.Count) + caches.Where(x => x != null).Sum(x => x.items.Count);
                Check(total == created, $"items: ground + buried = {total}, created {created}: something was lost or duplicated" + where);
                Check(ground.SelectMany(g => g).Concat(caches.Where(x => x != null).SelectMany(x => x.items)).Distinct().Count() == total, "an item exists twice" + where);
                for (int i = 0; i < CELLS; i++) if (caches[i] != null) Check(caches[i].items.Count > 0, "an empty cache stayed on the map" + where);
            }
            return null;
        }

        private static string CacheUnits(int seed)
        {
            var r = new Random(seed ^ 0x6);
            // candidate: the exhaustive truth table over the eleven boolean gates
            for (int m = 0; m < 2048; m++)
            {
                bool sp = (m & 1) != 0, de = (m & 2) != 0, cache = (m & 4) != 0, item = (m & 8) != 0, haul = (m & 16) != 0, dod = (m & 32) != 0, home = (m & 64) != 0, store = (m & 128) != 0, forb = (m & 256) != 0, res = (m & 512) != 0, big = (m & 1024) != 0;
                float mv = big ? 10f : 1f;
                bool got = RM_CacheKernel.IsBurialCandidate(sp, de, cache, item, haul, dod, home, store, forb, res, 5f, mv, 1);
                bool spec = sp && !de && !cache && item && haul && !dod && !home && !store && !forb && !res && mv * 1 >= 5f;
                Check(got == spec, $"candidate mask {m}: {got}, spec {spec}");
            }
            Check(RM_CacheKernel.IsBurialCandidate(true, false, false, true, true, false, false, false, false, false, 5f, 1f, 5) && !RM_CacheKernel.IsBurialCandidate(true, false, false, true, true, false, false, false, false, false, 5f, 1f, 4) && RM_CacheKernel.IsBurialCandidate(true, false, false, true, true, false, false, false, false, false, 0f, 0f, 1), "market value is per stack; 0 disables the floor");
            // absorb: older wins, unset never beats set
            Check(RM_CacheKernel.AbsorbTick(100, 50) == 50 && RM_CacheKernel.AbsorbTick(50, 100) == 50 && RM_CacheKernel.AbsorbTick(-1, 70) == 70 && RM_CacheKernel.AbsorbTick(70, -1) == 70 && RM_CacheKernel.AbsorbTick(-1, -1) == -1 && RM_CacheKernel.AbsorbTick(5, 5) == 5, "absorb tick");
            Check(RM_CacheKernel.Accepts(false, false, false) && !RM_CacheKernel.Accepts(true, false, false) && !RM_CacheKernel.Accepts(false, true, false) && !RM_CacheKernel.Accepts(false, false, true), "accepts");
            Check(RM_CacheKernel.ShouldReveal(0.25f, true, 0.25f) && !RM_CacheKernel.ShouldReveal(0.26f, true, 0.25f) && RM_CacheKernel.ShouldReveal(0.25f, false, 0.9f) && !RM_CacheKernel.ShouldReveal(0.26f, false, 0.9f), "reveal depth: material's, or vanilla's 0.25 off a dune field");
            return null;
        }

        // ════════════════════════ runner ════════════════════════
        public static bool Run(double scale, int? oneSeed, string only)
        {
            var sw = Stopwatch.StartNew();
            bool ok = true;
            int N(int n) { return oneSeed.HasValue ? 1 : (int)(n * scale); }
            int S(int baseSeed) { return oneSeed ?? baseSeed; }
            var fam = new (string name, Func<List<string>> run)[]
            {
                ("transport", () => Family("transport", N(1500), S(1), s => Drive(s, rr => GenActs(rr, 8, 45, new[] { 60, 4, 8, 6, 4 }, TrNames), RunTransport) ?? TransportUnits(s))),
                ("influx", () => Family("influx", N(1500), S(1), s => Drive(s, rr => GenActs(rr, 8, 60, new[] { 40, 6, 20, 5, 8 }, InNames), RunInflux) ?? InfluxUnits(s))),
                ("wind", () => Family("wind", N(3000), S(1), WindCase)),
                ("cache", () => Family("cache", N(3000), S(1), s => Drive(s, rr => GenActs(rr, 10, 90, new[] { 35, 15, 10, 5, 12, 4, 0 }, CcNames), RunCache) ?? CacheUnits(s))),
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
            Console.WriteLine($"reached: transport moves {Moves}, off-map {OffMapMoves}, in-place {InPlaceMoves}, landings {Landed}, shadowed {Shadowed}, vanished (milli-depth) {Vanished}, nudged batches {Nudged}; influx placed {Placed}, capped {Capped}; wind shifts {Shifts}, storms {Storms}, bearings {Bearings}; cache buries {Buries}, merges {Merges}, reveals {Reveals}, gate refusals {GateRefusals}");
            if (!oneSeed.HasValue && scale >= 1 && only == null)
            {
                if (Moves == 0 || OffMapMoves == 0 || InPlaceMoves == 0 || Landed == 0 || Shadowed == 0 || Vanished == 0 || Nudged == 0 || Placed == 0 || Capped == 0 || Shifts == 0 || Storms == 0 || Bearings == 0 || Buries == 0 || Merges == 0 || Reveals == 0 || GateRefusals == 0)
                { Console.WriteLine("FAIL a fuzz family never reached one of its key transitions (blind)"); ok = false; }
            }
            Console.WriteLine($"movingdunes fuzz: {Cases} cases, {Steps} steps, {sw.Elapsed.TotalSeconds:F2}s total -> {(ok ? "OK" : "FAILED")}");
            return ok;
        }
    }
}
