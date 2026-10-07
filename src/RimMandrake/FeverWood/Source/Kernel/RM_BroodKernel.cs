// Verse-free kernel of the brood ransom (FEVERWOOD_BROOD_RANSOM_1): the world's tally of the deep's young, the
// boldness multiplier and its letter hysteresis, the emergence chance, the ambient limb table and the gift roll, and
// the young-cask trader gates. RM_BroodRansom.cs and RM_MapComponent_TentacleWatch.cs call these with the same
// expressions; SelfTest/FeverWoodFuzz.cs compiles this file alone, so it must stay free of Verse/RimWorld/UnityEngine.
// (Math.Min/Max/Round here match Mathf.Min/Max/RoundToInt for every non-NaN input; no setting can be NaN.)
using System;
using System.Collections.Generic;

namespace RimMandrake.FeverWood
{
    public static class RM_BroodKernel
    {
        public const int RecomputeIntervalTicks = 15000; // 6 in-game hours
        public const int AmbientCheckIntervalTicks = 2500; // 1 in-game hour
        public const float TicksPerHour = 2500f;

        // INVENTED thresholds: the letter the player gets as the tally rises.
        public static readonly int[] Thresholds = { 1, 3, 6, 10 };

        // ---- the tally -------------------------------------------------------------------------------
        // RM_DeepYoungKeeperExtension.YoungFor: a null settlement keeps none; a non-empty name filter that does not
        // list this settlement keeps none; otherwise youngPerSettlement, never negative.
        public static int KeeperYoung(bool settlementExists, int youngPerSettlement, bool hasNameFilter, bool nameListed)
        {
            if (!settlementExists) return 0;
            if (hasNameFilter && !nameListed) return 0;
            return Math.Max(0, youngPerSettlement);
        }

        // Override wins over the faction's extension; no extension keeps none.
        public static int SettlementYoung(bool hasOverride, int overrideYoung, bool hasExtension, int extensionYoung)
        {
            if (hasOverride) return overrideYoung;
            return hasExtension ? extensionYoung : 0;
        }

        public static int OverrideFor(int count) { return Math.Max(0, count); }

        // Occupied tanks on player home maps + casks on player home maps + casks in player caravans + every settlement.
        public static int Tally(int occupiedTanks, int casksOnMaps, int casksInCaravans, long settlementYoung)
        {
            long n = (long)occupiedTanks + casksOnMaps + casksInCaravans + settlementYoung;
            return n > int.MaxValue ? int.MaxValue : n < 0 ? 0 : (int)n;
        }

        // Notify_DisplayTankFreed: a settlement's display tank counts once; the first time, the town keeps one fewer.
        public static bool FreedTankLowersYoung(bool alreadyFreed) { return !alreadyFreed; }
        public static int YoungAfterFreedTank(int currentYoung) { return Math.Max(0, currentYoung - 1); }

        // ---- boldness --------------------------------------------------------------------------------
        // 1 when the brood ransom is off; otherwise min(cap, 1 + perYoung * tally), cap never below 1, slope never negative.
        public static float Boldness(bool enabled, float perYoung, float cap, int tally)
        {
            if (!enabled) return 1f;
            float c = Math.Max(1f, cap);
            return Math.Min(c, 1f + Math.Max(0f, perYoung) * tally);
        }

        public static float EffectiveAmbientMtbHours(float settingMtbHours, float boldness)
        {
            return Math.Max(0.1f, settingMtbHours) / Math.Max(1f, boldness);
        }

        // Per-check chance Rand.MTBEventOccurs is asked for: checkDuration / (mtb * mtbUnit), capped at 1.
        public static float EmergenceChancePerCheck(float effectiveMtbHours)
        {
            return Math.Min(1f, AmbientCheckIntervalTicks / (effectiveMtbHours * TicksPerHour));
        }

        // 0 quiet, 1 uneasy, 2 restless, 3 bold, 4 savage.
        public static int MoodIndex(int tally)
        {
            return tally == 0 ? 0 : tally < Thresholds[1] ? 1 : tally < Thresholds[2] ? 2 : tally < Thresholds[3] ? 3 : 4;
        }

        // ---- the letter ------------------------------------------------------------------------------
        // Steps the announced level down (quietly) while the tally is below the threshold the level stands for, then up
        // while the tally clears the next. Returns true exactly when the level rose (a letter is owed).
        public static bool AnnounceStep(bool enabled, ref int announcedLevel, int tally)
        {
            if (!enabled) return false;
            while (announcedLevel > 0 && tally < Thresholds[announcedLevel - 1])
            {
                announcedLevel--;
            }
            int reached = announcedLevel;
            while (reached < Thresholds.Length && tally >= Thresholds[reached])
            {
                reached++;
            }
            if (reached <= announcedLevel) return false;
            announcedLevel = reached;
            return true;
        }

        // ---- the ambient limb table ------------------------------------------------------------------
        // The snare and lash weigh more the more young the world holds.
        public static float AmbientWeight(bool grows, float weight, float boldness) { return grows ? weight * boldness : weight; }

