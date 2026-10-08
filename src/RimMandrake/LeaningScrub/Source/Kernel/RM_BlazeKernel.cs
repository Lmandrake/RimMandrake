// Verse-free kernel of the fire-stamping giants (RM_FireStamp.cs): which open-fire cluster is the blaze, who is sent to it, who
// stamps what. SelfTest/LeaningScrubFuzz.cs compiles this file alone: no Verse/RimWorld/UnityEngine.
using System;

namespace RimMandrake.LeaningScrub
{
    public static class RM_BlazeKernel
    {
        public const int MinOpenFires = 5;
        public const float ClusterRadius = 6f;
        public const float StampRadius = 2.9f;

        public static bool InHorDist(int ax, int az, int bx, int bz, float r)
        {
            float dx = ax - bx, dz = az - bz;
            return dx * dx + dz * dz <= r * r;
        }

        // The index of the fire at the centre of the largest cluster of at least minFires (each fire counts the fires within
        // radius of it, itself included); the first such fire wins a tie. -1 when no cluster is big enough.
        public static int FindBlaze(int n, int[] xs, int[] zs, int minFires, float radius)
        {
            int best = -1, bestN = minFires - 1;
            for (int i = 0; i < n; i++)
            {
                int c = 0;
                for (int j = 0; j < n; j++) if (InHorDist(xs[i], zs[i], xs[j], zs[j], radius)) c++;
                if (c > bestN) { bestN = c; best = i; }
            }
            return best;
        }

        // ConvergePass, per available stamper: 0 = ignore (already at the blaze), 1 = already walking there (counts as sent),
        // 2 = dispatch a new Goto.
        public static int ConvergeAction(int px, int pz, int bx, int bz, bool onGotoNearBlaze, int gotoX, int gotoZ)
        {
            if (InHorDist(px, pz, bx, bz, StampRadius)) return 0;
            if (onGotoNearBlaze && InHorDist(gotoX, gotoZ, bx, bz, ClusterRadius)) return 1;
            return 2;
        }

        // A message goes out for a blaze only when it is not the one already known (within two cluster radii).
        public static bool NewBlaze(bool haveLast, int lx, int lz, int bx, int bz)
        {
            return !haveLast || !InHorDist(lx, lz, bx, bz, ClusterRadius * 2f);
        }

        public static bool Stamps(int sx, int sz, int fx, int fz) { return InHorDist(sx, sz, fx, fz, StampRadius); }
    }
}
