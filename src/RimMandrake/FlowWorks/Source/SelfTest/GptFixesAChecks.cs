// FlowWorks pre-release GPT consult fixes, builder A (liquid network, tanks, hoses, bottles), 2026-10-15.
// Triage: Transient/release_push_2026-10-15/gpt_FlowWorks/TRIAGE.md. Each case runs the PRODUCTION rule and would have gone red
// on the code the finding was made against.
using System;
using System.Collections.Generic;
using RimMandrake.FlowWorks.LiquidTypes;
using RimMandrake.FlowWorks.Machinery;

namespace RimMandrake.FlowWorks.SelfTest
{
    internal static class GptFixesAChecks
    {
        private static void Assert(bool ok, string msg)
        {
            if (!ok) throw new Exception(msg);
        }

        public static void Run(Action<string, Action> Case)
        {
            // final review row 33: apparel corroded to 0 HP is destroyed (vanilla wear-out), never orphaned by a bare Remove.
            Case("GptA_corrosion_destroys_worn_out_apparel", () =>
            {
                string src = RiverSwitchFlipChecks.Src(System.IO.Path.Combine("LiquidTypes", "LiquidCorrosion.cs"));
                Assert(!src.Contains("pawn.apparel.Remove(piece)"), "a corroded-away piece is not merely removed (orphaned Thing)");
                RiverSwitchFlipChecks.Has(src, @"if \(piece\.HitPoints <= 0\)\s*\{[^}]*piece\.Destroy\(\);", "a piece at 0 HP is destroyed");
                RiverSwitchFlipChecks.Has(src, @"if \(!piece\.def\.useHitPoints\)", "an item without hit points is never worn away");
                Assert(!src.Contains("has never ticked inside a running game") && !RiverSwitchFlipChecks.Src(System.IO.Path.Combine("LiquidTypes", "LiquidIgnition.cs")).Contains("this has never shipped"),
                    "corrosion/ignition comments no longer say they never shipped");
            });

            // LIQUID_ROTATION_FIX_STARVED_STRANGER C1-F4: B sits on another store with less than one batch; A must keep drawing.
            Case("GptA_rotation_starved_stranger_on_another_store_never_stalls", () =>
            {
                var rot = new RM_ConsumerRotation();
                int aDrew = 0;
                for (int c = 0; c < 20; c++)
                {
                    int now = c * 250;
                    object ka = RM_ConsumerRotation.Key("water", 100), kb = RM_ConsumerRotation.Key("water", 200);
                    if (rot.MayDraw(ka, 1, now)) { aDrew++; rot.Served(ka, 1, now); } else rot.Starved(ka, 1, now);
                    rot.Starved(kb, 2, now + 50);   // B: its own store never holds a batch
                }
                Assert(aDrew == 20, "A on store 100 draws every cycle while B starves on store 200 (" + aDrew + "/20)");
                Assert(!Equals(RM_ConsumerRotation.Key("water", 1), RM_ConsumerRotation.Key("water", 2)) && Equals(RM_ConsumerRotation.Key("water", 1), RM_ConsumerRotation.Key("water", 1)),
                    "keys differ per store, equal within one");
            });

            // C1-F4 on ONE store: B's batch is more than the store ever holds; A yields once, B still goes without, A resumes.
            Case("GptA_rotation_unservable_neighbour_forfeits_after_one_yield", () =>
            {
                foreach (bool bFirst in new[] { false, true })
                {
                    var rot = new RM_ConsumerRotation();
                    object k = RM_ConsumerRotation.Key("water", 7);
                    int pool = 0, aDrew = 0;
                    for (int c = 0; c < 30; c++)
                    {
                        pool += 3;   // A needs 3 a batch, B needs 50: B can never run
                        for (int step = 0; step < 2; step++)
                        {
                            bool isA = (step == 0) != bFirst;
                            int now = c * 250 + step * 100;
                            if (isA)
                            {
                                if (pool >= 3 && rot.MayDraw(k, 1, now)) { pool -= 3; aDrew++; rot.Served(k, 1, now); }
                                else rot.Starved(k, 1, now);
                            }
                            else if (pool >= 50 && rot.MayDraw(k, 2, now)) { pool -= 50; rot.Served(k, 2, now); }
                            else rot.Starved(k, 2, now);
                        }
                    }
                    Assert(aDrew >= 18, "B " + (bFirst ? "ticking first" : "ticking second") + " with an unservable batch must not stall A: A drew " + aDrew + "/30");
                }
            });

            // C1-F16: a machine with two runnable inputs takes them in turn.
            Case("GptA_converter_multi_input_rotates", () =>
            {
                var b = new List<int> { 2, 3 };
                Assert(RM_ConversionMath.NextRunnable(b, -1) == 0, "nothing ran yet: the first runnable");
                Assert(RM_ConversionMath.NextRunnable(b, 0) == 1, "input 0 ran last: input 1 runs");
                Assert(RM_ConversionMath.NextRunnable(b, 1) == 0, "input 1 ran last: wraps to input 0");
                Assert(RM_ConversionMath.NextRunnable(new List<int> { 0, 3 }, 1) == 1, "the only runnable input runs every cycle");
                Assert(RM_ConversionMath.NextRunnable(new List<int> { 0, 0 }, 0) == -1 && RM_ConversionMath.NextRunnable(new List<int>(), -1) == -1, "nothing runnable: -1");
                string conv = RiverSwitchFlipChecks.Src(System.IO.Path.Combine("Machinery", "CompLiquidConverter.cs"));
                RiverSwitchFlipChecks.Has(conv, @"int pick = RM_ConversionMath\.NextRunnable\(batches, cand\.FindIndex\(c => c\.input == lastInput\)\);", "converter picks after the last input");
                RiverSwitchFlipChecks.Has(conv, @"lastInput = inputLiquid;", "converter records the input that ran");
                RiverSwitchFlipChecks.Has(conv, @"Scribe_Defs\.Look\(ref lastInput, ""RM_convLastInput""\);", "the last input is saved");
            });

            // BOTTLE_STOCK_MEND_FREE_REFILLS C2-F2/C2-F3: fill and wash from terrain pay the pond body; C2-F9: no free repair.
            Case("GptA_bottle_fill_and_wash_pay_the_body_and_keep_wear", () =>
            {
                Assert(Math.Abs(RM_ContainerMaterialMath.BodyStockFor(5, 1f, 5) - 1f) < 1e-6f, "a level's worth of units costs one level of stock");
                Assert(Math.Abs(RM_ContainerMaterialMath.BodyStockFor(1, 2f, 5) - 0.4f) < 1e-6f, "a viscous liquid (2 per tile) costs its share");
                Assert(RM_ContainerMaterialMath.BodyStockFor(0, 1f, 5) == 0f && RM_ContainerMaterialMath.BodyStockFor(3, 0f, 5) == 0f, "nothing for nothing");
                Assert(RM_ContainerMaterialMath.CarriedHitPoints(30, 60, 60) == 30, "a half-worn bottle stays half-worn");
                Assert(RM_ContainerMaterialMath.CarriedHitPoints(30, 60, 100) == 50, "the worn fraction carries to a bigger max");
                Assert(RM_ContainerMaterialMath.CarriedHitPoints(1, 100, 10) == 1, "never rounds a live container to 0");
                Assert(RM_ContainerMaterialMath.CarriedHitPoints(5, 0, 40) == 40, "a source with no hit points gives full");
                Assert(RM_ContainerMaterialMath.CarriedHitPoints(80, 60, 60) == 60, "never above the max");
                string util = RiverSwitchFlipChecks.Src(System.IO.Path.Combine("LiquidTypes", "RM_LiquidBottleUtility.cs"));
                RiverSwitchFlipChecks.Has(util, @"made\.HitPoints = RM_ContainerMaterialMath\.CarriedHitPoints\(from\.HitPoints, from\.MaxHitPoints, made\.MaxHitPoints\);", "MakeContainer carries the wear");
                RiverSwitchFlipChecks.Has(util, @"return ex\.Stock\.TryDebit\(map, c, stock, ex\);", "terrain debit spends the body");
                RiverSwitchFlipChecks.Has(util, @"if \(ex\?\.Stock != null && !ex\.Stock\.CanSupply\(map, c, ex\)\)", "the search skips a spent body");
                string fill = RiverSwitchFlipChecks.Src(System.IO.Path.Combine("LiquidTypes", "JobDriver_FillBottle.cs"));
                RiverSwitchFlipChecks.Has(fill, @"if \(!RM_LiquidBottleUtility\.TryDebitTerrain\(Map, job\.targetB\.Cell, RM_ContainerMaterials\.UnitsIn\(carried, liquid, size\)\)\) \{ return; \} Thing filled", "fill debits before it makes the bottle");
                string wash = RiverSwitchFlipChecks.Src(System.IO.Path.Combine("LiquidTypes", "JobDriver_WashBottle.cs"));
                RiverSwitchFlipChecks.Has(wash, @"if \(!RM_LiquidBottleUtility\.TryDebitTerrain\(Map, job\.targetB\.Cell, liquid\.UnitsFor\(size\)\)\) \{ return; \} Thing empty", "wash debits before it cleans");
            });

            // TANK_SETTLE_FIX_DOUBLE_DIPPED C1-F5: a Store tank in two components is settled once per cycle, not once per component.
            Case("GptA_settle_tank_in_two_components_shares_one_budget", () =>
            {
                // component 1: Empty tank E (id 1, 50 water) and Store S (id 2, empty). component 2: S and Fill tank F (id 3, empty).
                int sUnits = 0, fUnits = 0;
                List<(int src, int dst, int units)> Run(bool shared, Dictionary<int, int> sent, Dictionary<int, int> recv)
                {
                    var c1 = new List<RM_SettleTank> { new RM_SettleTank(1, 50, 100, "water", RM_TankMode.Empty), new RM_SettleTank(2, sUnits, 100, "water", RM_TankMode.Store) };
                    var p1 = shared ? RM_LiquidNetKernel.SettlePlan(c1, 10, 0, sent, recv) : RM_LiquidNetKernel.SettlePlan(c1, 10, 0);
                    foreach (var m in p1) { if (c1[m.dst].Id == 2) sUnits += m.units; if (shared) { sent[c1[m.src].Id] = (sent.TryGetValue(c1[m.src].Id, out int a) ? a : 0) + m.units; recv[c1[m.dst].Id] = (recv.TryGetValue(c1[m.dst].Id, out int b) ? b : 0) + m.units; } }
                    var c2 = new List<RM_SettleTank> { new RM_SettleTank(2, sUnits, 100, "water", RM_TankMode.Store), new RM_SettleTank(3, fUnits, 100, null, RM_TankMode.Fill) };
                    var p2 = shared ? RM_LiquidNetKernel.SettlePlan(c2, 10, 0, sent, recv) : RM_LiquidNetKernel.SettlePlan(c2, 10, 0);
                    foreach (var m in p2) if (c2[m.dst].Id == 3) { fUnits += m.units; sUnits -= m.units; }
                    return p2;
                }
                Run(false, null, null);
                Assert(fUnits == 10, "can-fail: today's per-component plan sends on the 10 units S received this settle (F got " + fUnits + ")");
                sUnits = 0; fUnits = 0;
                Run(true, new Dictionary<int, int>(), new Dictionary<int, int>());
                Assert(fUnits == 0 && sUnits == 10, "with the shared budget S sends nothing it received this settle (F " + fUnits + ", S " + sUnits + ")");
                // a sender's budget is shared too: S starts with 40, sends 10 to F in component 2 after sending 10 elsewhere
                var sent2 = new Dictionary<int, int> { { 2, 10 } };
                var plan = RM_LiquidNetKernel.SettlePlan(new List<RM_SettleTank> { new RM_SettleTank(2, 40, 100, "water", RM_TankMode.Store), new RM_SettleTank(3, 0, 100, null, RM_TankMode.Fill) }, 10, 0, sent2, new Dictionary<int, int>());
                Assert(plan.Count == 0, "a tank that already sent its 10 this settle sends no more (" + plan.Count + " moves)");
                string net = RiverSwitchFlipChecks.Src(System.IO.Path.Combine("Machinery", "RM_LiquidNet.cs"));
                RiverSwitchFlipChecks.Has(net, @"sentById\[src\.thingIDNumber\] = .*\+ mv\.Moved; recvById\[dst\.thingIDNumber\] = .*\+ mv\.Moved;", "SettleTick records committed moves per tank");
            });
        }
    }
}
