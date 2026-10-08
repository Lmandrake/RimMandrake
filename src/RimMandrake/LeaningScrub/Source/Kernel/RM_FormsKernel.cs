// Verse-free kernel of the six venomvine forms (RM_VenomvineForms.cs) and the twitcher lash (RM_TwitcherLash.cs): the scratch
// clocks, rearing, quench and lash timing, the hoard's grow-in clock, and the walking stands' march. SelfTest/LeaningScrubFuzz.cs
// compiles this file alone: no Verse/RimWorld/UnityEngine.
using System;
using System.Collections.Generic;

namespace RimMandrake.LeaningScrub
{
    public static class RM_FormsKernel
    {
        public const int TicksPerDay = 60000;
        public const int TicksPerHour = 2500;

        // ── per-pawn scratch clocks ──
        public static bool Due(bool hasClock, int next, int now) { return !hasClock || now >= next; }
        public static int NextScratch(int now, int intervalTicks) { return now + Math.Max(1, intervalTicks); }
        // Marked thorns hurt only an armed (grown) cane, only a pawn not spared by the sap-mark, and only when the clock is due.
        public static bool ThornsHurt(float growth, float minGrowth, bool spared, bool due) { return growth >= minGrowth && !spared && due; }
        // A clock is dropped when its pawn is gone or its due time passed more than 2500 ticks ago.
        public static bool ClockStale(bool pawnGone, int now, int next) { return pawnGone || now - next > 2500; }

        // ── lash ──
        public static bool Poised(int now, int readyTick) { return now >= readyTick; }
        public static bool LashStrikes(int now, int readyTick, float growth, float minGrowth, bool hasDamageDef) { return Poised(now, readyTick) && growth >= minGrowth && hasDamageDef; }
        public static int LashReady(int now, int recoveryTicks, float recoveryFactor) { return now + Math.Max(60, (int)Math.Round(recoveryTicks * recoveryFactor)); }

        // ── rearing ──
        public static int RearTicks(float hours, bool stall, float stallFactor)
        {
            int ticks = (int)Math.Round(Math.Max(0.05f, hours) * TicksPerHour);
            return stall ? (int)Math.Round(ticks * stallFactor) : ticks;
        }
        public static int Rear(int rearedUntil, int now, int ticks) { return Math.Max(rearedUntil, now + ticks); }
        public static bool Reared(int now, int rearedUntil) { return now < rearedUntil; }
        public static bool RearsFor(float bodySize, float minBodySize, float growth, float minGrowth) { return growth >= minGrowth && bodySize >= minBodySize; }

        // ── quench ──
        public static int QuenchReady(int now, float recoveryDays) { return now + (int)Math.Round(Math.Max(0.1f, recoveryDays) * TicksPerDay); }
        public static bool QuenchReadyNow(int now, int readyTick) { return now >= readyTick; }
        public static bool FireInReach(int dx, int dz, float triggerRadius) { return (float)dx * dx + (float)dz * dz <= triggerRadius * triggerRadius; }

        // ── hoard: items lying against the stand are grown in after growInTicks; capacity maxHeld ──
        // Items are visited in order. `take(id)` does the engine work and returns how many things it added to the hoard
        // (0 when it could not hold it). firstSeen maps item id -> the tick it was first seen. Returns the number of items taken.
        public static int HoardSweep(Dictionary<int, int> firstSeen, int n, int[] ids, bool[] isCorpse, int now, int growInTicks, int held, int maxHeld, bool keepDeadGear, bool growthOk, Func<int, int> take)
        {
            if (!growthOk) return 0;
            int taken = 0;
            for (int i = 0; i < n && held < maxHeld; i++)
            {
                if (isCorpse[i] && !keepDeadGear) continue;
                int seen;
                if (!firstSeen.TryGetValue(ids[i], out seen)) { firstSeen[ids[i]] = now; continue; }
                if (now - seen < growInTicks) continue;
                firstSeen.Remove(ids[i]);
                held += take(ids[i]);
                taken++;
            }
            return taken;
        }

