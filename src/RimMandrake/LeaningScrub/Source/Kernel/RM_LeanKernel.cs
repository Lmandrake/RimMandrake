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

        // ── SCRUB_WIND_BUILD_LEAN_ON_PURPOSE: the visible lean (RM_PlantLean.cs) ──
        // Vanilla Plant.Print mirrors every plant mesh on a coin flip (Rand.Bool). On a leaning map a listed plant's mesh is
        // mirrored exactly when its art's own lean disagrees with the wind, so every listed plant on the map shows one lean.
        // Art leans EAST (screen right) unless its texture is listed as leaning west; the wind leans west only when the
        // downwind vector points west (x < 0). A due north/south wind has no screen lean and resolves EAST, one way, never mixed.
        public static bool WindLeansWest(float downwindX) { return downwindX < 0f; }

        // The mirror decision for one mesh: true = flip the UVs.
        public static bool FaceFlip(bool windWest, bool artWest) { return windWest != artWest; }

        // What the player sees after the flip: the art's lean, mirrored when flipped. Always equals windWest under FaceFlip.
        public static bool VisibleWest(bool artWest, bool flip) { return artWest != flip; }

        // "Things/Plant/RM_Fuzz/RM_Fuzz_c" -> "RM_Fuzz_c". Cache-build time only (it allocates).
        public static string TextureName(string path)
        {
            if (path == null) return "";
            int i = path.LastIndexOf('/');
            return i < 0 ? path : path.Substring(i + 1);
        }

        // Per-variant west-leaning flags for a graphic's sub-texture paths, from the biome's list of west-leaning texture
        // names (case-sensitive, like ContentFinder). Null when no variant is listed, so the caller can skip the peek.
        public static bool[] WestByVariant(IList<string> variantPaths, ICollection<string> westNames)
        {
            if (variantPaths == null || variantPaths.Count == 0 || westNames == null || westNames.Count == 0) return null;
            bool[] west = new bool[variantPaths.Count];
            bool any = false;
            for (int i = 0; i < west.Length; i++)
            {
                west[i] = westNames.Contains(TextureName(variantPaths[i]));
                any |= west[i];
            }
            return any ? west : null;
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
