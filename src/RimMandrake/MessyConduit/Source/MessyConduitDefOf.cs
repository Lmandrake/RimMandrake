using RimWorld;

namespace RimMandrake.MessyConduit
{
    [DefOf]
    public static class MessyConduitDefOf
    {
        /// <summary>Our own map-mesh change flag (Defs/MapMeshFlagDefs.xml): the cord component
        /// dirties a section with it when a cord that section owns changed elsewhere.</summary>
        public static MapMeshFlagDef RM_MessyCords;

        static MessyConduitDefOf() => DefOfHelper.EnsureInitializedInCtor(typeof(MessyConduitDefOf));
    }
}
