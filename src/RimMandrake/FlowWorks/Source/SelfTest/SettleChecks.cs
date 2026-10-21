// Liquid networks build step L4 (design/RimMandrake/liquid_network_semantics_design_2026-10-11.md rev 2 §3.2, §6 L4): tank
// jobs and the settle, on the PRODUCTION planner (RM_LiquidNetKernel.SettlePlan) and the production SettleTick read from source.
// Gates: ship Fill from base; ship Empty to base; two Fill tanks; Empty + Fill + Dump on one component; epoch-start stock.
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using RimMandrake.FlowWorks.Machinery;

namespace RimMandrake.FlowWorks.SelfTest
{
    internal static class SettleChecks
    {
        private static void Assert(bool ok, string msg)
        {
            if (!ok) throw new Exception(msg);
        }

        private static RM_SettleTank T(int id, int units, int cap, string liquid, RM_TankMode mode) => new RM_SettleTank(id, units, cap, units > 0 ? liquid : null, mode);

        /// <summary>Runs <paramref name="cycles"/> settles, applying each plan; returns the units per tank afterwards.</summary>
        private static int[] Run(List<RM_SettleTank> tanks, int cycles, int per = RM_LiquidNetKernel.TankUnitsPerCycle)
        {
            var t = tanks.ToList();
            for (int c = 0; c < cycles; c++)
            {
                foreach ((int s, int d, int n) in RM_LiquidNetKernel.SettlePlan(t, per, c))
                {
                    object l = t[s].Liquid;
                    t[s] = new RM_SettleTank(t[s].Id, t[s].Units - n, t[s].Cap, t[s].Units - n > 0 ? l : null, t[s].Mode);
                    t[d] = new RM_SettleTank(t[d].Id, t[d].Units + n, t[d].Cap, l, t[d].Mode);
                }
            }
            return t.Select(x => x.Units).ToArray();
        }

        private static string S(int[] u) => string.Join("/", u);

