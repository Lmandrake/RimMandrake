// Verse-free kernel of the aerosol screen (RM_CompAerosolScreen): radius, liveness and the coverage union.
// RM_AerosolScreen.cs calls these with the same expressions it used inline; SelfTest/ScarlandsFuzz.cs compiles this
// file alone (no RimWorld/Unity), so a `using Verse;` landing here breaks that build - the guard rail.
using System.Collections.Generic;

namespace RimMandrake.Scarlands
{
    // What the coverage union needs from a registered screen. CountsFor is "non-null, registered on THIS map, and live".
    public interface IAerosolScreenView
    {
        bool CountsFor(object map);
        int ScreenX { get; }
        int ScreenZ { get; }
        float ScreenRadius { get; }
    }

    public static class RM_AerosolKernel
    {
        // Settings-scaled radius; a refuelable parent with an empty gel feed halves it (spec 4). No refuelable: full.
        public static float Radius(float propsRadius, float radiusFactor, bool hasRefuelable, bool hasFuel)
        {
            float r = propsRadius * radiusFactor;
            if (hasRefuelable && !hasFuel) r *= 0.5f;
            return r;
        }

        // Self-powered screens (needsPower=false) ignore power entirely; a missing power comp counts as powered.
        public static bool IsLive(bool spawned, bool hasFlickable, bool switchOn, bool needsPower, bool hasPowerTrader, bool powerOn)
        {
            if (!spawned) return false;
            if (hasFlickable && !switchOn) return false;
            if (needsPower && hasPowerTrader && !powerOn) return false;
            return true;
        }

        // IntVec3.DistanceToSquared(b) is dx*dx+dz*dz in int; compared against the float r*r.
        public static bool Covers(int cx, int cz, int sx, int sz, float r)
        {
            int dx = cx - sx;
            int dz = cz - sz;
            return dx * dx + dz * dz <= r * r;
        }

        // True iff the setting is on and some counting screen's radius reaches the cell. Never a whole-map scan.
        public static bool Screened<T>(bool enabled, object map, int cx, int cz, List<T> screens) where T : class, IAerosolScreenView
        {
            if (!enabled || map == null) return false;
            for (int i = 0; i < screens.Count; i++)
            {
                T s = screens[i];
                if (s == null || !s.CountsFor(map)) continue;
                if (Covers(cx, cz, s.ScreenX, s.ScreenZ, s.ScreenRadius)) return true;
            }
            return false;
        }
    }
}
