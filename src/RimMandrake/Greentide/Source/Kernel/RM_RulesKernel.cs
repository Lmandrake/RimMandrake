// Verse-free kernel of Greentide's small rules: biome score, cross-biome opt-in, greatbole seedling growth, the Roil toggle,
// the thurrock tuning, fever mark / frenzy dose, stellock branch. SelfTest/GreentideFuzz.cs compiles this file alone.
using System;
using System.Collections.Generic;

namespace RimMandrake.Greentide
{
    public static class RM_RulesKernel
    {
        // ── biome worker ──
        public static float BiomeScore(bool waterCovered, float temperature, float rainfall, float elevation, bool mountainousOrImpassable,
                                       float tMin, float tMax, float rMin, float rMax, float eMin, float eMax, float baseScore, float degreeWeight, float rainfallDivisor)
        {
            if (waterCovered) return -100f;
            if (temperature < tMin || temperature > tMax) return 0f;
            if (rainfall < rMin || rainfall >= rMax) return 0f;
            if (elevation < eMin || elevation > eMax) return 0f;
            if (mountainousOrImpassable) return 0f;
            float divisor = (rainfallDivisor > 0.0001f) ? rainfallDivisor : 1f;
            return baseScore + (temperature - tMin) * degreeWeight + (rainfall - rMin) / divisor;
        }

        // ── cross-biome opt-in ──
        public static List<string> ParseBiomeList(string list)
        {
            var result = new List<string>();
            if (string.IsNullOrEmpty(list)) return result;
            foreach (string part in list.Split(',', ';'))
            {
                string t = part.Trim();
                if (t.Length > 0) result.Add(t);
            }
            return result;
        }

        public static bool AppliesToBiome(bool enabled, string biomeDef, string nativeBiome, bool everywhere, string list)
        {
            if (!enabled || biomeDef == null || biomeDef == nativeBiome) return false;
            if (everywhere) return true;
            return ParseBiomeList(list).Contains(biomeDef);
        }

        public static float Coverage(float setting) { return setting < 0f ? 0f : (setting > 1f ? 1f : setting); }

        // One Mud cell, after generation: converted when coverage is full or the roll is within coverage.
        public static bool ConvertsMud(bool isMud, float coverage, float roll) { return isMud && !(coverage < 1f && roll > coverage); }

        // ── greatbole seedling ──
        public const int WaterRecheckTicks = 2500;
        public static bool WaterRecheckDue(int now, int last) { return now - last >= WaterRecheckTicks || now < last; }
        public static float SeedlingGrowthRate(float baseRate, bool seedRulesApply, bool hasWater, float sownMultiplier)
        {
            if (!seedRulesApply) return baseRate;
            if (!hasWater) return 0f;
            return baseRate * sownMultiplier;
        }

        // ── the Roil toggle on the biome (idempotent) ──
        public sealed class RoilBiome
        {
            public bool HasLock, HasRecord, HaveStash;
            public void Apply(bool enabled)
            {
                if (enabled)
                {
                    if (!HasLock) HasLock = true;
                    if (HaveStash && !HasRecord) HasRecord = true;
                }
                else
                {
                    HasLock = false;
                    if (HasRecord) { HaveStash = true; HasRecord = false; }
                }
            }
        }

        // ── thurrock aura tuning ──
        public static int ThurrockInterval(int shippedTicks, float pace)
        {
            float p = Math.Max(0.05f, pace);
            return Math.Max(1, (int)Math.Round(shippedTicks / p));
        }
        public static float Gated(bool enabled, float shipped) { return enabled ? shipped : 0f; }

        // ── fever ──
        public static bool GateReached(bool reached, int curStageIndex, int gateStage) { return reached || curStageIndex >= gateStage; }
        public static bool EarnsMark(bool settingOn, bool hasMarkHediffDef, bool reachedGate, bool pawnDeadOrNoHealth, bool alreadyMarked)
        {
            return settingOn && hasMarkHediffDef && reachedGate && !pawnDeadOrNoHealth && !alreadyMarked;
        }
        public static bool FrenzyCandidate(bool immunityOn, bool hasMark) { return !immunityOn || !hasMark; }
        // The dose: 0 = nothing happens, 1 = wasted on a marked pawn, 2 = applies at the returned severity.
        public static int FrenzyDose(bool enabled, bool immunityOn, bool hasMark, float severity, float multiplier, out float applied)
        {
            applied = severity;
            if (!enabled) return 0;
            if (immunityOn && hasMark) return 1;
            if (severity > 0f) applied = severity * multiplier;
            return 2;
        }

        // ── stellock ──
        public static bool Felled(bool killFinalizeLeavingsOnly, bool vanishWhileFelling) { return killFinalizeLeavingsOnly || vanishWhileFelling; }
        public static bool DropsBranch(bool settingOn, bool hasMapAndDef, bool felled, bool inGreentide, float chance, float roll)
        {
            return settingOn && hasMapAndDef && felled && inGreentide && (chance >= 1f || (chance > 0f && roll < chance));
        }
        public static int StellockTicks(float hours) { return (int)(hours * 2500f); }
    }
}