        public static void Run(Action<string, Action> Case)
        {
            Case("Settle_ship_Fill_loads_from_base", () =>
            {
                var tanks = new List<RM_SettleTank> { T(1, 200, 300, "fuel", RM_TankMode.Store), T(2, 0, 100, null, RM_TankMode.Fill) };
                Assert(S(Run(tanks, 1)) == "190/10", "one cycle: 10 units into the Fill tank (" + S(Run(tanks, 1)) + ")");
                Assert(S(Run(tanks, 30)) == "100/100", "it fills to capacity and stops (" + S(Run(tanks, 30)) + ")");
                var noJob = new List<RM_SettleTank> { T(1, 200, 300, "fuel", RM_TankMode.Store), T(2, 0, 100, null, RM_TankMode.Store) };
                Assert(S(Run(noJob, 10)) == "200/0", "can-fail: two Store tanks never move anything (no equalising)");
            });

            Case("Settle_ship_Empty_unloads_to_base", () =>
            {
                var tanks = new List<RM_SettleTank> { T(1, 0, 300, null, RM_TankMode.Store), T(2, 100, 100, "fuel", RM_TankMode.Empty), T(3, 290, 300, "fuel", RM_TankMode.Store) };
                Assert(S(Run(tanks, 1)) == "0/90/300", "the fullest Store tank holding the liquid takes it first (" + S(Run(tanks, 1)) + ")");
                Assert(S(Run(tanks, 20)) == "90/0/300", "then an empty Store tank, until the ship is empty (" + S(Run(tanks, 20)) + ")");
                var other = new List<RM_SettleTank> { T(1, 50, 300, "water", RM_TankMode.Store), T(2, 100, 100, "fuel", RM_TankMode.Empty) };
                Assert(S(Run(other, 5)) == "50/100", "a tank of another liquid never takes it");
            });

            Case("Settle_two_Fill_tanks_never_take_from_each_other", () =>
            {
                var tanks = new List<RM_SettleTank> { T(1, 50, 100, "water", RM_TankMode.Fill), T(2, 50, 100, "water", RM_TankMode.Fill) };
                Assert(S(Run(tanks, 10)) == "50/50", "Fill to Fill moves nothing");
                var empties = new List<RM_SettleTank> { T(1, 50, 100, "water", RM_TankMode.Empty), T(2, 50, 100, "water", RM_TankMode.Empty) };
                Assert(S(Run(empties, 10)) == "50/50", "Empty to Empty moves nothing (two Empty tanks both send, nothing receives)");
            });

            Case("Settle_Empty_Fill_Dump_on_one_component", () =>
            {
                var tanks = new List<RM_SettleTank> { T(1, 60, 100, "tar", RM_TankMode.Empty), T(2, 0, 100, null, RM_TankMode.Fill), T(3, 40, 100, "tar", RM_TankMode.Dump), T(4, 0, 100, null, RM_TankMode.Store) };
                List<(int src, int dst, int units)> plan = RM_LiquidNetKernel.SettlePlan(tanks, 10, 0);
                Assert(plan.All(m => m.src != 2 && m.dst != 2), "the Dump tank never trades with tanks");
                Assert(plan.Count == 1 && plan[0].src == 0 && plan[0].dst == 1 && plan[0].units == 10, "the Empty tank feeds the Fill tank first (" + string.Join(",", plan) + ")");
                Assert(S(Run(tanks, 6)) == "0/60/40/0", "over cycles the Empty tank ends in the Fill tank, Store untouched while a Fill tank has room");
            });

            Case("Settle_moves_only_stock_present_at_the_start", () =>
            {
                // Empty -> Store (step 1) must not be forwarded Store -> Fill (step 2) in the same settle
                var tanks = new List<RM_SettleTank> { T(1, 10, 100, "oil", RM_TankMode.Empty), T(2, 0, 100, null, RM_TankMode.Store), T(3, 0, 100, null, RM_TankMode.Fill) };
                List<(int src, int dst, int units)> plan = RM_LiquidNetKernel.SettlePlan(tanks, 10, 0);
                Assert(plan.Count == 1 && plan[0] == (0, 2, 10), "this settle: Empty -> Fill directly; nothing via the Store tank (" + string.Join(",", plan) + ")");
                // the property, over random components: no tank sends more than it held at the start, and a tank that started
                // empty sends nothing (a unit received in this settle is never forwarded in it)
                var rnd = new Random(3);
                for (int trial = 0; trial < 500; trial++)
                {
                    var t = new List<RM_SettleTank>();
                    int n = 2 + rnd.Next(6);
                    string[] liq = { "oil", "water" };
                    for (int i = 0; i < n; i++) t.Add(T(i + 1, rnd.Next(3) == 0 ? 0 : rnd.Next(1, 100), 100, liq[rnd.Next(2)], (RM_TankMode)rnd.Next(4)));
                    var p = RM_LiquidNetKernel.SettlePlan(t, 10, trial);
                    for (int i = 0; i < n; i++)
                    {
                        int out_ = p.Where(m => m.src == i).Sum(m => m.units), in_ = p.Where(m => m.dst == i).Sum(m => m.units);
                        Assert(out_ <= t[i].Units && out_ <= 10 && in_ <= 10, "trial " + trial + " tank " + i + ": sent " + out_ + " of " + t[i].Units + ", got " + in_);
                        var into = p.Where(m => m.dst == i).Select(m => t[m.src].Liquid).Distinct().ToList();
                        Assert(into.Count <= 1 && (into.Count == 0 || t[i].Liquid == null || Equals(into[0], t[i].Liquid)),
                            "trial " + trial + " tank " + i + ": receives one liquid, its own or into empty (" + string.Join(",", into) + ")");
                        Assert(t[i].Mode != RM_TankMode.Dump || (out_ == 0 && in_ == 0), "trial " + trial + ": a Dump tank never trades");
                        Assert(t[i].Mode != RM_TankMode.Fill || out_ == 0, "trial " + trial + ": a Fill tank never sends to tanks");
                        Assert(t[i].Mode != RM_TankMode.Empty || in_ == 0, "trial " + trial + ": an Empty tank never receives");
                    }
                }
                var budget = new List<RM_SettleTank> { T(1, 100, 100, "oil", RM_TankMode.Empty), T(2, 0, 100, null, RM_TankMode.Fill), T(3, 0, 100, null, RM_TankMode.Fill) };
                Assert(RM_LiquidNetKernel.SettlePlan(budget, 10, 0).Where(m => m.src == 0).Sum(m => m.units) == 10, "an Empty tank sends at most tankUnitsPerCycle per settle, both steps together");
            });

            Case("Settle_empty_Fill_tank_rotates_liquids_by_cycle", () =>
            {
                var tanks = new List<RM_SettleTank> { T(5, 50, 100, "water", RM_TankMode.Store), T(3, 50, 100, "tar", RM_TankMode.Store), T(9, 0, 100, null, RM_TankMode.Fill) };
                var p0 = RM_LiquidNetKernel.SettlePlan(tanks, 10, 0);
                var p1 = RM_LiquidNetKernel.SettlePlan(tanks, 10, 1);
                Assert(p0.Count == 1 && p0[0].src == 1 && p1.Count == 1 && p1[0].src == 0, "cycle 0 takes the lowest-id source's liquid (tar), cycle 1 the next (water)");
            });

            Case("Settle_production_tick_and_jobs", () =>
            {
                string net = RiverSwitchFlipChecks.Src(Path.Combine("Machinery", "RM_LiquidNet.cs"));
                RiverSwitchFlipChecks.Has(net, @"public static void SettleTick\(Map map\) \{ if \(map == null \|\| !RM_HoseSettings\.tankModesEnabled\) \{ return; \}", "SettleTick returns first with tank jobs off");
                RiverSwitchFlipChecks.Has(net, @"foreach \(\(int si, int di, int n\) in RM_LiquidNetKernel\.SettlePlan\(view, per, cycle, sentById, recvById\)\)", "SettleTick executes the kernel's plan");
                RiverSwitchFlipChecks.Has(net, @"new RM_SettleTank\(t\.thingIDNumber, t\.storedUnits, t\.Capacity, t\.storedLiquid, t\.EffectiveMode\)", "the plan reads each tank's job in force");
                RiverSwitchFlipChecks.Has(net, @"tanks\.RemoveAll\(t => t == except \|\| \(fill \? !t\.TakesFromMachines : !t\.GivesToMachines\)\);", "machines never fill an Empty tank nor draw from a Dump tank");
                Assert(!net.Contains("TankFeedTick") && !RiverSwitchFlipChecks.Src(Path.Combine("Machinery", "RM_LiquidNetKernel.cs")).Contains("FeedTarget"), "the equalising tank feed is deleted");
                string tank = RiverSwitchFlipChecks.Src(Path.Combine("LiquidTypes", "Building_LiquidTank.cs"));
                RiverSwitchFlipChecks.Has(tank, @"Scribe_Values\.Look\(ref mode, ""rmTankMode"", Machinery\.RM_TankMode\.Store\);", "saved as rmTankMode, default Store (old saves load as Store)");
                RiverSwitchFlipChecks.Has(tank, @"public bool TakesFromMachines => EffectiveMode != Machinery\.RM_TankMode\.Empty;", "Empty takes nothing from pumps and machines");
                RiverSwitchFlipChecks.Has(tank, @"public bool GivesToMachines => EffectiveMode != Machinery\.RM_TankMode\.Dump;", "Dump gives nothing to machines");
                string ex = RiverSwitchFlipChecks.Src("RM_MapComponent_Excavation.cs");
                RiverSwitchFlipChecks.Has(ex, @"if \(Find\.TickManager\.TicksGame % RM_PumpMath\.CycleTicks == 7\) \{ Machinery\.RM_Levelling\.Tick\(map\); Machinery\.RM_LiquidNet\.SettleTick\(map\);", "the settle runs once per pump cycle, right after passive levelling (PIPE_LEVELLING)");
            });
        }
    }
}
