// POND_VOLUME_UNIFY_DEEP_NOTCH_YARDSTICK (design/RimMandrake/natural_bodies_as_canals_design_2026-10-11.md §8, §9.6): one
// tank square = one deep canal square = one deep pond square. The arithmetic is the PRODUCTION RM_Volume; the wiring (pond
// capacity, tank capacity, migration, the deleted 5:1 field) is read from production source and defs.
using System;
using System.IO;
using System.Text.RegularExpressions;

namespace RimMandrake.FlowWorks.SelfTest
{
    internal static class VolumeChecks
    {
        private static void Assert(bool ok, string msg)
        {
            if (!ok) throw new Exception(msg);
        }

        public static void Run(Action<string, Action> Case)
        {
            Case("Volume_one_square_is_one_square", () =>
            {
                Assert(RM_Volume.LevelsPerSquare == 4 && RM_Volume.UnitsPerLevel == 10000 && RM_Volume.UnitsPerSquare == 40000,
                    "one deep notch = 4 levels = 4,000 L = 40,000 decilitre units (owner 2026-10-12, 2026-10-16)");
                Assert(RM_PumpMath.TankUnitsPerLevel == RM_Volume.UnitsPerLevel, "the pump's level is the yardstick's level");
                // deep pond square, in levels -> units
                int deepBed = RM_Volume.BedLevels(true, 300);
                float pondSquareUnits = RM_Volume.BodyCapacity(deepBed, 1, 1f) * RM_Volume.UnitsPerLevel;
                Assert(Math.Abs(pondSquareUnits - RM_Volume.UnitsPerSquare) < 1e-6, "deep pond square " + pondSquareUnits + " != " + RM_Volume.UnitsPerSquare);
                // deep canal square: MaxDepth levels
                Assert(RM_ExcavationDepthLevels() * RM_Volume.UnitsPerLevel == RM_Volume.UnitsPerSquare, "deep canal square = one tank square");
                // tank square: capacity / footprint area at multiplier 1, every footprint the owner named
                foreach ((int x, int z) in new[] { (1, 1), (1, 2), (2, 2), (3, 3) })
                {
                    int a = x * z;
                    Assert(RM_Volume.TankCapacity(a, false, 1f) == a * RM_Volume.UnitsPerSquare, x + "x" + z + " tank = " + a + " squares");
                    Assert(RM_Volume.TankCapacity(a, true, 1f) == 2 * a * RM_Volume.UnitsPerSquare, x + "x" + z + " tall tank = twice");
                }
                Assert(RM_Volume.TankCapacity(4, false, 1f) == 160000 && RM_Volume.TankCapacity(4, true, 1f) == 320000, "2x2 = 16 kL, tall 32 kL (§8.2)");
                Assert(RM_Volume.TankCapacity(4, 4f, 1f) == 640000 && RM_Volume.TankCapacity(4, 2f, 1f) == RM_Volume.TankCapacity(4, true, 1f), "2x2 extra-tall 64 kL, factor 2 = tall (TANK_TALL)");
                Assert(RM_Volume.TankCapacity(1, false, 0.01f) == RM_Volume.UnitsPerLevel, "never below one level at the lowest slider");
            });

            Case("Volume_one_ruler_scheme_A", () =>
            {
                // LIQUID_DEPTH_REWIRE_FIVE_IS_DEAD (unified depth spec §3): a square is 2 m², a notch 0.5 m, so 1,000 L a notch,
                // DERIVED from the two (never a third literal); the yardstick is 2 m = 4 notches = 4,000 L
                Assert(RM_Volume.SquareAreaM2 == 2 && RM_Volume.CentimetresPerNotch == 50, "a square is 2 m², a notch 50 cm");
                Assert(RM_Volume.LitresPerNotch == RM_Volume.SquareAreaM2 * RM_Volume.CentimetresPerNotch * 10 && RM_Volume.LitresPerNotch == 1000,
                    "litres per notch derived: 2 m² x 0.5 m = 1 m³ = 1,000 L");
                Assert(RM_Volume.LitresPerLevel == RM_Volume.LitresPerNotch && RM_Volume.MetresPerLevel == RM_Volume.MetresPerNotch,
                    "the code's 'level' is the notch");
                Assert(RM_Volume.LevelsPerSquare * RM_Volume.MetresPerNotch == 2f && RM_Volume.LevelsPerSquare * RM_Volume.LitresPerNotch == 4000,
                    "the yardstick: 2 m, 4,000 L");
                Assert(RM_Volume.AbyssBedLevels == 8 && RM_Volume.LakebedFor(3) == "RM_Lakebed_Shallow" && RM_Volume.LakebedFor(4) == "RM_Lakebed_Deep"
                    && RM_Volume.LakebedFor(7) == "RM_Lakebed_Deep" && RM_Volume.LakebedFor(8) == "RM_Lakebed_Abyss", "lakebeds: 2 m deep, 4 m abyss");
                string vol = RiverSwitchFlipChecks.Src("RM_Volume.cs");
                Assert(Regex.IsMatch(vol, @"public const int LitresPerNotch = SquareAreaM2 \* CentimetresPerNotch \* LitresPerM2Cm;"),
                    "LitresPerNotch is the product, not a literal");
            });

            Case("Volume_bed_depth_follows_the_water", () =>
            {
                // vanilla Core Terrain_Water.xml: WaterDeepBase Impassable/300, WaterChestDeepBase 42, WaterShallowBase 30
                Assert(RM_Volume.BedLevels(true, 300) == 4, "deep water (WaterDeep, WaterOceanDeep) = 4");
                Assert(RM_Volume.BedLevels(false, 42) == 4, "chest-deep moving water = 4");
                Assert(RM_Volume.BedLevels(false, 30) == 2, "shallow water, marsh = 2 (ruling 3/7)");
                // a mixed pond: 10 shallow + 10 deep holds 60 levels (trip 12)
                float mixed = RM_Volume.BodyCapacity(10 * 2 + 10 * 4, 20, 1f);
                Assert(Math.Abs(mixed - 60f) < 1e-6, "mixed pond holds 60, got " + mixed);
                Assert(RM_Volume.BodyCapacity(1, 20, 1f) >= 20 * RM_StockMath.MinPerCellVolume, "never below the per-cell floor");
                Assert(RM_Volume.BodyCapacity(0, 0, 1f) == 0f, "no cells, no capacity");
            });

            Case("Volume_migration_keeps_the_fill_fraction_and_every_tank_unit", () =>
            {
                // §8.3 / trip 13: an old 25-cell deep pond (125) 40% full -> new capacity 100, still 40% full
                float s = RM_Volume.MigratedStock(50f, 125f, 100f);
                Assert(Math.Abs(s - 40f) < 1e-4, "pond keeps its fraction: got " + s);
                Assert(RM_Volume.MigratedStock(200f, 125f, 100f) == 100f, "an over-capacity stock clamps to full");
                Assert(RM_Volume.MigratedStock(5f, 0f, 100f) == 100f, "an unsized body loads full");
                // an old 300-unit tank holding 250 is overfull at 80: kept, refuses input
                Assert(RM_Volume.Overfull(250, 80) && !RM_Volume.Overfull(80, 80), "250 in an 80 tank is overfull; 80 is not");
            });

            Case("Volume_litres_model_3", () =>
            {
                // LIQUID_LITRES_MIGRATE_DRUMS_ARE_DRUMS (owner 2026-10-16): a level is 1,000 L, half a metre; the unit is a decilitre
                Assert(RM_Volume.LitresPerLevel == 1000 && Math.Abs(RM_Volume.MetresPerLevel - 0.5f) < 1e-6 && RM_Volume.CurrentModel == 3,
                    "a level is 1,000 L and 0.5 m; the save model is 3");
                Assert(RM_Volume.Units(1.5f) == 15 && RM_Volume.Units(15f) == 150 && RM_Volume.Units(208f) == 2080, "bottle 15, bucket 150, barrel 2,080 units");
                Assert(Math.Abs(RM_Volume.Litres(2080) - 208f) < 1e-4, "units back to litres");
                // the old unit was a fifth of a level: 200 L, so one old unit is 2,000 new ones, and a level converts to a level
                Assert(RM_Volume.LegacyUnitScale == 2000 && RM_Volume.LegacyUnitLitres == 200, "one model-2 unit = 200 L = 2,000 units");
                Assert(RM_Volume.FromLegacyUnits(RM_Volume.LegacyUnitsPerLevel) == RM_Volume.UnitsPerLevel, "a saved level (5 old units) loads as a level");
                Assert(RM_Volume.FromLegacyUnits(80) == RM_Volume.TankCapacity(4, false, 1f), "a full old 2x2 tank (80) loads full (16 kL)");
                Assert(RM_Volume.FromLegacyUnits(int.MaxValue / 2) == int.MaxValue, "the conversion clamps, never wraps");
                // mutation probe: a converted stock that skipped the scale would read 2,000x too small
                Assert(RM_Volume.FromLegacyUnits(25) != 25, "mutation probe: the migration must change the number");
                // what players read
                Assert(RM_Volume.FormatLitres(1.5) == "1.5 L" && RM_Volume.FormatLitres(15) == "15 L" && RM_Volume.FormatLitres(208) == "208 L",
                    "container sizes read 1.5 L / 15 L / 208 L: " + RM_Volume.FormatLitres(1.5) + " " + RM_Volume.FormatLitres(208));
                Assert(RM_Volume.FormatUnits(RM_Volume.UnitsPerSquare) == "4 kL" && RM_Volume.FormatUnits(160000) == "16 kL" && RM_Volume.FormatLitres(12500) == "12.5 kL",
                    "squares and tanks read in kL: " + RM_Volume.FormatUnits(RM_Volume.UnitsPerSquare));
                Assert(RM_Volume.Readout(4, 0, 40000) == "Hole 2 m \u00b7 Water 2.00 m (4,000 L)", "mouseover: " + RM_Volume.Readout(4, 0, 40000));
                // a bottle from a deep pond square barely dents it (C2-F2 debit in fill-units: 15 units of a 40,000-unit square)
                float bottleStock = RimMandrake.FlowWorks.LiquidTypes.RM_ContainerMaterialMath.BodyStockFor(15, 1f, RM_Volume.UnitsPerLevel);
                Assert(Math.Abs(bottleStock - 0.0015f) < 1e-7, "a bottle costs 0.0015 of a level, got " + bottleStock);
                float barrelStock = RimMandrake.FlowWorks.LiquidTypes.RM_ContainerMaterialMath.BodyStockFor(2080, 1f, RM_Volume.UnitsPerLevel);
                Assert(barrelStock < RM_Volume.LevelsPerSquare / 10f, "a barrel takes about a twentieth of a deep square, got " + barrelStock + " levels");
            });

            Case("Volume_litres_production_wiring", () =>
            {
                // every holder of tank units converts a model-2 save once, on load, behind its own marker
                foreach (string f in new[] { Path.Combine("LiquidTypes", "Building_LiquidTank.cs"), Path.Combine("Hose", "CompHoseReel.cs"),
                                             Path.Combine("Machinery", "CompLiquidConverter.cs"), Path.Combine("Machinery", "CompLiquidPipeAdapter.cs") })
                {
                    string src = RiverSwitchFlipChecks.Src(f);
                    RiverSwitchFlipChecks.Has(src, @"Scribe_Values\.Look\(ref volumeModel, ""rmVolumeModel"", RM_Volume\.LegacyModel\);", f + ": an unmarked save loads as model 2");
                    RiverSwitchFlipChecks.Has(src, @"if \(Scribe\.mode == LoadSaveMode\.LoadingVars && volumeModel < RM_Volume\.CurrentModel\)", f + ": converted once on load");
                    RiverSwitchFlipChecks.Has(src, @"RM_Volume\.FromLegacyUnits\(", f + ": by the one conversion");
                }
                string hs = RiverSwitchFlipChecks.Src(Path.Combine("Hose", "RM_HoseSettings.cs"));
                RiverSwitchFlipChecks.Has(hs, @"tankLitresPerCycle = tu \* RM_Volume\.LegacyUnitLitres;", "old tank-to-tank setting read once into litres");
                RiverSwitchFlipChecks.Has(hs, @"dumpLitresPerCycle = du \* RM_Volume\.LegacyUnitLitres;", "old dump setting read once into litres");
                string ms = RiverSwitchFlipChecks.Src(Path.Combine("Machinery", "RM_MachinerySettings.cs"));
                RiverSwitchFlipChecks.Has(ms, @"litresPerFilth = oldUnits \* RM_Volume\.LegacyUnitLitres;", "old filth setting read once into litres");
                string mo = RiverSwitchFlipChecks.Src("RM_MouseoverDepth.cs");
                RiverSwitchFlipChecks.Has(mo, @"\[HarmonyPatch\(typeof\(MouseoverReadout\), nameof\(MouseoverReadout\.MouseoverReadoutOnGUI\)\)\]", "the cell readout is patched");
                RiverSwitchFlipChecks.Has(mo, @"cachedTerrain\(__instance\) = null;", "a dry square hands the line back to vanilla");
                string tk = RiverSwitchFlipChecks.Src(Path.Combine("LiquidTypes", "Building_LiquidTank.cs"));
                RiverSwitchFlipChecks.Has(tk, @"RM_Volume\.FormatUnits\(storedUnits\), RM_Volume\.FormatUnits\(Capacity\)", "the tank says litres");
            });

            Case("Volume_production_wiring", () =>
            {
                string st = RiverSwitchFlipChecks.Src("RM_LiquidStock.cs");
                RiverSwitchFlipChecks.Has(st, @"body\.capacity = CapacityOf\(body, owner\);", "a new pond is sized by its beds");
                RiverSwitchFlipChecks.Has(st, @"sum \+= owner\.BedLevelsAt\(body\.cells\[i\]\);", "capacity sums each square's bed");
                RiverSwitchFlipChecks.Has(st, @"body\.stock = RM_Volume\.MigratedStock\(oldStock, oldCap, newCap\);", "migration keeps the fraction");
                Assert(!Regex.IsMatch(st, @"canalCellsPerSourceCell"), "the 5:1 budget is gone from the stock model");
                string ex = RiverSwitchFlipChecks.Src("RM_MapComponent_Excavation.cs");
                RiverSwitchFlipChecks.Has(ex, @"Scribe_Values\.Look\(ref volumeModel, ""RM_volumeModel"", 1\);", "an old save loads as model 1");
                RiverSwitchFlipChecks.Has(ex, @"if \(volumeModel < RM_Volume\.CurrentModel\) \{ int rescaled = volumeModel < 2 \? stock\.MigrateVolumeModel\(this\) : 0;", "ponds migrated once in FinalizeInit, model 1 only");
                RiverSwitchFlipChecks.Has(ex, @"return RM_Volume\.BedLevels\(t\.passability == Traversability\.Impassable, t\.pathCost\);", "bed depth from the water terrain");
                string tk = RiverSwitchFlipChecks.Src(Path.Combine("LiquidTypes", "Building_LiquidTank.cs"));
                RiverSwitchFlipChecks.Has(tk, @"public int Capacity => RM_Volume\.TankCapacity\(def\.size\.x \* def\.size\.z,", "a tank is sized by its footprint");
                RiverSwitchFlipChecks.Has(tk, @"return storedUnits \+ units <= Capacity;", "an overfull tank refuses input");
                Assert(!Regex.IsMatch(tk, @"baseCapacityUnits"), "the 300/600 base is gone");
                string fd = RiverSwitchFlipChecks.Src("FluidDef.cs");
                Assert(!Regex.IsMatch(fd, @"public float canalCellsPerSourceCell"), "FluidDef has no 5:1 field");
                foreach (string xml in Directory.GetFiles(Path.Combine(RiverSwitchFlipChecks.SrcPath("FluidDef.cs"), "..", "..", "Defs"), "*.xml", SearchOption.AllDirectories))
                {
                    string t = File.ReadAllText(xml);
                    Assert(!t.Contains("<canalCellsPerSourceCell>"), "a def still sets the deleted field (config error): " + xml);
                    Assert(!t.Contains("<baseCapacityUnits>"), "a def still sets the deleted tank field (config error): " + xml);
                }
            });
        }

        /// <summary>The deepest dug canal square, read from production (RM_ExcavationDepth is Verse-bound, so its
        /// constant is parsed from source rather than linked).</summary>
        private static int RM_ExcavationDepthLevels()
        {
            string src = RiverSwitchFlipChecks.Src("RM_ExcavationDepth.cs");
            Match m = Regex.Match(src, @"public const byte Superdeep = (\d+);");
            Assert(m.Success, "RM_ExcavationDepth.Superdeep found");
            return int.Parse(m.Groups[1].Value);
        }
    }
}
