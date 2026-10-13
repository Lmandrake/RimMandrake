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
                Assert(RM_Volume.LevelsPerSquare == 4 && RM_Volume.UnitsPerLevel == 5 && RM_Volume.UnitsPerSquare == 20,
                    "one deep notch = 4 levels = 20 units (owner 2026-10-12)");
                Assert(RM_PumpMath.TankUnitsPerLevel == RM_Volume.UnitsPerLevel, "the pump's level is the yardstick's level");
                // deep pond square, in levels -> units
                int deepBed = RM_Volume.BedLevels(true, 300);
                float pondSquareUnits = RM_Volume.BodyCapacity(deepBed, 1, 1f, 1f) * RM_Volume.UnitsPerLevel;
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
                Assert(RM_Volume.TankCapacity(4, false, 1f) == 80 && RM_Volume.TankCapacity(4, true, 1f) == 160, "2x2 = 80, tall 160 (§8.2)");
                Assert(RM_Volume.TankCapacity(4, 4f, 1f) == 320 && RM_Volume.TankCapacity(4, 2f, 1f) == RM_Volume.TankCapacity(4, true, 1f), "2x2 extra-tall 320, factor 2 = tall (TANK_TALL)");
                Assert(RM_Volume.TankCapacity(1, false, 0.01f) == RM_Volume.UnitsPerLevel, "never below one level at the lowest slider");
            });

            Case("Volume_bed_depth_follows_the_water", () =>
            {
                // vanilla Core Terrain_Water.xml: WaterDeepBase Impassable/300, WaterChestDeepBase 42, WaterShallowBase 30
                Assert(RM_Volume.BedLevels(true, 300) == 4, "deep water (WaterDeep, WaterOceanDeep) = 4");
                Assert(RM_Volume.BedLevels(false, 42) == 4, "chest-deep moving water = 4");
                Assert(RM_Volume.BedLevels(false, 30) == 2, "shallow water, marsh = 2 (ruling 3/7)");
                // a mixed pond: 10 shallow + 10 deep holds 60 levels (trip 12)
                float mixed = RM_Volume.BodyCapacity(10 * 2 + 10 * 4, 20, 1f, 1f);
                Assert(Math.Abs(mixed - 60f) < 1e-6, "mixed pond holds 60, got " + mixed);
                Assert(RM_Volume.BodyCapacity(40, 20, 1f, 0f) > 0f, "a zero budget slider still gives a positive capacity");
                Assert(RM_Volume.BodyCapacity(0, 0, 1f, 1f) == 0f, "no cells, no capacity");
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

            Case("Volume_production_wiring", () =>
            {
                string st = RiverSwitchFlipChecks.Src("RM_LiquidStock.cs");
                RiverSwitchFlipChecks.Has(st, @"body\.capacity = CapacityOf\(body, owner\);", "a new pond is sized by its beds");
                RiverSwitchFlipChecks.Has(st, @"sum \+= owner\.BedLevelsAt\(body\.cells\[i\]\);", "capacity sums each square's bed");
                RiverSwitchFlipChecks.Has(st, @"body\.stock = RM_Volume\.MigratedStock\(oldStock, oldCap, newCap\);", "migration keeps the fraction");
                Assert(!Regex.IsMatch(st, @"canalCellsPerSourceCell"), "the 5:1 budget is gone from the stock model");
                string ex = RiverSwitchFlipChecks.Src("RM_MapComponent_Excavation.cs");
                RiverSwitchFlipChecks.Has(ex, @"Scribe_Values\.Look\(ref volumeModel, ""RM_volumeModel"", 1\);", "an old save loads as model 1");
                RiverSwitchFlipChecks.Has(ex, @"if \(volumeModel < RM_Volume\.CurrentModel\) \{ int rescaled = stock\.MigrateVolumeModel\(this\);", "migrated once in FinalizeInit");
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