        // Weighted pick over the table with some rows skipped; roll is uniform in [0, total). -1 when nothing can be picked.
        // A row of zero weight is never picked (the old loop picked one when the roll landed on exactly 0).
        public static int PickLimb(float[] weights, bool[] skipped, float roll)
        {
            float total = 0f;
            for (int i = 0; i < weights.Length; i++)
            {
                if (skipped != null && skipped[i]) continue;
                total += weights[i];
            }
            if (total <= 0f) return -1;
            float r = roll;
            int last = -1;
            for (int i = 0; i < weights.Length; i++)
            {
                if (skipped != null && skipped[i]) continue;
                if (weights[i] <= 0f) continue;
                last = i;
                r -= weights[i];
                if (r <= 0f) return i;
            }
            return last;
        }

        // ---- the deep's gift -------------------------------------------------------------------------
        public static float GiftWeight(float weight, bool hasMultiplier, float multiplier)
        {
            return Math.Max(0f, weight * (hasMultiplier ? multiplier : 1f));
        }

        // RandomElementByWeight over the candidate indices (u in [0,1)); the last candidate absorbs rounding.
        public static int PickByWeight(IList<float> weights, IList<int> candidates, float u)
        {
            if (candidates.Count == 0) return -1;
            double sum = 0;
            for (int i = 0; i < candidates.Count; i++) sum += weights[candidates[i]];
            double r = u * sum;
            for (int i = 0; i < candidates.Count; i++)
            {
                r -= weights[candidates[i]];
                if (r < 0) return candidates[i];
            }
            return candidates[candidates.Count - 1];
        }

        // RollAndPlace: candidates are the rows with a positive weight; a row that finds no footprint drops out and the
        // roll is retried. Returns the placed row, or -1 when none could be placed. rolls() yields uniform [0,1).
        public static int RollGift(IList<float> weights, Func<int, bool> tryPlace, Func<float> rolls)
        {
            var candidates = new List<int>();
            for (int i = 0; i < weights.Count; i++)
            {
                if (weights[i] > 0f) candidates.Add(i);
            }
            while (candidates.Count > 0)
            {
                int e = PickByWeight(weights, candidates, rolls());
                if (tryPlace(e)) return e;
                candidates.Remove(e);
            }
            return -1;
        }

        // ---- the young-cask trader -------------------------------------------------------------------
        public static float StockChance(float fixedChance, float settingChance)
        {
            float c = fixedChance >= 0f ? fixedChance : settingChance;
            return c < 0f ? 0f : c > 1f ? 1f : c;
        }

        // Empty onlyFactions: any trader. Otherwise only a listed faction's trader.
        public static bool StocksFor(int onlyFactionCount, bool factionKnown, bool factionListed)
        {
            if (onlyFactionCount == 0) return true;
            return factionKnown && factionListed;
        }

        public static bool StocksCask(bool ransomOn, bool stocksFor) { return ransomOn && stocksFor; }

        // ---- the display tank ------------------------------------------------------------------------
        public static bool DisplayTankApplies(bool hasSettlement, bool hasFaction, bool factionMatches, bool nameFilterEmpty, bool nameMatches)
        {
            if (!hasSettlement || !hasFaction || !factionMatches) return false;
            return nameFilterEmpty || nameMatches;
        }

        public static bool PlaceDisplayTank(bool ransomOn, bool tankOn, bool hasTankDef, bool applies, bool alreadyFreed)
        {
            return ransomOn && tankOn && hasTankDef && applies && !alreadyFreed;
        }

        // ---- the pending-gift queue (three parallel lists, scribed separately) -----------------------
        // Removes and returns the due entries, scanning from the end exactly as the tick does.
        public static List<KeyValuePair<T, int>> CollectDue<T>(List<int> ticks, List<T> cells, List<int> rolls, int now)
        {
            var due = new List<KeyValuePair<T, int>>();
            for (int i = ticks.Count - 1; i >= 0; i--)
            {
                if (now < ticks[i]) continue;
                T cell = cells[i];
                int r = i < rolls.Count ? rolls[i] : 1;
                ticks.RemoveAt(i);
                cells.RemoveAt(i);
                if (i < rolls.Count) rolls.RemoveAt(i);
                due.Add(new KeyValuePair<T, int>(cell, r));
            }
            return due;
        }

        // After load: mismatched tick/cell lists are dropped together; mismatched rolls fall back to one roll each.
        public static void RepairQueues<T>(ref List<int> ticks, ref List<T> cells, ref List<int> rolls)
        {
            if (ticks == null || cells == null || ticks.Count != cells.Count)
            {
                ticks = new List<int>();
                cells = new List<T>();
            }
            if (rolls == null || rolls.Count != ticks.Count)
            {
                rolls = new List<int>();
                for (int i = 0; i < ticks.Count; i++) rolls.Add(1);
            }
        }
    }
}
