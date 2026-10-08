// Verse-free kernel of the sun sphere (RM_Building_SunSphere): the husk -> seeded -> culturing -> mature culture clock with
// its starvation grace, and the glow factor per stage. SelfTest/TerminalBiomesFuzz.cs compiles this file alone, so it must
// stay free of Verse/RimWorld/UnityEngine.
using System;

namespace RimMandrake.TerminalBiomes
{
    public enum RM_SunSphereStage { Husk, Seeded, Culturing, Mature }

    public static class RM_SunSphereKernel
    {
        public const int CultureTicksToMature = 6 * 60000;
        public const float MatureRadius = 6f;

        // One 60-tick step. Returns true when the wild seed was consumed (a husk with a seed becomes Seeded).
        public static bool Step(ref RM_SunSphereStage stage, ref int cultureTicks, ref int starvedTicks, bool seedHasFuel, bool fed, int graceTicks, int delta)
        {
            if (stage == RM_SunSphereStage.Husk)
            {
                if (!seedHasFuel) return false;
                stage = RM_SunSphereStage.Seeded;
                cultureTicks = 0;
                starvedTicks = 0;
                return true;
            }
            if (fed)
            {
                starvedTicks = 0;
                cultureTicks += delta;
                if (stage == RM_SunSphereStage.Seeded && cultureTicks > 0) stage = RM_SunSphereStage.Culturing;
                if (cultureTicks >= CultureTicksToMature)
                {
                    cultureTicks = CultureTicksToMature;
                    stage = RM_SunSphereStage.Mature;
                }
            }
            else
            {
                starvedTicks += delta;
                if (graceTicks > 0 && starvedTicks >= graceTicks)
                {
                    stage = RM_SunSphereStage.Husk;
                    cultureTicks = 0;
                    starvedTicks = 0;
                }
            }
            return false;
        }

        public static float Factor(RM_SunSphereStage stage, int cultureTicks)
        {
            switch (stage)
            {
                case RM_SunSphereStage.Husk: return 0f;
                case RM_SunSphereStage.Seeded: return 0.1f;
                case RM_SunSphereStage.Culturing:
                    {
                        float t = (float)cultureTicks / CultureTicksToMature;
                        t = t < 0f ? 0f : (t > 1f ? 1f : t);
                        return 0.15f + (0.7f - 0.15f) * t;
                    }
                default: return 1f;
            }
        }

        public static float Radius(float factor) { return Math.Max(0.05f, MatureRadius * factor); }
    }
}
