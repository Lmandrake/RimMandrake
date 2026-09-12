using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.CreatureBehaviors
{
    // WEBWORK_KIT_BUILD_1, mechanic 5 (webwork_kit_spec.md §5) — "anchor-
    // beetles hate the web instinctively... rising up to chew through anchor
    // lines." Written directly against the map's RM_MapComponent_SenseWeb
    // node list rather than a generic scanning surface, per the spec's own
    // §4-review precedent for JobGiver_Mine-shaped work ("write it directly,
    // no generalization surface").
    //
    // Destroying the target automatically deregisters it from the sense-web
    // (RM_CompSenseWebNode.PostDeSpawn) — chewing genuinely blinds the web
    // locally, with no extra notify needed here.
    public class RM_JobGiver_ChewAnchors : ThinkNode_JobGiver
    {
        // ❓INVENTED (spec §5: "chew rate = anchor HP vs beetle DPS", not a
        // search radius) — a live-balance pass is owed.
        private const float SearchRadius = 30f;

        protected override Job TryGiveJob(Pawn pawn)
        {
            if (!RM_CreatureBehaviorsSettings.chewAnchorsBehaviorEnabled)
            {
                return null;
            }

            RM_MapComponent_SenseWeb senseWeb = pawn.Map?.GetComponent<RM_MapComponent_SenseWeb>();
            if (senseWeb == null || !senseWeb.AnyRegisteredCells)
            {
                return null;
            }

            Thing target = GenClosest.ClosestThing_Global_Reachable(
                pawn.Position,
                pawn.Map,
                senseWeb.ChewableNodes,
                PathEndMode.Touch,
                TraverseParms.For(pawn),
                SearchRadius,
                t => !t.IsForbidden(pawn) && pawn.CanReserveAndReach(t, PathEndMode.Touch, Danger.Some));

            if (target == null)
            {
                return null;
            }

            Job job = JobMaker.MakeJob(JobDefOf.AttackMelee, target);
            job.expiryInterval = Rand.Range(420, 900);
            job.checkOverrideOnExpire = true;
            return job;
        }
    }
}
