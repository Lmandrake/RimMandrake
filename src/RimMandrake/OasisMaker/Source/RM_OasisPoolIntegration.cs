using System;
using Verse;

namespace RimMandrake.OasisMaker
{
    /// <summary>
    /// OASIS_MAKER_BUILD_1 "watch out": the grown pool terrain must register
    /// with whatever pool-body bookkeeping STOCKED_POOL_BUILD_1 lands
    /// (RM_MapComponent_PoolStock) or a grown oasis is second-class to a
    /// natural one — the water-at-center ruling exists to prevent exactly
    /// that. STOCKED_POOL_BUILD_1 was still `proposed` (unclaimed, and
    /// RM_MapComponent_PoolStock did not exist yet anywhere on disk) when
    /// this mod was built, so guessing its class name/method signature would
    /// violate "never guess a defName, field, or namespace" for a type that
    /// is not there to check against.
    ///
    /// This is the emission side of the integration instead: a plain static
    /// C# event, no reflection, no assembly reference either direction.
    /// Whoever builds RM_MapComponent_PoolStock subscribes to
    /// PoolCellCreated (e.g. from its own MapComponent's FinalizeInit, or a
    /// static constructor) and registers the cell exactly as it would a
    /// natural pool cell found at map generation. If this mod's assembly
    /// never loads, the event simply has no publisher and nothing breaks.
    /// </summary>
    public static class RM_OasisPoolIntegration
    {
        /// <summary>map, cell, source ("RM_OasisMaker" — every event this
        /// mod raises carries the same source string, present for a future
        /// consumer that cares which mechanism made a given pool cell).</summary>
        public static event Action<Map, IntVec3, string> PoolCellCreated;

        public static void NotifyPoolCellCreated(Map map, IntVec3 cell)
        {
            PoolCellCreated?.Invoke(map, cell, "RM_OasisMaker");
        }
    }
}
