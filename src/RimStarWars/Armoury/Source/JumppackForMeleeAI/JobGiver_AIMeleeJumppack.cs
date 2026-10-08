using System.Collections.Generic;
using System.Linq;
using RimMandrake.StarWars.Armoury;
using RimWorld;
using UnityEngine;
using Verse;
using Verse.AI;

namespace JumppackForMeleeAI;

internal class JobGiver_AIMeleeJumppack : ThinkNode_JobGiver
{
    private float minTargetDistance = RSW_CombatKernel.MeleeJumpMinDistSq;

    public override ThinkNode DeepCopy(bool resolve = true)
    {
        JobGiver_AIMeleeJumppack copy = (JobGiver_AIMeleeJumppack)base.DeepCopy(resolve);
        copy.minTargetDistance = minTargetDistance;
        return copy;
    }

    protected override Job TryGiveJob(Pawn pawn)
    {
        Thing enemyTarget = pawn.mindState.enemyTarget;
        Verb jumpVerb = null;
        if (!RSW_CombatKernel.MeleeJump(RSW_ArmourySettings.jumppackEnabled, pawn.RaceProps.Humanlike, pawn.IsColonist,
            () => { if (enemyTarget == null) { DebugPoint(pawn, "[jumppack]no target"); return false; } return true; },
            () =>
            {
                Verb attackVerb = pawn.TryGetAttackVerb(enemyTarget, allowManualCastWeapons: false);
                if (attackVerb == null || !attackVerb.verbProps.IsMeleeAttack) { DebugPoint(pawn, "[jumppack]ranged"); return false; }
                return true;
            },
            () =>
            {
                if (ReachabilityImmediate.CanReachImmediate(pawn, enemyTarget, PathEndMode.Touch)) { DebugPoint(pawn, "[jumppack]reached, not required"); return true; }
                return false;
            },
            () => (pawn.Position - enemyTarget.Position).LengthHorizontalSquared, minTargetDistance, RSW_ArmourySettings.jumppackDistanceFactor,
            () => (jumpVerb = TryGetJumpVerb(pawn, enemyTarget)) != null))
        {
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
