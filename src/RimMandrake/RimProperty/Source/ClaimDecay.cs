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
            return RM_PropertyKernel.LifetimeTicks(
                recognizability,
                PropertyTuning.MinClaimLifetimeDays,
                PropertyTuning.MaxClaimLifetimeDays,
                PropertySettings.claimLifetimeMultiplier,
                GenDate.TicksPerDay);
        }

        // Linear decay from InitialStrength to 0 over LifetimeTicks(recognizability).
        public static float EffectiveStrength(float initialStrength, int ageTicks, float recognizability)
        {
            if (ageTicks <= 0) return initialStrength;

            return RM_PropertyKernel.EffectiveStrength(initialStrength, ageTicks, LifetimeTicks(recognizability));
        }
    }
}
