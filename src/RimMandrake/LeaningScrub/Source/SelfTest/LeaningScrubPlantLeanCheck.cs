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

        // Owner card 2026-10-20 17:28, "Point it at the sun, snap to a side": tile -> sun bearing -> heading -> side.
        // The bearing is DuneWindBearing.SunBearingDegrees, the pure-maths twin the CreatureBehaviors selftest proves equal
        // to RM_MapComponent_PinnedSun.SunGeometry, which the game calls (Unity's Mathf cannot load here).
        private static string Side(float lat, float lon)
        {
            float b = RimMandrake.MovingDunes.DuneWindBearing.SunBearingDegrees(lat, lon, 0f, 0f);
            RM_LeanKernel.Direction(RM_LeanKernel.HeadingFromSunBearing(b), out float x, out float _);
            return RM_LeanKernel.WindLeansWest(x) ? "west" : "east";
        }

        private static int SunBearingToSide()
        {
            int n = 0;
            // Worked cases, substellar point (0, 0): a tile west of the sun blows east toward it, and the reverse.
            Check(Side(0f, -90f) == "east", "a tile west of the sun must lean east (toward it)");
            Check(Side(10f, -40f) == "east", "a tile north-west of the sun must lean east");
            Check(Side(0f, 90f) == "west", "a tile east of the sun must lean west");
            Check(Side(-20f, 120f) == "west", "a tile south-east of the sun must lean west");
            // The tie: due north or due south of the sun (and the substellar tile itself) resolves EAST, every time.
            Check(Side(30f, 0f) == "east", "tie: a tile due north of the sun must resolve east");
            Check(Side(-30f, 0f) == "east", "tie: a tile due south of the sun must resolve east");
            Check(Side(0f, 0f) == "east", "tie: the substellar tile itself must resolve east");
            n += 7;
            // Heading = 90 - bearing: the downwind vector is (sin b, cos b) in map x/z for every bearing.
            for (int b = -180; b <= 360; b++)
            {
                RM_LeanKernel.Direction(RM_LeanKernel.HeadingFromSunBearing(b), out float x, out float z);
                double r = b * Math.PI / 180.0;
                Check(Math.Abs(x - Math.Sin(r)) < 1e-4 && Math.Abs(z - Math.Cos(r)) < 1e-4, $"bearing {b}: downwind ({x},{z}) is not toward the sun");
                float h = RM_LeanKernel.HeadingFromSunBearing(b);
                Check(h >= 0f && h < 360f, $"bearing {b}: heading {h} outside [0,360)");
                n++;
            }
            // Planet sweep: the side is the closer of east/west to the sun bearing; only the exact tie goes east by rule.
            for (int lat = -85; lat <= 85; lat += 5)
                for (int lon = -180; lon < 180; lon += 5)
                {
                    float b = RimMandrake.MovingDunes.DuneWindBearing.SunBearingDegrees(lat, lon, 0f, 0f);
                    double sx = Math.Sin(b * Math.PI / 180.0);
                    string want = sx < -RM_LeanKernel.TieX ? "west" : "east";
                    Check(Side(lat, lon) == want, $"tile ({lat},{lon}) bearing {b}: side {Side(lat, lon)}, closer side {want}");
                    if (Math.Abs(sx) > 0.01) Check(want == (lon < 0 ? "east" : "west"), $"tile ({lat},{lon}): the sun at (0,0) lies the other way");
                    n++;
                }
            return n;
        }

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
                cases += SunBearingToSide();
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
