using System.Collections.Generic;
using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.DivingInteraction
{
    // SCALD_WALKING_PASTURE_1 — the crew follows the herd. Offers only the loose pigment mat lying
    // within FollowRadius of a living walker, so the work moves wherever the herd grazes. It stops
    // by itself when the herd turns: no job is offered for a mat with a MOVING walker within
    // TurnRadius, and none for a mat or a worker inside BackOffRadius of any walker (never crowd it).
    // The haul itself is vanilla (HaulAIUtility), so storage, forbids and reservations all apply.
    public class RM_WorkGiver_GatherGrazedMat : WorkGiver_Scanner
    {
        public const float FollowRadius = 12f;
        public const float TurnRadius = 6f;
        public const float BackOffRadius = 3.5f;

        public override PathEndMode PathEndMode => PathEndMode.ClosestTouch;

        public override bool ShouldSkip(Pawn pawn, bool forced = false)
        {
            return !RM_DivingSettings.masterEnabled || !RM_DivingSettings.walkerGrazingEnabled
                || RM_MapComponent_ScaldWalkerGrazing.WalkerDef == null
                || RM_MapComponent_ScaldWalkerGrazing.FreshMatDef == null;
        }

        public override IEnumerable<Thing> PotentialWorkThingsGlobal(Pawn pawn)
        {
            ThingDef fresh = RM_MapComponent_ScaldWalkerGrazing.FreshMatDef;
            if (fresh == null)
            {
                return new List<Thing>();
            }
            return pawn.Map.listerThings.ThingsOfDef(fresh);
        }

        public override Job JobOnThing(Pawn pawn, Thing t, bool forced = false)
        {
            Map map = pawn.Map;
            if (t.IsForbidden(pawn) || t.IsInAnyStorage()
                || !RM_MapComponent_ScaldWalkerGrazing.WalkerNear(map, t.Position, FollowRadius, false)
                || RM_MapComponent_ScaldWalkerGrazing.WalkerNear(map, t.Position, TurnRadius, true)
                || RM_MapComponent_ScaldWalkerGrazing.WalkerNear(map, t.Position, BackOffRadius, false)
                || RM_MapComponent_ScaldWalkerGrazing.WalkerNear(map, pawn.Position, BackOffRadius, false))
            {
                return null;
            }
            if (!HaulAIUtility.PawnCanAutomaticallyHaulFast(pawn, t, forced))
            {
                return null;
            }
            return HaulAIUtility.HaulToStorageJob(pawn, t, forced);
        }
    }
}
