// TANK_DEBUG_BUILD_FILL_AT_WILL: the pure half of the god-mode tank fill / empty (production RM_TankDebugMath). The Verse-bound
// click tools, the float menu and the gizmo are NOT proven here; that is the owner's live use.
using System;
using System.Linq;
using RimMandrake.FlowWorks.LiquidTypes;

namespace RimMandrake.FlowWorks.SelfTest
{
    internal static class TankDebugChecks
    {
        private static void Assert(bool ok, string msg)
        {
            if (!ok) throw new Exception(msg);
        }

        public static void Run(Action<string, Action> Case)
        {
            Case("TankDebug_picker_water_first", () =>
            {
                var l = RM_TankDebugMath.PickerOrder(new[] { "RM_Liquid_Tar", "RM_Liquid_FreshWater", "RM_Liquid_Brine", "RM_Liquid_Tar", "" });
                Assert(l.Count == 3, "deduped, blanks dropped");
                Assert(l[0] == "RM_Liquid_FreshWater", "water first");
                Assert(l[1] == "RM_Liquid_Brine" && l[2] == "RM_Liquid_Tar", "rest alphabetical");
                Assert(RM_TankDebugMath.PickerOrder(new[] { "B", "A" }).SequenceEqual(new[] { "A", "B" }), "no water: plain alphabetical");
            });
            Case("TankDebug_fill_is_capacity_and_ledger_records", () =>
            {
                Assert(RM_TankDebugMath.FillUnits(16000) == 16000, "fill = capacity");
                Assert(RM_TankDebugMath.FillUnits(-5) == 0, "can-fail: negative capacity fills nothing");
                long a = RM_TankDebugMath.DebugAddedUnits, r = RM_TankDebugMath.DebugRemovedUnits;
                RM_TankDebugMath.RecordFill(300, 16000);
                RM_TankDebugMath.RecordEmpty(50);
                Assert(RM_TankDebugMath.DebugAddedUnits - a == 16000, "added recorded");
                Assert(RM_TankDebugMath.DebugRemovedUnits - r == 350, "overwritten + emptied recorded as sink");
            });
        }
    }
}
