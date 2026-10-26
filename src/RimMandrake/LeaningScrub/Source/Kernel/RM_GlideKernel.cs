using System;

// Verse-free kernel of the shirrel's Gale glide (RM_ShirrelGlide.cs). SelfTest/LeaningScrubGlideCheck.cs compiles it.
//
// SHIRREL_DECIDE_GALE_GLIDE, owner by card 2026-10-26 ("How should the Gale glide work? -> Real glide as a flyer"): in the
// Gale a shirrel launches from a tree as a real 1.6 flyer (Pawn_FlightTracker, the eruptors' RM_Flight path) for a short
// hop downwind, and keeps a home tether to the sweetline trees. Flight is otherwise OFF for the race: the def carries
// MaxFlightTime (so the tracker can fly it) but the CanFlyNow gate below refuses every take-off that is not the glide
// itself, so vanilla's job-start chance never lifts a shirrel on a calm day. Numbers PROVISIONAL.
namespace RimMandrake.LeaningScrub
{
    public static class RM_GlideKernel
    {
        public const float TicksPerHour = 2500f;

        // The flight-tracker gate (Harmony postfix on Pawn_FlightTracker.CanFlyNow). A pawn without the glide comp keeps
        // vanilla's answer untouched; a glider may fly only while its own launch is in progress.
        public static bool CanFlyNow(bool vanilla, bool isGlider, bool launching)
        {
            return isGlider ? vanilla && launching : vanilla;
        }

        // Whether this check starts a glide. Every gate is required: the feature on, the Gale blowing, a known wind,
        // a wild idle (wandering) pawn that is awake, not downed, not in a mental state, next to a launch tree, off flight
        // cooldown, and the roll under the per-check chance.
        public static bool ShouldGlide(bool featureOn, bool gale, bool hasWind, bool wild, bool idle, bool awake, bool downed,
            bool inMentalState, bool nearLaunchTree, bool canFlyVanilla, float roll, float chance)
        {
            return featureOn && gale && hasWind && wild && idle && awake && !downed && !inMentalState && nearLaunchTree
                && canFlyVanilla && roll < chance;
        }

        public static float ChancePerCheck(float mtbHours, int intervalTicks)
        {
            if (mtbHours <= 0f || intervalTicks <= 0) return 0f;
            return (float)(1.0 - Math.Exp(-(double)intervalTicks / (mtbHours * TicksPerHour)));
        }

        // Hop length from a unit roll: hopMin..hopMax cells, clamped, min never above max.
        public static float HopDistance(float hopMin, float hopMax, float roll01)
        {
            float lo = Math.Max(1f, Math.Min(hopMin, hopMax));
            float hi = Math.Max(lo, hopMax);
            float r = roll01 < 0f ? 0f : (roll01 > 1f ? 1f : roll01);
            return lo + (hi - lo) * r;
        }

        // The landing aim: the start cell carried `distance` cells along the downwind unit vector (dirX, dirZ), rounded to
        // the nearest cell and clamped inside a map of width x height with a margin (never aim at the edge: no map exit).
        public static void HopTarget(int x, int z, float dirX, float dirZ, float distance, int width, int height, int margin,
            out int tx, out int tz)
        {
            double len = Math.Sqrt((double)dirX * dirX + (double)dirZ * dirZ);
            double ux = len > 1e-6 ? dirX / len : 0.0, uz = len > 1e-6 ? dirZ / len : 0.0;
            tx = (int)Math.Round(x + ux * distance);
            tz = (int)Math.Round(z + uz * distance);
            int m = Math.Max(0, margin);
            tx = Math.Max(m, Math.Min(width - 1 - m, tx));
            tz = Math.Max(m, Math.Min(height - 1 - m, tz));
        }

        // Inspect-pane line. Feature off -> no line (a plain wild animal).
        public static string Describe(bool featureOn, bool bound, string treeLabel, bool flying)
        {
            if (!featureOn) return null;
            string home = bound ? "Home: " + treeLabel : "No sweetline tree on this map";
            return flying ? home + ". Gliding on the Gale." : home + ".";
        }
    }
}
