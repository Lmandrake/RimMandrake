// Verse-free kernel of the ledge refuge (RM_LedgeRefuge.cs): who seeks shelter, what each seeker is told to do and which ledge cell
// it is sent to. SelfTest/FloodedCanyonFuzz.cs compiles this file alone: no Verse/RimWorld/UnityEngine.
using System;
using System.Collections.Generic;

namespace RimMandrake.FloodedCanyon
{
    public static class RM_RefugeKernel
    {
        public const int MaxReachProbes = 12;
        public enum Action { Skip, Hold, Go, NoReach }

        // Our own trained animals and non-hostile humanlike people of other factions run for the ledges; nobody else does.
        public static bool IsSeeker(bool isNull, bool dead, bool downed, bool noFaction, bool noJobs, bool mental, bool drafted, bool prisoner,
                                    bool playerFaction, bool animal, bool trained, bool humanlike, bool hostileToPlayer)
        {
            if (isNull || dead || downed || noFaction || noJobs) return false;
            if (mental || drafted || prisoner) return false;
            if (playerFaction) return animal && trained;
            return humanlike && !hostileToPlayer;
        }

        // What the sweep does to one seeker: on a ledge it holds (unless already waiting); already walking to a ledge it is left be;
        // otherwise it is sent to the nearest reachable ledge cell (or reported unreachable).
        public static Action Decide(bool onLedge, bool alreadyWaiting, bool enRouteToLedge, bool destFound)
        {
            if (onLedge) return alreadyWaiting ? Action.Skip : Action.Hold;
            if (enRouteToLedge) return Action.Skip;
            return destFound ? Action.Go : Action.NoReach;
        }

        // The nearest ledge cell the seeker can reach: probes at most MaxReachProbes cells in order of distance, prefers an empty one,
        // and falls back to the first reachable occupied cell. Returns the cell index or -1.
        public static int NearestReachable(int n, int[] xs, int[] zs, int px, int pz, Func<int, bool> isEmpty, Func<int, bool> canReach)
        {
            var order = new List<int>();
            for (int i = 0; i < n; i++) order.Add(i);
            order.Sort((a, b) =>
            {
                long da = (long)(xs[a] - px) * (xs[a] - px) + (long)(zs[a] - pz) * (zs[a] - pz);
                long db = (long)(xs[b] - px) * (xs[b] - px) + (long)(zs[b] - pz) * (zs[b] - pz);
                int c = da.CompareTo(db);
                return c != 0 ? c : a.CompareTo(b);
            });
            int fallback = -1, probes = 0;
            for (int k = 0; k < order.Count && probes < MaxReachProbes; k++)
            {
                int i = order[k];
                bool empty = isEmpty(i);
                if (!empty && fallback >= 0) continue;
                probes++;
                if (!canReach(i)) continue;
                if (empty) return i;
                fallback = i;
            }
            return fallback;
        }

        // The anchor nearest a point (first of equals wins); with anchors switched off, the point itself.
        public static int NearestAnchor(bool anchorsOn, int n, int[] xs, int[] zs, int px, int pz)
        {
            if (!anchorsOn) return -1;
            int best = -1; float bestD = float.MaxValue;
            for (int i = 0; i < n; i++)
            {
                float dx = xs[i] - px, dz = zs[i] - pz;
                float d = dx * dx + dz * dz;
                if (d < bestD) { bestD = d; best = i; }
            }
            return best;
        }
    }
}
