using System;

namespace RimMandrake.Pyrelands
{
    // Verse-free decisions of the fire-hawk's sortie (JobGiver_RUT_FireHawkCarryEmber): whether a found fire is inside the scan circle,
    // whether a cell is fuel worth an ember, and which cell inside the carry range the ember goes to. The mod passes PyrelandsTuning's
    // constants and the engine's own cell facts; the offline fuzz (family hawk) drives the same functions over random cell grids.

    public static class RM_FireHawkKernel
    {
        /// <summary>The spread-only gate's distance half: a fire dx, dz cells from the hawk is one it may steal from only inside
        /// scanRadius. Beyond it there is no fire, so there is no behaviour.</summary>
        public static bool FireInScan(int dx, int dz, float scanRadius)
        {
            return dx * dx + dz * dz <= scanRadius * scanRadius;
        }

        /// <summary>A lawful ember drop: on the map, flammable (vanilla's ChanceToStartFireIn above 0), standing grass grown past
        /// minGrowth (plantGrowth below 0 is no plant), and nothing burning on or beside it.</summary>
        public static bool FuelledDrop(bool inBounds, bool flammable, float plantGrowth, float minGrowth, bool fireOnOrBeside)
        {
            return inBounds && flammable && plantGrowth >= minGrowth && !fireOnOrBeside;
        }

        /// <summary>
        /// Owner, 2026-11-13: "Prefers to carry it farther rather than shorter if available fuel exists." Candidates 0..count-1 are
        /// the cells inside the carry range in ascending distSq from the stolen fire (GenRadial.RadialPattern's order). Walks from the
        /// farthest ring inwards; inside one ring the cell farthest ahead of the blaze (largest ahead) is tried first. The first
        /// fuelled cell that is also reachable wins, so a nearer cell is chosen only when no farther one is lawful. The fire's own
        /// cell (distSq 0) is never a drop. Returns -1 when no lawful cell exists, or when maxReachTries reach checks (the costly
        /// predicate, asked only of fuelled cells) have all failed: a hawk walled off from its fuel waits out its cooldown.
        /// </summary>
        public static int FarthestFuelledDrop(int count, Func<int, int> distSq, Func<int, bool> fuelled, Func<int, float> ahead,
            Func<int, bool> reachable, int maxReachTries)
        {
            int tries = 0;
            int end = count - 1;
            var ring = new System.Collections.Generic.List<int>();
            while (end >= 0)
            {
                int d = distSq(end);
                if (d <= 0)
                {
                    return -1;
                }
                int start = end;
                while (start > 0 && distSq(start - 1) == d)
                {
                    start--;
                }
                ring.Clear();
                for (int i = start; i <= end; i++)
                {
                    if (fuelled(i))
                    {
                        ring.Add(i);
                    }
                }
                // Most ahead first; equal scores keep the radial order, so the pick is deterministic.
                ring.Sort((a, b) => { int c = ahead(b).CompareTo(ahead(a)); return c != 0 ? c : a.CompareTo(b); });
                for (int k = 0; k < ring.Count; k++)
                {
                    if (tries >= maxReachTries)
                    {
                        return -1;
                    }
                    tries++;
                    if (reachable(ring[k]))
                    {
                        return ring[k];
                    }
                }
                end = start - 1;
            }
            return -1;
        }
    }
}
