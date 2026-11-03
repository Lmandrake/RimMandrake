// Verse-free kernel of the lure stake's prey-quality gate (FEVERWOOD_TWO_FRONT_LURE_TUNING_1 spec 1;
// fever_wood_deep_and_mud_2026-09-23.md §6l: "Either the lure must care about the quality of the prey, or the cheap
// route needs its own cost"). Quality is the bait's worth as prey: its race's base market value times its life
// stage's market-value factor (a calf is worth less than a cow), never its current health - every bait is wounded
// and chained by design, and that must not count against it. Bait under the floor draws nothing (a rat or a chicken
// is not worth a raid); above it the draw grows with worth up to full at fullValue, and the hourly raid MTB is divided
// by the draw. Delegated design call 2026-11-03 (not on delegation_policy §2), numbers INVENTED: floor 150 silver
// shuts out every vanilla animal cheaper than a capybara, fullValue 500 gives a prisoner (1750) or a horse the full
// draw and a muffalo (300) 0.6 of it. SelfTest/FeverWoodFuzz.cs compiles this file alone: keep it free of Verse.
using System;

namespace RimMandrake.FeverWood
{
    public static class RM_LureKernel
    {
        public const float MinDraw = 0.05f; // a draw this small would make the MTB 20x the base: treat as no draw

        /// <summary>The bait's worth as prey, in silver.</summary>
        public static float BaitValue(float raceBaseMarketValue, float lifeStageMarketValueFactor)
        {
            if (float.IsNaN(raceBaseMarketValue) || raceBaseMarketValue < 0f) raceBaseMarketValue = 0f;
            if (float.IsNaN(lifeStageMarketValueFactor) || lifeStageMarketValueFactor < 0f) lifeStageMarketValueFactor = 0f;
            return raceBaseMarketValue * lifeStageMarketValueFactor;
        }

        /// <summary>0 = this bait draws no raid; 1 = full draw. Gate off = always 1.</summary>
        public static float Draw(bool gateOn, float baitValue, float floorValue, float fullValue)
        {
            if (!gateOn) return 1f;
            if (float.IsNaN(baitValue)) return 0f;
            floorValue = Math.Max(0f, floorValue);
            fullValue = Math.Max(fullValue, floorValue);
            if (baitValue < floorValue) return 0f;
            if (fullValue <= 0f) return 1f;
            float d = baitValue / fullValue;
            if (d > 1f) d = 1f;
            return d < MinDraw ? MinDraw : d;
        }

        /// <summary>The hourly first-wave MTB in days for this bait; +infinity when it draws nothing.</summary>
        public static float EffectiveMtbDays(float baseMtbHours, float draw)
        {
            float baseDays = Math.Max(0.05f, baseMtbHours / 24f);
            if (!(draw > 0f)) return float.PositiveInfinity;
            return baseDays / Math.Min(1f, draw);
        }

        /// <summary>Several baited stakes: the map rolls once an hour on the BEST bait's draw (two chickens are not
        /// a muffalo).</summary>
        public static float BestDraw(float[] draws)
        {
            float best = 0f;
            if (draws == null) return 0f;
            foreach (float d in draws) if (d > best) best = d;
            return best;
        }
    }
}
