// Miasma pure kernel: the rules of the warden mother's creche (young ledger, succession, self-taming), the mother's price (buyers,
// betrayal, returns), the decay cell's digestion, the rotting bed, the flotsam yard, the nearest-thing pickers, the attar balm and the
// biome score. Each used to be an inline expression in a comp, hediff comp or map component tangled with Verse/Unity calls; they live
// here so an offline fuzz (Source/MiasmaFuzz) can drive the SAME code the game runs. NO `using Verse;` / `using UnityEngine;` may ever
// land in this file: the fuzz project compiles it on plain net8.0 and the build breaks - the guard rail working.
// Mathf.RoundToInt / Lerp / Clamp01 are restated with their Unity definitions (RoundToInt is Math.Round, round-half-even).
using System;
using System.Collections.Generic;

namespace RimMandrake.Miasma
{
    public static class RM_MiasmaKernel
    {
        public static float Clamp01(float v) { return v < 0f ? 0f : (v > 1f ? 1f : v); }

        /// <summary>Mathf.Lerp (t clamped).</summary>
        public static float Lerp(float a, float b, float t) { return a + (b - a) * Clamp01(t); }

        // ================================================================= nearest-thing pickers (three flavours the code already had)

        /// <summary>First strictly-closest within max (distSq &lt;= maxSq): the creche marker search. -1 when none.</summary>
        public static int NearestFirstInclusive(IList<float> distSq, float maxSq)
        {
            int best = -1; float bestD = float.MaxValue;
            for (int i = 0; i < distSq.Count; i++)
                if (distSq[i] <= maxSq && distSq[i] < bestD) { best = i; bestD = distSq[i]; }
            return best;
        }

        /// <summary>First closest strictly inside max (distSq &lt; maxSq): the young call's mother search.</summary>
        public static int NearestFirstStrict(IList<float> distSq, float maxSq)
        {
            int best = -1; float bestD = maxSq;
            for (int i = 0; i < distSq.Count; i++)
                if (distSq[i] < bestD) { best = i; bestD = distSq[i]; }
            return best;
        }

        /// <summary>LAST of the closest within max (distSq &lt;= the running best): the plant predator's prey pick.</summary>
        public static int NearestLastInclusive(IList<float> distSq, float maxSq)
        {
            int best = -1; float bestD = maxSq;
            for (int i = 0; i < distSq.Count; i++)
                if (distSq[i] <= bestD) { best = i; bestD = distSq[i]; }
            return best;
        }

        // ================================================================= the creche: young ledger + succession

        public sealed class CrecheLedger<T> where T : class
        {
            public List<T> young = new List<T>();
            public bool recordClean = true, successionDone, betrayed;
            public T heir;
            public int returnedCount;

            public void Register(T y) { if (y != null && !young.Contains(y)) young.Add(y); }

            /// <summary>The player harmed one of this creche's young: no more self-taming from it.</summary>
            public void BreakRecord() { recordClean = false; }

            /// <summary>The player sold a young: the record is gone, succession is void for good.</summary>
            public void Betray()
            {
                betrayed = true;
                recordClean = false;
                successionDone = true;
                heir = null;
            }

            /// <summary>A young was carried back to its mother: no longer owed.</summary>
            public void NoteReturned(T y)
            {
                returnedCount++;
                young.Remove(y);
            }

            /// <summary>How many registered young are still owed to her (alive, and not the player's).</summary>
            public int YoungOwed(Func<T, bool> owed)
            {
                int n = 0;
                for (int i = 0; i < young.Count; i++)
                    if (young[i] != null && owed(young[i])) n++;
                return n;
            }

            /// <summary>The comp polls for the mother's death only while a succession is still possible and the option is on.</summary>
            public bool PollDue(bool settingOn) { return !successionDone && settingOn; }

            /// <summary>
            /// The mother has died: the first registered young that is still alive and the player's becomes heir. One attempt per creche,
            /// ever: with no such young the attempt is spent and nothing is inherited.
            /// </summary>
            public T TryPromote(Func<T, bool> eligible)
            {
                T chosen = null;
                for (int i = 0; i < young.Count; i++)
                {
                    if (young[i] == null || !eligible(young[i])) continue;
                    chosen = young[i];
                    break;
                }
                successionDone = true;
                if (chosen != null) heir = chosen;
                return chosen;
            }
        }

