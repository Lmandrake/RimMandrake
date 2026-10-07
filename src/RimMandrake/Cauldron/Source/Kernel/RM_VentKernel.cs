// Verse-free kernel of the Cauldron vents (CAULDRON_VENT_ENRICHMENT_HOOKS_1): silence and recovery, the weather multiplier and
// its falter, the blowout memory, the habitat match, the suppression meter, how many vents a map gets and how they are mixed,
// the exposure weight the bloom's metal load scales by, and which vent a vexxiss drinks. RM_CauldronVents.cs and
// RM_CompVexxissBehaviour.cs call these with the same expressions; SelfTest/CauldronFuzz.cs compiles this file alone, so it
// must stay free of Verse/RimWorld/UnityEngine. (Math.Min/Max/Round here match Mathf.Min/Max/RoundToInt for non-NaN input.)
using System;

namespace RimMandrake.Cauldron
{
    public enum RM_VentTemperament { Stable, Leaking }

    public enum RM_VentHabitat { None, StableRing, ChronicLeak, RecentBlowout }

    public static class RM_VentKernel
    {
        public const int NeverBlew = -900000000;
        public const float VentsPerCell = 1f / 14000f;
        public const float ExposureNear = 8f;
        public const float ExposureFar = 45f;
        public const float ExposureFloor = 0.1f;
        public const int MinVents = 2;
        public const int MaxVents = 8;

        // ---- silence and recovery ---------------------------------------------------------------------
        public static bool IsSilenced(int silencedUntil, int now) { return silencedUntil >= 0 && now < silencedUntil; }

        // 0 while silenced, climbing to 1 over recoverTicks after; 1 for a vent never silenced.
        public static float Recovery01(int silencedUntil, int now, int recoverTicks)
        {
            if (silencedUntil < 0) return 1f;
            if (now < silencedUntil) return 0f;
            int span = Math.Max(1, recoverTicks);
            float t = (now - silencedUntil) / (float)span;
            return t < 0f ? 0f : t > 1f ? 1f : t;
        }

        // Mathf.Approximately(x, 1f)
        public static bool ApproximatelyOne(float lerp)
        {
            return Math.Abs(1f - lerp) < Math.Max(1E-06f * Math.Max(Math.Abs(lerp), 1f), 1.401298E-45f * 8f);
        }

        // ---- weather ----------------------------------------------------------------------------------
        // The weather is the bloom's and its transition has not finished: the hush before a bloom.
        public static bool Faltering(bool weatherEnabled, bool hasMap, bool hasExt, bool bloomWeatherSet, bool curIsBloom, float lerp)
        {
            if (!weatherEnabled || !hasMap || !hasExt || !bloomWeatherSet) return false;
            return curIsBloom && !ApproximatelyOne(lerp);
        }

        public static bool Blooming(bool weatherEnabled, bool hasMap, bool hasExt, bool bloomWeatherSet, bool curIsBloom, float lerp)
        {
            if (!weatherEnabled || !hasMap || !hasExt || !bloomWeatherSet) return false;
            return curIsBloom && ApproximatelyOne(lerp);
        }

        // First matching row wins; no row = the default. A falter beats every row. No extension, the switch off, or no map = 1.
        public static float WeatherMultiplier(bool hasExt, bool weatherEnabled, bool hasMap, bool faltering, float falterOutput,
            int curWeather, int[] rowWeathers, float[] rowOutputs, float defaultOutput)
        {
            if (!hasExt || !weatherEnabled || !hasMap) return 1f;
            if (faltering) return falterOutput;
            for (int i = 0; i < rowWeathers.Length; i++)
                if (rowWeathers[i] == curWeather) return rowOutputs[i];
            return defaultOutput;
        }

        public static float Output(float weatherMultiplier, float recovery01) { return weatherMultiplier * recovery01; }

        // ---- blowout memory and habitat ---------------------------------------------------------------
        // The bloom's first full tick is a blowout; the flag clears when the bloom is over (not while it falters).
        public static void BloomTick(ref bool bloomSeen, ref int lastBlowoutTick, bool blooming, bool faltering, int now)
        {
            if (blooming)
            {
                if (!bloomSeen) { bloomSeen = true; lastBlowoutTick = now; }
            }
            else if (!faltering)
            {
                bloomSeen = false;
            }
        }

        public static bool RecentlyBlewOut(int now, int lastBlowoutTick, int window) { return now - lastBlowoutTick < window; }

        public static bool Matches(RM_VentHabitat h, RM_VentTemperament t, bool recentlyBlewOut)
        {
            switch (h)
            {
                case RM_VentHabitat.StableRing: return t == RM_VentTemperament.Stable && !recentlyBlewOut;
                case RM_VentHabitat.ChronicLeak: return t == RM_VentTemperament.Leaking;
                case RM_VentHabitat.RecentBlowout: return recentlyBlewOut;
                default: return false;
            }
        }

