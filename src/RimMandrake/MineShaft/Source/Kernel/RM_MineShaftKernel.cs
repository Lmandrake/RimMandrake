// Verse-free decisions for the Mine Shaft (mandrake.rm.mineshaft). The mod and the offline fuzz (../SelfTest) compile this same
// file; a `using Verse;` here breaks the fuzz build, which is the guard rail.
using System;
using System.Collections.Generic;

namespace RimMandrake.MineShaft
{
    public static class RM_MineShaftKernel
    {
        public const string RecipePrefix = "RM_MineShaft_";
        public const float WorkTicksPerUnit = 60f;   // one "unit" per 80 rock hit points, as Mines 2.0 measured it
        public const float MinWorkTicks = 60f;
        public const int MaxYieldPerBill = 5000;
        public const float MinMultiplier = 0.25f, MaxMultiplier = 4f;

        public static string RecipeDefName(string rockDefName) { return RecipePrefix + rockDefName; }

        public static bool IsShaftRecipe(string recipeDefName)
        {
            return recipeDefName != null && recipeDefName.StartsWith(RecipePrefix, StringComparison.Ordinal);
        }

        /// <summary>Which rocks give a bill: mineable, with a product, and a resource rock; natural stone only when stone bills are on.</summary>
        public static bool IsEligibleSource(bool mineable, bool hasProduct, bool isResourceRock, bool isNaturalRock, bool stoneBills)
        {
            if (!mineable || !hasProduct) return false;
            return isResourceRock || (stoneBills && isNaturalRock);
        }

        public static bool IsBanned(string productDefName, ICollection<string> banned)
        {
            return productDefName != null && banned != null && banned.Contains(productDefName);
        }

        public static float ClampMultiplier(float m)
        {
            if (float.IsNaN(m) || float.IsInfinity(m)) return 1f;
            return m < MinMultiplier ? MinMultiplier : (m > MaxMultiplier ? MaxMultiplier : m);
        }

        /// <summary>Work in ticks: tougher rock takes longer (ceil(hp/80) units of 60 ticks), scaled by the work multiplier.</summary>
        public static float WorkTicks(int rockMaxHitPoints, float workMultiplier)
        {
            float units = (float)Math.Max(1.0, Math.Ceiling(Math.Max(0, rockMaxHitPoints) / 80.0));
            float t = units * WorkTicksPerUnit * ClampMultiplier(workMultiplier);
            return t < MinWorkTicks ? MinWorkTicks : t;
        }

        /// <summary>A product that only exists singly (stack limit 1: chunks, slag) is always exactly 1 and ignores every multiplier.</summary>
        public static bool YieldFixedAtOne(int productStackLimit) { return productStackLimit <= 1; }

        public static int Yield(int productStackLimit, int rockMineableYield, float yieldMultiplier)
        {
            if (YieldFixedAtOne(productStackLimit)) return 1;
            double raw = Math.Round(Math.Max(1, rockMineableYield) * (double)ClampMultiplier(yieldMultiplier), MidpointRounding.AwayFromZero);
            // clamp in double first: a huge yield times the multiplier overflows an int cast
            if (raw > MaxYieldPerBill) return MaxYieldPerBill;
            return raw < 1 ? 1 : (int)raw;
        }

        /// <summary>Sort key when several rocks yield one product (one bill per product): real ore before stone, rocks that scatter on
        /// maps before event-only ones, the commoner rock, the weaker rock, then defName so the result never depends on mod order.</summary>
        public static int CompareSources(bool aResource, float aCommonality, int aHp, string aName,
                                         bool bResource, float bCommonality, int bHp, string bName)
        {
            int c = (aResource ? 0 : 1).CompareTo(bResource ? 0 : 1);
            if (c != 0) return c;
            c = (aCommonality > 0f ? 0 : 1).CompareTo(bCommonality > 0f ? 0 : 1);
            if (c != 0) return c;
            c = bCommonality.CompareTo(aCommonality);
            if (c != 0) return c;
            c = aHp.CompareTo(bHp);
            if (c != 0) return c;
            return string.CompareOrdinal(aName, bName);
        }

        /// <summary>Is a bill offered on this map? With the vein rule off, always. With it on, only when the map holds the source rock
        /// (still standing) or a deep deposit of the product.</summary>
        public static bool OfferedOnMap(bool veinRuleOn, bool mapHasSourceRock, bool mapHasDeepDeposit)
        {
            return !veinRuleOn || mapHasSourceRock || mapHasDeepDeposit;
        }
    }
}
