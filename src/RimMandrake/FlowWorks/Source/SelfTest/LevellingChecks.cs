// PIPE_LEVELLING_BUILD_WATER_FINDS_ITS_LEVEL: passive gravity levelling between bodies joined by pipes and hoses, on the
// PRODUCTION kernel (RM_LevellingMath.cs). Design P6 of design/RimMandrake/flowworks_pipes_across_pits_design_2026-10-20.md.
// Gates: (1) volume conserved exactly; (2) heights converge monotonically (energy never rises; a two-body gap never grows);
// (3) no oscillation (no link reverses in a two-body scene; no gap changes sign); (4) different liquids never exchange; plus
// the item's L1 list (1-cell vs 100-cell basin, ten parallel links, same-body loop, crest siphon, exposed intake, water/oil,
// dry receiver) and a budget case (N bodies on one network, cost per cycle).
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;

namespace RimMandrake.FlowWorks.SelfTest
{
    internal static class LevellingChecks
    {
        private const int U = RM_LevelSolve.U;
        private static readonly object Water = "water", Oil = "oil";

        private static void Assert(bool ok, string msg)
        {
            if (!ok) throw new Exception(msg);
        }

        /// <summary>A flat-floored basin of <paramref name="squares"/> squares <paramref name="depth"/> notches deep.</summary>
        private static int[] Flat(int squares, int depth)
        {
            var h = new int[depth + 1];
            for (int l = 1; l <= depth; l++) h[l] = squares;
            return h;
        }

        private static RM_LevelBody Body(long key, int[] hist, long water, object fluid, bool limitless = false) =>
            new RM_LevelBody { Key = key, Hist = hist, Water = water, Fluid = water > 0 || limitless ? fluid : null, Limitless = limitless };

        private static RM_LevelLink Link(int a, int b, double floorA = double.NegativeInfinity, double floorB = double.NegativeInfinity) =>
            new RM_LevelLink { A = a, B = b, FloorA = floorA, FloorB = floorB, TakeA = long.MaxValue, TakeB = long.MaxValue, RoomA = long.MaxValue, RoomB = long.MaxValue };

        private static double S(RM_LevelBody b) => RM_LevellingMath.Surface(b, b.Water);

        /// <summary>Runs cycles until nothing moves (or <paramref name="maxCycles"/>), checking the four gates every cycle.
        /// Returns the cycles taken; throws on any gate failure.</summary>
        private static int Drive(List<RM_LevelBody> bodies, List<RM_LevelLink> links, long rate, int maxLinks, int maxCycles,
            string label, bool twoBody = false)
        {
            int cursor = 0;
            long limitlessNet = 0;
            long total0 = RM_LevellingMath.FiniteTotal(bodies);
            double e0 = RM_LevellingMath.Energy(bodies);
            var wet = bodies.Select(b => b.Fluid).ToArray();
            var dir = new int[links.Count];
            double gap0 = twoBody ? S(bodies[0]) - S(bodies[1]) : 0;
            int quiet = 0;
            for (int c = 1; c <= maxCycles; c++)
            {
                var snapshot = bodies.Select(b => (b.Water, b.Fluid)).ToArray();
                var moves = RM_LevellingMath.Plan(bodies, links, rate, maxLinks, ref cursor, null, ref limitlessNet);
                // (1) conservation: finite total + limitless net is constant, and the moves account for every change
                long total = RM_LevellingMath.FiniteTotal(bodies);
                Assert(total + limitlessNet == total0, $"{label}: cycle {c}: volume {total} + limitless {limitlessNet} != {total0}");
                var delta = new long[bodies.Count];
                foreach (RM_LevelMove m in moves)
                {
                    Assert(m.Dl > 0, $"{label}: a move of {m.Dl} dL");
                    if (!bodies[m.From].Limitless) delta[m.From] -= m.Dl;
                    if (!bodies[m.To].Limitless) delta[m.To] += m.Dl;
                    // (4) liquids: a move goes only between the same liquid or into a body dry at the start of the cycle
                    object fs = bodies[m.From].Fluid, ts = snapshot[m.To].Fluid;
                    Assert(fs != null && (ts == null || ReferenceEquals(fs, ts)), $"{label}: {fs} moved into {ts}");
                    // (3) direction: a link never reverses in a two-body scene
                    int d = m.From == links[m.Link].A ? 1 : -1;
                    Assert(!twoBody || dir[m.Link] == 0 || dir[m.Link] == d, $"{label}: link {m.Link} reversed at cycle {c}");
                    dir[m.Link] = d;
                }
                for (int i = 0; i < bodies.Count; i++)
                {
                    Assert(bodies[i].Limitless || snapshot[i].Water + delta[i] == bodies[i].Water, $"{label}: body {i} changed by other than its moves");
                    Assert(bodies[i].Water >= 0, $"{label}: body {i} went negative");
                    Assert(bodies[i].Limitless || bodies[i].Water <= RM_LevellingMath.Capacity(bodies[i]), $"{label}: body {i} overfilled");
                    Assert(wet[i] == null || ReferenceEquals(bodies[i].Fluid, wet[i]), $"{label}: body {i} changed liquid");
                    if (wet[i] == null && bodies[i].Fluid != null) wet[i] = bodies[i].Fluid;
                }
                // (2) monotone: energy never rises; a two-body gap never grows and never changes sign
                double e = RM_LevellingMath.Energy(bodies);
                Assert(e <= e0 + 1e-6 * Math.Max(1.0, Math.Abs(e0)), $"{label}: energy rose at cycle {c}: {e0} -> {e}");
                e0 = e;
                if (twoBody)
                {
                    double gap = S(bodies[0]) - S(bodies[1]);
                    Assert(Math.Abs(gap) <= Math.Abs(gap0) + 1e-9, $"{label}: gap grew at cycle {c}: {gap0} -> {gap}");
                    Assert(gap0 == 0 || gap == 0 || Math.Sign(gap) == Math.Sign(gap0) || Math.Abs(gap) < RM_LevellingMath.LevelTolerance,
                        $"{label}: gap changed sign at cycle {c}: {gap0} -> {gap}");
                    gap0 = gap;
                }
                quiet = moves.Count == 0 ? quiet + 1 : 0;
                // a full rotation of the budget with nothing moving is the fixed point
                int rotation = (links.Count + Math.Max(1, Math.Min(links.Count, maxLinks)) - 1) / Math.Max(1, Math.Min(links.Count, maxLinks));
                if (quiet >= Math.Max(1, rotation)) return c;
            }
            return -1;
        }

