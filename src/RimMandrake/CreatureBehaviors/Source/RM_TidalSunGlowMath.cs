// SUN_GLOW_DECIDE_WEST_TERMINATOR_SUNBATHING — daylight on a tidally locked world as a pure function of sun angle.
// Verse-free (compiled into the SelfTest and ported line for line in Utils/remake/world_physics_audit.py).
//
// Owner, by card 2026-10-20 ("Lopsided tidal-lock daylight: what should light do?" -> "Light follows the sun"). The
// borrowed Alien Worlds - Tidally Locked prefix on GenCelestial.CelestialSunGlow(PlanetTile,int) feeds LONGITUDE into
// vanilla's latitude fudges, so the west night-side rim reads lit and the east day-side rim reads dark
// (design/RimMandrake/world_physics_audit_2026-10-20.md §2). This replaces it with the geometry Direct Sun heat
// already uses (design/RimMandrake/unified_direct_sun_heat_2026-10-19.md): elevation = 90 - arc from the
// substellar point (lat 0, long 0), the same arc as RM_MapComponent_PinnedSun.SunGeometry.
//
// The curve, chosen so vanilla's day/night test (GenCelestial.IsDaytime: glow > 0.6) agrees with the geometry:
//   elevation > 0           glow = 0.6 + 0.4 * clamp01(sin(e) / sin(FullDayElevation))  -> always daytime, 1.0 from 30°
//   -band < elevation <= 0  glow = 0.6 * smoothstep((e + band) / band)                   -> dusk band, never daytime
//   elevation <= -band      glow = 0                                                     -> night
// No time input: constant in time. Depends only on the arc: symmetric west/east and north/south.
using System;

namespace RimMandrake.CreatureBehaviors
{
    public static class RM_TidalSunGlowMath
    {
        /// <summary>GenCelestial.IsDaytime: glow strictly above this is day (RimSage, 1.6).</summary>
        public const float DayNightThreshold = 0.6f;

        /// <summary>Sun elevation (degrees) at and above which the day is at full glow.</summary>
        public const float FullDayElevationDegrees = 30f;

        /// <summary>Default width (degrees below the horizon) of the dusk band on the night-side rim.</summary>
        public const float DefaultTwilightBandDegrees = 6f;

        /// <summary>Great-circle arc (degrees) from the substellar point (lat 0, long 0) to (lat, lon).</summary>
        public static double ArcDegrees(double latDeg, double lonDeg)
        {
            const double d2r = Math.PI / 180.0;
            double c = Math.Cos(latDeg * d2r) * Math.Cos(lonDeg * d2r);
            if (c > 1.0) c = 1.0;
            if (c < -1.0) c = -1.0;
            return Math.Acos(c) / d2r;
        }

        /// <summary>Celestial sun glow for a sun at elevationDeg above the horizon (negative = below).</summary>
        public static float GlowFromElevation(double elevationDeg, float twilightBandDegrees)
        {
            if (elevationDeg > 0.0)
            {
                double f = Math.Sin(elevationDeg * Math.PI / 180.0) / Math.Sin(FullDayElevationDegrees * Math.PI / 180.0);
                if (f > 1.0) f = 1.0;
                return (float)(DayNightThreshold + (1.0 - DayNightThreshold) * f);
            }
            if (twilightBandDegrees <= 0f || elevationDeg <= -twilightBandDegrees) return 0f;
            double t = (elevationDeg + twilightBandDegrees) / twilightBandDegrees;
            return (float)(DayNightThreshold * t * t * (3.0 - 2.0 * t));
        }

        /// <summary>Glow at a tile by its latitude/longitude (degrees).</summary>
        public static float GlowAt(double latDeg, double lonDeg, float twilightBandDegrees)
            => GlowFromElevation(90.0 - ArcDegrees(latDeg, lonDeg), twilightBandDegrees);
    }
}
