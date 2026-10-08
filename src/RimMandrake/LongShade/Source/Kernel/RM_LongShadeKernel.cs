// Verse-free kernel of the Long Shade: the lee-side midden heaps (tending, searching, building), the dewfringe's rim test, the Crawler Road
// and Long Carry map-generation arithmetic (shade islands, rim sampling, closest pair, road segments, the graves' distance band) and the
// Shipfall Commons ladder (which rungs are open, who a rung admits, the commons cell set and its cache). The comps, map components and gen
// steps call these with the same expressions; SelfTest/LongShadeFuzz.cs compiles this file alone. Keep it free of Verse/RimWorld/UnityEngine
// (a `using Verse;` here breaks the self-test build, which is the guard rail).
// Unity's Mathf.RoundToInt rounds half to even, as Math.Round does.
using System;
using System.Collections.Generic;

namespace RimMandrake.LongShade
{
    public static class RM_LongShadeKernel
    {
        // ================================================================= midden heaps
        /// <summary>A heap can be tended while it has room for another layer and its cooldown since the last tend has run out.</summary>
        public static bool CanTendNow(int layers, int maxLayers, int now, int lastTendTick, int cooldownTicks)
        {
            return layers < maxLayers && now - lastTendTick >= cooldownTicks;
        }

        /// <summary>One tend: add the gain; every full unit of progress becomes a layer, up to the cap; a full heap holds no progress.</summary>
        public static void Tend(ref int layers, ref float progress, float gain, int maxLayers)
        {
            progress += gain;
            while (progress >= 1f && layers < maxLayers)
            {
                progress -= 1f;
                layers++;
            }
            if (layers >= maxLayers) progress = 0f;
        }

        public static int SearchRolls(int layers, int rollsPerLayer) { return layers * rollsPerLayer; }

        /// <summary>Stack sizes for <paramref name="n"/> items at a stack limit (a limit under 1 is read as 1 so the loop always ends).</summary>
        public static List<int> StackSplit(int n, int stackLimit)
        {
            int limit = Math.Max(1, stackLimit);
            var stacks = new List<int>();
            while (n > 0)
            {
                int s = Math.Min(n, limit);
                stacks.Add(s);
                n -= s;
            }
            return stacks;
        }

        public static int ClampStartLayers(int startLayers, int maxLayers)
        {
            return startLayers < 0 ? 0 : (startLayers > maxLayers ? maxLayers : startLayers);
        }

        /// <summary>A vrekka with no heap within its search radius starts one, unless the map already holds the maximum.</summary>
        public static bool ShouldBuildHeap(bool anyHeapInRange, int existingHeaps, int maxHeapsPerMap)
        {
            return !anyHeapInRange && existingHeaps < maxHeapsPerMap;
        }

        /// <summary>A new heap's cell is acceptable when it is at least the spacing from every existing heap.</summary>
        public static bool SpacingOk(float distanceToExisting, float minSpacing)
        {
            return !(distanceToExisting < minSpacing);
        }

        /// <summary>
        /// The heap a vrekka goes to tend: the nearest within <paramref name="radius"/> (inclusive) that can be tended; the first of equals wins.
        /// <paramref name="anyInRange"/> is true when any heap at all lies within the radius, tendable or not. -1 when none can be tended.
        /// </summary>
        public static int NearestTendable(IList<float> distances, IList<bool> canTend, float radius, out bool anyInRange)
        {
            anyInRange = false;
            int best = -1;
            float bestDist = float.MaxValue;
            for (int i = 0; i < distances.Count; i++)
            {
                if (distances[i] > radius) continue;
                anyInRange = true;
                if (!canTend[i] || distances[i] >= bestDist) continue;
                best = i;
                bestDist = distances[i];
            }
            return best;
        }

        /// <summary>"Untended: nothing is adding to it": never tended (negative tick) or not for ten days.</summary>
        public static bool Untended(int lastTendTick, int now, int ticksPerDay)
        {
            return lastTendTick < 0 || now - lastTendTick > ticksPerDay * 10;
        }

        // ================================================================= dewfringe
        public const float MinRimShade = 0.05f, MaxRimShade = 0.85f;

        /// <summary>The rim: strictly between full sun and full shade.</summary>
        public static bool OnRim(float shade)
        {
            return shade > MinRimShade && shade < MaxRimShade;
        }

        // ================================================================= Crawler Road and Long Carry
        /// <summary>A human's one-way dash in cells: the ring cost over the cardinal step cost, capped at the animals' own dash cap.</summary>
        public static float DashCells(int ringCost, int cardinalCost, float maxDashCells)
        {
            return Math.Min(ringCost / (float)cardinalCost, maxDashCells);
        }

