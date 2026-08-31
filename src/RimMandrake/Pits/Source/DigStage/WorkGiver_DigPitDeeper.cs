using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.Pits
{
    // Modeled directly on RimWorld/WorkGiver_FillIn : WorkGiver_RemoveBuilding -
    // the vanilla precedent for "designate a thing, a pawn walks up and works
    // on it with a progress bar until a callback fires."
    public class WorkGiver_DigPitDeeper : WorkGiver_RemoveBuilding
    {
        protected override DesignationDef Designation => RMPits_DesignationDefOf.RM_DigPitDeeper;

        protected override JobDef RemoveBuildingJob => RMPits_JobDefOf.RM_DigPitDeeper;
    }
}
