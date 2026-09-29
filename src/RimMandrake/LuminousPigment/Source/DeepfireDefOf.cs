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

        static DeepfireDefOf()
        {
            DefOfHelper.EnsureInitializedInCtor(typeof(DeepfireDefOf));
        }
    }
}
