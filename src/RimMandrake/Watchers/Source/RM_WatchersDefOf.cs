using RimWorld;
using Verse;

namespace RimMandrake.Watchers
{
    [DefOf]
    public static class RM_WatchersDefOf
    {
        public static JobDef RM_WatcherWatch;
        public static JobDef RM_WatcherRelocate;
        public static JobDef RM_WatcherFlush;
        public static DesignationDef RM_WatcherFlushMark;
        public static HediffDef RM_WatcherHidden;

        static RM_WatchersDefOf()
        {
            DefOfHelper.EnsureInitializedInCtor(typeof(RM_WatchersDefOf));
        }
    }
}