        /// <summary>
        /// RM_HediffComp_SelfTameOnRecord's timer: the first call schedules, a due call reschedules and then may tame. Barred with the option
        /// off and when the creche's ledger exists and its record is broken (a ledger-less young can still tame).
        /// </summary>
        public static bool SelfTameStep(ref int nextCheckTick, int now, Func<int> intervalRoll, bool settingOn, bool hasLedger, bool recordClean, Func<bool> chance)
        {
            if (nextCheckTick < 0) { nextCheckTick = now + intervalRoll(); return false; }
            if (now < nextCheckTick) return false;
            nextCheckTick = now + intervalRoll();
            if (!settingOn) return false;
            if (hasLedger && !recordClean) return false;
            return chance();
        }

        // ================================================================= the mother's price

        public const int BuyerDelayMin = 60000, BuyerDelayMax = 120000, BuyerRetryTicks = 60000;
        public const float DefaultReach = 16f;

        /// <summary>RM_MothersPrice.ReachOf: the anchor's radius if it reads as a positive float, else 16.</summary>
        public static float ReachOrDefault(float? read) { return read.HasValue && read.Value > 0f ? read.Value : DefaultReach; }

        /// <summary>A young is taken back when it stands in water within the mother's reach.</summary>
        public static bool ReturnInReach(bool inWater, float distance, float reach) { return inWater && distance <= reach; }

        /// <summary>Selling is ignored with the option off or for a young that is not stranded; a betrayed mother refuses every return.</summary>
        public static bool SaleCounts(bool enabled, bool strandedYoung) { return enabled && strandedYoung; }

        public static bool ReturnRefused(bool motherBetrayed) { return motherBetrayed; }

        /// <summary>
        /// RM_MapComponent_MothersPrice.CheckBuyers over the stranded young the player holds: the first sighting schedules a buyer 60k..120k
        /// ticks out, a due one is sent (success: offered for good; failure: try again in 60k). rangeExclusive is Rand.Range(int,int).
        /// </summary>
        public static void BuyerPoll(List<int> offered, Dictionary<int, int> buyerAt, IEnumerable<int> heldStranded, int now,
            Func<int, int, int> rangeExclusive, Func<int, bool> trySend)
        {
            foreach (int id in heldStranded)
            {
                if (offered.Contains(id)) continue;
                if (!buyerAt.TryGetValue(id, out int at))
                {
                    buyerAt[id] = now + rangeExclusive(BuyerDelayMin, BuyerDelayMax);
                    continue;
                }
                if (now >= at)
                {
                    if (trySend(id))
                    {
                        offered.Add(id);
                        buyerAt.Remove(id);
                    }
                    else buyerAt[id] = now + BuyerRetryTicks;
                }
            }
        }

        // ================================================================= decay cells

        /// <summary>Output fraction by fuel fullness: nothing when empty, else min..1 along the fullness.</summary>
        public static float OutputFraction(float fullness, float minFraction)
        {
            if (fullness <= 0f) return 0f;
            return Lerp(minFraction, 1f, Clamp01(fullness));
        }

        /// <summary>
        /// One fuel observation (every 250 ticks): fuel that fell since the last look is digested, a refill is not. Returns true when the cell
        /// is spent (digested its lifetime) and has a bed to rot into.
        /// </summary>
        public static bool DecayObserve(ref float lastFuel, ref float digested, float fuel, float lifetimeFeed, bool hasSpentDef, bool spawned)
        {
            if (lastFuel >= 0f && fuel < lastFuel) digested += lastFuel - fuel;
            lastFuel = fuel;
            return digested >= lifetimeFeed && hasSpentDef && spawned;
        }

        // ================================================================= rotting bed

        public const int TickRareInterval = 250;

        /// <summary>Ticks to rot a corpse down: the setting's days, never under one rare tick of ten (2500).</summary>
        public static int RotDownTicks(float days, int ticksPerDay)
        {
            return Math.Max(2500, (int)Math.Round(days * ticksPerDay));
        }

        public static int BonesFor(float bodySize, float perBodySize)
        {
            return Math.Max(1, (int)Math.Round(bodySize * perBodySize));
        }

