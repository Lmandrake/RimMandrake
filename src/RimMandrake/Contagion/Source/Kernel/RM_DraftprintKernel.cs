// Verse-free kernel of the Draftprints, the Helix contract and the amoeba gestation batch (CompDraftprint,
// DraftprintUtility, QuestPart_RM_DraftprintContract, AmoebaHostUtility, the Unfinished spawner / randomiser).
// The classes call these with the same expressions; SelfTest/ContagionFuzz.cs compiles this file alone, so it must stay
// free of Verse/RimWorld/UnityEngine.
using System;
using System.Collections.Generic;

namespace RimMandrake.Contagion
{
    public enum GestationPlan { OneLimb = 0, OrganBatch = 1 }

    public static class RM_DraftprintKernel
    {
        // ---- sampling ----------------------------------------------------------------------------
        public static bool CanBeSampled(bool hasComp, bool alreadyTaken, bool spawned, bool dead) { return hasComp && !alreadyTaken && spawned && !dead; }

        public static bool MaybeProvokes(bool downed, bool inMentalState, float provokeChance, Func<float> roll)
        {
            if (downed || inMentalState) return false;
            if (provokeChance <= 0f) return false;
            if (provokeChance >= 1f) return true;
            return roll() < provokeChance;
        }

        // The stat furthest from its kind's base, as a log ratio (absolute difference when the base is ~0). -1 = none.
        public static int ExtremeStat(IList<float> baseValues, IList<float> values)
        {
            int best = -1; float bestScore = 0f;
            for (int i = 0; i < baseValues.Count; i++)
            {
                float baseV = baseValues[i], v = values[i];
                float score = baseV > 0.001f ? (float)Math.Abs(Math.Log(Math.Max(v, 0.001f) / baseV)) : Math.Abs(v - baseV);
                if (score > bestScore) { best = i; bestScore = score; }
            }
            return best;
        }

        // The worst-working rolled limb (lowest efficiency; first wins a tie). -1 = none.
        public static int WorstLimb(IList<bool> isRolledLimb, IList<float> efficiency)
        {
            int worst = -1;
            for (int i = 0; i < isRolledLimb.Count; i++)
            {
                if (!isRolledLimb[i]) continue;
                float eff = efficiency[i];
                float worstEff = worst < 0 ? 1f : efficiency[worst];
                if (worst < 0 || eff < worstEff) worst = i;
            }
            return worst;
        }
        public static bool IsAbandonedAttempt(float efficiency) { return efficiency <= 0.3f; }

        // ---- value and contract ----------------------------------------------------------------
        // A richer print is worth more to any trader; a monstrous one multiplies. An unrecorded print is neutral (1).
        public static float MarketFactor(bool recorded, int limbCount, float valuePerLimb, float baseMarketValue, bool monstrous, float monstrousValueFactor)
        {
            if (!recorded) return 1f;
            float v = 1f + limbCount * valuePerLimb / Math.Max(1f, baseMarketValue);
            return monstrous ? v * monstrousValueFactor : v;
        }

        // Does a recorded print carry everything the contract wants? requiredLimbs entries < 0 are dead defs and are ignored.
        public static bool Matches(bool recorded, bool requireMonstrous, bool printMonstrous, IList<int> requiredLimbs, ICollection<int> printLimbs)
        {
            if (!recorded) return false;
            if (requireMonstrous && !printMonstrous) return false;
            foreach (int d in requiredLimbs)
            {
                if (d >= 0 && !printLimbs.Contains(d)) return false;
            }
            return true;
        }

        public static int Reward(int silverPerFeature, int limbCount, bool requireMonstrous, float monstrousRewardFactor, float settingFactor)
        {
            int per = silverPerFeature > 0 ? silverPerFeature : 120;
            float reward = per * (limbCount + (requireMonstrous ? 1 : 0));
            if (requireMonstrous) reward *= monstrousRewardFactor > 0f ? monstrousRewardFactor : 2f;
            return Math.Max(1, (int)Math.Round(reward * settingFactor));
        }

        public static int FeatureCount(int limbCountRangeRoll, int poolCount) { return Math.Min(Math.Max(limbCountRangeRoll, 1), poolCount); }

        // ---- the amoeba gestation ---------------------------------------------------------------
        public static bool GestationDone(float severity, float maxSeverity) { return severity >= maxSeverity - 0.001f; }

        // A monstrous sample (with grown limbs on and a non-empty limb pool) grows one limb; anything else, the organ batch.
        public static GestationPlan Plan(bool monstrous, bool grownLimbsEnabled, int limbPoolCount)
        {
            return monstrous && grownLimbsEnabled && limbPoolCount > 0 ? GestationPlan.OneLimb : GestationPlan.OrganBatch;
        }

        public static int BatchSize(int rolled, int organPoolCount) { return organPoolCount > 0 ? rolled : 0; }

        // ---- the Unfinished ---------------------------------------------------------------------
        public static bool SpawnDue(int now, int nextSpawnTick) { return now >= nextSpawnTick; }
        public static bool NearbyAllows(int nearby, int maxNearby) { return nearby < maxNearby; }
        public static int NextSpawn(int now, float intervalDays) { return now + (int)(intervalDays * 60000f); }
        public static int LimbCount(int rolled, int leafParts, int poolSize) { return Math.Min(rolled, Math.Min(leafParts, poolSize)); }
    }
}
