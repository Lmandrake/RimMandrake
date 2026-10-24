// FlowWorks GPT high-depth review 2026-10-23, batch A (liquid-sim core), fixed 2026-10-24.
// Report: Transient/flowworks_takeover_20261023/GPT_REVIEW.md. Each case runs the PRODUCTION rule; the Verse-bound call
// sites are held by selftest_flowworks_gpt_batch_a.py (source shape, each with an undo probe that must go red).
using System;
using RimMandrake.FlowWorks.Drilling;
using RimMandrake.FlowWorks.LiquidTypes;

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
        }
    }
}
