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

        // Stage 5, the pasture wander. A destination is good inside a column, or within a positive leash of one.
        public static bool WanderDestOk(bool destInColumn, float leash, bool columnWithinLeash)
        {
            return destInColumn || (leash > 0f && columnWithinLeash);
        }

        // Who the pasture wander governs: wild only (a tame animal keeps its colony wander); a drifter while the sky wander is
        // on; otherwise a dhokkur-extension pawn while its toggle is on and it is not sealed in dormancy.
        public static bool PastureGoverns(bool wild, bool hasDrifter, bool skyWanderOn, bool hasDhokkurExt, bool dhokkurOn, bool isSealed)
        {
            if (!wild) return false;
            if (hasDrifter) return skyWanderOn;
            return hasDhokkurExt && dhokkurOn && !isSealed;
        }

        // Stage 5b, the pasture homing (sits ahead of needs, at Animal_PreMain): a governed pawn away from home (not in a column
        // nor within its leash of one) with a column in reach walks home first, so it eats and sleeps in the pasture; it yields
        // only to an urgent need (urgently hungry or starving, or exhausted), which vanilla's need nodes then take.
        public static bool HomingWanted(bool governed, bool atHome, bool columnInReach, bool urgentlyHungry, bool exhausted)
        {
            return governed && !atHome && columnInReach && !urgentlyHungry && !exhausted;
        }

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
