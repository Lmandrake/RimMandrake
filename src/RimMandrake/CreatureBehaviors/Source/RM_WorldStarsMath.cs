// WORLD_STARS_REPAIR_STILL_SPINNING_FOR_NOBODY — the stars' yearly drift, Verse-free (compiled into the SelfTest).
//
// Vanilla (GlobalDrawLayer_Stars.Rotation, 1.6): the starfield aims along GenCelestial.CurSunPositionInWorldSpace(), which
// turns 360° per DAY, so on a tidally locked world the stars wheel round the planet daily. Owner, by card 2026-10-20: the
// stars drift slowly once a YEAR instead (60 days: 6° per day); a Mod Setting freezes them completely.
// The same item pins the world-view SUN (disc, planet light) toward the substellar point: RM_WorldSunPatch.
using System;

namespace RimMandrake.CreatureBehaviors
{
    public static class RM_WorldStarsMath
    {
        /// <summary>GenDate.TicksPerYear (60 days x 60,000 ticks).</summary>
        public const int TicksPerYear = 3600000;

        /// <summary>Degrees the starfield has turned about the planet's axis at ticksAbs: one full turn per year, or 0 when
        /// frozen. Always in [0, 360).</summary>
        public static float DriftDegrees(long ticksAbs, bool drift)
        {
            if (!drift) return 0f;
            long t = ticksAbs % TicksPerYear;
            if (t < 0) t += TicksPerYear;
            return (float)(t * 360.0 / TicksPerYear);
        }

        /// <summary>Unit vector from the planet's centre toward the point at (latDeg, lonDeg): the exact inverse of
        /// PlanetLayer.LongLatOf (1.6: lon = atan2(x, -z), lat = asin(y / radius)). (0, 0) gives (0, 0, -1), the vector
        /// vanilla's sun starts from and the one Alien Worlds - Tidally Locked freezes it at (noon of day 0).</summary>
        public static void SubstellarDirection(double latDeg, double lonDeg, out float x, out float y, out float z)
        {
            double lat = latDeg * Math.PI / 180.0, lon = lonDeg * Math.PI / 180.0;
            x = (float)(Math.Cos(lat) * Math.Sin(lon));
            y = (float)Math.Sin(lat);
            z = (float)(-Math.Cos(lat) * Math.Cos(lon));
        }

        /// <summary>Whether the world-view sun is pinned: the setting is on and a game is being played. The main menu and
        /// world generation (ProgramState.Entry) keep vanilla's sun, which aims at the chosen start tile's noon.</summary>
        public static bool PinsWorldSun(bool settingOn, bool playing)
        {
            return settingOn && playing;
        }
    }
}
