// SCRUB_WIND_BUILD_LEAN_ON_PURPOSE: the facing rule (RM_LeanKernel.WindLeansWest / FaceFlip / VisibleWest / WestByVariant),
// over every whole-degree heading and every mix of variant art. Invariant: on one map every listed mesh shows ONE lean
// (scrub_never_lean_mixed), and that lean is the wind's screen side (scrub_lean_visible); unlisted variants lean east.
using System;
using System.Collections.Generic;

namespace RimMandrake.LeaningScrub.SelfTest
{
    internal static class LeaningScrubPlantLeanCheck
    {
        private static void Check(bool ok, string msg) { if (!ok) throw new Exception(msg); }

        public static bool Run()
        {
            try
            {
                string[] paths = { "Things/Plant/RM_Fuzz/RM_Fuzz_a", "Things/Plant/RM_Fuzz/RM_Fuzz_c", "Things/Plant/RM_Fuzz/RM_Fuzz_e" };
                var west = new HashSet<string> { "RM_Fuzz_c", "RM_Fuzz_e", "RM_Other_x" };
                bool[] flags = RM_LeanKernel.WestByVariant(paths, west);
                Check(flags != null && !flags[0] && flags[1] && flags[2], "WestByVariant misread the listed variants");
                Check(RM_LeanKernel.WestByVariant(paths, new HashSet<string> { "RM_Grellbush_a" }) == null,
                    "a graphic with no listed variant must skip the peek (null)");
                Check(RM_LeanKernel.WestByVariant(paths, new HashSet<string>()) == null, "an empty west list must give null");
                Check(RM_LeanKernel.WestByVariant(new[] { "RM_Fuzz_c" }, west)[0], "a bare path (no folder) must still match");
                Check(RM_LeanKernel.WestByVariant(new[] { "Things/Plant/RM_Fuzz/rm_fuzz_c" }, west) == null,
                    "matching must be case-sensitive like ContentFinder");
                Check(RM_LeanKernel.TextureName("A/B/C") == "C" && RM_LeanKernel.TextureName(null) == "", "TextureName");

                int cases = 0;
                for (int deg = 0; deg < 360; deg++)
                {
                    RM_LeanKernel.Direction(deg, out float dx, out float dz);
                    bool windWest = RM_LeanKernel.WindLeansWest(dx);
                    if (Math.Abs(dx) > 1e-3f)
                    {
                        Check(windWest == (dx < 0f), $"heading {deg}: wind side {windWest} but downwind x {dx}");
                    }
                    bool? seen = null;
                    foreach (bool artWest in new[] { false, true })
                    {
                        bool flip = RM_LeanKernel.FaceFlip(windWest, artWest);
                        bool visible = RM_LeanKernel.VisibleWest(artWest, flip);
                        Check(visible == windWest, $"heading {deg}: art west={artWest} shows west={visible}, wind west={windWest}");
                        Check(seen == null || seen == visible, $"heading {deg}: mixed lean on one map");
                        seen = visible;
                        cases++;
                    }
                }
                // Due north and due south have no screen lean: both resolve EAST, the same way every time.
                Check(!RM_LeanKernel.WindLeansWest(0f) && !RM_LeanKernel.WindLeansWest(-0f), "a due north/south wind must resolve east");
                Console.WriteLine($"plantlean check: {cases} heading x art cases, one visible lean each map: OK");
                return true;
            }
            catch (Exception e)
            {
                Console.WriteLine("plantlean check FAILED: " + e.Message);
                return false;
            }
        }
    }
}
