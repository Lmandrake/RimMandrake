using System;

namespace RimMandrake.Pyrelands
{
    /// <summary>
    /// PYRELANDS_FURNACE_WARMTH_AMBIENT_1 - the pure maths of the walking hearth's local felt-temperature
    /// offset. System.Math only, so the offline selftest (Source/SelfTest) compiles THIS file rather than
    /// a copy. A pawn at the beast feels +maxC; the offset falls off linearly to 0 at the radius.
    /// </summary>
    public static class FurnaceWarmthMath
    {
        /// <summary>Degrees C added to a pawn's felt temperature at distance sqrt(distSq) from a beast whose aura
        /// reaches radius, before the Mod Settings strength dial. 0 outside the radius.</summary>
        public static float Offset(float distSq, float radius, float maxC, float strength)
        {
            if (radius <= 0f || strength <= 0f || maxC <= 0f)
            {
                return 0f;
            }
            float r2 = radius * radius;
            if (distSq >= r2)
            {
                return 0f;
            }
            float fall = 1f - (float)Math.Sqrt(distSq) / radius;
            return maxC * fall * strength;
        }

        /// <summary>Radius from the beast's thermal charge (0..1): a run-down beast is faintly warm, a fresh one a hearth.
        /// With no charge comp (hasCharge false) the full radius.</summary>
        public static float Radius(float fullRadius, float minFraction, bool hasCharge, float charge)
        {
            if (!hasCharge)
            {
                return fullRadius;
            }
            float c = charge < 0f ? 0f : (charge > 1f ? 1f : charge);
            return fullRadius * (minFraction + (1f - minFraction) * c);
        }

        /// <summary>Two beasts are not twice as warm: the warmest one counts.</summary>
        public static float Combine(float a, float b)
        {
            return a > b ? a : b;
        }
    }
}
