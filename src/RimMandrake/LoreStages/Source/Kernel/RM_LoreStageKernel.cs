// Verse-free kernel of the staged lore text: which rung of a ladder is showing at a stage, how a stage is clamped and gated by the
// master toggle, and what is wrong with a ladder's rungs (the rules RM_LoreStageTableDef.ConfigErrors reports). The applier, the game
// component and the def call these with the same expressions; SelfTest/LoreStagesFuzz.cs drives the REAL applier on real engine defs and
// also compiles this file. Keep it free of Verse/RimWorld/UnityEngine.
using System.Collections.Generic;

namespace RimMandrake.LoreStages
{
    public enum RungProblem { Duplicate, Negative, AboveMax, NoText }

    public static class RM_LoreStageKernel
    {
        /// <summary>
        /// Index of the rung a ladder shows at <paramref name="stage"/>: the highest rung at or below the stage that has text; among rungs
        /// sharing a stage the FIRST listed wins (ConfigErrors reports the duplicate). -1 when no rung applies - the field keeps its shipped
        /// (or another ladder's) text. Rungs may be listed in any order.
        /// </summary>
        public static int ChooseRung(IList<int> rungStages, IList<bool> hasText, int stage)
        {
            int best = -1;
            int bestStage = int.MinValue;
            for (int i = 0; i < rungStages.Count; i++)
            {
                if (!hasText[i]) continue;
                if (rungStages[i] <= stage && rungStages[i] > bestStage)
                {
                    bestStage = rungStages[i];
                    best = i;
                }
            }
            return best;
        }

        /// <summary>SetStage's clamp: never below 0, never above a positive maxStage (0 means no clamp).</summary>
        public static int ClampStage(int stage, int maxStage)
        {
            if (maxStage > 0 && stage > maxStage) stage = maxStage;
            if (stage < 0) stage = 0;
            return stage;
        }

        /// <summary>The master toggle: off means every ladder reads as stage 0 without touching the stored progress.</summary>
        public static int EffectiveStage(bool stagedTextEnabled, int storedStage)
        {
            return stagedTextEnabled ? storedStage : 0;
        }

        /// <summary>The key a ladder's stage is saved under: the explicit ladderId, else the def's name.</summary>
        public static string LadderKey(string ladderId, string defName)
        {
            return string.IsNullOrEmpty(ladderId) ? defName : ladderId;
        }

        /// <summary>
        /// What is wrong with one target's rungs, as (rung index, problem) pairs in rung order: a stage seen before (the earlier rung wins by
        /// list order, i.e. load order, which is undefined), a negative stage, a stage above a positive maxStage (unreachable), a rung with no text.
        /// </summary>
        public static List<KeyValuePair<int, RungProblem>> RungProblems(IList<int> rungStages, IList<bool> hasText, int maxStage)
        {
            var found = new List<KeyValuePair<int, RungProblem>>();
            var seen = new HashSet<int>();
            for (int i = 0; i < rungStages.Count; i++)
            {
                if (!seen.Add(rungStages[i])) found.Add(new KeyValuePair<int, RungProblem>(i, RungProblem.Duplicate));
                if (rungStages[i] < 0) found.Add(new KeyValuePair<int, RungProblem>(i, RungProblem.Negative));
                if (maxStage > 0 && rungStages[i] > maxStage) found.Add(new KeyValuePair<int, RungProblem>(i, RungProblem.AboveMax));
                if (!hasText[i]) found.Add(new KeyValuePair<int, RungProblem>(i, RungProblem.NoText));
            }
            return found;
        }
    }
}
