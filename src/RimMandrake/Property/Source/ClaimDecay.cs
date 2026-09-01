using RimWorld;
using UnityEngine;

namespace RimMandrake.Property
{
    // Spec item 3: "Decay is computed lazily; no tick cost, no comp on ten
    // thousand rocks." Every method here is a pure function of (strength,
    // age, recognizability) evaluated at query time — nothing here is
    // driven by a tick, a CompTick, or any per-interval scan. The curve
    // SHAPE (linear-to-zero) is a deliberately simple first pass; per-band
    // curve tuning is explicitly out of scope for this fabric (see
    // PropertyTuning's header) and lands as RimUtinni data.
    public static class ClaimDecay
    {
        public static float LifetimeTicks(float recognizability)
        {
            recognizability = Mathf.Clamp01(recognizability);
            float days = Mathf.Lerp(
                PropertyTuning.MinClaimLifetimeDays,
                PropertyTuning.MaxClaimLifetimeDays,
                recognizability);
            return days * GenDate.TicksPerDay;
        }

        // Linear decay from InitialStrength to 0 over LifetimeTicks(recognizability).
        public static float EffectiveStrength(float initialStrength, int ageTicks, float recognizability)
        {
            if (ageTicks <= 0) return initialStrength;

            float lifetime = LifetimeTicks(recognizability);
            if (ageTicks >= lifetime) return 0f;

            return initialStrength * (1f - ageTicks / lifetime);
        }
    }
}
