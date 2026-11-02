// Verse-free kernel of the one salvage rule (SALVAGE_YIELD_UNIFY_THREE_RULES_TODAY): how a total splits into legal stacks, what a
// process cycle still owes after its first output, when a cycle's plan may be dropped, and when a cremation pays. Compiled alone by
// mod self-tests; keep it free of Verse/RimWorld/UnityEngine/HarmonyLib.
using System;
using System.Collections.Generic;

namespace RimMandrake.Shared
{
    internal static class RM_SalvageRuleKernel
    {
        /// <summary>A material total as stacks no larger than the limit; nothing is lost and a non-positive total is no stack.</summary>
        public static List<int> Stacks(int total, int stackLimit)
        {
            var stacks = new List<int>();
            int limit = Math.Max(1, stackLimit);
            for (int left = total; left > 0; left -= limit) stacks.Add(Math.Min(left, limit));
            return stacks;
        }

        /// <summary>Stacks the caller must place itself once the process has placed the plan's first one. A cycle that placed nothing owes
        /// nothing yet: PipeSystem retries it, and paying the rest now would pay it again on the retry.</summary>
        public static int ExtrasOwed(int planned, int placedByProcess)
        {
            return placedByProcess > 0 ? Math.Max(0, planned - 1) : 0;
        }

        /// <summary>The plan may be forgotten: everything is paid, or the item yielded nothing and the process has reset.</summary>
        public static bool CycleOver(int planned, int placedByProcess)
        {
            return planned == 0 || placedByProcess > 0;
        }

        /// <summary>Cremation pays only for a corpse, and only with the player's toggle on.</summary>
        public static bool CremationPays(bool cremateWithoutStripping, bool ingredientIsCorpse)
        {
            return cremateWithoutStripping && ingredientIsCorpse;
        }
    }
}
