// Verse-free kernel of the murrek reseed after an ice-sand drift (RM_MurrekDrift.cs): where idle murrek burrow and where new ones
// surface. SelfTest/BlueDesertFuzz.cs compiles this file alone: no Verse/RimWorld/UnityEngine.
using System;
using System.Collections.Generic;
using System.Linq;

namespace RimMandrake.BlueDesert
{
    public static class RM_MurrekKernel
    {
        public sealed class Plan
        {
            public readonly List<int[]> Burrows = new List<int[]>();   // murrek index, x, z
            public readonly List<int[]> Spawns = new List<int[]>();    // x, z
        }

        public static bool Clear(int x, int z, List<int[]> taken, float spacing)
        {
            float sq = spacing * spacing;
            for (int i = 0; i < taken.Count; i++)
            {
                float dx = taken[i][0] - x, dz = taken[i][1] - z;
                if (dx * dx + dz * dz < sq) return false;
            }
            return true;
        }

        // drift cells are candidates (x,z). murrek: position, eligible (idle, wild, not hungry...), busyTarget (their current burrow cell, if any).
        // Each eligible murrek takes the nearest reachable drift cell within the search radius that keeps minSpacing from every taken cell
        // (considering the 12 nearest); then up to min(newRolled, maxOnMap - murrekCount) new murrek surface on the spawnable cells (given in random order).
        public static Plan Make(int nDrift, int[] dx, int[] dz, int nMurrek, int[] mx, int[] mz, bool[] eligible, bool[] hasBurrow, int[] bx, int[] bz,
                                float searchRadius, float spacing, int newRolled, int maxOnMap, bool ecosystemFull,
                                int nSpawnable, int[] spx, int[] spz, Func<int, int, int, bool> canReach)
        {
            var plan = new Plan();
            var taken = new List<int[]>();
            for (int i = 0; i < nMurrek; i++) if (hasBurrow[i]) taken.Add(new[] { bx[i], bz[i] });
            for (int m = 0; m < nMurrek; m++)
            {
                if (!eligible[m]) continue;
                float maxSq = searchRadius * searchRadius;
                var cand = new List<int>();
                for (int c = 0; c < nDrift; c++)
                {
                    float ddx = dx[c] - mx[m], ddz = dz[c] - mz[m];
                    if (ddx * ddx + ddz * ddz <= maxSq && Clear(dx[c], dz[c], taken, spacing)) cand.Add(c);
                }
                var ordered = cand.Select((c, k) => new { c, k }).OrderBy(t => { float ddx = dx[t.c] - mx[m], ddz = dz[t.c] - mz[m]; return ddx * ddx + ddz * ddz; }).ThenBy(t => t.k).Take(12).Select(t => t.c);
                foreach (int c in ordered)
                {
                    if (!canReach(m, dx[c], dz[c])) continue;
                    taken.Add(new[] { dx[c], dz[c] });
                    plan.Burrows.Add(new[] { m, dx[c], dz[c] });
                    break;
                }
            }
            int toSpawn = Math.Min(newRolled, maxOnMap - nMurrek);
            if (toSpawn <= 0 || ecosystemFull) return plan;
            for (int s = 0; s < nSpawnable; s++)
            {
                if (toSpawn <= 0) break;
                if (!Clear(spx[s], spz[s], taken, spacing)) continue;
                plan.Spawns.Add(new[] { spx[s], spz[s] });
                taken.Add(new[] { spx[s], spz[s] });
                toSpawn--;
            }
            return plan;
        }

        // The buried murrek's check (every 30 ticks): 0 stay buried, 1 job ends incompletable, 2 job ends succeeded (gets up), 3 ambush.
        public static int LieBuried(bool propsMissingOrDisabled, bool mapOrGridMissing, float depthHere, float flushDepth, int now, int buriedSince, int maxBuriedTicks,
                                    bool urgentlyHungry, bool veryTired, bool preyInReach)
        {
            if (propsMissingOrDisabled) return 1;
            if (mapOrGridMissing || depthHere < flushDepth) return 1;
            if (now - buriedSince > maxBuriedTicks) return 2;
            if (urgentlyHungry || veryTired) return 2;
            return preyInReach ? 3 : 0;
        }
    }
}
