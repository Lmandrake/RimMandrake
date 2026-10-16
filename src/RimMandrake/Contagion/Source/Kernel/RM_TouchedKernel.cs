// Verse-free kernel of Contagion-touched (CONTAGION_MECHANICS_BUILD_1, owner rulings 2026-10-15 Q3 and N4):
//   - N4: "Bloom time, stronger in burn, and contact." Three exposure sources feed one condition: time under open sky in a
//     Bloom (slow), under open sky in a Burn (stronger), and standing against an Unfinished or a Coalescence (contact).
//   - Q3: "Stops current mutations. No protection if you get exposed again later." The Sunbeam arrest removes the condition;
//     mutations already grown stay; the next exposure starts a fresh condition.
//   - The deck (MUTATION_MODIFIERS_SURVEY_1, ruled 2026-09-12): "50% all negative and 50% positive + negative."
// RM_MapComponent_ContagionTouch and HediffComp_RM_ContagionTouched call these with the same expressions;
// SelfTest/ContagionFuzz.cs compiles this file alone, so it must stay free of Verse/RimWorld/UnityEngine.
using System.Collections.Generic;

namespace RimMandrake.Contagion
{
    public static class RM_TouchedKernel
    {
        // Severity added to one pawn in one 250-tick poll. Only a fleshy, non-native humanlike is ever dosed. The sky dose
        // needs open sky; a Burn replaces the Bloom dose (it never stacks with it); contact adds on top of either.
        public static float Dose(bool eligible, bool exposed, bool bloomSky, bool burnSky, bool contact,
            float bloomDose, float burnDose, float contactDose, float factor)
        {
            if (!eligible || factor <= 0f) return 0f;
            float d = 0f;
            if (exposed)
            {
                if (burnSky) d += burnDose;
                else if (bloomSky) d += bloomDose;
            }
            if (contact) d += contactDose;
            return d > 0f ? d * factor : 0f;
        }

        // Mean days between mutations for a touched pawn, or -1 when none can come: below the threshold, the rate at 0, or
        // the pawn already carrying the cap. Heavier exposure mutates faster (inverse in severity).
        public static float MutationMtbDays(float severity, float minSeverity, float mtbDaysAtFull, float rate, int mutationsHeld, int cap)
        {
            if (severity < minSeverity || severity <= 0f || rate <= 0f || mtbDaysAtFull <= 0f || mutationsHeld >= cap) return -1f;
            return mtbDaysAtFull / (severity * rate);
        }

        // The ruled split: a roll below the all-negative share draws from the all-negative half of the deck.
        public static bool AllNegative(float roll01, float allNegativeShare)
        {
            return roll01 < allNegativeShare;
        }

        // Weighted pick among the eligible entries; roll01 in [0,1). -1 when nothing is eligible or every weight is zero.
        public static int PickWeighted(IList<float> weights, IList<bool> eligible, float roll01)
        {
            float total = 0f;
            for (int i = 0; i < weights.Count; i++)
            {
                if (eligible[i] && weights[i] > 0f) total += weights[i];
            }
            if (total <= 0f) return -1;
            float x = roll01 * total;
            int last = -1;
            for (int i = 0; i < weights.Count; i++)
            {
                if (!eligible[i] || weights[i] <= 0f) continue;
                last = i;
                if (x < weights[i]) return i;
                x -= weights[i];
            }
            return last;   // float round-off at the top end lands on the last eligible entry
        }

        // Which half of the deck a mutation comes from: the rolled half when it has anything eligible, else the other half
        // (so a pawn who already grew every all-negative entry still mutates), else none (-1). 1 = all-negative, 0 = mixed.
        public static int Half(bool rolledAllNegative, bool anyAllNegativeEligible, bool anyMixedEligible)
        {
            if (rolledAllNegative) return anyAllNegativeEligible ? 1 : (anyMixedEligible ? 0 : -1);
            return anyMixedEligible ? 0 : (anyAllNegativeEligible ? 1 : -1);
        }

        // The never-upgrade law, checkable on a deck entry's own numbers: an all-negative entry carries no benefit and at
        // least one cost; a mixed entry carries at least one benefit AND at least one cost. Nothing may be benefit-only.
        public static bool EntryLawful(bool allNegative, int benefits, int costs)
        {
            if (costs <= 0) return false;
            return allNegative ? benefits == 0 : benefits > 0;
        }
    }
}
