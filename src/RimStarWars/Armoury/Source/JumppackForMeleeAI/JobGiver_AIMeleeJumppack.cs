using System.Collections.Generic;
using System.Linq;
using RimWorld;
using UnityEngine;
using Verse;
using Verse.AI;

namespace JumppackForMeleeAI;

internal class JobGiver_AIMeleeJumppack : ThinkNode_JobGiver
{
    private float minTargetDistance = 25f;

    public override ThinkNode DeepCopy(bool resolve = true)
    {
        JobGiver_AIMeleeJumppack copy = (JobGiver_AIMeleeJumppack)base.DeepCopy(resolve);
        copy.minTargetDistance = minTargetDistance;
        return copy;
    }

    protected override Job TryGiveJob(Pawn pawn)
    {
        if (!pawn.RaceProps.Humanlike || pawn.IsColonist)
        {
            return null;
        }
        Thing enemyTarget = pawn.mindState.enemyTarget;
        if (enemyTarget == null)
        {
            DebugPoint(pawn, "[jumppack]no target");
            return null;
        }
        Verb attackVerb = pawn.TryGetAttackVerb(enemyTarget, allowManualCastWeapons: false);
        if (attackVerb == null || !attackVerb.verbProps.IsMeleeAttack)
        {
            DebugPoint(pawn, "[jumppack]ranged");
            return null;
        }
        if (ReachabilityImmediate.CanReachImmediate(pawn, enemyTarget, PathEndMode.Touch))
        {
            DebugPoint(pawn, "[jumppack]reached, not required");
            return null;
        }
        if ((pawn.Position - enemyTarget.Position).LengthHorizontalSquared < minTargetDistance)
        {
            DebugPoint(pawn, "[jumppack]too close (distance:" + (pawn.Position - enemyTarget.Position).LengthHorizontalSquared + ")");
            return null;
        }
        Verb jumpVerb = TryGetJumpVerb(pawn, enemyTarget);
        if (jumpVerb == null)
        {
            DebugPoint(pawn, "[jumppack]no jump verb");
            return null;
        }
        DebugPoint(pawn, "[jumppack]distance: " + (pawn.Position - enemyTarget.Position).LengthHorizontalSquared);
        Job job = JobMaker.MakeJob(JumpJobDefOf.CastJumpOnce, enemyTarget);
        job.verbToUse = jumpVerb;
        return job;
    }

    private static void DebugPoint(Pawn pawn, string text)
    {
        if (!DebugSettings.godMode)
        {
            return;
        }
        Vector3 pos = pawn.DrawPosHeld ?? pawn.PositionHeld.ToVector3Shifted();
        MoteMaker.ThrowText(pos, pawn.MapHeld, text);
    }

    public static Verb TryGetJumpVerb(Pawn pawn, LocalTargetInfo target)
    {
        IEnumerable<Verb> jumpVerbs = pawn.VerbTracker.AllVerbs
            .Concat(pawn.equipment.AllEquipmentVerbs)
            .Concat(pawn.apparel.AllApparelVerbs)
            .Where((Verb t) => t is Verb_Jump);
        if (jumpVerbs.EnumerableNullOrEmpty())
        {
            return null;
        }
        return jumpVerbs.FirstOrDefault((Verb t) => t.IsStillUsableBy(pawn) && t.CanHitTarget(target));
    }
}
