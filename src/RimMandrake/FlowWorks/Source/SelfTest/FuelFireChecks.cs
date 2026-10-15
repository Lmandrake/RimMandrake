// CHEMFUEL_MOAT_WIRE_MISSING_CHANNEL (owner by card, 2026-10-15): the two fuel fires' arithmetic, driven through the
// production RM_FuelFireMath / RM_FireMath. Chemfuel: fast spread, burn-down in seconds, every level accounted for.
// Astrofuel: one detonation empties every cell exactly once, inside per-tick budgets, with every cell under a blast.
// Each budget case carries a can-fail: the naive schedule (no budget) computed beside it must break the same bound.
using System;
using System.Collections.Generic;
using System.Diagnostics;

namespace RimMandrake.FlowWorks.SelfTest
{
    internal static class FuelFireChecks
    {
        private static void Assert(bool cond, string msg)
        {
            if (!cond) throw new Exception(msg);
        }

        // RM_FireMath's 250-tick default pulse (RimMandrakeFlowWorksSettings.pulseIntervalTicks).
        private const int Pulse = 250;
        private const int ChemfuelTicksPerCell = 2;   // FlowWorks_PitFluids.xml RM_Fluid_Chemfuel fireFrontTicksPerCell
        private const int OilTicksPerCell = 90;       // RM_Fluid_Oil

        private static int FrontTime(int cells, int ticksPerCell, float speed)
        {
            int due = 0;
            for (int k = 1; k < cells; k++) due = RM_FireMath.FrontDue(due, ticksPerCell, speed);
            return due;
        }

        // A body walked breadth-first from (ox,oz) over a w x h rectangle: the BFS order and rings the Verse side builds.
        private static void Body(int w, int h, int ox, int oz, out int[] ring, out int[] x, out int[] z)
        {
            var r = new List<int>(); var xs = new List<int>(); var zs = new List<int>();
            var seen = new bool[w, h];
            var q = new Queue<(int, int, int)>();
            q.Enqueue((ox, oz, 0)); seen[ox, oz] = true;
            while (q.Count > 0)
            {
                var (cx, cz, d) = q.Dequeue();
                r.Add(d); xs.Add(cx); zs.Add(cz);
                foreach (var (dx, dz) in new[] { (1, 0), (-1, 0), (0, 1), (0, -1) })
                {
                    int nx = cx + dx, nz = cz + dz;
                    if (nx < 0 || nz < 0 || nx >= w || nz >= h || seen[nx, nz]) continue;
                    seen[nx, nz] = true;
                    q.Enqueue((nx, nz, d + 1));
                }
            }
            ring = r.ToArray(); x = xs.ToArray(); z = zs.ToArray();
        }