        /// <summary>Link spacing: the dash times the spacing factor, held inside the step's range.</summary>
        public static float RoadSpacing(float dashCells, float spacingFactor, float minSpacing, float maxSpacing)
        {
            float v = dashCells * spacingFactor;
            return v < minSpacing ? minSpacing : (v > maxSpacing ? maxSpacing : v);
        }

        /// <summary>
        /// Groups patches joined by edges into islands (depth-first). Returns each patch's island index; <paramref name="islandCells"/> holds each
        /// island's total cell count. Edges are followed as given, so they must be symmetric for the groups to be true islands.
        /// </summary>
        public static int[] Islands(IList<IList<int>> adjacency, IList<long> cellCounts, out int count, out long[] islandCells)
        {
            int n = cellCounts.Count;
            int[] island = new int[n];
            for (int i = 0; i < n; i++) island[i] = -1;
            var size = new List<long>();
            var stack = new Stack<int>();
            count = 0;
            for (int s = 0; s < n; s++)
            {
                if (island[s] >= 0) continue;
                long total = 0;
                island[s] = count;
                stack.Push(s);
                while (stack.Count > 0)
                {
                    int u = stack.Pop();
                    total += cellCounts[u];
                    IList<int> edges = adjacency[u];
                    for (int k = 0; k < edges.Count; k++)
                    {
                        int v = edges[k];
                        if (island[v] < 0)
                        {
                            island[v] = count;
                            stack.Push(v);
                        }
                    }
                }
                size.Add(total);
                count++;
            }
            islandCells = size.ToArray();
            return island;
        }

        /// <summary>The two biggest islands by cell count (the first of equals wins the larger slot). False when fewer than two.</summary>
        public static bool TwoBiggest(long[] islandCells, int islandCount, out int a, out int b)
        {
            a = -1;
            b = -1;
            for (int i = 0; i < islandCount; i++)
            {
                if (a < 0 || islandCells[i] > islandCells[a])
                {
                    b = a;
                    a = i;
                }
                else if (b < 0 || islandCells[i] > islandCells[b])
                {
                    b = i;
                }
            }
            return a >= 0 && b >= 0;
        }

        /// <summary>At most <paramref name="sample"/> evenly spaced entries of the rim list.</summary>
        public static List<int> RimSample(List<int> all, int sample)
        {
            if (all.Count <= sample) return all;
            var picked = new List<int>(sample);
            float step = all.Count / (float)sample;
            for (int i = 0; i < sample; i++) picked.Add(all[(int)(i * step)]);
            return picked;
        }

        /// <summary>The closest pair (squared Euclidean, row-major cell indices over <paramref name="width"/>) between two cell lists; the first pair found wins a tie.</summary>
        public static bool ClosestPair(IList<int> ra, IList<int> rb, int width, out int ca, out int cb)
        {
            ca = cb = -1;
            long best = long.MaxValue;
            for (int i = 0; i < ra.Count; i++)
            {
                int ax = ra[i] % width, az = ra[i] / width;
                for (int j = 0; j < rb.Count; j++)
                {
                    int dx = ax - rb[j] % width, dz = az - rb[j] / width;
                    long d = (long)dx * dx + (long)dz * dz;
                    if (d < best)
                    {
                        best = d;
                        ca = ra[i];
                        cb = rb[j];
                    }
                }
            }
            return ca >= 0;
        }

        /// <summary>
        /// The road across a gap: 0 segments when the gap is shorter than <paramref name="minGapSpacings"/> spacings or longer than the cap;
        /// otherwise ceil(gap / spacing) segments of an even <paramref name="stride"/> (never more than the spacing).
        /// </summary>
        public static int RoadSegments(float gap, float spacing, float minGapSpacings, float maxGapCells, out float stride)
        {
            stride = 0f;
            if (gap < spacing * minGapSpacings || gap > maxGapCells) return 0;
            int segments = (int)Math.Ceiling(gap / spacing);
            stride = gap / segments;
            return segments;
        }

        /// <summary>The link indices along the road that get a wreck: 1..segments-1, except the last stop when a terminus takes it.</summary>
        public static List<int> RoadLinkIndices(int segments, bool terminus)
        {
            var ks = new List<int>();
            for (int k = 1; k < segments; k++)
            {
                if (terminus && k == segments - 1) break;
                ks.Add(k);
            }
            return ks;
        }

        /// <summary>
        /// The distance band (path cost to shade) the graves lie in: more than half a bare human's ring but no more than half a gear-bearer's;
        /// when gear does not help, the far fraction of the ring cap out to the cap.
        /// </summary>
        public static void GraveBand(int bareCost, int gearedCost, int capCost, float fallbackFarFraction, out int lo, out int hi)
        {
            if (gearedCost > bareCost)
            {
                lo = bareCost / 2 + 1;
                hi = gearedCost / 2;
            }
            else
            {
                lo = (int)Math.Round(capCost * fallbackFarFraction);
                hi = capCost;
            }
        }

