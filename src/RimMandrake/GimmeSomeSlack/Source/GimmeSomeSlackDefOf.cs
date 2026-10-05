using RimWorld;

namespace RimMandrake.GimmeSomeSlack
{
    [DefOf]
    public static class GimmeSomeSlackDefOf
    {
        /// <summary>Our own map-mesh change flag (Defs/MapMeshFlagDefs.xml): the cord component
        /// dirties a section with it when a cord that section owns changed elsewhere.</summary>
        public static MapMeshFlagDef RM_MessyCords;

        static GimmeSomeSlackDefOf() => DefOfHelper.EnsureInitializedInCtor(typeof(GimmeSomeSlackDefOf));
    }
}
