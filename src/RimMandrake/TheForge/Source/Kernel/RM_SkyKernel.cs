// Verse-free kernel of the sky pastures (FORGE_SKY_PASTURES_1): the jossur stoop band, the column-aware prey score, the
// highlight reach and the ash mote geometry. RM_ForgeSkyPastures.cs calls these with the same expressions;
// SelfTest/TheForgeFuzz.cs compiles this file alone (no Verse/RimWorld/UnityEngine).
using System;

namespace RimMandrake.TheForge
{
    public static class RM_SkyKernel
    {
        public const float InColumnBonus = 30f;
        public const float OpenAshPenalty = 60f;
        public const int MoteLifeTicks = 240;
        public const int MoteStepTicks = 4;

        // Closer than min it simply runs the prey down; farther than max the hunt is still a walk-up.
        public static bool StoopBand(float dist, float min, float max) { return !(dist < min || dist > max); }

        public static float PreyScoreDelta(bool preyInColumn, float forageRadiusBeyondColumns, bool nearestColumnWithinForage)
        {
            if (preyInColumn) return InColumnBonus;
            if (forageRadiusBeyondColumns <= 0f || !nearestColumnWithinForage) return -OpenAshPenalty;
            return 0f;
        }

        public static float HighlightReach(float searchRadius) { return Math.Min(60f, Math.Max(8f, searchRadius)); }

        public static bool MoteAlive(int age) { return age < MoteLifeTicks; }

        public static void MotePos(float cx, float cz, float phase, float spin, int age, out float x, out float z)
        {
            float t = age / (float)MoteLifeTicks;
            float ang = phase + t * spin;
            float r = 1.6f * (1f - 0.65f * t);
            x = cx + (float)Math.Cos(ang) * r;
            z = cz + (float)Math.Sin(ang) * r * 0.55f + t * 3.2f;
        }
    }
}
