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
                // can-fail is NOT a copy of the old rule written here: the old circle about Position lived in Building_LiquidPump.ReachCells (Verse, not compiled here);
                // selftest_flowworks_call_sites.py asserts that production site calls the function above, that the old rule
                // is absent from it, and proves both go red on a temp copy with the call deleted / the old rule spliced back.
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
                // can-fail is NOT a copy of the old rule written here: the old fill-to-DepthAt, debit-one-level rule lived in Flood_FlowWorks.PlaceFluid (Verse);
                // selftest_flowworks_call_sites.py asserts that production site calls the function above, that the old rule
                // is absent from it, and proves both go red on a temp copy with the call deleted / the old rule spliced back.
            });
            Case("P6a_flood_switch_off_keeps_hands_off_engine_cells", () =>
            {
                Assert(RM_StockMath.FloodPolicy(true, true) == RM_StockMath.FloodCellPolicy.ViaEngine, "on: an excavated cell fills through the engine");
                Assert(RM_StockMath.FloodPolicy(true, false) == RM_StockMath.FloodCellPolicy.HandsOff, "off: an excavated cell is left alone");
                Assert(RM_StockMath.FloodPolicy(false, false) == RM_StockMath.FloodCellPolicy.TempTerrain
                    && RM_StockMath.FloodPolicy(false, true) == RM_StockMath.FloodCellPolicy.TempTerrain, "a cell outside the engine gets the puddle");
                // can-fail is NOT a copy of the old rule written here: the old setting-and-excavated guard lived in Flood_FlowWorks.PlaceFluid (Verse);
                // selftest_flowworks_call_sites.py asserts that production site calls the function above, that the old rule
                // is absent from it, and proves both go red on a temp copy with the call deleted / the old rule spliced back.
            });
            Case("P6b_tar_cooling_never_glazes_an_engine_cell", () =>
            {
                Assert(RM_StockMath.MayCoolToGlass(true, false), "a front cell outside the engine cools to glass");
                Assert(!RM_StockMath.MayCoolToGlass(true, true), "an excavated front cell is the engine's: no glass");
                Assert(!RM_StockMath.MayCoolToGlass(false, false), "an inner cell never cools");
                // can-fail is NOT a copy of the old rule written here: the old every-front-cell loop lived in Flood_FlowWorks.CoolFrontToGlass (Verse);
                // selftest_flowworks_call_sites.py asserts that production site calls the function above, that the old rule
                // is absent from it, and proves both go red on a temp copy with the call deleted / the old rule spliced back.
            });
            Case("P8_burn_pulse_never_consumes_replacement_water", () =>
            {
                // the timing guard: a Maintain check always lands between two flow pulses
                Assert(RM_FireMath.FireCheckIntervalTicks < RM_FireMath.MinFlowPulseTicks,
                       "fire check (" + RM_FireMath.FireCheckIntervalTicks + ") is shorter than the pulse floor (" + RM_FireMath.MinFlowPulseTicks + ")");
                int canal = RM_FireMath.TicksPerCanalLevel(1f);
                int acc = canal - 1;
                Assert(RM_FireMath.CanalLevelsToBurn(false, ref acc, 250, canal) == 0 && acc == canal - 1,
                       "water standing on a lit cell burns no level and does not advance the accumulator");
                Assert(RM_FireMath.CanalLevelsToBurn(true, ref acc, 250, canal) == 1, "oil still burns its due level");
                // can-fail: the old pulse ran LevelsDue on whatever filled the cell, so a refill one tick before the due level burned it
                int oldAcc = canal - 1;
                Assert(RM_FireMath.LevelsDue(ref oldAcc, 250, canal) == 1, "can-fail: the old rule burned a level of the replacement water");
            });
            Case("P9b_natural_heat_list_goes_stale_on_a_kind_change_not_15000_ticks_later", () =>
            {
                Assert(RM_LiquidHeatMath.TerrainChangeStalesNatural(1, 0, false), "hot water drained to sand: stale");
                Assert(RM_LiquidHeatMath.TerrainChangeStalesNatural(0, -1, false), "icy water painted in: stale");
                Assert(RM_LiquidHeatMath.TerrainChangeStalesNatural(1, -1, false), "hot to icy: stale");
                Assert(!RM_LiquidHeatMath.TerrainChangeStalesNatural(1, 1, false) && !RM_LiquidHeatMath.TerrainChangeStalesNatural(0, 0, false),
                       "same kind (a floor laid on sand, hot shallow to hot deep): the cached entry is still right");
                Assert(!RM_LiquidHeatMath.TerrainChangeStalesNatural(0, 1, true), "an excavated cell is read live every interval: no rescan");
                // the production wiring: the postfix sits on the one choke point every vanilla terrain write ends in, binds the
                // decompiled parameter names (a wrong name fails Harmony's binding), and marks the list stale
                string heat = RiverSwitchFlipChecks.Src("RM_LiquidHeat.cs");
                RiverSwitchFlipChecks.Has(heat, @"\[HarmonyPatch\(typeof\(TerrainGrid\), ""DoTerrainChangedEffects""\)\]", "patch target");
                RiverSwitchFlipChecks.Has(heat, @"Postfix\(Map ___map, IntVec3 c, TerrainDef oldTerr, TerrainDef newTerr\)", "parameter names");
                RiverSwitchFlipChecks.Has(heat, @"TerrainChangeStalesNatural\(o, n, ex\.IsExcavated\(c\)\)\) \{ ex\.LiquidHeat\.NotifyNaturalStale\(\);", "stale notice");
                RiverSwitchFlipChecks.Has(heat, @"public void NotifyNaturalStale\(\) \{ nextRescanTick = 0;", "notice forces the next interval's rescan");
                // can-fail: the old rule had no notice, so a drained hot spring kept heating for up to RescanTicks
                var m = System.Text.RegularExpressions.Regex.Match(heat, @"public const int RescanTicks = (\d+);");
                Assert(m.Success && int.Parse(m.Groups[1].Value) / RM_LiquidHeatMath.IntervalTicks == 60,
                       "can-fail: without the notice the stale list lives 60 intervals (RescanTicks), with it at most one");
                Assert(!System.Text.RegularExpressions.Regex.IsMatch(heat.Replace("IntVec3 c, TerrainDef oldTerr", "IntVec3 cell, TerrainDef oldTerr"),
                                                                     @"Postfix\(Map ___map, IntVec3 c, TerrainDef oldTerr, TerrainDef newTerr\)"),
                       "can-fail probe: the binding check rejects a mis-named parameter");
            });
        }
    }
}
