// Verse-free kernel of the Joining Water (GELATINOUSSLIME_JOINING_WATER_STANDALONE_1): who the donor is, how much of a permanent
// hediff leaves them, and how the shared remainder is split into weak ones. Same rule as the other kernels: no Verse/RimWorld/UnityEngine.
using System.Collections.Generic;

namespace RimMandrake.GelatinousSlime
{
    public static class RM_JoiningWaterKernel
    {
        /// <summary>The donor is the participant carrying the most permanent severity; ties go to the first. -1 when nobody carries any.</summary>
        public static int PickDonor(IList<float> permanentTotals)
        {
            int best = -1; float bestV = 0f;
            for (int i = 0; i < permanentTotals.Count; i++)
            {
                if (permanentTotals[i] > bestV) { bestV = permanentTotals[i]; best = i; }
            }
            return best;
        }

        /// <summary>Fraction of a permanent hediff's severity that leaves the donor, by the rite's outcome (positivityIndex &lt; 0 poor, 0..1 fair, 2 good, 3+ excellent).</summary>
        public static float ShareFraction(int positivityIndex, float poor, float fair, float good, float excellent)
        {
            if (positivityIndex < 0) return poor;
            if (positivityIndex <= 1) return fair;
            return positivityIndex == 2 ? good : excellent;
        }

        /// <summary>
        /// Severity is shared, not erased: <paramref name="taken"/> leaves the donor, and the recipients together carry at most
        /// that much (weakFactor &lt;= 1 makes each share a weak echo). Never more than the donor had.
        /// </summary>
        public static void Split(float severity, float fraction, int recipients, float weakFactor, out float taken, out float perRecipient)
        {
            float f = fraction < 0f ? 0f : (fraction > 1f ? 1f : fraction);
            taken = severity <= 0f ? 0f : severity * f;
            float w = weakFactor < 0f ? 0f : (weakFactor > 1f ? 1f : weakFactor);
            perRecipient = recipients > 0 ? taken / recipients * w : 0f;
        }
    }
}
