// Verse-free kernel of the Lean (RM_TheLean.cs): the wind heading, alignment, the scent gate, the downwind fire pick and
// the Shed V. SelfTest/LeaningScrubFuzz.cs compiles this file alone, so it must stay free of Verse/RimWorld/UnityEngine.
using System;
using System.Collections.Generic;

namespace RimMandrake.LeaningScrub
{
    public static class RM_LeanKernel
    {
        public const float ScentAlignment = 0.7f;   // within ~45 degrees of straight downwind
        public const float FireAlignment = 0.3f;    // a fire neighbour counts as downwind above this
        public const float Deg2Rad = 0.017453292f;  // UnityEngine.Mathf.Deg2Rad

        // The eight cells around a fire (any order: the pick among them is uniform).
        public static readonly int[] NeighbourDx = { 0, 1, 1, 1, 0, -1, -1, -1 };
        public static readonly int[] NeighbourDz = { 1, 1, 0, -1, -1, -1, 0, 1 };

        // The heading locks the first time it is asked for and never changes after (Scribed; -1 = not yet chosen).
        public static float LockHeading(float current, float roll0to360) { return current < 0f ? roll0to360 : current; }

        public static void Direction(float headingDegrees, out float x, out float z)
        {
            float r = headingDegrees * Deg2Rad;
            x = (float)Math.Cos(r);
            z = (float)Math.Sin(r);
        }

        // Cosine between "from -> to" and the downwind heading; 0 for a displacement under 0.1 of a cell.
        public static float Alignment(int dx, int dz, float dirX, float dirZ)
        {
            float sq = (float)dx * dx + (float)dz * dz;
            if (sq < 0.01f) return 0f;
            float mag = (float)Math.Sqrt(sq);
            return (dx / mag) * dirX + (dz / mag) * dirZ;
        }

        public static bool InHorDist(int dx, int dz, float range) { return (float)dx * dx + (float)dz * dz <= range * range; }

        // Verse's Rand.Chance with an injected roll in [0,1].
        public static bool Chance(float c, float roll) { return c >= 1f || (c > 0f && roll < c); }

        // Scent: the index of the first person who is alive, up, within range, upwind of the animal, and whom the animal can
        // flee (fleeOk), or -1. Persons are (dx,dz) = animal - person, the displacement scent travels along.
        public static int FirstScentThreat(int n, int[] dx, int[] dz, bool[] downedOrDead, float range, float dirX, float dirZ, Func<int, bool> fleeOk)
        {
            for (int i = 0; i < n; i++)
            {
                if (downedOrDead[i] || !InHorDist(dx[i], dz[i], range)) continue;
                if (Alignment(dx[i], dz[i], dirX, dirZ) < ScentAlignment) continue;
                if (fleeOk(i)) return i;
            }
            return -1;
        }

        // The neighbour indices (into NeighbourDx/Dz) that lie downwind of a fire.
        public static int DownwindNeighbours(float dirX, float dirZ, int[] outIdx)
        {
            int n = 0;
            for (int i = 0; i < 8; i++)
                if (Alignment(NeighbourDx[i], NeighbourDz[i], dirX, dirZ) > FireAlignment) outIdx[n++] = i;
            return n;
        }

        // Fire spread: -1 = vanilla's own omnidirectional roll runs; else the neighbour index to try.
        public static int FireSpreadPick(bool leanApplies, float bias, float biasRoll, float dirX, float dirZ, float pickRoll01)
        {
            if (!leanApplies || !Chance(bias, biasRoll)) return -1;
            int[] idx = new int[8];
            int n = DownwindNeighbours(dirX, dirZ, idx);
            if (n == 0) return -1;
            int k = (int)(pickRoll01 * n);
            if (k >= n) k = n - 1;
            return idx[k];
        }

        // Mathf.RoundToInt(dir * k): banker's rounding.
        public static void Step(int x, int z, float dirX, float dirZ, float k, out int ox, out int oz)
        {
            ox = x + (int)Math.Round(dirX * k);
            oz = z + (int)Math.Round(dirZ * k);
        }

        // The Shed V: for each distance d in 1..length the V is 2*(d/3)+1 cells wide; every cell passes one chance roll. The cells
        // that pass are appended (the caller still filters bounds and walkability).
        public static void ShedCells(int rootX, int rootZ, float dirX, float dirZ, int length, float cellChance, Func<float> roll, List<int> outX, List<int> outZ)
        {
            if (length < 1) length = 1;
            float sideX = -dirZ, sideZ = dirX;
            for (int d = 1; d <= length; d++)
            {
                int half = d / 3;
                for (int w = -half; w <= half; w++)
                {
                    if (!Chance(cellChance, roll())) continue;
                    outX.Add(rootX + (int)Math.Round(dirX * d + sideX * w));
                    outZ.Add(rootZ + (int)Math.Round(dirZ * d + sideZ * w));
                }
            }
        }
    }
}
