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
                RiverSwitchFlipChecks.Has(ex, @"TerrainDef want = fluid\.FillTerrainForLook\(RM_ExcavationDepth\.FillTier\(WaterDl\(i\)\)\);",
                    "ApplyFillTerrain: one rule, by the cell's decilitres, for canals AND pits");
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
                RiverSwitchFlipChecks.Has(sc, @"if \(temp != null && temp\.pathCost < pit\) \{ baseCostOverride = pit; \}", "a wet pit costs at least a pit");
            });
        }
    }
}
