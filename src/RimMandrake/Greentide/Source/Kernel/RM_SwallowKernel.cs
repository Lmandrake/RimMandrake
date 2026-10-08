// Verse-free kernel of the churnmud swallow (RM_MapComponent_MudSwallow.cs): the dwell clock of loose items on mire terrain,
// the per-cell buried caches and the dig-out. SelfTest/GreentideFuzz.cs compiles this file alone: no Verse/RimWorld/UnityEngine.
using System;
using System.Collections.Generic;

namespace RimMandrake.Greentide
{
    public static class RM_SwallowKernel
    {
        public const int CheckIntervalTicks = 250;

        // Item id -> the tick it was first seen on mire ground. Not saved: a reload only restarts the dwell clocks.
        public sealed class Dwell
        {
            public readonly Dictionary<int, int> FirstSeen = new Dictionary<int, int>();

            // One scan. An item on mire ground is noted the first time it is seen and is due for burial once it has lain there
            // swallowTicks (its own terrain's value). Anything no longer on mire ground (or gone) loses its clock. Returns the ids
            // to bury, in scan order; a buried id's clock is cleared.
            public List<int> Scan(int now, int n, int[] ids, bool[] onMire, int[] swallowTicks)
            {
                var still = new HashSet<int>();
                var bury = new List<int>();
                for (int i = 0; i < n; i++)
                {
                    if (!onMire[i]) continue;
                    still.Add(ids[i]);
                    int first;
                    if (!FirstSeen.TryGetValue(ids[i], out first)) { FirstSeen[ids[i]] = now; continue; }
                    if (now - first >= swallowTicks[i]) { bury.Add(ids[i]); FirstSeen.Remove(ids[i]); }
                }
                if (FirstSeen.Count > 0)
                {
                    var stale = new List<int>();
                    foreach (var kv in FirstSeen) if (!still.Contains(kv.Key)) stale.Add(kv.Key);
                    foreach (int id in stale) FirstSeen.Remove(id);
                }
                return bury;
            }
        }

        public class Cache
        {
            public int X, Z, Count, Tick;
            public object Def, Stuff;   // def identity (the mod stores its ThingDefs here)
        }

        // Burying a stack: the same def+stuff at the same cell merges into one cache (its clock restarts), else a new cache.
        public static void Bury<T>(List<T> caches, int x, int z, object def, object stuff, int count, int now, Func<T> make) where T : Cache
        {
            foreach (var c in caches)
                if (c.X == x && c.Z == z && Equals(c.Def, def) && Equals(c.Stuff, stuff)) { c.Count += count; c.Tick = now; return; }
            T n = make();
            n.X = x; n.Z = z; n.Def = def; n.Stuff = stuff; n.Count = count; n.Tick = now;
            caches.Add(n);
        }

        // Digging a cell out. Every cache at the cell is put back in stacks of at most the def's stack limit (a merged cache can
        // hold many stacks' worth); `place(cache, n)` spawns n of it and says whether it landed. A chunk that cannot land stays
        // buried (the cache keeps the remainder). Returns how many caches are still buried at the cell: the caller clears the
        // dig designation only when that is 0.
        public static int DigOut<T>(List<T> caches, int x, int z, Func<object, int> stackLimitOf, Func<T, int, bool> place) where T : Cache
        {
            for (int i = caches.Count - 1; i >= 0; i--)
            {
                T c = caches[i];
                if (c.X != x || c.Z != z) continue;
                int limit = Math.Max(1, stackLimitOf(c.Def));
                int remaining = c.Count;
                while (remaining > 0)
                {
                    int chunk = Math.Min(remaining, limit);
                    if (!place(c, chunk)) break;
                    remaining -= chunk;
                }
                c.Count = remaining;
                if (remaining == 0) caches.RemoveAt(i);
            }
            int left = 0;
            foreach (var c in caches) if (c.X == x && c.Z == z) left++;
            return left;
        }

        public static bool HasBuriedAt<T>(List<T> caches, int x, int z) where T : Cache
        {
            foreach (var c in caches) if (c.X == x && c.Z == z) return true;
            return false;
        }

        // The oldest cache at the cell sets the dig effort.
        public static int BuriedDurationAt<T>(List<T> caches, int x, int z, int now) where T : Cache
        {
            int longest = 0;
            foreach (var c in caches)
                if (c.X == x && c.Z == z) { int age = now - c.Tick; if (age > longest) longest = age; }
            return longest;
        }

        public static int WorkAmount(int age) { return Math.Max(300, Math.Min(6000, 300 + age / 10)); }
    }
}
