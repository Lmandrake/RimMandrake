// Verse-free kernel of the Nightside Ice: the heat dial (how loud the colony is), the breach loop (when a crack opens, how many shivven
// come up, when the crack warns and breaks) and the shivven's ice-only path search. The map components, the crack building and the shivven
// comp call these with the same expressions; SelfTest/NightsideIceFuzz.cs compiles this file alone. Keep it free of
// Verse/RimWorld/UnityEngine (a `using Verse;` here breaks the self-test build, which is the guard rail).
// Unity's Mathf.RoundToInt rounds half to even, as Math.Round does; Mathf.Lerp clamps t; Mathf.Exp is Math.Exp in float.
using System;
using System.Collections.Generic;

namespace RimMandrake.NightsideIce
{
    /// <summary>The map as the shivven's path search sees it.</summary>
    public interface IIceGrid
    {
        bool InBounds(int x, int z);
        bool Standable(int x, int z);
        bool IsIce(int x, int z);
    }

    public static class RM_NightsideIceKernel
    {
        // ---------------------------------------------------------------- heat dial
        public const int IntervalTicks = 2500;           // one hour
        public const int DialTickOffset = 71, BreachTickOffset = 76;
        public const float FireWeight = 20f, PowerWeight = 0.01f, RoomWeight = 0.002f;
        public const int SourceCacheTicks = 250;

        public static float Clamp01(float v) { return v < 0f ? 0f : (v > 1f ? 1f : v); }

        /// <summary>Heat the room adds: only a room warmer than outdoors counts, per cell.</summary>
        public static float RoomHeat(float roomTemp, float outdoorTemp, int cellCount)
        {
            float delta = roomTemp - outdoorTemp;
            return delta > 0f ? delta * cellCount * RoomWeight : 0f;
        }

        public static float FireHeat(float fireSize) { return fireSize * FireWeight; }

        /// <summary>A powered consumer that is on and drawing (output below zero) adds its draw in watts times the weight.</summary>
        public static float PowerHeat(float powerOutput) { return -powerOutput * PowerWeight; }

        /// <summary>The target the dial eases to: 1 - exp(-raw / scale), the scale never under 1 (a raw of one scale reads about 63%).</summary>
        public static float Target(float raw, float scale)
        {
            return 1f - (float)Math.Exp(-raw / Math.Max(1f, scale));
        }

        /// <summary>Halfway to the target every hour, held in 0..1.</summary>
        public static float Ease(float dial, float target)
        {
            float t = 0.5f;
            return Clamp01(dial + (target - dial) * Clamp01(t));
        }

        public static bool DialDue(int ticksGame) { return ticksGame % IntervalTicks == DialTickOffset; }
        public static bool BreachDue(int ticksGame) { return ticksGame % IntervalTicks == BreachTickOffset; }

        /// <summary>Index of the hottest working heater: the first one strictly above every earlier one, a heater must push more than 0. -1 for none.</summary>
        public static int HottestIndex(IList<float> heatPerSecond, IList<bool> working)
        {
            int best = -1;
            float bestHeat = 0f;
            for (int i = 0; i < heatPerSecond.Count; i++)
            {
                if (working[i] && heatPerSecond[i] > bestHeat)
                {
                    bestHeat = heatPerSecond[i];
                    best = i;
                }
            }
            return best;
        }

        /// <summary>Whether the cached hottest source can be returned: read within the cache window, and (if there is one) still working.</summary>
        public static bool SourceCacheValid(int now, int readTick, bool hasCached, bool cachedStillWorking)
        {
            return now - readTick < SourceCacheTicks && (!hasCached || cachedStillWorking);
        }

        // ---------------------------------------------------------------- breach loop
        public const float BreachThreshold = 0.15f;
        public const int TicksPerHour = 2500, TicksPerDay = 60000;
        public const int CooldownTicks = 2 * TicksPerDay;

        /// <summary>The hourly chance of a crack: scale x dial^2 / 24, held in 0..1 (a full dial at scale 1 is 1/24 an hour).</summary>
        public static float BreachChance(float frequencyScale, float dial)
        {
            return Clamp01(frequencyScale * dial * dial / 24f);
        }

        /// <summary>Whether the hourly roll is made at all: applies, no crack open, past the cooldown, dial at the threshold.</summary>
        public static bool BreachRollMade(bool applies, bool crackOpen, int now, int cooldownUntil, float dial)
        {
            if (!applies || crackOpen || now < cooldownUntil) return false;
            return !(dial < BreachThreshold);
        }

        /// <summary>Shivven in a breach: 2 plus the dial times 6, rounded half to even (the dial held in 0..1).</summary>
        public static int ShivvenCount(float dial)
        {
            return 2 + (int)Math.Round(Clamp01(dial) * 6f);
        }

        /// <summary>Hours until a crack breaks: the first, taught crack uses the setting (at least 1); later ones the roll (8..16).</summary>
        public static int BreakHours(bool teach, int firstCountdownHours, int laterRoll)
        {
            return teach ? Math.Max(1, firstCountdownHours) : laterRoll;
        }

        /// <summary>A cell is the base's edge when the nearest player building is 3 to 12 cells away (squared 9..144, inclusive).</summary>
        public static bool InEdgeBand(float nearestSquared)
        {
            return nearestSquared >= 9f && nearestSquared <= 144f;
        }

