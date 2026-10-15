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
        }
    }
}
