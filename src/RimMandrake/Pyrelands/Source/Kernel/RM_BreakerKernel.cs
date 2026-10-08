using System;
using System.Collections.Generic;

namespace RimMandrake.Pyrelands
{
    // Verse-free decisions of the lightning breaker (RM_LightningBreaker / RM_LightningBreakerUtility): whether a breaker is armed, the
    // flood-fill of the faulted section of a power net up to the armed breakers around it, the battery partition, whether the plan is
    // worth tripping, and the blast. Generic over the node type so the offline fuzz drives it with plain integers.

    public static class RM_BreakerKernel
    {
        public static bool Armed(bool tripped, bool breakersEnabled, bool hasHopper, float fuel, float tripCost)
        {
            return !tripped && breakersEnabled && (!hasHopper || fuel >= tripCost);
        }

        /// <summary>The faulted section: every node reachable from `start` through nodes of the net without crossing an armed breaker;
        /// the armed breakers met on the way are the boundary (they are never entered).</summary>
        public static void Section<T>(T start, Func<T, IEnumerable<T>> neighbours, Func<T, bool> inNet, Func<T, bool> armedBreaker,
            out HashSet<T> visited, out HashSet<T> boundary)
        {
            visited = new HashSet<T> { start };
            boundary = new HashSet<T>();
            var queue = new Queue<T>();
            queue.Enqueue(start);
            while (queue.Count > 0)
            {
                T cur = queue.Dequeue();
                foreach (T n in neighbours(cur))
                {
                    if (!inNet(n) || visited.Contains(n))
                    {
                        continue;
                    }
                    if (armedBreaker(n))
                    {
                        boundary.Add(n);
                        continue;
                    }
                    visited.Add(n);
                    queue.Enqueue(n);
                }
            }
        }

        /// <summary>A battery is lost when it, or the conduit it hangs off, is in the faulted section.</summary>
        public static bool InSection<T>(HashSet<T> visited, T battery, bool hasParent, T parent)
        {
            return visited.Contains(battery) || (hasParent && visited.Contains(parent));
        }

        /// <summary>A trip is planned only when a breaker bounds the fault AND at least one battery is spared by it.</summary>
        public static bool WorthTripping(int boundaryCount, int protectedBatteries)
        {
            return boundaryCount > 0 && protectedBatteries > 0;
        }

        /// <summary>Does the faulted side hold enough charge to blow (any lost battery above 20 Wd)?</summary>
        public static bool LostCanBlast(IEnumerable<float> lostStoredEnergy)
        {
            foreach (float e in lostStoredEnergy)
            {
                if (e > 20f)
                {
                    return true;
                }
            }
            return false;
        }

        public static float BlastRadius(float lostEnergy)
        {
            float r = (float)Math.Sqrt(lostEnergy) * 0.05f;
            return r < 1.5f ? 1.5f : r > 14.9f ? 14.9f : r;
        }

        public static bool SecondBlast(float radius)
        {
            return radius > 3.5f;
        }
    }
}
