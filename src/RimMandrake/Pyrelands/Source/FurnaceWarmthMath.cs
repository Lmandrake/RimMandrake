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

        /// <summary>FURNACE_AURA_FIX_WARMS_THROUGH_WALLS: the aura is the OPEN-FIELD half only. A pawn in an enclosed room
        /// (a room that does not use the outdoor temperature) is warmed by the beast's vanilla heat pusher through the room
        /// temperature, so the aura would stack on it; and a wall between pawn and beast (no line of sight) blocks it.</summary>
        public static bool AuraReaches(bool pawnInEnclosedRoom, bool lineOfSight)
        {
            return !pawnInEnclosedRoom && lineOfSight;
        }

        /// <summary>The smallest offset the recipient's inspect pane shows ("Warmed by furnace-beast (+N C)"); below it the line would
        /// read +0 C. FURNACE_WARMTH_FIX_NO_SIGN_TO_READ.</summary>
        public const float SignMinC = 0.5f;

        /// <summary>Whether a pawn feeling this offset shows the warmth sign.</summary>
        public static bool ShowsSign(float offsetC)
        {
            return offsetC >= SignMinC;
        }

        /// <summary>Two beasts are not twice as warm: the warmest one counts.</summary>
        public static float Combine(float a, float b)
        {
            return a > b ? a : b;
        }
    }
}
