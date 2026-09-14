using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.EnvironmentalHazards
{
    // GREENTIDE_MECHANICS_2 M6 build, feller 3 ("gnawed from below"). Written
    // directly for this one job, not a generic extension-driven scanner —
    // same posture RM_JobGiver_ChewAnchors already set in this repo for
    // JobGiver_Mine-shaped work ("write it directly per creature", per that
    // item's own review note), not RM_JobGiver_GnawTargets' more general
    // shape. Lives in EnvironmentalHazards (not CreatureBehaviors) because it
    // calls RM_TreeFallUtility/RM_FellableTreeExtension directly — same
    // assembly as what it drives, no new cross-project reference needed.
    public class RM_JobGiver_GnawTreeBase : ThinkNode_JobGiver
    {
        protected override Job TryGiveJob(Pawn pawn)
        {
            if (!RM_EnvironmentalHazardsSettings.treeFallEnabled)
            {
                return null;
            }

            RM_GnawTreeBaseExtension ext = pawn.def?.GetModExtension<RM_GnawTreeBaseExtension>();
            if (ext == null || pawn.Map == null)
            {
                return null;
            }

            Thing target = GenClosest.ClosestThingReachable(
                pawn.Position,
                pawn.Map,
                ThingRequest.ForGroup(ThingRequestGroup.Plant),
                PathEndMode.Touch,
                TraverseParms.For(pawn),
                ext.searchRadius,
                t => t is Plant p && p.def.GetModExtension<RM_FellableTreeExtension>() != null
                     && !t.IsForbidden(pawn) && pawn.CanReserveAndReach(t, PathEndMode.Touch, Danger.Some));

            if (target == null)
            {
                return null;
            }

            return JobMaker.MakeJob(RM_EnvironmentalHazardsJobDefOf.RM_GnawTreeBase, target);
        }
    }
}
