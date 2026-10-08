using System;
using System.Collections.Generic;

namespace RimMandrake.Pyrelands
{
    // Verse-free decisions of the fire-ecology hooks and the biome (FireEcologyHook.cs, WildPlantAllowlist.cs, RM_PyrelandsMod.cs): the
    // biome placement score, the terrain-family predicates, the fulgurite / ash-dusting / scorch-fruit gates, the ash-fall rate and
    // attempt count, the once-per-fire roll set, the cross-biome list parser and the wild-plant allowlist. The mod calls these with the
    // same expressions; the offline fuzz drives them.

    public static class RM_FireEcoKernel
    {
        /// <summary>BiomeWorker_Pyrelands.GetScore: -100 when generation is off or the tile is water, 0 outside the climate band (rainfall is
        /// half-open, like vanilla's workers), else a base score rising with warmth and rainfall.</summary>
        public static float BiomeScore(bool generationEnabled, bool hasTile, bool waterCovered, float temperature, float rainfall,
            float elevation, bool mountainousOrImpassable, float tMin, float tMax, float rMin, float rMax, float eMin, float eMax,
            float baseScore, float degreeWeight, float rainfallDivisor)
        {
            if (!generationEnabled)
            {
                return -100f;
            }
            if (!hasTile || waterCovered)
            {
                return -100f;
            }
            if (temperature < tMin || temperature > tMax)
            {
                return 0f;
            }
            if (rainfall < rMin || rainfall >= rMax)
            {
                return 0f;
            }
            if (elevation < eMin || elevation > eMax)
            {
                return 0f;
            }
            if (mountainousOrImpassable)
            {
                return 0f;
            }
            float divisor = rainfallDivisor > 0.0001f ? rainfallDivisor : 1f;
            return baseScore + (temperature - tMin) * degreeWeight + (rainfall - rMin) / divisor;
        }

        /// <summary>Vanilla BiomeWorker_AridShrubland's score, the rival the Pyrelands has to out-bid on its band.</summary>
        public static float AridShrublandScore(float temperature, float rainfall)
        {
            return 22.5f + (temperature - 20f) * 2.2f + (rainfall - 600f) / 100f;
        }

        public static bool IsSandFamily(string terrainDefName, IReadOnlyList<string> family)
        {
            if (terrainDefName == null)
            {
                return false;
            }
            for (int i = 0; i < family.Count; i++)
            {
                if (terrainDefName == family[i])
                {
                    return true;
                }
            }
            return false;
        }

        public static bool IsPyrelandsGround(string terrainDefName)
        {
            return terrainDefName != null && terrainDefName.StartsWith("RM_FE_", StringComparison.Ordinal);
        }

        public static bool IsScorchableGround(string n)
        {
            if (n == null)
            {
                return false;
            }
            return n.StartsWith("RM_FE_Ground_", StringComparison.Ordinal)
                || n == "Sand" || n == "Gravel" || n == "Soil" || n == "SoilRich";
        }

        /// <summary>The fulgurite postfix: a valid in-bounds strike on sand-family ground; the Pyrelands master switch governs only the
        /// Pyrelands' own ground. (The chance roll follows.)</summary>
        public static bool FulguriteMayRoll(bool fulguriteEnabled, bool strikeUsable, bool sandFamily, bool pyrelandsEnabled, bool pyrelandsGround)
        {
            if (!fulguriteEnabled || !strikeUsable || !sandFamily)
            {
                return false;
            }
            return pyrelandsEnabled || !pyrelandsGround;
        }

        /// <summary>The fire-tick postfix, before any roll: master on, one of the two outcomes on, a spawned ground fire (not a burning pawn)
        /// on scorchable ground.</summary>
        public static bool FireTickMayRoll(bool pyrelandsEnabled, bool ashOn, bool fruitOn, bool spawned, bool attachedToPawn, bool scorchable)
        {
            if (!pyrelandsEnabled || (!ashOn && !fruitOn) || !spawned || attachedToPawn)
            {
                return false;
            }
            return scorchable;
        }

        /// <summary>Per-interval ash chance: the per-tick chance times the batch size, so a watched and an unwatched fire roll alike.</summary>
        public static float DustChance(float perTick, int delta)
        {
            return perTick * delta;
        }

        public static bool UnderFruitCap(int existing, int cap)
        {
            return existing < cap;
        }

        /// <summary>The ash-fall rate this map gets this batch, or -1 when it gets none: ash fall full, cinderfall reduced, an opted-in
        /// foreign biome the coverage slider, anything else nothing.</summary>
        public static float AshRate(bool ashFall, bool cinderfall, float cinderFactor, bool nativeBiome, bool crossBiomeApplies,
            float crossCoverage, float rateMultiplier)
        {
            float rate;
            if (ashFall)
            {
                rate = 1f;
            }
            else if (cinderfall)
            {
                rate = cinderFactor;
            }
            else if (!nativeBiome && crossBiomeApplies)
            {
                rate = crossCoverage;
            }
            else
            {
                return -1f;
            }
            return rate * rateMultiplier;
        }

        /// <summary>Deposit attempts this batch: map area per attempt scaled by the rate; a rate of zero deposits nothing, any positive
        /// rate deposits at least one.</summary>
        public static int AshAttempts(int area, float cellsPerAttempt, float rate)
        {
            if (rate <= 0f)
            {
                return 0;
            }
            int attempts = (int)((float)area / cellsPerAttempt * rate);
            return attempts < 1 ? 1 : attempts;
        }

        /// <summary>True exactly once per id; the set is cleared wholesale when it passes a bound no live map reaches.</summary>
        public static bool MarkOnce(HashSet<int> rolled, int id, int bound)
        {
            if (rolled.Count > bound)
            {
                rolled.Clear();
            }
            return rolled.Add(id);
        }

        /// <summary>"a, b; c" -> ["a","b","c"]: comma / semicolon separated, trimmed, blanks dropped.</summary>
        public static List<string> ParseList(string text)
        {
            var result = new List<string>();
            if (string.IsNullOrEmpty(text))
            {
                return result;
            }
            string[] parts = text.Split(',', ';');
            for (int i = 0; i < parts.Length; i++)
            {
                string trimmed = parts[i].Trim();
                if (trimmed.Length > 0)
                {
                    result.Add(trimmed);
                }
            }
            return result;
        }

        /// <summary>Cross-biome ash opt-in: never the native biome, "everywhere" covers all, else the named list.</summary>
        public static bool CrossBiomeApplies(bool enabled, bool hasBiome, bool isNative, bool everywhere, bool listed)
        {
            if (!enabled || !hasBiome || isNative)
            {
                return false;
            }
            return everywhere || listed;
        }
    }
}
