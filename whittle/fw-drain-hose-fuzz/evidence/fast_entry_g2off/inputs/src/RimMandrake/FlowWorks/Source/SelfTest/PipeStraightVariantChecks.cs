// SCRAPPER_PIPE_REDRAW_ASKED_TWICE_NOW: the straight-run variant pick (Machinery/PipeStraightVariants.cs) is a pure, stable function
// of the cell with the intended mix, its UVs land on the shown cell of the right sheet tile, and the production draw prefix
// (Machinery/RM_PipeStraightVariantsDraw.cs) is read so the gates proven here are the gates the game runs.
using System;
using System.IO;
using RimMandrake.FlowWorks.Machinery;

namespace RimMandrake.FlowWorks.SelfTest
{
    internal static class PipeStraightVariantChecks
    {
        private static void Assert(bool ok, string msg)
        {
            if (!ok) throw new Exception(msg);
        }

        private static bool Near(float a, float b) => Math.Abs(a - b) < 1e-6f;

        public static void Run(Action<string, Action> Case)
        {
            Case("PipeStraightVariants_pick_is_pinned_and_stable", () =>
            {
                // golden values shared with the offline mock (scratch render_layout.py): the same cell draws the same tile on
                // every machine, load and redraw, so a pick can never shuffle under a save
                Assert(PipeStraightVariants.CellHash(1, 0) == 0x3aee2dbcu && PipeStraightVariants.CellHash(0, 1) == 0xe7d58b85u
                       && PipeStraightVariants.CellHash(-5, 9) == 0xe7a7c01bu, "hash pinned to its golden values");
                Assert(PipeStraightVariants.Pick(0, 0) == 0 && PipeStraightVariants.Pick(1, 0) == 1 && PipeStraightVariants.Pick(0, 1) == 2
                       && PipeStraightVariants.Pick(37, 112) == 0 && PipeStraightVariants.Pick(-5, 9) == 1, "pick pinned");
                for (int x = -40; x < 40; x++)
                    for (int z = -40; z < 40; z++)
                    {
                        int k = PipeStraightVariants.Pick(x, z);
                        Assert(k >= 0 && k <= PipeStraightVariants.Count, $"pick {k} at ({x},{z}) is a sheet column or the atlas");
                        Assert(k == PipeStraightVariants.Pick(x, z), "pure: the same cell picks the same tile twice");
                    }
            });
            Case("PipeStraightVariants_mix_breaks_the_repeat", () =>
            {
                // over a 250x250 map: the atlas straight ~3/8, plain stretches ~3/8, hardware ~2/8; and no long east-west run is
                // one tile (the owner's complaint was the same spot every cell)
                int[] n = new int[PipeStraightVariants.Count + 1];
                int longest = 0;
                for (int z = 0; z < 250; z++)
                {
                    int run = 0, prev = -1;
                    for (int x = 0; x < 250; x++)
                    {
                        int k = PipeStraightVariants.Pick(x, z);
                        n[k]++;
                        run = k == prev ? run + 1 : 1; prev = k;
                        longest = Math.Max(longest, run);
                    }
                }
                double all = 250.0 * 250.0;
                Assert(Math.Abs(n[0] / all - 0.375) < 0.02, $"atlas straight share {n[0] / all:F3} ~ 0.375");
                Assert(Math.Abs((n[1] + n[2]) / all - 0.375) < 0.02, $"plain share {(n[1] + n[2]) / all:F3} ~ 0.375");
                Assert(Math.Abs((n[3] + n[4]) / all - 0.25) < 0.02, $"hardware share {(n[3] + n[4]) / all:F3} ~ 0.25");
                Assert(longest <= 12, $"longest single-tile run {longest} cells");
            });
            Case("PipeStraightVariants_uvs_and_sheet_path", () =>
            {
                float[] uv = new float[8];
                PipeStraightVariants.Uvs(1, true, uv);      // column 0, top row (east-west): shown 3/4 inside 1/8 padding
                Assert(Near(uv[0], 0.03125f) && Near(uv[1], 0.5625f) && Near(uv[2], 0.03125f) && Near(uv[3], 0.9375f)
                       && Near(uv[4], 0.21875f) && Near(uv[5], 0.9375f) && Near(uv[6], 0.21875f) && Near(uv[7], 0.5625f),
                       "variant 1 east-west: bottom-left, top-left, top-right, bottom-right of tile (0, top)");
                PipeStraightVariants.Uvs(4, false, uv);     // column 3, bottom row (north-south)
                Assert(Near(uv[0], 0.78125f) && Near(uv[1], 0.0625f) && Near(uv[3], 0.4375f) && Near(uv[4], 0.96875f),
                       "variant 4 north-south: tile (3, bottom)");
                Assert(PipeStraightVariants.SheetPathFor("RimMandrake/FlowWorks/Pipe/Scrapper/UniversalPipe_Atlas")
                       == "RimMandrake/FlowWorks/Pipe/Scrapper/UniversalPipe_Straights", "sheet beside the atlas");
                Assert(PipeStraightVariants.SheetPathFor("Things/Building/Linked/Wall_Atlas") == null && PipeStraightVariants.SheetPathFor(null) == null,
                       "not a pipe atlas: no sheet");
                Assert(PipeStraightVariants.IsStraight(5) && PipeStraightVariants.IsStraight(10) && !PipeStraightVariants.IsStraight(15)
                       && !PipeStraightVariants.IsStraight(1) && !PipeStraightVariants.IsStraight(3), "straight = N+S or E+W only");
            });
            Case("PipeStraightVariants_draw_prefix_gates", () =>
            {
                string d = RiverSwitchFlipChecks.Src(Path.Combine("Machinery", "RM_PipeStraightVariantsDraw.cs"));
                RiverSwitchFlipChecks.Has(d, @"\[HarmonyPatch\(typeof\(Graphic_Linked\), nameof\(Graphic_Linked\.Print\)\)\]", "prefixes Graphic_Linked.Print");
                RiverSwitchFlipChecks.Has(d, @"if \(!RM_MachinerySettings\.pipeStraightVariants \|\| thing == null \|\| extraRotation != 0f \|\| !thing\.Spawned\s+\|\| !RM_LiquidNet\.IsPipe\(thing\)\) return true;",
                    "switch off, a rotated print or anything but a spawned universal pipe prints as vanilla");
                RiverSwitchFlipChecks.Has(d, @"if \(sheetPath == null\) return true;", "a look without a straights sheet prints as vanilla");
                RiverSwitchFlipChecks.Has(d, @"if \(!PipeStraightVariants\.IsStraight\(mask\)\) return true;", "only straight cells vary");
                RiverSwitchFlipChecks.Has(d, @"if \(k == 0\) return true;", "pick 0 prints the atlas straight as vanilla");
                RiverSwitchFlipChecks.Has(d, @"Printer_Plane\.PrintPlane\(layer, thing\.TrueCenter\(\), Vector2\.one, m, 0f, false, uvs\);",
                    "the same 1x1 plane at the same centre as vanilla");
                string set = RiverSwitchFlipChecks.Src(Path.Combine("Machinery", "RM_MachinerySettings.cs"));
                RiverSwitchFlipChecks.Has(set, @"public static bool pipeStraightVariants = true;", "default on");
                RiverSwitchFlipChecks.Has(set, @"Scribe_Values\.Look\(ref pipeStraightVariants, ""pipeStraightVariants"", true\);", "saved");
                RiverSwitchFlipChecks.Has(set, @"list\.CheckboxLabeled\(""Varied straight pipe runs[^""]*"", ref pipeStraightVariants,", "a checkbox");
            });
        }
    }
}
