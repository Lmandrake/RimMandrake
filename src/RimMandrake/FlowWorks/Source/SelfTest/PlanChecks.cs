// Liquid networks build step L3 (design/RimMandrake/liquid_network_semantics_design_2026-10-11.md rev 2 §3.2-3.3, §6 L3):
// fill and draw order, split levels and consumer rotation, on the PRODUCTION kernel (../Machinery/RM_LiquidNetKernel.cs:
// FillPlan, DrawPlan, RM_ConsumerRotation), then the production callers read from source. Gates: 3 + 2 units of room take a
// 5-unit level (G8); two origins get the same plan; two machines on one liquid take turns (G9).
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using RimMandrake.FlowWorks.Machinery;

namespace RimMandrake.FlowWorks.SelfTest
{
    internal static class PlanChecks
    {
        private static void Assert(bool ok, string msg)
        {
            if (!ok) throw new Exception(msg);
        }

        private static RM_TankView V(int id, int units, int cap, bool holds) => new RM_TankView(id, units, cap, holds && units > 0, units <= 0);

        private static string Ids(IList<RM_TankView> t, List<KeyValuePair<int, int>> plan) =>
            plan == null ? "null" : string.Join(" ", plan.Select(p => t[p.Key].Id + ":" + p.Value));

        public static void Run(Action<string, Action> Case)
        {
            Case("Plan_three_plus_two_room_takes_a_level", () =>
            {
                var t = new List<RM_TankView> { V(10, 97, 100, true), V(11, 98, 100, true) };
                List<KeyValuePair<int, int>> plan = RM_LiquidNetKernel.FillPlan(t, 5);
                Assert(Ids(t, plan) == "11:2 10:3", "3 + 2 units of room take the level, fullest first: " + Ids(t, plan));
                Assert(RM_LiquidNetKernel.FillPlan(new List<RM_TankView> { V(1, 97, 100, true), V(2, 99, 100, true) }, 5) == null,
                    "3 + 1 units of room: no part-level is placed (null)");
            });

            Case("Plan_fill_order_fullest_holder_then_empty_by_id", () =>
            {
                var t = new List<RM_TankView> { V(5, 0, 100, false), V(3, 40, 100, true), V(7, 90, 100, true), V(2, 0, 100, false), V(9, 50, 100, false) };
                // 9 holds ANOTHER liquid: never used; 7 (90%) before 3 (40%); then the empty tanks 2 then 5
                Assert(Ids(t, RM_LiquidNetKernel.FillPlan(t, 5)) == "7:5", "the fullest holder with room first");
                Assert(Ids(t, RM_LiquidNetKernel.FillPlan(t, 80)) == "7:10 3:60 2:10", "then the next holder, then the lowest-id empty tank: " + Ids(t, RM_LiquidNetKernel.FillPlan(t, 80)));
                Assert(RM_LiquidNetKernel.FillRoom(t) == 10 + 60 + 100 + 100, "room = holders' room + empty tanks, never another liquid's tank");
                var tie = new List<RM_TankView> { V(8, 50, 100, true), V(4, 50, 100, true) };
                Assert(Ids(tie, RM_LiquidNetKernel.FillPlan(tie, 5)) == "4:5", "equal fullness: the lowest id");
            });

            Case("Plan_draw_order_emptiest_holder_first", () =>
            {
                var t = new List<RM_TankView> { V(1, 80, 100, true), V(2, 10, 100, true), V(3, 20, 300, true), V(4, 99, 100, false) };
                Assert(Ids(t, RM_LiquidNetKernel.DrawPlan(t, 5)) == "3:5", "emptiest by fraction first (20/300 before 10/100)");
                Assert(Ids(t, RM_LiquidNetKernel.DrawPlan(t, 45)) == "3:20 2:10 1:15", "split across holders: " + Ids(t, RM_LiquidNetKernel.DrawPlan(t, 45)));
                Assert(RM_LiquidNetKernel.DrawPlan(t, 111) == null && RM_LiquidNetKernel.DrawAvailable(t) == 110, "more than the store holds: null; another liquid never counts");
            });

            Case("Plan_two_origins_get_the_same_plan", () =>
            {
                // the store's order differs by who asks (touching tanks lead), the plan never does
                var rnd = new Random(5);
                for (int trial = 0; trial < 200; trial++)
                {
                    var t = new List<RM_TankView>();
                    int n = 2 + rnd.Next(6);
                    for (int i = 0; i < n; i++) t.Add(V(100 + i, rnd.Next(4) == 0 ? 0 : rnd.Next(0, 100), 100, rnd.Next(5) != 0));
                    var shuffled = t.OrderBy(_ => rnd.Next()).ToList();
                    int units = 1 + rnd.Next(60);
                    string a = Ids(t, RM_LiquidNetKernel.FillPlan(t, units)), b = Ids(shuffled, RM_LiquidNetKernel.FillPlan(shuffled, units));
                    string c = Ids(t, RM_LiquidNetKernel.DrawPlan(t, units)), d = Ids(shuffled, RM_LiquidNetKernel.DrawPlan(shuffled, units));
                    Assert(a == b && c == d, "trial " + trial + ": fill " + a + " vs " + b + "; draw " + c + " vs " + d);
                }
            });

            Case("Plan_consumer_rotation_two_machines_take_turns", () =>
            {
                // one batch of liquid arrives per 250-tick cycle; machine A always ticks first (t+0), B second (t+100)
                int[] Simulate(bool rotate)
                {
                    var rot = new RM_ConsumerRotation();
                    var got = new int[2];
                    int pool = 0;
                    for (int cycle = 0; cycle < 40; cycle++)
                    {
                        pool++;
                        for (int m = 0; m < 2; m++)
                        {
                            int now = cycle * 250 + m * 100;
                            bool may = !rotate || rot.MayDraw("water", m, now);
                            if (may && pool > 0) { pool--; got[m]++; rot.Served("water", m, now); }
                            else rot.Starved("water", m, now);
                        }
                    }
                    return got;
                }
                int[] with = Simulate(true), without = Simulate(false);
                Assert(with[0] == 20 && with[1] == 20, "with rotation the two machines share 40 batches 20/20 (" + with[0] + "/" + with[1] + ")");
                Assert(without[0] == 40 && without[1] == 0, "can-fail: first-come gives A all 40 (" + without[0] + "/" + without[1] + ")");
                var solo = new RM_ConsumerRotation();
                bool held = false;
                for (int c = 0; c < 10; c++) { if (!solo.MayDraw("water", 7, c * 250)) held = true; solo.Served("water", 7, c * 250); }
                Assert(!held, "a machine alone on its liquid is never held back");
                var other = new RM_ConsumerRotation();
                other.Served("water", 1, 0);
                other.Starved("tar", 2, 10);
                Assert(other.MayDraw("water", 1, 250), "a machine starved of ANOTHER liquid does not hold this one back");
            });

            Case("Plan_callers_use_plans_and_rotation", () =>
            {
                string net = RiverSwitchFlipChecks.Src(Path.Combine("Machinery", "RM_LiquidNet.cs"));
                Assert(!net.Contains("public static Building_LiquidTank TankToFill("), "TankToFill (one tank must take the whole level) is deleted");
                RiverSwitchFlipChecks.Has(net, @"return Parts\(tanks, RM_LiquidNetKernel\.FillPlan\(Views\(tanks, liquid\), units\)\);", "FillPlan reads the kernel's fill order");
                RiverSwitchFlipChecks.Has(net, @"return Parts\(tanks, RM_LiquidNetKernel\.DrawPlan\(Views\(tanks, liquid\), units\)\);", "DrawPlan reads the kernel's draw order");
                RiverSwitchFlipChecks.Has(net, @"v\.Add\(new RM_TankView\(t\.thingIDNumber, t\.storedUnits, t\.Capacity, !t\.Empty && t\.storedLiquid == liquid, t\.Empty\)\);", "the views carry stock and id only");
                string pump = RiverSwitchFlipChecks.Src(Path.Combine("LiquidTypes", "Building_LiquidPump.cs"));
                Assert(System.Text.RegularExpressions.Regex.Matches(pump, @"plan = l == null \? null : Machinery\.RM_LiquidNet\.FillPlan\(this, l, units\);").Count == 1
                       && System.Text.RegularExpressions.Regex.Matches(pump, @"RM_TransferLeg\.Split\(plan\.Count, i => plan\[i\]\.units, \(i, k\) => plan\[i\]\.tank\.CanAccept\(l, k\)").Count == 2,
                    "the pump plans the level once (L6: per source) and both draws (channel, body) move it by the plan");
                string conv = RiverSwitchFlipChecks.Src(Path.Combine("Machinery", "CompLiquidConverter.cs"));
                RiverSwitchFlipChecks.Has(conv, @"inPlan = RM_LiquidNet\.DrawPlan\(parent, inputLiquid, n \* step\.InputUnits\);", "converter input: draw plan");
                RiverSwitchFlipChecks.Has(conv, @"outPlan = step\.product != null \? RM_LiquidNet\.FillPlan\(parent, step\.product, made\) : null;", "converter output: fill plan");
                RiverSwitchFlipChecks.Has(conv, @"if \(n > 0 && !rotation\.MayDraw\(RM_ConsumerRotation\.Key\(liquid, storeId\), parent\.thingIDNumber, now\)\)", "converter: rotation gate");
                RiverSwitchFlipChecks.Has(conv, @"rotation\.Served\(RM_ConsumerRotation\.Key\(inputLiquid, storeId\), parent\.thingIDNumber, now\);", "converter: a committed draw is recorded");
                string re = RiverSwitchFlipChecks.Src(Path.Combine("Machinery", "Kits", "RM_LiquidReaction.cs"));
                RiverSwitchFlipChecks.Has(re, @"if \(n > 0 && !rotation\.MayDraw\(rotKey, parent\.thingIDNumber, now\)\)", "reactor: rotation gate");
                RiverSwitchFlipChecks.Has(re, @"pp = toTank \? RM_LiquidNet\.FillPlan\(parent, r\.productLiquid, n \* r\.ProductUnits\) : null;", "reactor product: fill plan");
                string bath = RiverSwitchFlipChecks.Src(Path.Combine("Machinery", "Kits", "RM_LiquidBath.cs"));
                RiverSwitchFlipChecks.Has(bath, @"plan = RM_LiquidNet\.DrawPlan\(bench, bathed, ext\.UnitsPerCraft\);", "bath: draw plan");
                string ad = RiverSwitchFlipChecks.Src(Path.Combine("Machinery", "CompLiquidPipeAdapter.cs"));
                RiverSwitchFlipChecks.Has(ad, @"RM_LiquidNet\.DrawPlan\(parent, Props\.liquid, take\)", "adapter send: draw plan");
                RiverSwitchFlipChecks.Has(ad, @"RM_LiquidNet\.FillPlan\(parent, Props\.liquid, units\)", "adapter take: fill plan");
            });
        }
    }
}
