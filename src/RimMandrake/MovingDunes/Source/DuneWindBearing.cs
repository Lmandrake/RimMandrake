using System;

namespace RimMandrake.MovingDunes
{
    /// <summary>
    /// STILLSAND_WIND_SUN_BEARING_1 — "one bearing for everything". Pure maths
    /// (System.Math only, so the CreatureBehaviors sun-heat selftest compiles it
    /// straight in and checks it against the pinned sun's own SunGeometry).
    ///
    /// The sun's bearing from a tile is the great-circle initial bearing toward
    /// the substellar point — the SAME formula as
    /// RimMandrake.CreatureBehaviors.RM_MapComponent_PinnedSun.SunGeometry, which
    /// this engine cannot reference (no dependency between the two mods). The
    /// selftest asserts the two agree, so they cannot drift apart unnoticed.
    ///
    /// A locked wind blows ALONG the shadows (away from the sun) by default, so
    /// the dune lees fall on the same side as every shadow on the map; a biome
    /// may set windBlowsTowardSubstellar to reverse it.
    /// </summary>
    public static class DuneWindBearing
    {
        /// <summary>Degrees clockwise from north, from (lat, lon) toward the
        /// substellar point. 0 (north) when the tile IS the substellar point.</summary>
        public static float SunBearingDegrees(float latDeg, float lonDeg, float subLatDeg, float subLonDeg)
        {
            double d2r = Math.PI / 180.0;
            double lat1 = latDeg * d2r;
            double lat2 = subLatDeg * d2r;
            double dLon = (subLonDeg - lonDeg) * d2r;
            double y = Math.Sin(dLon) * Math.Cos(lat2);
            double x = Math.Cos(lat1) * Math.Sin(lat2) - Math.Sin(lat1) * Math.Cos(lat2) * Math.Cos(dLon);
            if (Math.Abs(x) < 1e-12 && Math.Abs(y) < 1e-12)
            {
                return 0f;
            }
            return (float)(Math.Atan2(y, x) / d2r);
        }

        /// <summary>The 8-way wind index (0 = north, clockwise — the dune
        /// engine's own numbering) the wind blows TOWARD: along the shadows
        /// (sun bearing + 180) or, when towardSun, at the sun.</summary>
        public static int WindDirFromSunBearing(float sunBearingDeg, bool towardSun)
        {
            double b = towardSun ? sunBearingDeg : sunBearingDeg + 180.0;
            b %= 360.0;
            if (b < 0)
            {
                b += 360.0;
            }
            return (int)Math.Round(b / 45.0) & 7;
        }
    }
}
