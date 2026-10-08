// Verse-free kernel of the Gelatinous Slime world rules: the biome worker's score and spawn gate, the farm-conversion
// attempt budget, the titanoslime chunk's shelf life and burst ground, the archive vat's payment plan.
// SelfTest/GelatinousSlimeFuzz.cs compiles this file alone, so it must stay free of Verse/RimWorld/UnityEngine.
using System;
using System.Collections.Generic;

namespace RimMandrake.GelatinousSlime
{
    public static class RM_SlimeWorld
    {
        // BiomeWorker_GelatinousSlime.GetScore. Returns -100 (never), 0 (not here) or the score; the spawn gate is a seeded
        // chance the caller evaluates (gatePasses) only when the gate is below 1.
        public static float BiomeScore(bool waterCovered, float rarity, float temperature, float tMin, float tMax, float rainfall, float rMin, float rMax,
            float elevation, float eMin, float eMax, bool mountainous, float spawnChance, Func<float, bool> gatePasses, float baseScore, float degreeWeight, float rainfallDivisor)
        {
            if (waterCovered) return -100f;
            if (rarity <= 0.001f) return -100f;
            if (temperature < tMin || temperature > tMax) return 0f;
            if (rainfall < rMin || rainfall >= rMax) return 0f;
            if (elevation < eMin || elevation > eMax) return 0f;
            if (mountainous) return 0f;
            float gate = spawnChance * rarity;
            if (gate < 1f && !gatePasses(gate)) return 0f;
            float divisor = rainfallDivisor > 0.0001f ? rainfallDivisor : 1f;
            return baseScore + (temperature - tMin) * degreeWeight + (rainfall - rMin) / divisor;
        }

        // Farm conversion: cells tried this pass = floor(area/1000*rate) plus one more with the fractional chance, at least 1.
        public static int ConversionAttempts(int area, float rate, float cellsPerAttempt, float roll01)
        {
            float wanted = area / cellsPerAttempt * rate;
            int attempts = (int)wanted;
            if (roll01 < wanted - attempts) attempts++;
            return attempts < 1 ? 1 : attempts;
        }

        // Chunk shelf life.
        public static int ShelfTicks(float shelfDays, float ticksPerDay) { return (int)Math.Round(Math.Max(0.1f, shelfDays) * ticksPerDay, MidpointRounding.AwayFromZero); }
        // born < 0: stamp it now (not expired). Else expired once its age reaches the shelf.
        public static bool ShelfSweep(ref int born, int now, int shelf)
        {
            if (born < 0) { born = now; return false; }
            return now - born >= shelf;
        }

        // Chunk burst ground: open natural ground only (not built, not water, not already slime, not over a foundation).
        public static bool CanConvertGround(bool hasTerrain, bool natural, bool water, bool alreadySlime, bool foundationDiffers)
        {
            return hasTerrain && natural && !water && !alreadySlime && !foundationDiffers;
        }

        // The archive vat takes stacks in order skipping forbidden ones; returns what each stack gives and the shortfall.
        public static int[] PayPlan(IList<int> stacks, IList<bool> forbidden, int need, out int shortfall)
        {
            var takes = new int[stacks.Count];
            int left = need;
            for (int i = 0; i < stacks.Count && left > 0; i++)
            {
                if (forbidden[i]) continue;
                int take = Math.Min(left, stacks[i]);
                takes[i] = take;
                left -= take;
            }
            shortfall = left;
            return takes;
        }

        // Only the colony's humanlike people are filed (visitors and raiders are not).
        public static bool ArchiveFiles(bool exists, bool dead, bool humanlike, bool named, bool colonistPrisonerOrSlave)
        {
            return exists && !dead && humanlike && named && colonistPrisonerOrSlave;
        }
    }
}
