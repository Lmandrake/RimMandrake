using System;
using System.Collections.Generic;

namespace RimMandrake.DivingInteraction
{
    /// <summary>A per-world-tile novelty record (what RM_ElderTileRecord is). Lets the kernel stay free of Verse types.</summary>
    public interface IElderTileRecord
    {
        int Tile { get; }
        List<string> SeenKeys { get; }
    }

    /// <summary>
    /// The Brine Elder novelty economy's bookkeeping and payout arithmetic, with no Verse or UnityEngine type in it so the
    /// offline fuzz (Source/SelfTest/DivingFuzz.cs, `python3 src/RimMandrake/Utils/selftest_divinginteraction_fuzz.py`)
    /// compiles THIS file and drives the code the game runs. RM_GameComponent_BrineElders and RM_ElderTradeUtility call it;
    /// nothing here is a copy. A `using Verse;` landing in this file breaks the selftest build.
    /// </summary>
    public static class RM_ElderEconomyKernel
    {
        public const float NovelValueMultiplier = 8f;
        public const int NovelValueFloor = 50;
        public const float StaleValueMultiplier = 0.05f;
        public const int StaleValueFloor = 1;

        /// <summary>Largest silver a single offer pays. Without it a huge stack overflows the float-to-int cast, which yields int.MinValue and pays the FLOOR instead of a fortune.</summary>
        public const int MaxSilver = 1000000;

        public static T FindRecord<T>(List<T> records, int tile) where T : class, IElderTileRecord
        {
            for (int i = 0; i < records.Count; i++)
            {
                if (records[i] != null && records[i].Tile == tile)
                {
                    return records[i];
                }
            }
            return null;
        }

        public static bool HasSeen<T>(List<T> records, int tile, string key) where T : class, IElderTileRecord
        {
            T rec = FindRecord(records, tile);
            return rec != null && rec.SeenKeys.Contains(key);
        }

        public static void MarkSeen<T>(List<T> records, int tile, string key, Func<int, T> make) where T : class, IElderTileRecord
        {
            T rec = FindRecord(records, tile);
            if (rec == null)
            {
                rec = make(tile);
                records.Add(rec);
            }
            if (!rec.SeenKeys.Contains(key))
            {
                rec.SeenKeys.Add(key);
            }
        }

        public static bool TryClaim(List<string> granted, string defName)
        {
            if (granted.Contains(defName))
            {
                return false;
            }
            granted.Add(defName);
            return true;
        }

        /// <summary>
        /// Claims one still-ungranted treasure from <paramref name="pool"/> and returns its defName, or null when none is left.
        /// Only treasures whose def actually resolves are candidates: a claim on a def that cannot be made would burn the
        /// world's only copy and pay nothing (a Utinni-patch-added name with its mod absent).
        /// <paramref name="pick"/> maps a candidate count to an index in [0,count).
        /// </summary>
        public static string ChooseTreasure(IList<string> pool, List<string> granted, Func<string, bool> resolvable, Func<int, int> pick)
        {
            var candidates = new List<string>();
            for (int i = 0; i < pool.Count; i++)
            {
                if (!granted.Contains(pool[i]) && resolvable(pool[i]))
                {
                    candidates.Add(pool[i]);
                }
            }
            if (candidates.Count == 0)
            {
                return null;
            }
            string chosen = candidates[pick(candidates.Count)];
            return TryClaim(granted, chosen) ? chosen : null;
        }

        // SPECIMEN_CABINET_DISPLAY_1 (DI-7): the home display counts DISTINCT novelty keys, the same keys the Elder trades on.
        // PROVISIONAL numbers.
        public const float CabinetBeautyPerKind = 2f;
        public const float CabinetBeautyCap = 40f;
        public static readonly int[] MuseumMoodThresholds = { 1, 4, 10 };

        /// <summary>How many different kinds are on display (empty/null keys ignored; the same key counted once).</summary>
        public static int DistinctKinds(IEnumerable<string> keys)
        {
            if (keys == null) return 0;
            var seen = new HashSet<string>();
            foreach (string k in keys) if (!string.IsNullOrEmpty(k)) seen.Add(k);
            return seen.Count;
        }

        /// <summary>Beauty a cabinet adds for its kinds; never negative, capped.</summary>
        public static float CabinetBeauty(int kinds) => kinds <= 0 ? 0f : System.Math.Min(CabinetBeautyCap, kinds * CabinetBeautyPerKind);

        /// <summary>Museum thought stage for the colony's kinds on display: -1 none, else 0..2 by threshold.</summary>
        public static int MuseumMoodStage(int kinds)
        {
            int stage = -1;
            for (int i = 0; i < MuseumMoodThresholds.Length; i++) if (kinds >= MuseumMoodThresholds[i]) stage = i;
            return stage;
        }

        public struct Decision
        {
            public bool Novel;
            /// <summary>defName of the unique treasure claimed, or null.</summary>
            public string Treasure;
            /// <summary>Silver to pay; 0 whenever a treasure is paid instead.</summary>
            public int Silver;
        }

        /// <summary>
        /// One offer, end to end: is this (tile, key) novel, mark it seen, maybe claim a unique treasure, and the silver due.
        /// <paramref name="tracked"/> is false when the map has no world tile (nothing is novel then, nothing is recorded).
        /// </summary>
        public static Decision Decide<T>(List<T> records, List<string> granted, Func<int, T> make, int tile, string key, bool tracked,
            float marketValue, int stackCount, IList<string> pool, Func<string, bool> resolvable, Func<bool> rollTreasure, Func<int, int> pick)
            where T : class, IElderTileRecord
        {
            var d = new Decision();
            d.Novel = tracked && !HasSeen(records, tile, key);
            if (d.Novel)
            {
                MarkSeen(records, tile, key, make);
                if (rollTreasure())
                {
                    d.Treasure = ChooseTreasure(pool, granted, resolvable, pick);
                }
            }
            d.Silver = d.Treasure != null ? 0 : SilverFor(d.Novel, marketValue, stackCount);
            return d;
        }

        /// <summary>Silver for a plain (non-treasure) trade: a novel kind is worth a great deal, a seen one nearly nothing.</summary>
        public static int SilverFor(bool novel, float marketValue, int stackCount)
        {
            float value = marketValue * stackCount;
            if (float.IsNaN(value) || value < 0f)
            {
                value = 0f;   // invalid data earns the floor, never the cap (NaN used to fall into MaxSilver)
            }
            float scaled = value * (novel ? NovelValueMultiplier : StaleValueMultiplier);
            int rounded = !(scaled < MaxSilver) ? MaxSilver : (int)Math.Round(scaled);   // also catches NaN
            return Math.Max(novel ? NovelValueFloor : StaleValueFloor, rounded);
        }
    }
}
