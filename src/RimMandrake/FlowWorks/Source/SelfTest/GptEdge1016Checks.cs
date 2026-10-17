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
        }
    }
}