        private static string CheckPlan(int w, int h, int ox, int oz, out double ms)
        {
            Body(w, h, ox, oz, out int[] ring, out int[] x, out int[] z);
            int n = ring.Length;
            var consume = new int[n];
            var blast = new int[n];
            var clock = Stopwatch.StartNew();
            int spacing = RM_FuelFireMath.PlanDetonation(ring, x, z, RM_FuelFireMath.DetonationTicksPerRing,
                RM_FuelFireMath.MaxCellsConsumedPerTick, RM_FuelFireMath.MaxBlastsPerTick, RM_FuelFireMath.MaxBlastsPerDetonation,
                RM_FuelFireMath.BaseBlastSpacing, consume, blast);
            ms = clock.Elapsed.TotalMilliseconds;
            var perTickCells = new Dictionary<int, int>();
            var perTickBlasts = new Dictionary<int, int>();
            var anchors = new List<int>();
            int last = 0;
            for (int k = 0; k < n; k++)
            {
                Assert(consume[k] >= 0, "cell " + k + " never emptied");
                Assert(consume[k] >= ring[k] * RM_FuelFireMath.DetonationTicksPerRing, "cell " + k + " emptied before the wave reached it");
                perTickCells[consume[k]] = perTickCells.TryGetValue(consume[k], out int c) ? c + 1 : 1;
                if (blast[k] >= 0)
                {
                    Assert(blast[k] >= consume[k], "a blast before its cell was reached");
                    perTickBlasts[blast[k]] = perTickBlasts.TryGetValue(blast[k], out int b) ? b + 1 : 1;
                    anchors.Add(k);
                }
                last = Math.Max(last, Math.Max(consume[k], blast[k]));
            }
            int maxCells = 0, maxBlasts = 0;
            foreach (int v in perTickCells.Values) maxCells = Math.Max(maxCells, v);
            foreach (int v in perTickBlasts.Values) maxBlasts = Math.Max(maxBlasts, v);
            Assert(maxCells <= RM_FuelFireMath.MaxCellsConsumedPerTick, "a tick empties " + maxCells + " cells");
            Assert(maxBlasts <= RM_FuelFireMath.MaxBlastsPerTick, "a tick starts " + maxBlasts + " blasts");
            Assert(anchors.Count >= 1 && anchors.Count <= RM_FuelFireMath.MaxBlastsPerDetonation, anchors.Count + " blasts");
            // coverage: every cell within the anchor spacing of some blast, and the spacing inside the blast radius
            // the spacing only grows when the blast cap binds, and the radius grows with it
            Assert(spacing == RM_FuelFireMath.BaseBlastSpacing || anchors.Count * 2 > RM_FuelFireMath.MaxBlastsPerDetonation,
                "spacing " + spacing + " grew with only " + anchors.Count + " blasts");
            Assert(RM_FuelFireMath.BlastRadiusFor(1f, spacing) >= Math.Min(spacing * 0.8f, 7.9f) - 0.01f, "radius does not grow with spacing");
            var grid = new HashSet<(int, int)>();
            foreach (int a in anchors) grid.Add((x[a], z[a]));
            for (int k = 0; k < n; k++)
            {
                bool near = false;
                for (int dx = -(spacing - 1); dx <= spacing - 1 && !near; dx++)
                    for (int dz = -(spacing - 1); dz <= spacing - 1 && !near; dz++)
                        near = grid.Contains((x[k] + dx, z[k] + dz));
                Assert(near, "cell " + x[k] + "," + z[k] + " lies under no blast");
            }
            return $"{w}x{h}: {n} cells, {anchors.Count} blasts (spacing {spacing}), {last} ticks, max {maxCells} cells / {maxBlasts} blasts per tick, plan {ms:F1} ms";
        }

