// Verse-free kernel of the Deepfire cuisine (IngestionOutcomeDoer_SteeredFamily): the steer-chance curve, the intended-family
// roll with its re-roll among the others, the weighted plain roll and the per-pawn family cap. The rolls are injected so the
// mod passes the engine's Rand and the fuzz passes its own. SelfTest/LuminousPigmentFuzz.cs compiles this file alone, so it
// must stay free of Verse/RimWorld/UnityEngine.
using System;

namespace RimMandrake.LuminousPigment
{
    public enum FamilyOutcome { None, Bumped, Added, CapBlocked }

    public static class RM_DeepfireCuisine
    {
        public const float TopSkill = 20f;

        // Spec §6.2: linear from `minSkill` -> 50% up to skill 20 -> 100%; a cook below minSkill never steers. A minSkill at
        // or above 20 (the vermilion slider reaches 20) has no run to interpolate over: a cook who qualifies always steers.
        public static float SteerChance(int minSkill, int cookSkill)
        {
            if (cookSkill < minSkill) return 0f;
            if (cookSkill >= TopSkill || minSkill >= TopSkill) return 1f;
            float t = (cookSkill - minSkill) / (TopSkill - minSkill);
            float c = 0.5f + 0.5f * t;
            return c < 0f ? 0f : (c > 1f ? 1f : c);
        }

        public static bool Enabled(bool[] enabled, int i) { return enabled == null || i < 0 || i >= enabled.Length || enabled[i]; }

        // Index of the chosen family, or -1 for none. roll(total) returns a value in [0,total].
        public static int WeightedRandom(float[] weights, bool[] enabled, int excludeIdx, int vermilionIdx, Func<float, float> roll)
        {
            float total = 0f;
            for (int i = 0; i < weights.Length; i++)
            {
                if (!Enabled(enabled, i) || i == excludeIdx || i == vermilionIdx || weights[i] <= 0f) continue;
                total += weights[i];
            }
            if (total <= 0f) return -1;
            float r = roll(total), cum = 0f;
            int last = -1;
            for (int i = 0; i < weights.Length; i++)
            {
                if (!Enabled(enabled, i) || i == excludeIdx || i == vermilionIdx || weights[i] <= 0f) continue;
                cum += weights[i];
                last = i;
                if (r <= cum) return i;
            }
            return last;
        }

        // intendedIdx < 0 = a plain dish (or an unresolvable target). A steered dish whose target is disabled rolls plain.
        public static int Choose(int intendedIdx, int cookSkill, int steerMin, int vermilionMin, int vermilionIdx, float[] weights, bool[] enabled,
            Func<float, bool> chance, Func<float, float> roll)
        {
            if (intendedIdx >= 0 && Enabled(enabled, intendedIdx))
            {
                int min = intendedIdx == vermilionIdx ? vermilionMin : steerMin;
                if (cookSkill >= min && chance(SteerChance(min, cookSkill))) return intendedIdx;
                return WeightedRandom(weights, enabled, intendedIdx, vermilionIdx, roll);
            }
            return WeightedRandom(weights, enabled, -1, vermilionIdx, roll);
        }

        public static float Bump(float severity, float max) { return Math.Min(severity + 1f, max); }

        // Same family again bumps a whole tier; a new family is added unless the pawn already carries `cap` distinct ones.
        public static FamilyOutcome Apply(bool hasThisFamily, int distinctFamilies, int cap)
        {
            if (hasThisFamily) return FamilyOutcome.Bumped;
            return distinctFamilies >= cap ? FamilyOutcome.CapBlocked : FamilyOutcome.Added;
        }
    }
}
