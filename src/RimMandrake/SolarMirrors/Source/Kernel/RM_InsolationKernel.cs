// VEE_SOLAR_REWIRE_GEOMETRY_PAINTS_IT (design/RimMandrake/vee_port_plan_2026-10-22.md §4). Verse-free.
//
// Solar panels follow ONE Direct Sun, a pure function of geometry (owner, 2026-09-29 / 2026-10-19: "no biome-specific
// heat, no biome-specific sun. It's a matter of geometry"). The sun elevation e is 90 - (arc from the substellar point
// at lat 0, long 0), with the single [0°, 90°] clamp of unified_direct_sun_heat_2026-10-19.md DS1 for the factor. No
// mutator, biome or per-tile number is read anywhere.
//
//   InsolationFactor(e) = 1 + bonus * smoothstep(RampStart, RampFull, clamp(e, 0, 90))
//   bonus = the "high-sun bonus" Mod Setting (shipped 0.25: reproduces VEE_MoreSolarPower's x1.25 on every tile it
//   marked, which were exactly e >= 35°, with a smooth ramp instead of a seam).
//
// The world-map labels RM_StrongInsolation / RM_Sunless are DERIVED from the same e (LabelFor): painted at the one
// stamp, never read by code. Ported line for line in src/RimMandrake/Utils/remake/solar_insolation.py, which
// selftest_solar_insolation.py checks against these constants (it parses this file).
using System;

namespace RimMandrake.SolarMirrors
{
    public static class RM_InsolationKernel
    {
        /// <summary>Elevation (degrees) where the high-sun bonus starts to ramp in.</summary>
        public const float RampStartDegrees = 20f;

        /// <summary>Elevation (degrees) at and above which the full bonus applies.</summary>
        public const float RampFullDegrees = 35f;

        /// <summary>A tile with e at or above this carries the RM_StrongInsolation label.</summary>
        public const float StrongInsolationMinDegrees = 35f;

        /// <summary>A tile with e at or below this carries the RM_Sunless label.</summary>
        public const float SunlessMaxDegrees = -35f;

        /// <summary>Shipped high-sun bonus (fraction). PROVISIONAL: VEE's x1.25, tune live.</summary>
        public const float DefaultHighSunBonus = 0.25f;

        /// <summary>Great-circle arc (degrees) from the substellar point (lat 0, long 0) to (lat, lon).
        /// Same formula as RimMandrake.CreatureBehaviors.RM_TidalSunGlowMath.ArcDegrees.</summary>
        public static double ArcDegrees(double latDeg, double lonDeg)
        {
            const double d2r = Math.PI / 180.0;
            double c = Math.Cos(latDeg * d2r) * Math.Cos(lonDeg * d2r);
            if (c > 1.0) c = 1.0;
            if (c < -1.0) c = -1.0;
            return Math.Acos(c) / d2r;
        }

        /// <summary>Sun elevation (degrees, unclamped: negative below the horizon) at (lat, lon).</summary>
        public static double ElevationDegrees(double latDeg, double lonDeg) => 90.0 - ArcDegrees(latDeg, lonDeg);

        /// <summary>Multiplier on a solar panel's output for a sun at elevationDeg. 1 at and below RampStart.</summary>
        public static float InsolationFactor(double elevationDeg, float bonus)
        {
            if (bonus <= 0f) return 1f;
            double e = elevationDeg < 0.0 ? 0.0 : (elevationDeg > 90.0 ? 90.0 : elevationDeg);
            double t = (e - RampStartDegrees) / (RampFullDegrees - RampStartDegrees);
            if (t <= 0.0) return 1f;
            if (t >= 1.0) return 1f + bonus;
            return (float)(1.0 + bonus * t * t * (3.0 - 2.0 * t));
        }

        /// <summary>The derived world-map label: +1 = RM_StrongInsolation, -1 = RM_Sunless, 0 = none (the terminator belt).</summary>
        public static int LabelFor(double elevationDeg)
        {
            if (elevationDeg >= StrongInsolationMinDegrees) return 1;
            if (elevationDeg <= SunlessMaxDegrees) return -1;
            return 0;
        }
    }
}
