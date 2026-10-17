// WATER_SURFACE_REPAIR_LEVEL_OR_BUST (owner 2026-10-17): "We need VERY smooth water. That's water's one primary
// characteristic: a level surface." The live S5/S6 scenes as offline scenes, at the SHIPPED kernel flags, through the
// PRODUCTION RM_FlowKernel (head rule + return half) and the PRODUCTION pond picture (RM_PondDepthMath, what StagePond lays).
using System;
using System.Collections.Generic;
using System.Linq;

namespace RimMandrake.FlowWorks.SelfTest
{
    internal static class LevelSurfaceChecks
    {
        private static void Assert(bool ok, string msg)
        {
            if (!ok) throw new Exception(msg);
        }

        /// <summary>The shipped kernel configuration (RimMandrakeFlowWorksSettings defaults through DoPulse's copy lines).</summary>
        private static void Shipped(ArrayWorld world)
        {
            world.k.levelBySurfaceEnabled = true;
            world.k.levelSetEnabled = true;
            world.k.creepWaterEnabled = true;
            world.k.viscosityEnabled = true;
            world.k.sourceDrawdown = world.Drawdown;
            world.k.returnLevel = (src, dug) =>
            {
                var body = world.bodies[world.bodyOf[src]];
                float cap = body.cells.Sum(c => world.bed.TryGetValue(c, out int b) ? b : 0);
                if (body.limitless || body.stock + 1f > cap + 1e-4f) return false;
                body.stock += 1f;
                return true;
            };
        }

        /// <summary>The pond's water per square as StagePond lays it from the stock (Σ == floor(stock), S1).</summary>
        private static int[] Picture(ArrayWorld world, ArrayWorld.Body body)
        {
            var cells = body.cells.Where(c => world.k.depth[c] == 0).ToList();
            var beds = cells.Select(c => world.bed[c]).ToList();
            RM_PondDepthMath.Drawdown(RM_BedMath.SupportedLevels(body.stock, 1f), RM_PondDepthMath.Histogram(beds), out int s, out int r);
            HashSet<int> patch = RM_PondDepthMath.PickPatch(world.w, world.h, cells, beds, s, r);
            return cells.Select((c, i) => RM_PondDepthMath.WaterAt(beds[i], s, patch.Contains(c))).ToArray();
        }

        private static void Step(ArrayWorld world, List<int> seeds, long p)
        {
            world.k.Pulse(seeds, p);
            world.k.ReturnToPonds(seeds);
            world.Sync();
        }

