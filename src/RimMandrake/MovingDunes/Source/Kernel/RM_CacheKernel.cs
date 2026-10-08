// Verse-free kernel of the dune burial rules (DuneBurialUtility.cs, Thing_BuriedCache.cs, MapComponent_DuneField.TryBuryAt):
// when a deposit buries, what may be buried, the cache cap, absorbing, and when a cache gives its contents back.
// SelfTest/MovingDunesFuzz.cs compiles this file alone: no Verse/RimWorld/UnityEngine.
using System;
using System.Collections.Generic;

namespace RimMandrake.MovingDunes
{
    public static class RM_CacheKernel
    {
        public const float VanillaRevealDepth = 0.25f;

        // A slab buries when it carries a cell up through the burial depth (not when it lands on an already buried cell).
        public static bool CrossedBurial(float before, float after, float burialDepth) { return after >= burialDepth && before < burialDepth; }

        // The burial gate: switched on, and a NEW cache cell only while under the per-map cap (existing cells still merge).
        public static bool BuryAllowed(bool enabled, bool cacheAlreadyAtCell, int cacheCount, int maxCaches)
        {
            if (!enabled) return false;
            if (!cacheAlreadyAtCell && cacheCount >= maxCaches) return false;
            return true;
        }

        public static bool IsBurialCandidate(bool spawned, bool destroyed, bool isCache, bool isItem, bool haulable, bool destroyOnDrop, bool inHome,
                                             bool inStorage, bool forbidden, bool reserved, float minMarketValue, float marketValue, int stackCount)
        {
            if (!spawned || destroyed) return false;
            if (isCache) return false;
            if (!isItem || !haulable) return false;
            if (destroyOnDrop || inHome || inStorage || forbidden || reserved) return false;
            if (minMarketValue > 0f && marketValue * stackCount < minMarketValue) return false;
            return true;
        }

        // A cache gives its contents back once the sand over it has fallen to the reveal depth; off a dune field it uses vanilla's.
        public static bool ShouldReveal(float depth, bool hasMaterial, float revealDepth) { return depth <= (hasMaterial ? revealDepth : VanillaRevealDepth); }

        // The older burial wins when two caches merge; an unset (negative) tick never beats a set one.
        public static int AbsorbTick(int myTick, int otherTick)
        {
            if (otherTick >= 0 && (myTick < 0 || otherTick < myTick)) return otherTick;
            return myTick;
        }

        // May this thing be put in the cache at all?
        public static bool Accepts(bool isNull, bool destroyed, bool isSelf) { return !(isNull || destroyed || isSelf); }
    }
}
