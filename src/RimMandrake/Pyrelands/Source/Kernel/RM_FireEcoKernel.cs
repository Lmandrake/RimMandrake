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

        /// <summary>RM_PyrelandsSettings.MechanicsOn: this mod's own master switch AND, when the Baroque Biomes shell is loaded, its
        /// "Pyrelands" roster toggle (biome_mod_unification_spec.md §5 arm 2). No shell (the standalone mod) = the master alone.</summary>
        public static bool MechanicsOn(bool modMaster, bool shellPresent, bool shellOn)
        {
            return modMaster && (!shellPresent || shellOn);
        }

        /// <summary>RM_JobGiver_BurrowOnFire: a burrow may start unless the last one TIMED OUT less than cooldownTicks ago.
        /// lastTimeoutTick &lt; 0 = never timed out; now &lt; lastTimeoutTick (a record from another game) = expired.</summary>
        public static bool BurrowMayStart(int now, int lastTimeoutTick, int cooldownTicks)
        {
            return lastTimeoutTick < 0 || now < lastTimeoutTick || now - lastTimeoutTick >= cooldownTicks;
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

        /// <summary>The late ruin sweep's subject (PYRE_RUINS_DIAGNOSE_JUNKYARD_STAYS_PRISTINE): an unowned, destroyable, artificial
        /// building - a ruin wall, ancient junk, a utility building - never natural rock, a geyser (not destroyable) or anything a
        /// faction owns.</summary>
        public static bool IsScorchableRuin(bool artificial, bool hasFaction, bool destroyable, bool naturalRock)
        {
            return artificial && !hasFaction && destroyable && !naturalRock;
        }

        /// <summary>Which ash rung the late ruin sweep lays on a cell: 2 = heavy (the footprint), 1 = light (its rim), 0 = leave it -
        /// water, or already at least as scorched (a rim never lightens a heavy cell, and heavy/deep stay as they are).</summary>
        public static int RuinScorchRung(bool atRim, bool water, string currentTerrain)
        {
            if (water || currentTerrain == "RM_FE_Ash_Heavy" || currentTerrain == "RM_FE_Ash_Deep")
            {
                return 0;
            }
            if (atRim)
            {
                return currentTerrain == "RM_FE_Ash_Light" ? 0 : 1;
            }
            return 2;
        }

        /// <summary>The scorch-fruit spot scan order over a fire's 3x3: its OWN cell first (the cell that just burned out; the fruit
        /// is Flammability 0, so the dying fire there cannot hurt it), then the eight neighbours.</summary>
        public static readonly int[] FruitSpotDx = { 0, -1, -1, -1, 0, 0, 1, 1, 1 };
        public static readonly int[] FruitSpotDz = { 0, -1, 0, 1, -1, 1, -1, 0, 1 };

        /// <summary>Index into FruitSpotDx/Dz of the first cell `legal(dx, dz)` accepts, or -1 when none does.</summary>
        public static int FirstFruitSpot(Func<int, int, bool> legal)
        {
            for (int i = 0; i < FruitSpotDx.Length; i++)
            {
                if (legal(FruitSpotDx[i], FruitSpotDz[i]))
                {
                    return i;
                }
            }
            return -1;
        }

        /// <summary>A fire's ONE scorch-fruit roll, deferred until it can land (SCORCH_FRUIT_FIX_ROLLS_BEFORE_THE_ASHES): returns the
        /// spot index when this fire takes its roll now, -1 when it does not — already rolled, or no legal spot yet because the grass
        /// it is burning still stands, so it waits for the ashes instead of spending the roll on a full 3x3. Taking the roll marks
        /// the fire; the chance and the map cap are the caller's.</summary>
        public static int TakeFruitRoll(HashSet<int> rolled, int fireId, int bound, Func<int, int, bool> legal)
        {
            if (rolled.Contains(fireId))
            {
                return -1;
            }
            int spot = FirstFruitSpot(legal);
            if (spot < 0)
            {
                return -1;
            }
            MarkOnce(rolled, fireId, bound);
            return spot;
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