        public static void Run(Action<string, Action> Case)
        {
            Case("Level_S5A_closed_pond_feeds_canal_one_surface", () =>
            {
                // Live S5 part A / S6: a 3x3 enclosed pond (bed 4, stock 36) and a 10-cell depth-1 canal off its east middle.
                var world = new ArrayWorld(16, 5);
                var pond = new List<int>();
                for (int z = 1; z <= 3; z++) for (int x = 1; x <= 3; x++) pond.Add(z * 16 + x);
                var body = world.AddBody(false, 36f, pond);
                foreach (int c in pond) world.bed[c] = 4;
                var canal = new List<int>();
                for (int x = 4; x < 14; x++) { canal.Add(2 * 16 + x); world.k.depth[2 * 16 + x] = 1; }
                Shipped(world);
                var log = new List<string>();
                for (int p = 1; p <= 60; p++)
                {
                    Step(world, canal, p);
                    int[] pic = Picture(world, body);
                    log.Add("p" + p + " stock " + body.stock + " pond [" + string.Join(" ", pic) + "] canal [" + string.Join(" ", canal.Select(c => world.k.fill[c])) + "]");
                }
                Console.WriteLine("    S5A trace:\n      " + string.Join("\n      ", log.Where((_, i) => i < 12 || i % 10 == 9)));
                int[] end = Picture(world, body);
                float total = body.stock + canal.Sum(c => world.k.fill[c]);
                Assert(Math.Abs(total - 36f) < 1e-4f, "conserved: " + total);
                Assert(end.Sum() == (int)Math.Floor(body.stock), "picture holds the stock: Σ " + end.Sum() + " vs " + body.stock);
                // One surface: every wet square of pond and canal stands within ONE level of every other (the smallest unit).
                var surf = new List<int>();
                surf.AddRange(end.Select(w => w - 4));
                surf.AddRange(canal.Select(c => world.k.fill[c] - world.k.depth[c]));
                Assert(surf.Max() - surf.Min() <= 1, "level surface: pond+canal surfaces span " + surf.Min() + ".." + surf.Max() + "\n" + log.Last());
            });

            Case("Level_S2_dug_pond_fills_as_one_surface", () =>
            {
                // Live S2: a limitless lake; a dug 2x2 depth-4 pond touching it (west column touches the lake); a 6-cell
                // depth-1 trench off the pond's far side. Live (old DLL) read pond [4 0 4 0] at pulse 4: two squares full
                // beside two dry ones of the same floor.
                var world = new ArrayWorld(14, 4);
                var lake = new List<int>();
                for (int z = 0; z < 4; z++) for (int x = 0; x < 3; x++) lake.Add(z * 14 + x);
                world.AddBody(true, 0f, lake);
                var pond = new List<int> { 1 * 14 + 3, 1 * 14 + 4, 2 * 14 + 3, 2 * 14 + 4 };
                foreach (int c in pond) world.k.depth[c] = 4;
                var trench = new List<int>();
                for (int x = 5; x < 11; x++) { trench.Add(2 * 14 + x); world.k.depth[2 * 14 + x] = 1; }
                Shipped(world);
                var seeds = pond.Concat(trench).ToList();
                var log = new List<string>();
                int worst = 0;
                for (int p = 1; p <= 30; p++)
                {
                    Step(world, seeds, p);
                    int[] pf = pond.Select(c => (int)world.k.fill[c]).ToArray();
                    worst = Math.Max(worst, pf.Max() - pf.Min());
                    log.Add("p" + p + " pond [" + string.Join(" ", pf) + "] trench [" + string.Join(" ", trench.Select(c => world.k.fill[c])) + "]");
                }
                Console.WriteLine("    S2 trace:\n      " + string.Join("\n      ", log.Where((_, i) => i < 16)));
                Assert(worst <= 1, "the dug pond's four squares (one floor) differ by " + worst + " levels at some pulse\n" + string.Join("\n", log.Take(10)));
            });

            Case("Level_S5F_pond_and_deep_canal_square_level", () =>
            {
                // Live S5 part F: a 1-square pond (bed 4, stock 4) beside one dry depth-4 dug square: 2 and 2.
                var world = new ArrayWorld(5, 3);
                var pond = new List<int> { 1 * 5 + 1 };
                var body = world.AddBody(false, 4f, pond);
                world.bed[pond[0]] = 4;
                int canal = 1 * 5 + 2;
                world.k.depth[canal] = 4;
                Shipped(world);
                var seeds = new List<int> { canal };
                for (int p = 1; p <= 20; p++) Step(world, seeds, p);
                Console.WriteLine("    S5F end: pond stock " + body.stock + " canal " + world.k.fill[canal]);
                Assert(Math.Abs(body.stock + world.k.fill[canal] - 4f) < 1e-4f, "conserved");
                Assert(Math.Abs(body.stock - world.k.fill[canal]) <= 1f, "level: pond " + body.stock + " canal " + world.k.fill[canal]);
            });

            Case("Level_S5B_one_square_pond_feeds_canal_no_shuttle", () =>
            {
                // Live S5 part B: a 1-square pond (bed 4, stock 4) and a 10-cell depth-1 canal. Live (old DLL) shuttled one level
                // pond<->canal cell 1 every pulse for 40 pulses.
                var world = new ArrayWorld(14, 3);
                var pond = new List<int> { 1 * 14 + 1 };
                var body = world.AddBody(false, 4f, pond);
                world.bed[pond[0]] = 4;
                var canal = new List<int>();
                for (int x = 2; x < 12; x++) { canal.Add(14 + x); world.k.depth[14 + x] = 1; }
                Shipped(world);
                var log = new List<string>();
                string prev = null; int moves = 0;
                for (int p = 1; p <= 60; p++)
                {
                    Step(world, canal, p);
                    string st = body.stock + "|" + string.Join(" ", canal.Select(c => world.k.fill[c]));
                    if (p > 20 && prev != null && st != prev) moves++;
                    prev = st;
                    log.Add("p" + p + " stock " + body.stock + " canal [" + string.Join(" ", canal.Select(c => world.k.fill[c])) + "]");
                }
                Console.WriteLine("    S5B trace:\n      " + string.Join("\n      ", log.Where((_, i) => i < 8 || i % 10 == 9)));
                float total = body.stock + canal.Sum(c => world.k.fill[c]);
                Assert(Math.Abs(total - 4f) < 1e-4f, "conserved: " + total);
                Assert(moves == 0, "settled: the state changed " + moves + " times after pulse 20\n" + log.Last());
            });
        }
    }
}
