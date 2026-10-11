// KHORRAK_STEEL_DIET_TIER_1 (owner, by question card 2026-10-05: "MOVE IT OVER"): the steel diet's pure decision kernel,
// moved here from the SWBestiary BeastMechanics assembly (was RSW_EatKernel) so the RM-tier khorrak can carry it.
// Numbers and rules unchanged. Exercised by SelfTestFuzz/MetalEaterFuzz.cs (family "eat").
using System;

namespace RimMandrake.CreatureBehaviors
{
    /// <summary>The metal eater's diet (RM_CompMetalEater). Pure: no Verse, no RimWorld, no UnityEngine, so the fuzz build compiles it.</summary>
    public static class RM_MetalEaterKernel
    {
        public const float EatPriorityValue = 9.5f;
        public const int MinStackLeft = 10;

        public struct Bite { public bool Destroy; public int HitPoints; public int StackCount; }

        /// <summary>What one bite does to the eaten thing. Fully-destroy eats it whole; a thing with hit points loses that fraction of its
        /// maximum (at least one point, so a tiny item cannot be eaten forever) and dies at zero; anything else loses that fraction of a
        /// full stack (at least one) and is gone once fewer than ten remain.</summary>
        public static Bite Chew(bool fullyDestroy, bool useHitPoints, bool ignoreUseHitPoints, float percentageOfDestruction, int maxHitPoints, int hitPoints, int stackLimit, int stackCount)
        {
            Bite b = new Bite { HitPoints = hitPoints, StackCount = stackCount };
            if (fullyDestroy) { b.Destroy = true; return b; }
            if (useHitPoints && !ignoreUseHitPoints)
            {
                b.HitPoints -= Math.Max(1, (int)Math.Round(maxHitPoints * percentageOfDestruction));
                if (b.HitPoints <= 0) b.Destroy = true;
                return b;
            }
            int bite = Math.Max(1, (int)Math.Round(percentageOfDestruction * stackLimit));
            b.StackCount -= bite;
            if (b.StackCount < MinStackLeft) b.Destroy = true;
            return b;
        }

        /// <summary>Hungry enough to look for metal: below the race's want-to-eat fraction.</summary>
        public static bool Hungry(float foodPct, float wantEatPct) { return foodPct < wantEatPct; }

        /// <summary>Think-node priority: the mechanic is on, the animal has a food need and the eater comp, and it is hungry.</summary>
        public static float Priority(bool enabled, bool hasFoodNeed, bool hasEaterComp, float foodPct, float wantEatPct)
        {
            if (!enabled || !hasFoodNeed || !hasEaterComp) return 0f;
            return Hungry(foodPct, wantEatPct) ? EatPriorityValue : 0f;
        }

        /// <summary>Digging up the diet: only with nothing to eat on the map, the dig configured, a very hungry and awake animal.</summary>
        public static bool DigDue(bool digEnabled, bool namesThing, float foodPct, float hungryPct, bool awake) { return digEnabled && namesThing && foodPct < hungryPct && awake; }

        /// <summary>The prefix that stops an eater seeking ordinary food.</summary>
        public static bool BlocksNormalFood(bool enabled, bool hasEaterComp, bool blockFlag) { return enabled && hasEaterComp && blockFlag; }
    }
}