        public static bool InRing(float distance, float minRadius, float radius) { return distance >= minRadius && distance <= radius; }

        // ---- suppression ------------------------------------------------------------------------------
        // A drinker adds `amount` of the 0..1 meter; at 1 the meter resets and the vent is due to fall silent.
        public static bool AddSuppression(ref float suppression, float amount, bool alreadySilenced, bool hasExt)
        {
            if (alreadySilenced || !hasExt) return false;
            suppression += amount;
            if (suppression < 1f) return false;
            suppression = 0f;
            return true;
        }

        public static int SilenceUntil(int now, float silenceDays, float jitter)
        {
            return now + (int)Math.Round(silenceDays * jitter * 60000f);
        }

        public static float Decay(float suppression, float decayPerDay)
        {
            return suppression > 0f ? Math.Max(0f, suppression - 250f * decayPerDay / 60000f) : suppression;
        }

        public static float DrinkPerTick(float suppressionNeeded) { return 1f / suppressionNeeded; }

        // ---- the puffs --------------------------------------------------------------------------------
        public static bool PuffsAt(float output) { return output > 0.05f; }
        public static float PuffChance(float output) { float c = output * 0.3f; return c < 0f ? 0f : c > 1f ? 1f : c; }
        public static bool Smokes(float output) { return output > 1.5f; }

        // ---- exposure ---------------------------------------------------------------------------------
        public static float Proximity(float distance)
        {
            return distance <= ExposureNear ? 1f : distance >= ExposureFar ? 0f : 1f - (distance - ExposureNear) / (ExposureFar - ExposureNear);
        }

        // 1 = the old map-wide tax (toggle off or no vents); otherwise the best (proximity x recovery) over all vents, lerped from the floor.
        public static float ExposureWeight(bool localEnabled, bool hasComp, int ventCount, float[] distances, float[] recoveries)
        {
            if (!localEnabled || !hasComp || ventCount == 0) return 1f;
            float best = 0f;
            for (int i = 0; i < distances.Length; i++)
                best = Math.Max(best, Proximity(distances[i]) * recoveries[i]);
            return ExposureFloor + (1f - ExposureFloor) * (best < 0f ? 0f : best > 1f ? 1f : best);
        }

        // ---- generation -------------------------------------------------------------------------------
        public static int VentCount(int mapArea, float jitter)
        {
            int n = (int)Math.Round(mapArea * VentsPerCell * jitter);
            return Math.Min(MaxVents, Math.Max(MinVents, n));
        }

        // Every map shows both a stable vent and a chronic leak. temps is mutated in place.
        public static void MixTemperaments(RM_VentTemperament[] temps)
        {
            if (temps.Length < 2) return;
            bool leaking = false, stable = false;
            foreach (var t in temps) { if (t == RM_VentTemperament.Leaking) leaking = true; else stable = true; }
            if (!leaking) temps[temps.Length - 1] = RM_VentTemperament.Leaking;
            stable = false;
            foreach (var t in temps) if (t == RM_VentTemperament.Stable) stable = true;
            if (!stable) temps[0] = RM_VentTemperament.Stable;
        }

        public static bool TooClose(float distance, float spacing) { return distance < spacing; }

        // ---- the vexxiss drinking ---------------------------------------------------------------------
        // Index of the nearest drinkable vent inside the radius, or -1: not silenced, output above the puff floor, reachable (asked lazily,
        // only of a vent that could beat the best so far).
        public static int NearestDrinkable(float[] distSq, bool[] silenced, float[] output, Func<int, bool> reachable, float radius)
        {
            int best = -1;
            float bestSq = radius * radius;
            for (int i = 0; i < distSq.Length; i++)
            {
                if (silenced[i] || output[i] <= 0.05f) continue;
                if (distSq[i] >= bestSq) continue;
                if (!reachable(i)) continue;
                best = i;
                bestSq = distSq[i];
            }
            return best;
        }

        // Wild, able, awake, calm, off cooldown, not busy with a fight or a drink; a groan skips the chance roll and widens the scan.
        public static bool DrinkAllowed(bool wild, bool downed, bool awake, bool inMental, bool hasJobs, int now, int nextDrinkTick, bool busy)
        {
            if (!wild || downed || !awake || inMental || !hasJobs) return false;
            if (now < nextDrinkTick) return false;
            return !busy;
        }

        public static float DrinkRadius(bool groan, float scanRadius, float groanRadius) { return groan ? groanRadius : scanRadius; }
        public static bool DrinkRollNeeded(bool groan) { return !groan; }
    }
}
