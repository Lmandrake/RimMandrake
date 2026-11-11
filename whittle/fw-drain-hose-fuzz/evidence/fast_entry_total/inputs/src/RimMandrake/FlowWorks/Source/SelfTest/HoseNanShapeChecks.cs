// HOSE_SETTINGS_FIX_NAN_SHAPE (full-file review of HoseMath.cs, 2026-10-22): the winding-speed fix
// (FLOWWORKS_HOSE_FIX_NAN_WINDING_INSTANT) left the hose SHAPE settings read through Mathf.Clamp, which passes a NaN from
// the settings file straight into every lay (width, bend radius, slack, plump, hose length). Each read site is pinned here
// to HoseMath.FiniteClamp; the rule itself is GptEdge1016Checks' case. Red on the code the finding was made against.
using System;
using RimMandrake.FlowWorks.Hose;

namespace RimMandrake.FlowWorks.SelfTest
{
    internal static class HoseNanShapeChecks
    {
        public static void Run(Action<string, Action> Case)
        {
            Case("HoseNan_shape_settings_read_through_FiniteClamp", () =>
            {
                if (HoseMath.FiniteClamp(float.NaN, 0.5f, 2f, 1f) != 1f) throw new Exception("NaN thickness must read as the shipped 1x");
                string set = RiverSwitchFlipChecks.Src(System.IO.Path.Combine("Hose", "RM_HoseSettings.cs"));
                RiverSwitchFlipChecks.Has(set, @"WidthScale = HoseMath\.FiniteClamp\(thickness, ThicknessMin, ThicknessMax, 1f\)", "thickness read through FiniteClamp");
                RiverSwitchFlipChecks.Has(set, @"MinBendRadius = HoseMath\.FiniteClamp\(minBendRadius, 0\.3f, 4f, 1\.2f\)", "bend radius read through FiniteClamp");
                RiverSwitchFlipChecks.Has(set, @"Slack = HoseMath\.FiniteClamp\(slack, 0f, 2f, 1f\)", "slack read through FiniteClamp");
                RiverSwitchFlipChecks.Has(set, @"PlumpAmount = HoseMath\.FiniteClamp\(plumpAmount, 0f, 2f, 1f\)", "plump amount read through FiniteClamp");
                RiverSwitchFlipChecks.Has(set, @"HoseUnitsPerCell => HoseMath\.FiniteClamp\(hoseLitresPerCell,", "hose litres per cell read through FiniteClamp");
                string reel = RiverSwitchFlipChecks.Src(System.IO.Path.Combine("Hose", "CompHoseReel.cs"));
                RiverSwitchFlipChecks.Has(reel, @"MaxLength => HoseMath\.FiniteClamp\(RM_HoseSettings\.maxLength, 4f, 80f,", "hose length read through FiniteClamp");
            });
        }
    }
}
