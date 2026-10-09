using System.Collections.Generic;

namespace RimMandrake.CreatureBehaviors
{
    /// <summary>VERMIN_EAT_BREEDING_FOOD_1 (CB-3). Verse-free arithmetic for a breeder eating the pile it breeds on (also compiled by
    /// SelfTestFuzz): how many units each reachable stack gives for one litter. Stacks arrive nearest-first and counts are the stack
    /// sizes; the plan never takes more than a stack holds, more than needed, or from an empty/negative stack.</summary>
    public static class RM_VerminFoodMath
    {
        /// <summary>Greedy take, nearest stack first. Returns units taken per stack (same length as input).</summary>
        public static int[] Plan(IList<int> stackCounts, int need)
        {
            var take = new int[stackCounts == null ? 0 : stackCounts.Count];
            if (stackCounts == null || need <= 0) return take;
            int left = need;
            for (int i = 0; i < stackCounts.Count && left > 0; i++)
            {
                int have = stackCounts[i] < 0 ? 0 : stackCounts[i];
                int t = have < left ? have : left;
                take[i] = t;
                left -= t;
            }
            return take;
        }

        public static int Total(int[] take)
        {
            int s = 0;
            if (take != null) foreach (int t in take) s += t;
            return s;
        }
    }
}
