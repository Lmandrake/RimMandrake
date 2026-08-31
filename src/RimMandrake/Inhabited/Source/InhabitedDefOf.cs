using RimWorld;
using RimWorld.Planet;
using Verse;
using Verse.AI;

namespace RimMandrake.Inhabited
{
    /// <summary>
    /// Every def this assembly names. DefOfHelper throws at startup if one is
    /// missing, which is the only early warning we get that a Defs file failed
    /// to load -- a patch that matches nothing logs nothing.
    /// </summary>
    [DefOf]
    public static class InhabitedDefOf
    {
        /// <summary>The one duty a resident ever holds. The ROUTE is the duty's
        /// focus moving, not the duty changing.</summary>
        public static DutyDef Inhabited_Resident;

        static InhabitedDefOf()
        {
            DefOfHelper.EnsureInitializedInCtor(typeof(InhabitedDefOf));
        }
    }
}
