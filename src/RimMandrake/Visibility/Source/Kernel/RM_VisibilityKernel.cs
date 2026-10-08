// Verse-free kernel of Colony Visibility: the 0-100 dial's five bands, the ruled threat curve, the player's strength slider, the raid-point
// scaling and its clamps, the launch reset, and the tile-memory decay and restore. GameComponent_ColonyVisibility, RM_VisibilitySettings and
// ColonyVisibilityRaidPatch call these with the same expressions; SelfTest/Fuzz/VisibilityFuzz.cs compiles this file alone.
// Keep it free of Verse/RimWorld/UnityEngine/HarmonyLib (a `using Verse;` here breaks the self-test build, which is the guard rail).
using System;

namespace RimMandrake.Visibility
{
    public static class RM_VisibilityKernel
    {
        public const float Min = 0f, Max = 100f;
        /// <summary>Band edges, ruled: Hidden under 20, Discreet under 40, Noticed under 60, Marked under 80, Exposed above.</summary>
        public const float BandWidth = 20f;
        public const int Hidden = 0, Discreet = 1, Noticed = 2, Marked = 3, Exposed = 4;

        public const float LaunchFloor = 5f, LaunchCeiling = 15f;
        /// <summary>GenDate.TicksPerSeason: 15 days of 60000 ticks.</summary>
        public const int TicksPerSeason = 900000;
        /// <summary>Hard cap on a scaled raid's points (vanilla's own global cap).</summary>
        public const float PointsCap = 10000f;

        // Annex A's ruled curve (0 .55 / 25 .80 / 50 1.00 / 75 1.25 / 100 1.60), linear between points, flat beyond the ends.
        public static readonly float[] CurveX = { 0f, 25f, 50f, 75f, 100f };
        public static readonly float[] CurveY = { 0.55f, 0.80f, 1.00f, 1.25f, 1.60f };

        public static int BandFor(float v)
        {
            if (v < 20f) return Hidden;
            if (v < 40f) return Discreet;
            if (v < 60f) return Noticed;
            if (v < 80f) return Marked;
            return Exposed;
        }

        public static float ThreatFactor(float visibility)
        {
            if (visibility <= CurveX[0]) return CurveY[0];
            for (int i = 1; i < CurveX.Length; i++)
            {
                if (visibility < CurveX[i])
                {
                    float t = (visibility - CurveX[i - 1]) / (CurveX[i] - CurveX[i - 1]);
                    return CurveY[i - 1] + (CurveY[i] - CurveY[i - 1]) * t;
                }
            }
            return CurveY[CurveY.Length - 1];
        }

        /// <summary>The player's strength slider lerps from "no effect" (1x) through the ruled curve (1) to an exaggeration (2).</summary>
        public static float ScaledThreatFactor(float curveFactor, float strength)
        {
            return 1f + (curveFactor - 1f) * strength;
        }

        public static float Clamp(float v, float lo, float hi)
        {
            if (v < lo) v = lo;
            else if (v > hi) v = hi;
            return v;
        }

        /// <summary>The dial after a delta: always inside 0..100.</summary>
        public static float Adjust(float dial, float delta)
        {
            return Clamp(dial + delta, Min, Max);
        }

        /// <summary>The dial right after a gravship launch: dial x multiplier, held to 5..15.</summary>
        public static float ResetOnLaunch(float dial, float multiplier)
        {
            return Clamp(dial * multiplier, LaunchFloor, LaunchCeiling);
        }

        public static float SeasonsAway(int ticksAway)
        {
            return Math.Max(0f, ticksAway) / (float)TicksPerSeason;
        }

        /// <summary>A departed tile's remembered dial, halved for every season away.</summary>
        public static float DecayedTileVisibility(float atDeparture, int ticksAway)
        {
            return atDeparture * (float)Math.Pow(0.5f, SeasonsAway(ticksAway));
        }

        /// <summary>What arriving back at a remembered tile adds to the dial: only the part of the decayed memory above the present dial.</summary>
        public static float RestoreDelta(float dial, float decayed)
        {
            return decayed > dial ? decayed - dial : 0f;
        }

        /// <summary>A hostile incident's points after scaling. Scaling never pushes a raid past the global floor/cap and leaves a raid
        /// that is already outside them alone, so a factor of exactly 1 (strength 0, or the middle of the curve) is truly "no effect".</summary>
        public static float ScalePoints(float points, float factor, float globalMin)
        {
            float lo = Math.Min(points, globalMin);
            float hi = Math.Max(points, PointsCap);
            return Clamp(points * factor, lo, hi);
        }
    }
}