        // ── walking stands ──
        public sealed class WalkResult
        {
            public readonly List<int> SpawnX = new List<int>(), SpawnZ = new List<int>(), SpawnFrom = new List<int>(), SpawnK = new List<int>();
            public readonly List<int> Kills = new List<int>();   // indices into the input arrays
        }

        // One Gale onset over the walking cells. Cells are grouped into stands (8-connected); a stand with any smothered cell does
        // nothing; otherwise each grown cell (growth >= 0.5) at the leading edge sends a runner 1..maxStep cells downwind (if the
        // map-wide cap is not reached and the destination is free), and each fully grown cell at the tail of a stand of two or more
        // dies back with tailDieChance. destOk(from,x,z) says the map would accept a runner of that cell's kind there; the kernel adds that no walking cell
        // (or runner already sent) is there. rangeIncl(lo,hi) and chance(p) are the caller's random draws.
        public static void Walk(int n, int[] xs, int[] zs, float[] growth, bool[] isPlant, bool[] smothered, int[] maxStep, float[] tailDie,
                                float dirX, float dirZ, int cap, Func<int, int, int, bool> destOk, Func<int, int, int> rangeIncl, Func<float, bool> chance, WalkResult res)
        {
            var byCell = new Dictionary<long, int>();     // cell -> last index at it (later duplicates win)
            var order = new List<long>();
            for (int i = 0; i < n; i++)
            {
                long key = Key(xs[i], zs[i]);
                if (!byCell.ContainsKey(key)) order.Add(key);
                byCell[key] = i;
            }
            var walking = new HashSet<long>(order);
            int total = order.Count;
            var seen = new HashSet<long>();
            foreach (long start in order)
            {
                if (seen.Contains(start)) continue;
                var stand = new List<int>();
                bool anySmothered = false;
                var open = new Queue<long>();
                open.Enqueue(start); seen.Add(start);
                while (open.Count > 0)
                {
                    long c = open.Dequeue();
                    int idx = byCell[c];
                    stand.Add(idx);
                    if (smothered[idx]) anySmothered = true;
                    for (int dx = -1; dx <= 1; dx++)
                        for (int dz = -1; dz <= 1; dz++)
                        {
                            if (dx == 0 && dz == 0) continue;
                            long nb = Key(xs[idx] + dx, zs[idx] + dz);
                            if (byCell.ContainsKey(nb) && seen.Add(nb)) open.Enqueue(nb);
                        }
                }
                if (anySmothered) continue;
                foreach (int idx in stand)
                {
                    if (!isPlant[idx] || growth[idx] < 0.5f) continue;
                    int x = xs[idx], z = zs[idx];
                    int lx, lz;
                    RM_LeanKernel.Step(x, z, dirX, dirZ, 1f, out lx, out lz);
                    if (total < cap && !walking.Contains(Key(lx, lz)))
                    {
                        int k = rangeIncl(1, Math.Max(1, maxStep[idx]));
                        int dx2, dz2;
                        RM_LeanKernel.Step(x, z, dirX, dirZ, (float)k, out dx2, out dz2);
                        if (!walking.Contains(Key(dx2, dz2)) && destOk(idx, dx2, dz2))
                        {
                            res.SpawnX.Add(dx2); res.SpawnZ.Add(dz2); res.SpawnFrom.Add(idx); res.SpawnK.Add(k);
                            walking.Add(Key(dx2, dz2));
                            total++;
                        }
                    }
                    int tx, tz;
                    RM_LeanKernel.Step(x, z, dirX, dirZ, -1f, out tx, out tz);
                    if (growth[idx] >= 0.999f && stand.Count > 1 && !walking.Contains(Key(tx, tz)) && chance(tailDie[idx]))
                        res.Kills.Add(idx);
                }
            }
        }

        public static long Key(int x, int z) { return ((long)x << 32) ^ (uint)z; }
    }
}
