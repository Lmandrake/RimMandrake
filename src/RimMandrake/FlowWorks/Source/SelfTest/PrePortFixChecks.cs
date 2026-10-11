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
            Case("P11_station_reach_is_measured_from_the_footprint", () =>
            {
                // a 3x2 pumping station (reach 4) at Position (10,10), North: OccupiedRect x 9..11, z 10..11
                const int minX = 9, minZ = 10, maxX = 11, maxZ = 11;
                const float reach = 4f;
                bool In(int x, int z) => RM_PumpMath.InFootprintReach(minX, minZ, maxX, maxZ, x, z, reach);
                Assert(In(10, 6) && In(10, 15) && In(5, 10) && In(15, 11), "4 cells off every side is in reach");
                Assert(!In(10, 5) && !In(10, 16) && !In(4, 10) && !In(16, 11), "5 cells off every side is out of reach");
                Assert(!In(10, 10) && !In(11, 11), "footprint cells are not reach cells");
                Assert(In(14, 13) && !In(14, 14), "corners: (3,2) off the corner is in (13 <= 16), (3,3) is out (18 > 16)");
                // can-fail: the old circle of reach + width/2 about Position reached 5 off the bottom but only 4 off the top
                float oldR = reach + 3 / 2f;
                bool Old(int x, int z) => (x - 10) * (x - 10) + (z - 10) * (z - 10) <= oldR * oldR;
                Assert(Old(10, 5) && !Old(10, 16) && !In(10, 5), "can-fail: the old rule reaches 5 off the bottom, the footprint rule does not");
            });
            Case("P5_flood_debits_every_level_it_fills_into_a_deep_cell", () =>
            {
                // a superdeep (D4) dry cell, water at 1 unit per level, a release holding 10 units
                int t = RM_StockMath.FloodFillTarget(4, 0, 10f, 1f);
                float debit = RM_StockMath.FloodLevelDebit(0, t, 1f);
                Assert(t == 4 && debit == 4f, "a D4 fill costs four levels (got fill " + t + ", debit " + debit + ")");
                // a release that can pay for only two levels fills two, not the brim
                Assert(RM_StockMath.FloodFillTarget(4, 0, 2f, 1f) == 2, "2 units fill 2 levels of a D4 cell");
                Assert(RM_StockMath.FloodFillTarget(4, 0, 2.5f, 1f) == 3, "a part-paid level is still placed (the surface overdraw rule)");
                Assert(RM_StockMath.FloodFillTarget(4, 1, 100f, 3f) == 4 && RM_StockMath.FloodLevelDebit(1, 4, 3f) == 9f,
                       "a viscous liquid tops up a part-full cell at volumePerTile per level added");
                Assert(RM_StockMath.FloodFillTarget(2, 2, 5f, 1f) == 2 && RM_StockMath.FloodLevelDebit(2, 2, 1f) == 0f,
                       "a brimming cell is passed through for nothing");
                Assert(RM_StockMath.FloodFillTarget(3, 0, 0.1f, 1f) == 1, "a nearly spent release still places one level");
                // conservation over a release: a 9-unit release down a row of dry D4 cells writes exactly 9 levels
                float vol = 9f; int written = 0;
                while (vol > 0f) { int f = RM_StockMath.FloodFillTarget(4, 0, vol, 1f); written += f; vol -= RM_StockMath.FloodLevelDebit(0, f, 1f); }
                Assert(written == 9, "a 9-unit release writes 9 levels (got " + written + ")");
                // can-fail: the old rule (fill to DepthAt, debit one volumePerTile) writes 36 levels from the same 9 units
                float oldVol = 9f; int oldWritten = 0;
                while (oldVol > 0f) { oldWritten += 4; oldVol -= 1f; }
                Assert(oldWritten == 36 && oldWritten != written, "can-fail: the old rule wrote " + oldWritten + " levels from 9 units");
            });
            Case("P6a_flood_switch_off_keeps_hands_off_engine_cells", () =>
            {
                Assert(RM_StockMath.FloodPolicy(true, true) == RM_StockMath.FloodCellPolicy.ViaEngine, "on: an excavated cell fills through the engine");
                Assert(RM_StockMath.FloodPolicy(true, false) == RM_StockMath.FloodCellPolicy.HandsOff, "off: an excavated cell is left alone");
                Assert(RM_StockMath.FloodPolicy(false, false) == RM_StockMath.FloodCellPolicy.TempTerrain
                    && RM_StockMath.FloodPolicy(false, true) == RM_StockMath.FloodCellPolicy.TempTerrain, "a cell outside the engine gets the puddle");
                // can-fail: the old guard (setting && excavated -> engine, else temp terrain) wrote the puddle onto an engine cell when off
                bool Old(bool excavated, bool on) => !(on && excavated);   // true = temp-terrain write
                Assert(Old(true, false) && RM_StockMath.FloodPolicy(true, false) != RM_StockMath.FloodCellPolicy.TempTerrain,
                       "can-fail: the old rule wrote temp terrain onto an excavated cell with the switch off");
            });
            Case("P6b_tar_cooling_never_glazes_an_engine_cell", () =>
            {
                Assert(RM_StockMath.MayCoolToGlass(true, false), "a front cell outside the engine cools to glass");
                Assert(!RM_StockMath.MayCoolToGlass(true, true), "an excavated front cell is the engine's: no glass");
                Assert(!RM_StockMath.MayCoolToGlass(false, false), "an inner cell never cools");
                // can-fail: the old loop glazed every front cell, excavated or not
                bool Old(bool front, bool engine) => front;
                Assert(Old(true, true) && !RM_StockMath.MayCoolToGlass(true, true), "can-fail: the old rule glazed an engine cell");
            });
        }
    }
}