        public static void Run(Action<string, Action> Case)
        {
            Case("FuelFire_classify_kinds_and_settings", () =>
            {
                Assert(RM_FuelFireMath.Classify(true, false, true, true) == RM_FuelBurn.Inferno, "chemfuel lit is an inferno");
                Assert(RM_FuelFireMath.Classify(false, true, true, true) == RM_FuelBurn.Detonation, "astrofuel lit detonates");
                Assert(RM_FuelFireMath.Classify(true, false, false, true) == RM_FuelBurn.Ordinary, "inferno off: chemfuel burns like oil");
                Assert(RM_FuelFireMath.Classify(false, true, true, false) == RM_FuelBurn.Inferno, "detonation off: astrofuel burns as an inferno");
                Assert(RM_FuelFireMath.Classify(false, true, false, false) == RM_FuelBurn.Ordinary, "both off: astrofuel burns like oil");
                Assert(RM_FuelFireMath.Classify(false, false, true, true) == RM_FuelBurn.Ordinary, "tar and oil are untouched");
            });

            Case("FuelFire_inferno_spreads_like_gasoline", () =>
            {
                // a 100-cell moat: lit end to end in seconds; the same moat of oil takes minutes
                int chem = FrontTime(100, ChemfuelTicksPerCell, RM_FuelFireMath.InfernoFrontSpeed(1f, 1f));
                int oil = FrontTime(100, OilTicksPerCell, 1f);
                Console.WriteLine($"      100-cell moat: chemfuel {chem} ticks ({chem / 60f:F1} s), oil {oil} ticks");
                Assert(chem <= 300, "chemfuel took " + chem + " ticks to run 100 cells");
                Assert(oil > 20 * chem, "can-fail: oil is not a fuse beside it");
                Assert(FrontTime(100, ChemfuelTicksPerCell, RM_FuelFireMath.InfernoFrontSpeed(1f, 0.25f)) > chem, "spread dial slows it");
            });

            Case("FuelFire_inferno_burns_down_in_seconds_and_conserves", () =>
            {
                int tpl = RM_FuelFireMath.InfernoTicksPerLevelAt(1f);
                var rnd = new Random(1015);
                int cells = 60;
                var level = new int[cells];
                var acc = new int[cells];
                int start = 0;
                for (int k = 0; k < cells; k++) { level[k] = 1 + rnd.Next(RM_Volume.LevelsPerSquare); start += level[k]; }
                int burned = 0, ticks = 0;
                while (ticks < 100000)
                {
                    bool any = false;
                    for (int k = 0; k < cells; k++)
                    {
                        if (level[k] == 0) continue;
                        int l = RM_FireMath.CanalLevelsToBurn(true, ref acc[k], Pulse, tpl);
                        int take = Math.Min(l, level[k]);
                        level[k] -= take; burned += take;
                        any |= level[k] > 0;
                    }
                    ticks += Pulse;
                    if (!any) break;
                }
                Console.WriteLine($"      {cells} cells, {start} levels: all gone in {ticks} ticks ({ticks / 60f:F0} s); oil would take {RM_FireMath.TicksPerCanalLevel(1f) * RM_Volume.LevelsPerSquare} ticks a brim cell");
                Assert(burned == start, "burned " + burned + " of " + start + " levels");
                Assert(ticks <= 60 * 60, "a brim moat took " + ticks + " ticks (over a minute)");
                Assert(RM_FireMath.TicksPerCanalLevel(1f) * RM_Volume.LevelsPerSquare > 100 * ticks, "can-fail: ruling 7's day-a-level beside it");
                Assert(RM_FuelFireMath.InfernoTicksPerLevelAt(4f) < tpl && RM_FuelFireMath.InfernoTicksPerLevelAt(0.25f) > tpl, "burn-rate dial");
            });

            Case("FuelFire_inferno_heat_and_halo_scale", () =>
            {
                Assert(RM_FuelFireMath.InfernoHeatPerCheck(1f) >= 8 * 60f, "an inferno pushes 8x ordinary liquid fire heat");
                Assert(RM_FuelFireMath.InfernoIgniteRadius(1f) >= 2.9f, "the halo reaches past a 1-wide moat's banks");
                Assert(RM_FuelFireMath.InfernoIgniteRadius(10f) <= 7.9f && RM_FuelFireMath.InfernoIgniteRadius(0f) >= 1.5f, "halo clamps");
                Assert(RM_FuelFireMath.InfernoHaloTriesPerCheck >= RM_FuelFireMath.InfernoHaloTriesPerCell, "halo budget");
            });

            Case("FuelFire_detonation_channel_goes_almost_at_once", () =>
            {
                string r = CheckPlan(60, 1, 0, 0, out _);
                Console.WriteLine("      " + r);
                Body(60, 1, 0, 0, out int[] ring, out _, out _);
                Assert(ring[ring.Length - 1] * RM_FuelFireMath.DetonationTicksPerRing <= 150, "a 60-cell channel takes over 2.5 s");
            });

            Case("FuelFire_detonation_budgets_hold_on_big_bodies", () =>
            {
                Console.WriteLine("      " + CheckPlan(30, 30, 15, 15, out _));
                Console.WriteLine("      " + CheckPlan(2000, 1, 1000, 0, out _));
                Console.WriteLine("      " + CheckPlan(141, 141, 0, 0, out double ms));
                Assert(ms < 500, "planning 20k cells took " + ms + " ms");
                // can-fail: without the budget a 141x141 square's diagonal ring empties ~141 cells AND blasts dozens at one tick
                Body(141, 141, 70, 70, out int[] ring, out int[] x, out int[] z);
                var anchor = new bool[ring.Length];
                RM_FuelFireMath.ChooseAnchors(x, z, RM_FuelFireMath.BaseBlastSpacing, anchor);
                var naive = new Dictionary<int, int>();
                int worst = 0;
                for (int k = 0; k < ring.Length; k++)
                    if (anchor[k]) { naive[ring[k]] = naive.TryGetValue(ring[k], out int c) ? c + 1 : 1; worst = Math.Max(worst, naive[ring[k]]); }
                Assert(worst > RM_FuelFireMath.MaxBlastsPerTick, "can-fail: the naive schedule already fits (" + worst + ")");
            });
        }
    }
}
