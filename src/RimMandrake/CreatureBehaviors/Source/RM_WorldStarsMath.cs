// WORLD_STARS_REPAIR_STILL_SPINNING_FOR_NOBODY — the stars' yearly drift, Verse-free (compiled into the SelfTest).
//
// Vanilla (GlobalDrawLayer_Stars.Rotation, 1.6): the starfield aims along GenCelestial.CurSunPositionInWorldSpace(), which
// turns 360° per DAY, so on a tidally locked world the stars wheel round the planet daily. Owner, by card 2026-10-20: the
// stars drift slowly once a YEAR instead (60 days: 6° per day); a Mod Setting freezes them completely.
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
    }
}