        /// <summary>The bone stacks for n bones at a stack limit: full stacks and a remainder.</summary>
        public static List<int> StackSplit(int n, int stackLimit)
        {
            var stacks = new List<int>();
            while (n > 0)
            {
                int s = Math.Min(n, stackLimit);
                stacks.Add(s);
                n -= s;
            }
            return stacks;
        }

        /// <summary>
        /// RM_Building_RottingBed.TickRare for the corpse being rotted (target &gt;= 0): a missing or moved corpse restarts the clock on whatever
        /// is stored now (candidate, -1 for none); each rare tick adds 250; at the setting's length the corpse rots down. done=true then.
        /// </summary>
        public static void RotStep(ref int target, ref int rotTicks, bool targetStillValid, int candidate, int rotDown, out bool done)
        {
            done = false;
            if (target < 0 || !targetStillValid)
            {
                target = candidate;
                rotTicks = 0;
                if (target < 0) return;
            }
            rotTicks += TickRareInterval;
            if (rotTicks >= rotDown)
            {
                done = true;
                target = -1;
                rotTicks = 0;
            }
        }

        // ================================================================= flotsam yard

        public const int SeedStacks = 24, RestockStacks = 14, CapStacks = 70;

        /// <summary>
        /// The yard seeds once, then restocks each time the gradient axis's recede-completed tick moves forward. Returns the base stack count
        /// to place now (0 for nothing).
        /// </summary>
        public static int FlotsamStep(ref bool seeded, ref int lastRecedeSeen, int recedeTickNow)
        {
            if (!seeded)
            {
                seeded = true;
                lastRecedeSeen = recedeTickNow;
                return SeedStacks;
            }
            if (recedeTickNow > lastRecedeSeen)
            {
                lastRecedeSeen = recedeTickNow;
                return RestockStacks;
            }
            return 0;
        }

        /// <summary>How many stacks one placement may make: the amount-scaled request, held under the amount-scaled cap less what is already out.</summary>
        public static int FlotsamWant(int baseStacks, float amount, int placedCount)
        {
            int want = (int)Math.Round(baseStacks * amount);
            int room = (int)Math.Round(CapStacks * amount) - placedCount;
            return Math.Min(want, room);
        }

        /// <summary>The table row a roll picks (weights in order; roll01 in [0,1)). Falls back to the first row.</summary>
        public static int FlotsamPick(IList<float> weights, float roll01)
        {
            float total = 0f;
            for (int i = 0; i < weights.Count; i++) total += weights[i];
            float roll = roll01 * total;
            for (int i = 0; i < weights.Count; i++)
            {
                roll -= weights[i];
                if (roll <= 0f) return i;
            }
            return 0;
        }

        // ================================================================= attar

        public const float GlazeBonus = 3f;

        /// <summary>Balm on a permanent scar: 3 off the severity, gone at or under 0.01.</summary>
        public static float BalmScar(float severity, out bool removed)
        {
            float s = Math.Max(0f, severity - 3f);
            removed = s <= 0.01f;
            return s;
        }

        // ================================================================= the biome worker

        public struct BiomeRanges
        {
            public float tempMin, tempMax, rainMin, rainMax, elevMin, elevMax, baseScore, degreeWeight, rainfallDivisor, riverOrCoastBonus, spawnChance;
        }

        public static float BiomeScore(bool tileNull, bool waterCovered, bool hillsBlock, bool hasRiver, float rarity, float temperature, float rainfall, float elevation,
            in BiomeRanges r, Func<float, bool> seededChance)
        {
            if (tileNull || waterCovered) return -100f;
            if (rarity <= 0.001f) return -100f;
            if (temperature < r.tempMin || temperature > r.tempMax) return 0f;
            if (rainfall < r.rainMin || rainfall >= r.rainMax) return 0f;
            if (elevation < r.elevMin || elevation > r.elevMax) return 0f;
            if (hillsBlock) return 0f;
            if (!hasRiver) return 0f;
            float gate = r.spawnChance * rarity;
            if (gate < 1f && !seededChance(gate)) return 0f;
            float divisor = (r.rainfallDivisor > 0.0001f) ? r.rainfallDivisor : 1f;
            return r.baseScore + (temperature - r.tempMin) * r.degreeWeight + (rainfall - r.rainMin) / divisor + r.riverOrCoastBonus;
        }
    }
}
