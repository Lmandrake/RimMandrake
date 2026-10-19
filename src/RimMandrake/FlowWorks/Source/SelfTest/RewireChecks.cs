// LIQUID_DEPTH_REWIRE_FIVE_IS_DEAD (plan P4, design/RimMandrake/flowworks_unified_depth_2026-10-17.md §7.2) and
// DEPTH_READOUT_BUILD_TWO_NUMBERS_NOT_ONE (plan P8): one ruler for every liquid. Arithmetic is the PRODUCTION Verse-free code;
// the wiring (look rule, readers, settings) is read from production source.
using System;
using System.IO;
using System.Text.RegularExpressions;

namespace RimMandrake.FlowWorks.SelfTest
{
    internal static class RewireChecks
    {
        private static void Assert(bool ok, string msg)
        {
            if (!ok) throw new Exception(msg);
        }

        public static void Run(Action<string, Action> Case)
        {
            Case("Rewire_fill_look_is_metres_of_water", () =>
            {
                int U = RM_LevelSolve.U;
                // the same water reads the same look in any hole: 1 m of water in a 1 m canal, a 1.5 m canal and a 2 m pit
                Assert(RM_LevelSolve.LookBand(2L * U) == 3, "1 m of water is the 1 m look");
                Assert(RM_LevelSolve.LookBand(U * 45L / 1000) == 1, "a 4.5 cm sheet is the very-shallow look, in a canal or a pit");
                string ex = RiverSwitchFlipChecks.Src("RM_MapComponent_Excavation.cs");
                RiverSwitchFlipChecks.Has(ex, @"want = fluid\.WetTerrainForBand\(RM_ExcavationDepth\.FillTier\(WaterDl\(i\)\)\);",
                    "ApplyFillTerrain: one rule, by the cell's decilitres, for canals AND pits (P14: via the one ladder)");
                Assert(!Regex.IsMatch(ex, @"FillTerrainFor\("), "no fullness-keyed look is left (FillTerrainFor deleted)");
                string fd = RiverSwitchFlipChecks.Src("FluidDef.cs");
                Assert(!Regex.IsMatch(fd, @"public TerrainDef FillTerrainFor\("), "FluidDef.FillTerrainFor (by fraction) is deleted");
                string dep = RiverSwitchFlipChecks.Src("RM_ExcavationDepth.cs");
                RiverSwitchFlipChecks.Has(dep, @"public static int FillTier\(long waterDl\) \{ return RM_LevelSolve\.LookBand\(waterDl\); \}",
                    "FillTier is the metres-of-water band");
                Assert(!Regex.IsMatch(dep, @"ratio <= 0\.34f"), "the fraction thresholds are gone");
                // the wet pit keeps a pit's route-planning cost (its look is now the water's)
                string sc = RiverSwitchFlipChecks.Src(Path.Combine("Superdeep", "RM_PitStepCost.cs"));
                RiverSwitchFlipChecks.Has(sc, @"public static class RM_Patch_WetPitPlanningCost", "the wet-pit cost floor exists");
                RiverSwitchFlipChecks.Has(sc, @"if \(temp != null && temp\.pathCost < dry\) \{ baseCostOverride = dry; \}", "a wet pit costs at least its dry hole (P7)");
            });

            Case("Rewire_five_is_dead_and_nothing_multiplies_a_pond", () =>
            {
                // L1: no 5:1 anywhere in FlowWorks code, defs or settings; the pond budget slider deleted (D4); volumePerTile pinned
                string root = Path.GetFullPath(Path.Combine(RiverSwitchFlipChecks.SrcPath("FluidDef.cs"), "..", ".."));   // the mod folder
                string src = Path.Combine(root, "Source");
                var five = new Regex(@"5:1|five-cell|five canal|per five days|twenty-five canal|sourceBudgetMultiplier|sourceBurnDaysPerLevel", RegexOptions.IgnoreCase);
                int files = 0;
                foreach (string dir in new[] { src, Path.Combine(root, "Defs"), Path.Combine(root, "Languages") })
                {
                    if (dir.EndsWith("Languages") && !Directory.Exists(dir)) continue;   // a staged copy (vv harness) may carry no Languages
                    Assert(Directory.Exists(dir), "sanity: no folder " + dir);
                    foreach (string f in Directory.GetFiles(dir, "*.*", dir == src ? SearchOption.TopDirectoryOnly : SearchOption.AllDirectories))
                    {
                        if (!(f.EndsWith(".xml") || f.EndsWith(".cs"))) continue;
                        files++;
                        Assert(!five.IsMatch(File.ReadAllText(f)), "the dead 'five' survives in " + f + ": " + five.Match(File.ReadAllText(f)).Value);
                    }
                }
                foreach (string sub in new[] { "MapControls", "LiquidTypes", "Superdeep", "Machinery", "Drilling" })
                {
                    foreach (string f in Directory.GetFiles(Path.Combine(src, sub), "*.cs", SearchOption.AllDirectories))
                    {
                        files++;
                        Assert(!five.IsMatch(File.ReadAllText(f)), "the dead 'five' survives in " + f);
                    }
                }
                Assert(files > 40, "sanity: the five census read only " + files + " files");
                // can-fail: the census pattern sees a planted 5:1
                Assert(five.IsMatch("// the 5:1 budget") && five.IsMatch("sourceBudgetMultiplier"), "the census can see the dead words");
                string set = RiverSwitchFlipChecks.Src("RimMandrakeFlowWorksMod.cs");
                Assert(!set.Contains("sourceBudgetMultiplier") && !set.Contains("sourceBurnDaysPerLevel"), "the slider and the second burn rate are gone");
                RiverSwitchFlipChecks.Has(set, @"Scribe\.loader\.curXmlParent\?\[""canalBurnDaysPerLevel""\] is System\.Xml\.XmlNode oldCanal", "the old canal rate is read once under its old name");
                foreach (string xml in Directory.GetFiles(Path.Combine(root, "Defs"), "*.xml", SearchOption.AllDirectories))
                {
                    foreach (Match m in Regex.Matches(File.ReadAllText(xml), @"<volumePerTile>([^<]*)</volumePerTile>"))
                        Assert(m.Groups[1].Value.Trim() == "1", "volumePerTile is pinned to 1: " + xml + " says " + m.Groups[1].Value);
                }
                string fd = RiverSwitchFlipChecks.Src("FluidDef.cs");
                RiverSwitchFlipChecks.Has(fd, @"else if \(System\.Math\.Abs\(volumePerTile - 1f\) > 1e-4f\)", "ConfigErrors refuses any other volumePerTile");
                // nothing multiplies a pond: capacity = Σ floor notches
                Assert(Math.Abs(RM_Volume.BodyCapacity(10 * 2 + 10 * 4, 20, 1f) - 60f) < 1e-6, "10 shallow + 10 deep squares hold 60 notches");
                // migration of a pond formed under the deleted slider: keeps its fill fraction, one line per pond
                string st = RiverSwitchFlipChecks.Src("RM_LiquidStock.cs");
                RiverSwitchFlipChecks.Has(st, @"public int MigrateBudgetMultiplier\(RM_MapComponent_Excavation owner\)", "the migration exists");
                RiverSwitchFlipChecks.Has(st, @"body\.stock = RM_Volume\.MigratedStock\(oldStock, oldCap, newCap\); body\.depthStaged = true;", "it keeps the fill fraction");
                Assert(Math.Abs(RM_Volume.MigratedStock(80f, 200f, 100f) - 40f) < 1e-4, "a x2 pond 40% full stays 40% full");
                string ex = RiverSwitchFlipChecks.Src("RM_MapComponent_Excavation.cs");
                RiverSwitchFlipChecks.Has(ex, @"Scribe_Values\.Look\(ref pondBudgetModel, ""RM_pondBudgetModel"", 0\);", "an old save loads as model 0");
                RiverSwitchFlipChecks.Has(ex, @"if \(pondBudgetModel < 1\) \{ int rescaled = stock\.MigrateBudgetMultiplier\(this\);", "migrated once in FinalizeInit");
                RiverSwitchFlipChecks.Has(ex, @"Scribe_Values\.Look\(ref depthViewModel, ""RM_depthViewModel"", 0\);", "the picture marker (spec §9)");
                // lake floors: settable to 125 m, shown in metres
                Assert(RM_BedMath.MaxBedCeiling == 250 && RM_Volume.FormatFloorMetres(RM_BedMath.MaxBedCeiling) == "125 m", "the floor ceiling is 125 m");
                RiverSwitchFlipChecks.Has(set, @"deepBedMaxDepth = list\.Slider\(deepBedMaxDepth, RM_Volume\.LevelsPerSquare, RM_BedMath\.MaxBedCeiling\);", "the slider reaches 125 m");
                RiverSwitchFlipChecks.Has(set, @"Mathf\.Clamp\(Mathf\.RoundToInt\(deepBedMaxDepth\), RM_Volume\.LevelsPerSquare, RM_BedMath\.MaxBedCeiling\)", "and the cap reads it");
            });

            Case("FluidDef_config_errors_check_every_fill_tier_including_very_shallow", () =>
            {
                string fd = RiverSwitchFlipChecks.Src("FluidDef.cs");
                RiverSwitchFlipChecks.Has(fd, @"new\[\] \{ floodTerrain, fillTerrainVeryShallow, fillTerrainHalf, fillTerrainBrim, fillTerrainSuperdeep \}",
                    "ConfigErrors layer-check covers every tier, the very-shallow one too (P14: own-tier liquids stage on the base layer)");
            });

            Case("Review_night_core_dig_scan_copies_and_pump_circle_ignores_hose_fill", () =>
            {
                string wg = RiverSwitchFlipChecks.Src("WorkGiver_DigCanal.cs");
                RiverSwitchFlipChecks.Has(wg, @"List<IntVec3> cells = new List<IntVec3>\(\);", "PotentialWorkCellsGlobal materialises (HasJobOnCell deletes designations mid-scan)");
                Assert(!Regex.IsMatch(wg, @"yield return item\.target\.Cell"), "no lazy walk over the live designation list");
                string pump = RiverSwitchFlipChecks.Src(Path.Combine("LiquidTypes", "Building_LiquidPump.cs"));
                RiverSwitchFlipChecks.Has(pump, @"circle \|= !fillHoses && RM_LiquidSpill\.WholeLevels", "A19 pump-circle warning only when the level reached the pond, not the hoses");
            });

            Case("Review_night_core_taken_letter_subject_and_proof_reset_bound", () =>
            {
                string tl = RiverSwitchFlipChecks.Src(Path.Combine("TakenByLand", "RM_TakenByLand.cs"));
                Assert(!Regex.IsMatch(tl, @"Possessive\(\)\.CapitalizeFirst\(\)\s*\+\s*"" will make"), "the letter's subject is ProSubj ('He will make his way'), not the possessive ('His will')");
                RiverSwitchFlipChecks.Has(tl, @"ProSubj\(\)\.CapitalizeFirst\(\)\s*\+\s*"" will make """, "swept-away letter opens with the subject pronoun");
                string np = RiverSwitchFlipChecks.Src("RM_NorthstarProofs.cs");
                RiverSwitchFlipChecks.Has(np, @"i < RM_ExcavationDepth\.MaxDigCeiling && eng\.ExcavatedDepthAt\(c\) > 0", "ProofResetRect fills in every level up to the dig ceiling, not a stale 8");
            });

            Case("Rewire_thin_sheets_are_pumped_burned_drowned_and_warm", () =>
            {
                int U = RM_Volume.UnitsPerLevel;
                // pump intake: a notch when there is one, else what the cell holds (4.5 cm = 900 dL)
                Assert(RM_PumpMath.ChannelTakeUnits(U, 900) == 900 && RM_PumpMath.ChannelTakeUnits(U, 3 * U) == U
                    && RM_PumpMath.ChannelTakeUnits(U, 0) == 0, "pump take in dL");
                string pump = RiverSwitchFlipChecks.Src(Path.Combine("LiquidTypes", "Building_LiquidPump.cs"));
                RiverSwitchFlipChecks.Has(pump, @"if \(ex\.IsExcavated\(c\) && ex\.WaterDlAt\(c\) > 0\) //", "a thin sheet is drawable");
                RiverSwitchFlipChecks.Has(pump, @"int take = RM_PumpMath\.ChannelTakeUnits\(units, ex\.WaterDlAt\(cell\)\);", "the channel take is in dL");
                RiverSwitchFlipChecks.Has(pump, @"k => ex\.TryTakeDl\(cell, k, out _\) == k", "taken by TryTakeDl");
                // drowning and toxin by the cell's decilitres (a fraction of a notch counts)
                // P7 (V2): a 4.5 cm sheet in a pit is wet (it counts as water) but covers nobody's head; drowning reads metres
                Assert(!RM_RelativeRulesMath.HeadUnder((float)RM_LevelSolve.Metres(900), RM_RelativeRulesMath.HeightMetres(2), false)
                    && !RM_RelativeRulesMath.HeadUnder((float)RM_LevelSolve.Metres(900), RM_RelativeRulesMath.HeightMetres(2), true), "a sheet drowns nobody");
                string fe = RiverSwitchFlipChecks.Src("RM_PitFillEffects.cs");
                RiverSwitchFlipChecks.Has(fe, @"float fill = ex\.WaterDlAt\(c\) / \(float\)RM_LevelSolve\.U;", "wet reads decilitres");
                RiverSwitchFlipChecks.Has(fe, @"RM_Drowning\.PerCheck\(map, ex, p, c, ex\.WaterMetresAt\(c\)\)", "drowning reads the water's metres");
                // heat: fractional notches; natural squares read their real water
                Assert(RM_LiquidHeatMath.CellEnergy(1, 0.09f, 1f) > 0f && Math.Abs(RM_LiquidHeatMath.CellEnergy(1, 0.5f, 1f) * 2f - RM_LiquidHeatMath.CellEnergy(1, 1, 1f)) < 1e-4,
                    "a sheet warms a little, in proportion");
                string ht = RiverSwitchFlipChecks.Src("RM_LiquidHeat.cs");
                RiverSwitchFlipChecks.Has(ht, @"float f = ex\.WaterDlAt\(c\) / \(float\)RM_LevelSolve\.U;", "a dug cell warms by its dL");
                RiverSwitchFlipChecks.Has(ht, @"RM_LiquidHeatMath\.CellEnergy\(k, NaturalLevels\(ex, nc\), strength\)", "a natural square by its real water, not 2");
                // burn: the burnable test sees a sheet; the pulse burns dL
                string lf = RiverSwitchFlipChecks.Src("RM_LiquidFire.cs");
                RiverSwitchFlipChecks.Has(lf, @"if \(ex\.WaterDlAt\(c\) > 0\)", "a thin sheet is burnable");
                RiverSwitchFlipChecks.Has(lf, @"long took = dl > 0 \? ex\.BurnOffDl\(c, dl\) : 0;", "burned in dL");
            });

            Case("Readout_two_numbers_and_the_limitless_mark", () =>
            {
                int U = RM_Volume.UnitsPerLevel;
                // V8's own example: Hole 7 m (ledge 4 m) · Water 2.37 m (4,740 L)
                Assert(RM_Volume.Readout(14, 8, 47400) == "Hole 7 m (ledge 4 m) \u00b7 Water 2.37 m (4,740 L)", "V8: " + RM_Volume.Readout(14, 8, 47400));
                Assert(RM_Volume.Readout(4, 0, 0) == "Hole 2 m \u00b7 Water 0.00 m (0 L)", "a dry pit: " + RM_Volume.Readout(4, 0, 0));
                Assert(RM_Volume.Readout(1, 0, 900) == "Hole 0.5 m \u00b7 Water 0.05 m (90 L)", "a 4.5 cm sheet reads 0.05 m: " + RM_Volume.Readout(1, 0, 900));
                Assert(RM_Volume.Readout(7, 7, U) == "Hole 3.5 m \u00b7 Water 0.50 m (1,000 L)" && RM_Volume.Readout(7, 9, U).IndexOf("ledge") < 0,
                    "no ledge unless it is between the hole and the ground");
                Assert(RM_Volume.FormatFloorMetres(3) == "1.5 m" && RM_Volume.FormatWaterMetres(4737) == "0.24 m", "floors to 0.5 m, water two decimals");
                // L1: water = body surface − cell floor; two squares of one body read ONE surface and differ only by floor
                // H[L] = squares whose floor reaches layer L: a 3x3 pond 2 m deep is {0, 9, 9, 9, 9}; S5-A's surface (1.737 m of water)
                double sh = RM_LevelSolve.PondSurfaceHeight(new[] { 0, 9, 9, 9, 9 }, 9L * 4 * U - 9L * 5263);
                double w4 = RM_LevelSolve.PondSquareWater(4, sh), w20 = RM_LevelSolve.PondSquareWater(20, sh);
                Assert(Math.Abs((w4 - 4 * U) - (w20 - 20 * U)) < 1e-6, "one surface: water − floor is the same in both squares");
                Assert(Math.Abs((w20 - w4) - 16.0 * U) < 1e-6, "the readouts differ only by floor depth");
                Assert(RM_Volume.Readout(4, 0, w4) == "Hole 2 m \u00b7 Water 1.74 m (3,474 L)", "S5-A pond square: " + RM_Volume.Readout(4, 0, w4));
                // R13: a limitless square carries the mark, a limited one never does
                Assert(RM_Volume.LimitlessReadout(4).StartsWith(RM_Volume.LimitlessMark) && RM_Volume.LimitlessReadout(4).IndexOf(" L)") < 0,
                    "limitless: the mark, never a litre count: " + RM_Volume.LimitlessReadout(4));
                foreach (string line in new[] { RM_Volume.Readout(4, 0, w4), RM_Volume.Readout(4, 0, 0), RM_Volume.Readout(14, 8, 47400) })
                    Assert(line.IndexOf("never runs dry", StringComparison.OrdinalIgnoreCase) < 0 && line.IndexOf("limit", StringComparison.OrdinalIgnoreCase) < 0,
                        "a limited readout carries no limited/limitless indicator: " + line);
                string ex = RiverSwitchFlipChecks.Src("RM_MapComponent_Excavation.cs");
                RiverSwitchFlipChecks.Has(ex, @"else if \(IsLimitlessWaterAt\(c, body\)\) \{ return RM_Volume\.LimitlessReadout\(hole\); \}", "the readout marks limitless bodies");
                RiverSwitchFlipChecks.Has(ex, @"return body\.limitless;", "by the body's sticky classification");
                RiverSwitchFlipChecks.Has(ex, @"water = WaterDl\(i\);", "a dug square reads its own decilitres");
                RiverSwitchFlipChecks.Has(ex, @"return stock\.SquareWaterDl\(map, body, c, floor, this\);", "a pond square reads the solver's surface");
                string st = RiverSwitchFlipChecks.Src("RM_LiquidStock.cs");
                RiverSwitchFlipChecks.Has(st, @"return RM_LevelSolve\.PondSquareWater\(floorNotches, SurfaceHeightOf\(map, body, owner\)\);", "surface − floor");
                RiverSwitchFlipChecks.Has(st, @"body\.surfaceHeight = RM_LevelSolve\.PondSurfaceHeight\(DepthHistogram\(map, body, owner\), LevelStockDl\(body, owner\)\);", "the exact kernel's surface");
                string mo = RiverSwitchFlipChecks.Src("RM_MouseoverDepth.cs");
                RiverSwitchFlipChecks.Has(mo, @"string line = ex\.DepthReadoutAt\(c\);", "the mouseover shows the readout");
                string np = RiverSwitchFlipChecks.Src("RM_NorthstarProofs.cs");
                RiverSwitchFlipChecks.Has(np, @"return ""OK "" \+ \(eng\.DepthReadoutAt\(c\) \?\? ""-""\);", "the readout is bridge-readable");
            });
        }
    }
}
