using System.Linq;
using Verse;
using Verse.AI;

namespace JumppackForMeleeAI;

public class JobDriver_CastJumpOnce : JobDriver_CastVerbOnce
{
    public override bool TryMakePreToilReservations(bool errorOnFailed)
    {
        Thing enemyTarget = pawn.mindState.enemyTarget;
        if (enemyTarget != null && enemyTarget.Position.DistanceToSquared(pawn.Position) < 10)
        {
            return false;
        }
        if (pawn.jobs.AllJobs().Count((Job t) => t.def == JumpJobDefOf.CastJumpOnce) > 1)
        {
            return false;
        }
        return true;
    }
}
