// Verse-free kernel of Wreckage: the loot-tier ladder and how a weathering folds into a wreck, the deconstruct yield fraction, the skill-scaled
// rare roll chance, the loot stack generosity, the salvager's hazard dose, the per-field on/off list, the wreck-field count and the placement loop
// (anchors, clusters, three misses and stop). RM_WreckWeathering, RM_CompSalvageLoot, RM_WreckageSettings and RM_GenStep_WreckField call these
// with the same expressions; SelfTest/WreckageFuzz.cs compiles this file alone. Keep it free of Verse/RimWorld/UnityEngine/HarmonyLib
// (a `using Verse;` here breaks the self-test build, which is the guard rail).
using System;
using System.Collections.Generic;
using System.Linq;

namespace RimMandrake.Wreckage
{
    public struct LootFold
    {
        public string tier;
        public float rareChance;
        public bool noLoot;
    }

    public static class RM_WreckageKernel
    {
        public const int MaxMisses = 3;
        public static readonly string[] MidTiers = { "Hull", "Tank", "Carapace" };
        // PROVISIONAL (design 3c): the skill factor runs 0.25x at level 0 to 2x at level 20.
        public const float SkillFactorAtZero = 0.25f, SkillFactorAtMax = 2f;
        public const int MaxSkill = 20;

        /// <summary>The ladder Scrap(0) &lt; Hull/Tank/Carapace(1) &lt; Sealed(2). A mid tier shifted up becomes Sealed, down becomes Scrap;
        /// Scrap shifted up to the middle becomes Hull; Sealed shifted down to the middle becomes Hull. A shift that stays on the same rung
        /// keeps the tier's own name.</summary>
        public static string ShiftTier(string tier, int shift)
        {
            int rank = Rank(tier);
            int to = Math.Max(0, Math.Min(2, rank + shift));
            if (to == rank) return tier;
            if (to == 0) return "Scrap";
            if (to == 2) return "Sealed";
            return "Hull";
        }

        public static int Rank(string tier)
        {
            return tier == "Scrap" ? 0 : tier == "Sealed" ? 2 : 1;
        }

        /// <summary>How a weathering folds into one wreck's loot comp: "nothing inside" first, then the tier shift (landing on Scrap removes the rare roll).</summary>
        public static LootFold Fold(string tier, float rareChance, bool noLoot, bool weatheringNoLoot, int totalShift)
        {
            var f = new LootFold { tier = tier, rareChance = rareChance, noLoot = noLoot };
            if (weatheringNoLoot) { f.noLoot = true; f.rareChance = 0f; }
            if (totalShift != 0)
            {
                f.tier = ShiftTier(f.tier, totalShift);
                if (f.tier == "Scrap") f.rareChance = 0f;
            }
            return f;
        }

        /// <summary>Deconstruct yield fraction after a weathering: the family fraction times the factor, never past everything.</summary>
        public static float YieldFraction(float familyFraction, float yieldFactor)
        {
            float v = familyFraction * yieldFactor;
            return v < 0f ? 0f : v > 1f ? 1f : v;
        }

        /// <summary>Chance of the rare roll: base x skill factor (0.25..2 across Construction 0..20), held to 0..1.</summary>
        public static float RareChance(float baseChance, bool skillScales, bool hasSkills, int level)
        {
            float factor = 1f;
            if (skillScales && hasSkills)
            {
                float t = level / (float)MaxSkill;
                t = t < 0f ? 0f : t > 1f ? 1f : t;
                factor = SkillFactorAtZero + (SkillFactorAtMax - SkillFactorAtZero) * t;
            }
            float c = baseChance * factor;
            return c < 0f ? 0f : c > 1f ? 1f : c;
        }

        /// <summary>A loot stack after the player's generosity slider (stackable things only; at least 1, at most the stack limit).</summary>
        public static int ScaleStack(int stack, int stackLimit, float generosity)
        {
            if (stackLimit > 1 && Math.Abs(generosity - 1f) >= 1e-6f)
            {
                int n = (int)Math.Round(stack * generosity);
                return n < 1 ? 1 : n > stackLimit ? stackLimit : n;
            }
            return stack;
        }

        /// <summary>The salvager's hazard dose: the weathering's severity, cut by toxic resistance when the hediff is vanilla toxic buildup.</summary>
        public static float HazardDose(float severity, bool toxic, float toxicResistance)
        {
            if (toxic) severity *= Math.Max(0f, 1f - toxicResistance);
            return severity;
        }

        public static bool FieldDisabled(string disabledCsv, string key)
        {
            return !string.IsNullOrEmpty(disabledCsv) && disabledCsv.Split(',').Any(k => k.Trim() == key);
        }

        public static string SetFieldEnabled(string disabledCsv, string key, bool on)
        {
            var keys = new List<string>((disabledCsv ?? "").Split(',').Select(k => k.Trim()).Where(k => k.Length > 0 && k != key));
            if (!on) keys.Add(key);
            return string.Join(",", keys);
        }

        public static bool FieldActive(bool wreckFields, string key, string disabledCsv, bool gateEnabled)
        {
            return wreckFields && !string.IsNullOrEmpty(key) && !FieldDisabled(disabledCsv, key) && gateEnabled;
        }

        /// <summary>A fixed-count field: count x density x the engine's placement factor, rounded; density never below 0.</summary>
        public static int FixedCount(int count, float density, float placementFactor)
        {
            return (int)Math.Round(count * Math.Max(0f, density) * placementFactor);
        }

        /// <summary>Per-10k-cells density after the slider; 0 or less means no field at all.</summary>
        public static float Per10k(float rangeSample, float density)
        {
            return rangeSample * Math.Max(0f, density);
        }

        public static int ScaledCount(float countFromPer10k, float placementFactor)
        {
            return (int)Math.Round(countFromPer10k * placementFactor);
        }

        public static float ClusterChance(float ownChance, float densityClassChance)
        {
            return ownChance >= 0f ? ownChance : densityClassChance;
        }

        public static bool UseOwnClusterSize(int ownMax)
        {
            return ownMax >= 2;
        }

        /// <summary>The placement loop: anchors until the target is met or three anchor attempts miss; after each anchor, maybe a cluster of extra
        /// wrecks around it (a cluster member that fails is simply skipped). Returns how many were placed, never more than total.</summary>
        public static int PlaceField(int total, Func<bool> tryAnchor, Func<bool> rollCluster, Func<int> clusterSize, Func<bool> tryClusterMember)
        {
            int placed = 0, misses = 0;
            while (placed < total && misses < MaxMisses)
            {
                if (!tryAnchor()) { misses++; continue; }
                placed++;
                if (placed < total && rollCluster())
                {
                    int extra = clusterSize() - 1;
                    for (int i = 0; i < extra && placed < total; i++)
                        if (tryClusterMember()) placed++;
                }
            }
            return placed;
        }

        /// <summary>A wreck fall may happen on a map that carries one of the required tile mutators (none required = any map).</summary>
        public static bool MapAllowed(bool hasMap, int requiredCount, bool anyRequiredPresent)
        {
            if (!hasMap) return false;
            if (requiredCount == 0) return true;
            return anyRequiredPresent;
        }
    }
}
