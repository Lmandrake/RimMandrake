// FlowWorks GPT high-depth review 2026-10-23, batch A (liquid-sim core), fixed 2026-10-24.
// Report: Transient/flowworks_takeover_20261023/GPT_REVIEW.md. Each case runs the PRODUCTION rule; the Verse-bound call
// sites are held by selftest_flowworks_gpt_batch_a.py (source shape, each with an undo probe that must go red).
using System;
using RimMandrake.FlowWorks.Drilling;
using RimMandrake.FlowWorks.LiquidTypes;
using RimMandrake.FlowWorks.MapControls;

namespace RimMandrake.FlowWorks.SelfTest
{
    internal static class GptBatchA1024Checks
    {
        private static void Assert(bool ok, string msg)
        {
            if (!ok) throw new Exception(msg);
        }

        public static void Run(Action<string, Action> Case)
        {
            // DUG_WATER_FILL_FIX_NO_CANAL_DEBIT (FA_core_sim_1.1): a fill from a dug cell is paid by the cell.
            Case("GptA1024_dug_cell_fill_pays_from_the_cell", () =>
            {
                const long U = RM_LevelSolve.U;
                Assert(RM_ContainerMaterialMath.DugCellDebitDl(50, 5000, true, U) == 50, "exact water pays the bottle to the decilitre");
                Assert(RM_ContainerMaterialMath.DugCellDebitDl(50, 40, true, U) == -1, "a sheet thinner than the bottle cannot pay");
                Assert(RM_ContainerMaterialMath.DugCellDebitDl(50, 0, true, U) == -1, "a dry dug cell cannot pay (the old code paid for free)");
                Assert(RM_ContainerMaterialMath.DugCellDebitDl(50, 2 * U, false, U) == U, "whole-notch water rounds the draw up to a notch");
                Assert(RM_ContainerMaterialMath.DugCellDebitDl((int)U + 1, 2 * U, false, U) == 2 * U, "just over a notch takes two");
                Assert(RM_ContainerMaterialMath.DugCellDebitDl((int)U + 1, U + 5, false, U) == -1, "never takes more than the cell holds");
                Assert(RM_ContainerMaterialMath.DugCellDebitDl(0, 0, true, U) == 0, "nothing for nothing");
            });

            // DRILL_FILL_FIX_LOSES_FRACTIONAL_BRIM (FA_core_sim_1.2): the drill is charged what landed in the outlet.
            Case("GptA1024_drill_spends_only_what_landed", () =>
            {
                const long U = RM_LevelSolve.U;
                // GPT's scene: a one-notch outlet holding 5,000 dL filled to its 10,000 dL brim. Old rule charged a whole level.
                float spent = RM_DrillSurveyMath.SpentUnits(5000, U, U, 1f);
                Assert(Math.Abs(spent - 0.5f) < 1e-6f, "half a level landed, half a level spent (old: 1, losing 5,000 dL), got " + spent);
                Assert(Math.Abs(RM_DrillSurveyMath.SpentUnits(0, 3 * U, U, 2f) - 6f) < 1e-5f, "whole levels of a viscous liquid cost their units");
                Assert(RM_DrillSurveyMath.SpentUnits(U, U, U, 1f) == 0f && RM_DrillSurveyMath.SpentUnits(U, 0, U, 1f) == 0f, "nothing landed, nothing spent");
            });

            // DISABLED_LIQUID_FIX_LIMITLESS_SOURCE (FA_core_sim_2.1): the exact kernel took the -2 "disabled" sentinel for a
            // limitless mouth. A finite pond of a switched-off liquid beside a dug channel must feed it nothing.
            Case("GptA1024_exact_kernel_disabled_pond_feeds_nothing", () =>
            {
                foreach (bool disabled in new[] { false, true })
                {
                    var w = new ArrayWorld(8, 3);
                    w.k.levelBySurfaceEnabled = true; w.k.levelSetEnabled = true; w.k.creepWaterEnabled = true;
                    w.k.creepEnabled = true; w.k.viscosityEnabled = true; w.k.levelExactEnabled = true;
                    var body = w.AddBody(false, 4f, new[] { 1 * 8 + 1 });
                    w.bed[1 * 8 + 1] = 4;
                    var canal = new System.Collections.Generic.List<int> { 1 * 8 + 2, 1 * 8 + 3, 1 * 8 + 4 };
                    foreach (int c in canal) w.k.depth[c] = 4;
                    if (disabled) w.disabledFluid = ArrayWorld.Water;
                    for (int p = 0; p < 60; p++) w.Pulse(canal);
                    long wet = 0; foreach (int c in canal) wet += w.k.WaterOf(c);
                    if (disabled)
                        Assert(wet == 0 && body.Dl() == 4L * RM_LevelSolve.U, $"a switched-off pond feeds no channel (old: limitless mouth): canal {wet} dL, pond {body.Dl()} dL");
                    else
                        Assert(wet > 0, "control: the same pond allowed does feed the channel (the scene can see a feed): " + wet);
                }
            });

            // LEVEL_HOLDER_FIX_REFILLS_FRACTIONAL_BASIN (FA_core_sim_2.3): the holder measures held water in dL.
            Case("GptA1024_level_holder_counts_a_spread_sheet", () =>
            {
                const long U = RM_LevelSolve.U;
                // GPT's scene: five depth-1 squares, 50%, three levels spread as a 60% sheet (6,000 dL each, no whole notch).
                int held = RM_MapControlMath.HeldLevels(5 * 6000, U);
                Assert(held == 3, "a 60% sheet over five squares holds three levels, got " + held);
                Assert(RM_MapControlMath.LevelHolderNeed(held, 5, 0.5f) == 0, "a satisfied basin needs nothing (old: read 0 held, poured 3)");
                Assert(RM_MapControlMath.HeldLevels(900, U) == 0 && RM_MapControlMath.HeldLevels(U / 2, U) == 1, "rounds to the nearest level");
                Assert(RM_MapControlMath.HeldLevels(-5, U) == 0 && RM_MapControlMath.HeldLevels(U, 0) == 0, "nothing from nothing");
            });

            // LEVELLING_BANDS_FIX_STOPS_PAST_EIGHT (FA_core_sim_2.6): whole-notch levelling below eight bands.
            Case("GptA1024_levelset_levels_a_deep_canal", () =>
            {
                foreach (byte dep in new byte[] { 4, 10, 40 })
                {
                    var w = new ArrayWorld(5, 3);
                    w.k.levelBySurfaceEnabled = true; w.k.levelSetEnabled = true; w.k.levelExactEnabled = false;
                    int[] cells = { 1 * 5 + 1, 1 * 5 + 2, 1 * 5 + 3 };
                    byte[] start = { 3, 2, 1 };
                    for (int i = 0; i < 3; i++) { w.k.depth[cells[i]] = dep; w.k.fill[cells[i]] = start[i]; }
                    w.Sync();
                    for (int p = 0; p < 20; p++) w.Pulse(cells);
                    string got = w.k.fill[cells[0]] + "," + w.k.fill[cells[1]] + "," + w.k.fill[cells[2]];
                    Assert(got == "2,2,2", $"three depth-{dep} squares holding 3,2,1 level to 2,2,2 (old: past eight bands the solve gave up), got {got}");
                }
            });

            // TAR_GLASS_FLOOD_FIX_UNREACHABLE_PATH (FA_core_sim_1.8, option A): a tar release only reaches dug cells and dug
            // cells never cool, so the old rule wrote no glass at all. The bank (undug ground beside the release) now hardens.
            Case("GptA1024_tar_release_in_a_dug_channel_leaves_a_glass_bank", () =>
            {
                // 5 x 3 grid: a dug channel along row 1 (x = 1..3), all placed; (0,1) was offered and refused; (4,1) is rock.
                const int W = 5, H = 3;
                var placed = new System.Collections.Generic.List<int> { 1 * W + 1, 1 * W + 2, 1 * W + 3 };
                var offered = new System.Collections.Generic.HashSet<int>(placed) { 1 * W + 0 };
                int rock = 1 * W + 4;
                Assert(!RM_StockMath.MayCoolToGlass(true, true), "the old rule alone: every placed cell is dug, so none cools");
                var bank = RM_StockMath.GlassBankCells(W, H, placed, offered.Contains, n => n != rock);
                var want = new System.Collections.Generic.HashSet<int> { 0 * W + 1, 0 * W + 2, 0 * W + 3, 2 * W + 1, 2 * W + 2, 2 * W + 3 };
                Assert(bank.Count == want.Count && want.SetEquals(bank), "the six undug cells either side of the channel harden, got " + string.Join(",", bank));
                Assert(!bank.Contains(1 * W + 0) && !bank.Contains(rock), "an offered cell and an unbankable cell never harden");
                var corner = RM_StockMath.GlassBankCells(W, H, new[] { 0 }, n => n == 0, n => true);
                Assert(corner.Count == 2 && corner.Contains(1) && corner.Contains(W), "a map-corner cell banks only its two in-grid neighbours");
                Assert(RM_StockMath.GlassBankCells(W, H, new int[0], n => false, n => true).Count == 0, "no placed cell, no bank");
            });
        }
    }
}
