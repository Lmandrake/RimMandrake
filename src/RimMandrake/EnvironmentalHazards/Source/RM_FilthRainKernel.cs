using System;

namespace RimMandrake.EnvironmentalHazards
{
    // SUMP_TAR_LIVING_SYSTEMS_1 part 2 (tar rain). The pure numbers behind a weather-pulse burst whose frequency a
    // biome mod's setting scales, and behind a filth rain (a weather that lays filth on open ground while it runs).
    // Kept free of Verse/Unity so the offline SelfTest compiles this exact file
    // (RimMandrake.EnvironmentalHazards.SelfTest.csproj lists it).
    public static class RM_FilthRainKernel
    {
        // A burst MTB, in hours, after a frequency scale. Scale 1 = the def's own MTB; 2 = twice as often; 0 (or
        // anything not a positive finite number) = never, returned as +infinity so a caller's MTB roll never fires.
        public static float EffectiveMtbHours(float baseMtbHours, float frequencyScale)
        {
            if (!(baseMtbHours > 0f) || float.IsInfinity(baseMtbHours))
            {
                return float.PositiveInfinity;
            }
            if (!(frequencyScale > 0f) || float.IsInfinity(frequencyScale))
            {
                return float.PositiveInfinity;
            }
            return baseMtbHours / frequencyScale;
        }

        // How many cells one filth-rain event tries to coat. The def's figure is per 250x250 map (vanilla's default
        // size), scaled to the real map area so a small map is not drowned and a big one not starved; an intensity
        // scale (a setting) multiplies it. Never negative, never more than the map holds, and at least one whenever
        // anything is asked for at all on a non-empty map.
        public const int ReferenceArea = 250 * 250;

        public static int CellsPerEvent(float cellsPerReferenceMap, int mapArea, float intensityScale)
        {
            if (mapArea <= 0 || !(cellsPerReferenceMap > 0f) || !(intensityScale > 0f)
                || float.IsInfinity(cellsPerReferenceMap) || float.IsInfinity(intensityScale))
            {
                return 0;
            }
            double want = (double)cellsPerReferenceMap * intensityScale * mapArea / ReferenceArea;
            if (want > mapArea)
            {
                return mapArea;
            }
            int n = (int)Math.Round(want);
            return n < 1 ? 1 : n;
        }

        // Chance an exposed pawn picks up one unit of the filth on one event, clamped to [0, 1].
        public static float PawnChance(float chance, float intensityScale)
        {
            if (float.IsNaN(chance) || float.IsNaN(intensityScale) || chance <= 0f || intensityScale <= 0f)
            {
                return 0f;
            }
            double p = (double)chance * intensityScale;
            return p >= 1.0 ? 1f : (float)p;
        }
    }
}
