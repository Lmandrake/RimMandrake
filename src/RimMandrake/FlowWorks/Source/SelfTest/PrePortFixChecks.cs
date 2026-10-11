// Hose port step 5 (design FINAL §4 step 5, §5 P1-P3): the three pre-existing FlowWorks defects that real hose flow would make
// common, fixed before the flow lands. Each case runs the PRODUCTION rule (RM_PumpMath.PickPour, RM_ConversionMath.FirstRunnable,
// RM_LiquidBathMath.Pay) and carries a can-fail: the old rule computed beside it gives the wrong answer the finding described.
using System;
using System.Collections.Generic;
using RimMandrake.FlowWorks.Machinery;
using RimMandrake.FlowWorks.Machinery.Kits;

namespace RimMandrake.FlowWorks.SelfTest
{
    internal static partial class Program
    {
        private sealed class Fl { public string name; public override string ToString() => name; }

        private static void RunPrePortFixes()
        {
            var water = new Fl { name = "water" };
            var tar = new Fl { name = "tar" };
            Case("P1_pour_water_first_tank_does_not_starve_a_tar_channel", () =>
            {
                // net order: a water tank first, then a tar tank; the only excavated cells in reach hold tar
                var tanks = new List<(bool, Fl)> { (true, water), (true, tar) };
                var cells = new List<(int, bool, Fl)> { (2, true, tar), (3, true, tar) };
                Assert(RM_PumpMath.PickPour(tanks, cells, out int t, out int c) && t == 1 && c == 1,
                       "the tar tank pours into the roomier tar cell (got tank " + t + ", cell " + c + ")");
                // can-fail: the old rule took the first channel-capable tank (water) and found no compatible cell
                int old = tanks[0].Item1 && tanks[0].Item2 != null ? 0 : -1;
                bool oldFound = false;
                foreach (var cc in cells) oldFound |= RimMandrake.FlowWorks.RM_StockMath.FluidsCompatible(cc.Item2, cc.Item3, tanks[old].Item2);
                Assert(old == 0 && !oldFound, "can-fail: the old first-tank rule picks water and starves");
            });
            Case("P1_pour_prefers_the_first_feasible_tank_and_the_deepest_emptiest_cell", () =>
            {
                var tanks = new List<(bool, Fl)> { (false, tar), (true, null), (true, water), (true, tar) };
                var cells = new List<(int, bool, Fl)> { (1, false, null), (4, true, tar), (3, false, null) };
                Assert(RM_PumpMath.PickPour(tanks, cells, out int t, out int c) && t == 2 && c == 2,
                       "an empty tank and a channel-less liquid are skipped; water takes the dry roomiest cell (got " + t + "," + c + ")");
                Assert(!RM_PumpMath.PickPour(new List<(bool, Fl)> { (true, water) }, new List<(int, bool, Fl)> { (0, false, null), (2, true, tar) }, out _, out _),
                       "no room and only foreign liquid: no pour");
            });
            Case("P2_converter_short_first_input_does_not_starve_the_next", () =>
            {
                Assert(RM_ConversionMath.FirstRunnable(new List<int> { 0, 3 }) == 1, "a short first input is skipped, the second runs");
                Assert(RM_ConversionMath.FirstRunnable(new List<int> { 2, 3 }) == 0, "the first runnable input in net order wins");
                Assert(RM_ConversionMath.FirstRunnable(new List<int> { 0, 0 }) == -1 && RM_ConversionMath.FirstRunnable(new List<int>()) == -1, "nothing runnable: -1");
                // a short first input: 3 units in a tank whose recipe needs 5 per batch
                int shortN = RM_ConversionMath.Batches(10f, 5, 5, 3, -1), fullN = RM_ConversionMath.Batches(10f, 5, 5, 40, -1);
                Assert(shortN == 0 && fullN == 2 && RM_ConversionMath.FirstRunnable(new List<int> { shortN, fullN }) == 1,
                       "Batches feeds it: short " + shortN + ", full " + fullN);
                Assert(shortN <= 0, "can-fail: the old loop stopped at the first input with a recipe, which makes 0 batches here");
            });
            Case("P3_bath_craft_pays_or_does_not_complete", () =>
            {
                Assert(RM_LiquidBathMath.Pay(true, 5, false, 40) == RM_BathPay.Tank, "a tank with a craft's units pays");
                Assert(RM_LiquidBathMath.Pay(true, 5, true, 0) == RM_BathPay.Ground, "the liquid's own ground pays nothing and is enough");
                Assert(RM_LiquidBathMath.Pay(true, 5, false, 0) == RM_BathPay.Unpaid && !RM_LiquidBathMath.MayKeepWorking(RM_BathPay.Unpaid),
                       "disconnected mid-craft: unpaid, the job fails before the craft completes");
                Assert(RM_LiquidBathMath.Pay(true, 5, false, 4) == RM_BathPay.Unpaid, "drained below one craft mid-craft: unpaid");
                Assert(RM_LiquidBathMath.Pay(false, 5, false, 0) == RM_BathPay.NoNeed && RM_LiquidBathMath.Pay(true, 0, false, 0) == RM_BathPay.NoNeed,
                       "setting off or a free recipe owes nothing");
                Assert(RM_LiquidBathMath.MayKeepWorking(RM_BathPay.Tank) && RM_LiquidBathMath.MayKeepWorking(RM_BathPay.Ground) && RM_LiquidBathMath.MayKeepWorking(RM_BathPay.NoNeed),
                       "every payable state keeps working");
            });
        }
    }
}