        /// <summary>
        /// One 60-tick look at a crack: sets the 6-hour and 1-hour warning flags once each (only a taught crack with warnings on speaks) and
        /// returns true when it breaks (time left at or under 0).
        /// </summary>
        public static bool CrackLook(int ticksLeft, bool taught, bool warningsOn, ref bool warned6, ref bool warned1, out bool say6, out bool say1)
        {
            say6 = false;
            say1 = false;
            if (taught && warningsOn)
            {
                if (!warned6 && ticksLeft <= 6 * TicksPerHour)
                {
                    warned6 = true;
                    say6 = true;
                }
                if (!warned1 && ticksLeft <= TicksPerHour)
                {
                    warned1 = true;
                    say1 = true;
                }
            }
            return ticksLeft <= 0;
        }

        // ---------------------------------------------------------------- the shivven's ice path
        /// <summary>The compass order of the eight neighbours (engine GenAdj.AdjacentCells): four cardinal first, then the diagonals.</summary>
        public static readonly int[] StepX = { 0, 1, 0, -1, 1, 1, -1, -1 };
        public static readonly int[] StepZ = { 1, 0, -1, 0, -1, 1, 1, -1 };

        /// <summary>A cell touches the source when it lies in the one-cell ring around the source's footprint (inside the footprint does not count).</summary>
        public static bool Touches(int x, int z, int minX, int minZ, int maxX, int maxZ)
        {
            bool inside = x >= minX && x <= maxX && z >= minZ && z <= maxZ;
            bool inRing = x >= minX - 1 && x <= maxX + 1 && z >= minZ - 1 && z <= maxZ + 1;
            return inRing && !inside;
        }

        /// <summary>Lower is better: 0 off the ice, -1 touching the source, else squared distance to the source cell.</summary>
        public static float Score(int x, int z, int srcX, int srcZ, int minX, int minZ, int maxX, int maxZ, bool onIce)
        {
            if (!onIce) return 0f;
            if (Touches(x, z, minX, minZ, maxX, maxZ)) return -1f;
            int dx = x - srcX, dz = z - srcZ;
            return dx * dx + dz * dz;
        }

        /// <summary>A diagonal step may not cut a corner off the ice (or through a wall).</summary>
        public static bool DiagonalOk(IIceGrid g, int fromX, int fromZ, int toX, int toZ, bool iceOnly)
        {
            return g.Standable(toX, fromZ) && g.Standable(fromX, toZ)
                && (!iceOnly || (g.IsIce(toX, fromZ) && g.IsIce(fromX, toZ)));
        }

        /// <summary>The index along a path of length <paramref name="pathCount"/> (>= 1) where a leg of <paramref name="legCells"/> cells ends; at least the first step.</summary>
        public static int LegIndex(int legCells, int pathCount)
        {
            return Math.Max(0, Math.Min(legCells, pathCount) - 1);
        }

        /// <summary>
        /// Breadth-first over standable ice from the shivven (or, off the ice, over any standable cell until the first ice is reached).
        /// Returns the cell path to the reached cell nearest the source, preferring one touching it; empty when it already stands on that
        /// cell. <paramref name="budget"/> counts cells taken off the queue.
        /// </summary>
        public static List<KeyValuePair<int, int>> IcePath(IIceGrid g, int startX, int startZ, bool startOnIce, int srcX, int srcZ,
            int minX, int minZ, int maxX, int maxZ, int budget)
        {
            long Key(int x, int z) { return ((long)x << 32) ^ (uint)z; }
            var parent = new Dictionary<long, KeyValuePair<int, int>>();
            var queue = new Queue<KeyValuePair<int, int>>();
            var start = new KeyValuePair<int, int>(startX, startZ);
            parent[Key(startX, startZ)] = start;
            queue.Enqueue(start);
            var best = start;
            float bestScore = Score(startX, startZ, srcX, srcZ, minX, minZ, maxX, maxZ, startOnIce);
            while (queue.Count > 0 && budget-- > 0)
            {
                var c = queue.Dequeue();
                bool cIce = g.IsIce(c.Key, c.Value);
                if (!startOnIce && cIce)
                {
                    best = c;      // off the ice: the first ice reached is the way home
                    break;
                }
                for (int i = 0; i < 8; i++)
                {
                    int nx = c.Key + StepX[i], nz = c.Value + StepZ[i];
                    if (parent.ContainsKey(Key(nx, nz)) || !g.InBounds(nx, nz) || !g.Standable(nx, nz)) continue;
                    if (startOnIce && !g.IsIce(nx, nz)) continue;
                    if (i >= 4 && !DiagonalOk(g, c.Key, c.Value, nx, nz, startOnIce)) continue;
                    var n = new KeyValuePair<int, int>(nx, nz);
                    parent[Key(nx, nz)] = c;
                    queue.Enqueue(n);
                    float s = Score(nx, nz, srcX, srcZ, minX, minZ, maxX, maxZ, startOnIce);
                    if (s < bestScore)
                    {
                        bestScore = s;
                        best = n;
                    }
                }
            }
            var path = new List<KeyValuePair<int, int>>();
            for (var c = best; !(c.Key == startX && c.Value == startZ); c = parent[Key(c.Key, c.Value)])
            {
                path.Add(c);
            }
            path.Reverse();
            return path;
        }
    }
}
