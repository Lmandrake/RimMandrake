// Pure decision kernel of the ikee thought (JawaIkee): no Verse, no RimWorld, no UnityEngine.
using System;

namespace RimMandrake.StarWars.JawaIkee
{
    public static class RSW_IkeeKernel
    {
        public const int Inactive = -1, Comforted = 0, Unsettled = 1;
        public const float DefaultRadius = 12f;

        /// <summary>An ikee is "nearby" when its horizontal squared distance does not exceed the squared radius.</summary>
        public static bool Nearby(int dx, int dz, float radius) { float r2 = radius * radius; return !((float)(dx * dx + dz * dz) > r2); }

        /// <summary>The thought stage for one pawn. Inactive unless the thought is on and the pawn is a spawned humanlike with an ikee near;
        /// then comforted for a tolerant xenotype, unsettled for everyone else (a pawn with no genes is not tolerant).</summary>
        public static int Stage(bool enabled, bool spawnedOnMap, bool humanlike, Func<bool> ikeeNear, bool tolerantXenotype)
        {
            if (!enabled) return Inactive;
            if (!spawnedOnMap || !humanlike) return Inactive;
            if (!ikeeNear()) return Inactive;
            return tolerantXenotype ? Comforted : Unsettled;
        }
    }
}
