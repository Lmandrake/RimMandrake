// FlowWorks fixes from the GPT edge-case consult of 2026-10-16 (design/RimMandrake/gpt_consults/FlowWorks_edge_cases_2026-10-16.md).
// Each case runs the PRODUCTION rule (or pins its call site) and went red on the code the finding was made against.
using System;
using System.Collections.Generic;
using RimMandrake.FlowWorks.Hose;
using RimMandrake.FlowWorks.Machinery;

namespace RimMandrake.FlowWorks.SelfTest
{
    internal static class GptEdge1016Checks
    {
        private static void Assert(bool ok, string msg)
        {
            if (!ok) throw new Exception(msg);
        }

        public static void Run(Action<string, Action> Case)
        {
            // FLOWWORKS_HOSE_FIX_NAN_WINDING_INSTANT: NaN in the settings file never reaches the winding rate.
            Case("Gpt1016_hose_nan_setting_reads_as_default", () =>
            {
                Assert(HoseMath.FiniteClamp(float.NaN, 0.5f, 10f, 3f) == 3f, "NaN winding speed reads as the default");
                Assert(HoseMath.FiniteClamp(float.PositiveInfinity, 0.5f, 10f, 3f) == 10f && HoseMath.FiniteClamp(float.NegativeInfinity, 0.5f, 10f, 3f) == 0.5f, "infinities clamp");
                Assert(HoseMath.FiniteClamp(4f, 0.5f, 10f, 3f) == 4f && HoseMath.FiniteClamp(0.1f, 0.5f, 10f, 3f) == 0.5f, "finite values clamp as before");
                Assert(!RM_HoseLegacyMath.TryFloat("NaN", out _) && !RM_HoseLegacyMath.TryFloat("Infinity", out _) && RM_HoseLegacyMath.TryFloat("2.5", out float f) && f == 2.5f,
                    "legacy import refuses non-finite floats");
                string job = RiverSwitchFlipChecks.Src(System.IO.Path.Combine("Hose", "Jobs", "JobDriver_CarryHoseEnd.cs"));
                RiverSwitchFlipChecks.Has(job, @"windCellsPerSecond => HoseMath\.FiniteClamp\(RM_HoseSettings\.windCellsPerSecond, 0\.5f, 10f, 3f\)", "winding speed read through FiniteClamp");
                RiverSwitchFlipChecks.Has(job, @"HoseMath\.FiniteClamp\(RM_HoseSettings\.handlingTime, 0\.25f, 3f, 1f\)", "handling time read through FiniteClamp");
            });

            // FLOWWORKS_CONVERTER_FIX_BLOCKED_STARVES_REST: recipes of 10 and 100 units at 1 unit a rare tick, the first blocked
            // (output full). The converter's own cycle (CapAccrued -> Batches -> NextRunnable -> AccruedAfterPick) must let the
            // 100-unit recipe run; keeping candidate 0's cap held the budget at 10 for ever.
            Case("Gpt1016_converter_blocked_small_recipe_does_not_starve_big_one", () =>
            {
                int[] iu = { 10, 100 };
                int Cycle(bool oldRule)
                {
                float accrued = 0f, perTick = 1f;
                int ran = 0, last = -1;
                for (int t = 0; t < 400; t++)
                {
                    accrued += perTick;
                    var capped = new List<float>();
                    var batches = new List<int>();
                    for (int i = 0; i < 2; i++)
                    {
                        float c = RM_ConversionMath.CapAccrued(accrued, iu[i], perTick);
                        capped.Add(c);
                        batches.Add(RM_ConversionMath.Batches(c, iu[i], 1, 1000, i == 0 ? 0 : 1000));
                    }
                    int pick = RM_ConversionMath.NextRunnable(batches, last);
                    accrued = oldRule ? capped[pick >= 0 ? pick : 0] : RM_ConversionMath.AccruedAfterPick(accrued, capped, pick);
                    if (pick >= 0) { accrued -= batches[pick] * iu[pick]; ran += batches[pick]; last = pick; }
                }
                return ran;
                }
                int ranNew = Cycle(false), ranOld = Cycle(true);
                Assert(ranNew >= 3 && ranOld == 0, "the 100-unit recipe ran " + ranNew + " batches in 400 rare ticks (want >= 3); old rule probe " + ranOld + " (want 0, else the scene cannot fail)");
                Assert(RM_ConversionMath.AccruedAfterPick(5f, new List<float> { 2f, 4f }, 0) == 2f && RM_ConversionMath.AccruedAfterPick(5f, new List<float>(), -1) == 5f, "a pick keeps its own cap; no candidates keeps the budget");
                string conv = RiverSwitchFlipChecks.Src(System.IO.Path.Combine("Machinery", "CompLiquidConverter.cs"));
                RiverSwitchFlipChecks.Has(conv, @"accrued = RM_ConversionMath\.AccruedAfterPick\(accrued, cand\.Select\(c => c\.capped\)\.ToList\(\), pick\);", "converter keeps the budget through AccruedAfterPick");
            });

            // FLOWWORKS_REACTOR_FIX_STUCK_ENDS_SHIFT: a supplied reaction that cannot run moves on to the next one (call-site pin;
            // the loop is Verse-bound). Exactly one `return` stays inside the reaction loop body: the failed committed move.
            Case("Gpt1016_reactor_stalled_reaction_does_not_end_the_shift", () =>
            {
                string src = RiverSwitchFlipChecks.Src(System.IO.Path.Combine("Machinery", "Kits", "RM_LiquidReaction.cs"));
                RiverSwitchFlipChecks.Has(src, @"if \(n <= 0\)\s*\{\s*stalled = stalled \?\? \(string\)""RMFlow_ReactorWorking""[^;]*;\s*continue;\s*\}", "n <= 0 continues");
                RiverSwitchFlipChecks.Has(src, @"if \(pa == null \|\| pb == null \|\| \(toTank && pp == null\)\)\s*\{\s*stalled = stalled \?\?[^;]*;\s*continue;\s*\}", "no draw/fill plan continues");
                RiverSwitchFlipChecks.Has(src, @"if \(stalled != null\)\s*\{\s*status = stalled;\s*return;\s*\}", "the first stall's status stands when nothing ran");
            });
        }
    }
}
