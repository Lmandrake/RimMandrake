using RimWorld;
using Verse;

namespace RimMandrake.LuminousPigment
{
    // DEEPFIRE_PAINT_LIVE_VERIFY_1, spec §10 step 5. Typed refs to the defs
    // this step's own code adds (Defs/ThingDefs_Misc/RM_DeepfireLightProxy.xml,
    // Defs/DesignationDefs/RM_DeepfireDesignations.xml,
    // Defs/JobDefs/RM_DeepfireJobs.xml). RM_Deepfire itself (the resource)
    // is looked up by string elsewhere in this mod (LuminousPigmentMod.cs's
    // own convention) rather than added here, to avoid a second lookup path
    // for a def piece 1 already owns.
    [DefOf]
    public static class DeepfireDefOf
    {
        public static ThingDef RM_DeepfireLightProxy;
        public static DesignationDef RM_ApplyDeepfireDesignation;
        public static JobDef RM_ApplyDeepfire;

        // DEEPFIRE_FLOOR_PAINT_1: the floor-cell branch.
        public static DesignationDef RM_ApplyDeepfireFloorDesignation;
        public static JobDef RM_ApplyDeepfireFloor;

        // DEEPFIRE_WORN_GLOW_1: the moving per-pawn proxy and the lacquer job.
        public static ThingDef RM_DeepfireWornLightProxy;
        public static JobDef RM_LacquerWornItem;

        // DEEPFIRE_STATUS_THOUGHTS_1: the room-stat reactions.
        public static ThoughtDef RM_DeepfireBedroom;
        public static HistoryEventDef RM_ImpressedByDeepfire;

        static DeepfireDefOf()
        {
            DefOfHelper.EnsureInitializedInCtor(typeof(DeepfireDefOf));
        }
    }
}
