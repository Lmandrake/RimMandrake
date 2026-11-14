using System;

namespace RimMandrake.Pyrelands
{
    // Verse-free decisions of the fire-hawk's sortie (JobGiver_RUT_FireHawkCarryEmber): whether a found fire is inside the scan circle,
    // whether a cell is fuel worth an ember, and which cell on the whole map the ember goes to (the largest easily found fuel). The mod passes PyrelandsTuning's
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

        /// <summary>One cell of the map-wide fuel map: flammable standing grass grown past minGrowth (growth below 0 is no plant),
        /// not burning, and easily found: not fogged and not under a roof.</summary>
        public static bool MapFuelCell(bool flammable, float growth, float minGrowth, bool burning, bool fogged, bool roofed)
        {
            return flammable && growth >= minGrowth && !burning && !fogged && !roofed;
        }

        /// <summary>Buckets along a map side of `cells` cells, `bucket` cells each (the last one may be short).</summary>
        public static int BucketsAlong(int cells, int bucket)
        {
            return cells <= 0 ? 0 : (cells + bucket - 1) / bucket;
        }

        /// <summary>The coarse fuel map: fuel cells per bucket x bucket square, bucket index bz * bw + bx. One pass over the map; the
        /// mod caches it per map (MapComponent_RM_FireHawkFuel) and asks fuel(x, z) of each cell once per refresh.</summary>
        public static int[] BucketFuel(int sx, int sz, int bucket, Func<int, int, bool> fuel)
        {
            int bw = BucketsAlong(sx, bucket), bh = BucketsAlong(sz, bucket);
            var counts = new int[bw * bh];
            for (int z = 0; z < sz; z++)
            {
                int row = z / bucket * bw;
                for (int x = 0; x < sx; x++)
                {
                    if (fuel(x, z))
                    {
                        counts[row + x / bucket]++;
                    }
                }
            }
            return counts;
        }

        /// <summary>Which buckets hold a fire, from the fires' cell indices (z * sx + x, the engine's CellIndices order).</summary>
        public static bool[] FireBuckets(int sx, int sz, int bucket, System.Collections.Generic.IEnumerable<int> fireCells)
        {
            int bw = BucketsAlong(sx, bucket), bh = BucketsAlong(sz, bucket);
            var fire = new bool[bw * bh];
            foreach (int c in fireCells)
            {
                if (c < 0 || c >= sx * sz)
                {
                    continue;
                }
                fire[c / sx / bucket * bw + c % sx / bucket] = true;
            }
            return fire;
        }

        /// <summary>
        /// Owner, 2026-11-13: "Carry distance should actually be anywhere on the map, unlimited. To the largest fuel source easily
        /// found." The candidate buckets, best first. A bucket's score is the fuel in its 3 x 3 block of buckets (a patch, not one
        /// dense square, so a big field beats a small full plot); it is a candidate only when it holds fuel itself and no bucket of
        /// its block is burning (the ember goes to unburnt fuel, not into the blaze). Order: score, then farther from the stolen
        /// fire's bucket (owner, same day: "Prefers to carry it farther rather than shorter"), then the lower bucket index.
        /// </summary>
        public static System.Collections.Generic.List<int> RankBuckets(int bw, int bh, int[] fuel, bool[] fire, int srcBx, int srcBz)
        {
            var score = new int[bw * bh];
            var far = new int[bw * bh];
            var cand = new System.Collections.Generic.List<int>();
            for (int bz = 0; bz < bh; bz++)
            {
                for (int bx = 0; bx < bw; bx++)
                {
                    int b = bz * bw + bx;
                    if (fuel[b] <= 0)
                    {
                        continue;
                    }
                    int sum = 0;
                    bool burning = false;
                    for (int az = Math.Max(0, bz - 1); az <= Math.Min(bh - 1, bz + 1); az++)
                    {
                        for (int ax = Math.Max(0, bx - 1); ax <= Math.Min(bw - 1, bx + 1); ax++)
                        {
                            sum += fuel[az * bw + ax];
                            burning |= fire[az * bw + ax];
                        }
                    }
                    if (burning)
                    {
                        continue;
                    }
                    score[b] = sum;
                    far[b] = (bx - srcBx) * (bx - srcBx) + (bz - srcBz) * (bz - srcBz);
                    cand.Add(b);
                }
            }
            cand.Sort((a, c) =>
            {
                int d = score[c].CompareTo(score[a]);
                if (d != 0) return d;
                d = far[c].CompareTo(far[a]);
                return d != 0 ? d : a.CompareTo(c);
            });
            return cand;
        }

        /// <summary>The drop cell inside bucket b: the fuel cell with the most fuel in its 3 x 3 (the densest), then the nearest the
        /// bucket's centre, then the lowest cell index (z * sx + x). -1 when the bucket holds no fuel now (the cached count is old).</summary>
        public static int DensestCell(int sx, int sz, int bucket, int b, Func<int, int, bool> fuel)
        {
            int bw = BucketsAlong(sx, bucket);
            int bx = b % bw, bz = b / bw;
            int cx2 = 2 * bx * bucket + bucket, cz2 = 2 * bz * bucket + bucket;
            int best = -1, bestN = -1, bestD = 0;
            for (int z = bz * bucket; z < Math.Min(sz, (bz + 1) * bucket); z++)
            {
                for (int x = bx * bucket; x < Math.Min(sx, (bx + 1) * bucket); x++)
                {
                    if (!fuel(x, z))
                    {
                        continue;
                    }
                    int n = 0;
                    for (int az = Math.Max(0, z - 1); az <= Math.Min(sz - 1, z + 1); az++)
                    {
                        for (int ax = Math.Max(0, x - 1); ax <= Math.Min(sx - 1, x + 1); ax++)
                        {
                            if (fuel(ax, az)) n++;
                        }
                    }
                    int dx = 2 * x + 1 - cx2, dz = 2 * z + 1 - cz2, d = dx * dx + dz * dz;
                    if (n > bestN || (n == bestN && d < bestD))
                    {
                        best = z * sx + x;
                        bestN = n;
                        bestD = d;
                    }
                }
            }
            return best;
        }

        /// <summary>
        /// The ember's target anywhere on the map: down RankBuckets' list, each bucket's DensestCell, the first that lawful(x, z)
        /// accepts (the mod: the full drop check and CanReach). Each lawful call spends one of maxTries, so a hawk walled off from
        /// the best fuel tries the next patches and then waits out its cooldown. Returns the cell index z * sx + x, or -1.
        /// fuel and fire are BucketFuel/FireBuckets of the same sx, sz and bucket; fuelCell is asked afresh (the counts may be old).
        /// </summary>
        public static int PickDrop(int sx, int sz, int bucket, int[] fuel, bool[] fire, int srcX, int srcZ, Func<int, int, bool> fuelCell,
            Func<int, int, bool> lawful, int maxTries)
        {
            int bw = BucketsAlong(sx, bucket), bh = BucketsAlong(sz, bucket);
            if (bw == 0 || bh == 0)
            {
                return -1;
            }
            var ranked = RankBuckets(bw, bh, fuel, fire, srcX / bucket, srcZ / bucket);
            int tries = 0;
            foreach (int b in ranked)
            {
                int c = DensestCell(sx, sz, bucket, b, fuelCell);
                if (c < 0)
                {
                    continue;
                }
                if (tries >= maxTries)
                {
                    return -1;
                }
                tries++;
                if (lawful(c % sx, c / sx))
                {
                    return c;
                }
            }
            return -1;
        }
    }
}