        public static bool InGraveBand(int dist, int unreached, int lo, int hi)
        {
            return dist != unreached && dist >= lo && dist <= hi;
        }

        /// <summary>Two graves must be further apart than 20 cells (squared 400).</summary>
        public static bool GravesFarEnough(float squaredDistance) { return squaredDistance > 400f; }

        // ================================================================= Shipfall Commons
        /// <summary>
        /// How many rungs of the ladder are open <paramref name="elapsedTicks"/> after the ship arrived: the leading run of rungs whose delay has
        /// passed. A rung never opens before the rung listed ahead of it, so an unsorted list cannot open a later rung early.
        /// </summary>
        public static int OpenStages(IList<float> afterHours, int elapsedTicks, int ticksPerHour)
        {
            int open = 0;
            for (int i = 0; i < afterHours.Count; i++)
            {
                if (elapsedTicks >= (int)Math.Round(afterHours[i] * ticksPerHour)) open = i + 1;
                else break;
            }
            return open;
        }

        /// <summary>Whether a rung admits an animal: the race list (when it has one), the body-size cap (when positive), the herd rule.</summary>
        public static bool Admits(bool hasRaceRule, bool raceListed, float maxBodySize, float bodySize, bool herdOnly, bool isHerdAnimal)
        {
            if (hasRaceRule && !raceListed) return false;
            if (maxBodySize > 0f && bodySize > maxBodySize) return false;
            if (herdOnly && !isHerdAnimal) return false;
            return true;
        }

        /// <summary>The first of the open rungs that admits the animal, or -1.</summary>
        public static int FirstAdmitting(int stagesOpen, int stageCount, Func<int, bool> admits)
        {
            for (int i = 0; i < stagesOpen && i < stageCount; i++)
            {
                if (admits(i)) return i;
            }
            return -1;
        }

        /// <summary>A commons cell lies within <paramref name="radius"/> (inclusive, Euclidean) of a substructure cell.</summary>
        public static bool NearSubstructure(int x, int z, int radius, Func<int, int, bool> inSubstructure)
        {
            int r2 = radius * radius;
            for (int dz = -radius; dz <= radius; dz++)
            {
                for (int dx = -radius; dx <= radius; dx++)
                {
                    if (dx * dx + dz * dz <= r2 && inSubstructure(x + dx, z + dz)) return true;
                }
            }
            return false;
        }

        /// <summary>
        /// The commons: standable, shaded (at least <paramref name="minShade"/>) cells within the radius of the substructure and never on it,
        /// scanned over the substructure's bounding rectangle grown by the radius and clipped to the map.
        /// </summary>
        public static List<KeyValuePair<int, int>> CommonsCells(int subMinX, int subMinZ, int subMaxX, int subMaxZ, int radius, int mapW, int mapH,
            Func<int, int, bool> inSubstructure, Func<int, int, bool> standable, Func<int, int, float> shadeAt, float minShade)
        {
            var cells = new List<KeyValuePair<int, int>>();
            int x0 = Math.Max(0, subMinX - radius), x1 = Math.Min(mapW - 1, subMaxX + radius);
            int z0 = Math.Max(0, subMinZ - radius), z1 = Math.Min(mapH - 1, subMaxZ + radius);
            for (int z = z0; z <= z1; z++)
            {
                for (int x = x0; x <= x1; x++)
                {
                    if (inSubstructure(x, z) || !standable(x, z) || shadeAt(x, z) < minShade) continue;
                    if (!NearSubstructure(x, z, radius, inSubstructure)) continue;
                    cells.Add(new KeyValuePair<int, int>(x, z));
                }
            }
            return cells;
        }

        /// <summary>
        /// What the commons list was built from: the shade grid's version, the substructure's size and where the engine sits. The list is reused
        /// only while all three match AND it has not been cleared since; clearing the list must also drop the key, or a ship that leaves and
        /// lands again would be served the emptied list.
        /// </summary>
        public sealed class CommonsKey
        {
            private int gridVersion = -1, count = -1, engineX = int.MinValue, engineZ = int.MinValue;

            public bool Fresh(int version, int subCount, int ex, int ez)
            {
                return gridVersion == version && count == subCount && engineX == ex && engineZ == ez;
            }

            public void Set(int version, int subCount, int ex, int ez)
            {
                gridVersion = version;
                count = subCount;
                engineX = ex;
                engineZ = ez;
            }

            public void Invalidate()
            {
                gridVersion = -1;
                count = -1;
                engineX = int.MinValue;
                engineZ = int.MinValue;
            }
        }
    }
}