        public static void Run(Action<string, Action> Case)
        {
            Case("LEVELLING_one_square_vs_hundred_square_basin_converge_to_one_surface", () =>
            {
                // a 1-square pit 10 notches deep, full; a 100-square basin 3 notches deep, dry; different floors
                var bodies = new List<RM_LevelBody> { Body(1, Flat(1, 10), 10L * U, Water), Body(2, Flat(100, 3), 0, null) };
                int cycles = Drive(bodies, new List<RM_LevelLink> { Link(0, 1) }, U, 64, 10000, "1v100", twoBody: true);
                Assert(cycles > 0, "1v100 never settled");
                Assert(Math.Abs(S(bodies[0]) - S(bodies[1])) < RM_LevellingMath.LevelTolerance, $"1v100 surfaces {S(bodies[0])} vs {S(bodies[1])}");
                Assert(ReferenceEquals(bodies[1].Fluid, Water), "the dry basin did not take the water");
                Console.WriteLine($"      settled in {cycles} cycles at {S(bodies[0]):F0} / {S(bodies[1]):F0} dL-per-square");
            });
            Case("LEVELLING_ten_parallel_links_sum_and_still_never_overshoot", () =>
            {
                var b1 = new List<RM_LevelBody> { Body(1, Flat(4, 6), 24L * U, Water), Body(2, Flat(4, 6), 0, null) };
                var b10 = new List<RM_LevelBody> { Body(1, Flat(4, 6), 24L * U, Water), Body(2, Flat(4, 6), 0, null) };
                int cursor = 0; long net = 0;
                long one = RM_LevellingMath.Plan(b1, new List<RM_LevelLink> { Link(0, 1) }, 1000, 64, ref cursor, null, ref net).Sum(m => m.Dl);
                cursor = 0;
                long ten = RM_LevellingMath.Plan(b10, Enumerable.Range(0, 10).Select(_ => Link(0, 1)).ToList(), 1000, 64, ref cursor, null, ref net).Sum(m => m.Dl);
                Assert(ten == 10 * one, $"ten links moved {ten}, one moved {one}");
                var b = new List<RM_LevelBody> { Body(1, Flat(4, 6), 24L * U, Water), Body(2, Flat(4, 6), 0, null) };
                int cycles = Drive(b, Enumerable.Range(0, 10).Select(_ => Link(0, 1)).ToList(), 5 * U, 64, 10000, "ten", twoBody: true);
                Assert(cycles > 0 && Math.Abs(S(b[0]) - S(b[1])) < RM_LevellingMath.LevelTolerance, "ten links did not level");
            });
            Case("LEVELLING_same_body_loop_moves_nothing", () =>
            {
                var bodies = new List<RM_LevelBody> { Body(7, Flat(3, 4), 5L * U, Water), Body(7, Flat(3, 4), 5L * U, Water) };
                var st = new RM_LevelLinkState[2];
                int cursor = 0; long net = 0;
                var moves = RM_LevellingMath.Plan(bodies, new List<RM_LevelLink> { Link(0, 0), Link(0, 1) }, U, 64, ref cursor, st, ref net);
                Assert(moves.Count == 0 && st[0] == RM_LevelLinkState.SameBody && st[1] == RM_LevelLinkState.SameBody, "a same-body link moved");
            });
            Case("LEVELLING_siphon_over_a_crest_flows", () =>
            {
                // no crest field exists: the solver has no priming rule, so a hose over a hill flows like any other (ruling 10)
                var bodies = new List<RM_LevelBody> { Body(1, Flat(2, 4), 8L * U, Water), Body(2, Flat(2, 8), 0, null) };
                int cycles = Drive(bodies, new List<RM_LevelLink> { Link(0, 1) }, U, 64, 10000, "siphon", twoBody: true);
                Assert(cycles > 0 && bodies[1].Water > 0, "the siphon moved nothing");
            });
            Case("LEVELLING_exposed_intake_stops", () =>
            {
                // source end sits on a shelf 2 notches down; the source must stop when its surface reaches it
                var bodies = new List<RM_LevelBody> { Body(1, Flat(4, 6), 24L * U, Water), Body(2, Flat(50, 10), 0, null) };
                double shelf = -2.0 * U;
                Drive(bodies, new List<RM_LevelLink> { Link(0, 1, shelf, double.NegativeInfinity) }, U, 64, 10000, "intake", twoBody: true);
                Assert(S(bodies[0]) >= shelf - 1e-9 && S(bodies[0]) < shelf + RM_LevellingMath.LevelTolerance + U, $"source stopped at {S(bodies[0])}, intake at {shelf}");
                var st = new RM_LevelLinkState[1];
                int cursor = 0; long net = 0;
                Assert(RM_LevellingMath.Plan(bodies, new List<RM_LevelLink> { Link(0, 1, shelf, double.NegativeInfinity) }, U, 64, ref cursor, st, ref net).Count == 0, "moved past the intake");
            });
            Case("LEVELLING_water_and_oil_never_exchange", () =>
            {
                var bodies = new List<RM_LevelBody> { Body(1, Flat(4, 6), 24L * U, Water), Body(2, Flat(4, 6), 2L * U, Oil) };
                var st = new RM_LevelLinkState[1];
                int cursor = 0; long net = 0;
                var moves = RM_LevellingMath.Plan(bodies, new List<RM_LevelLink> { Link(0, 1) }, U, 64, ref cursor, st, ref net);
                Assert(moves.Count == 0 && st[0] == RM_LevelLinkState.DifferentLiquids && bodies[1].Water == 2L * U, "water moved into oil");
            });
            Case("LEVELLING_dry_receiver_takes_the_source_liquid", () =>
            {
                var bodies = new List<RM_LevelBody> { Body(1, Flat(4, 6), 24L * U, Oil), Body(2, Flat(4, 6), 0, null) };
                int cursor = 0; long net = 0;
                RM_LevellingMath.Plan(bodies, new List<RM_LevelLink> { Link(0, 1) }, U, 64, ref cursor, null, ref net);
                Assert(ReferenceEquals(bodies[1].Fluid, Oil), "the dry pit did not take oil");
            });
            Case("LEVELLING_limitless_sea_fills_a_pit_to_the_brim_and_counts_it", () =>
            {
                var bodies = new List<RM_LevelBody> { Body(1, null, 0, Water, limitless: true), Body(2, Flat(3, 4), 0, null) };
                int cycles = Drive(bodies, new List<RM_LevelLink> { Link(0, 1) }, U, 64, 10000, "sea");
                Assert(cycles > 0 && S(bodies[1]) > -RM_LevellingMath.LevelTolerance, $"pit stopped at {S(bodies[1])}");
            });
            Case("LEVELLING_fuzz_conserves_converges_never_oscillates_never_mixes", () =>
            {
                var rng = new Random(20261020);
                int scenes = 0, settled = 0;
                for (int s = 0; s < 300; s++)
                {
                    int nb = 2 + rng.Next(7);
                    var bodies = new List<RM_LevelBody>();
                    for (int i = 0; i < nb; i++)
                    {
                        if (rng.Next(12) == 0) { bodies.Add(Body(i, null, 0, rng.Next(3) == 0 ? Oil : Water, limitless: true)); continue; }
                        int depth = 1 + rng.Next(8);
                        var h = new int[depth + 1];
                        int sq = 1 + rng.Next(rng.Next(2) == 0 ? 4 : 60);
                        for (int l = 1; l <= depth; l++) { h[l] = sq; if (rng.Next(3) == 0) sq = Math.Max(1, sq - rng.Next(sq)); }
                        long cap = RM_LevelSolve.PondCapacity(h);
                        long w = rng.Next(3) == 0 ? 0 : (long)(rng.NextDouble() * cap);
                        bodies.Add(Body(rng.Next(10) == 0 && i > 0 ? i - 1 : i, h, w, rng.Next(4) == 0 ? Oil : Water));
                    }
                    var links = new List<RM_LevelLink>();
                    int nl = 1 + rng.Next(nb * 2);
                    for (int k = 0; k < nl; k++)
                    {
                        int a = rng.Next(nb), b = rng.Next(nb);
                        double fa = rng.Next(3) == 0 ? -(double)rng.Next(1, 8) * U : double.NegativeInfinity;
                        double fb = rng.Next(3) == 0 ? -(double)rng.Next(1, 8) * U : double.NegativeInfinity;
                        var l = Link(a, b, fa, fb);
                        if (rng.Next(4) == 0) { l.TakeA = rng.Next(1, 3 * U); l.RoomB = rng.Next(1, 3 * U); }
                        links.Add(l);
                    }
                    bool two = nb == 2 && links.All(l => l.A != l.B) && bodies.All(b => !b.Limitless);
                    int c = Drive(bodies, links, U / 2 + rng.Next(2 * U), 1 + rng.Next(8), 20000, "seed " + s, twoBody: two);
                    scenes++;
                    if (c > 0) settled++;
                }
                Console.WriteLine($"      {scenes} scenes, {settled} reached a fixed point");
                Assert(settled == scenes, $"{scenes - settled} scene(s) still moving after 20,000 cycles");
            });
            Case("LEVELLING_budget_n_bodies_on_one_network", () =>
            {
                // 200 bodies (40 big basins, 160 pits) on one network, every body linked to the next and 200 extra random links:
                // a cycle visits at most maxLinks links and its cost stays bounded
                var rng = new Random(7);
                var bodies = new List<RM_LevelBody>();
                for (int i = 0; i < 200; i++)
                {
                    int[] h = i < 40 ? Flat(40000, 8) : Flat(1 + rng.Next(30), 1 + rng.Next(16));
                    bodies.Add(Body(i, h, (long)(rng.NextDouble() * RM_LevelSolve.PondCapacity(h)), Water));
                }
                var links = new List<RM_LevelLink>();
                for (int i = 0; i + 1 < bodies.Count; i++) links.Add(Link(i, i + 1));
                for (int k = 0; k < 201; k++) links.Add(Link(rng.Next(200), rng.Next(200)));
                const int maxLinks = 64;
                var st = new RM_LevelLinkState[links.Count];
                int cursor = 0; long net = 0;
                long total0 = RM_LevellingMath.FiniteTotal(bodies);
                var clock = Stopwatch.StartNew();
                int cycles = 2000;
                for (int c = 0; c < cycles; c++)
                {
                    RM_LevellingMath.Plan(bodies, links, RM_LevelSolve.U, maxLinks, ref cursor, st, ref net);
                    Assert(st.Count(x => x != RM_LevelLinkState.Skipped) <= maxLinks, "a cycle visited more than the budget");
                }
                double usPerCycle = clock.Elapsed.TotalMilliseconds * 1000.0 / cycles;
                Assert(RM_LevellingMath.FiniteTotal(bodies) == total0, "budget scene lost volume");
                Console.WriteLine($"      {links.Count} links, budget {maxLinks}/cycle: {usPerCycle:F1} us per cycle (one cycle = 250 ticks)");
                Assert(usPerCycle < 2000, $"a cycle took {usPerCycle:F0} us");
            });
        }
    }
}
