using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using System.Reflection.Emit;
using HarmonyLib;
using RimMandrake.StarWars.Armoury;
using RimWorld;
using Verse;
using Verse.AI;

namespace JumppackForMeleeAI;

[HarmonyPatch(typeof(JobGiver_AIFightEnemy), "TryGiveJob")]
public static class Patch_JobGiver_AIFightEnemy
{
    // ARMOURY_JUMPPACK_INVALID_IL_1: the old transpiler injected IL into
    // TryGiveJob and threw InvalidProgramException on first JIT, so the patch
    // never applied. A Postfix has no IL to get wrong. It swaps the vanilla
    // result (melee attack / shooting-position goto / wait) for a jump job
    // when GetJunpPack* offers one. PROVISIONAL: ranged also fires after vanilla's
    // cover/wait decision rather than before it as the transpiler did.
    [HarmonyPostfix]
    private static void Postfix(Pawn pawn, ref Job __result)
    {
        if (__result == null || pawn?.mindState?.enemyTarget == null || pawn.Map == null)
        {
            return;
        }
        JobDef def = __result.def;
        Job jump = null;
        if (def == JobDefOf.AttackMelee)
        {
            jump = GetJunpPackMelee(pawn);
        }
        else if (def == JobDefOf.Goto || def == JobDefOf.Wait_Combat)
        {
            jump = GetJunpPackRanged(pawn);
        }
        if (jump != null)
        {
            __result = jump;
        }
    }

    public static Job GetJunpPackMelee(Pawn pawn)
    {
        // MOD_OPTIONS_RETROFIT_1: mechanic off => null => the Postfix keeps
        // vanilla's job.
        if (!RSW_ArmourySettings.jumppackEnabled)
        {
            return null;
        }
        if (!pawn.RaceProps.Humanlike || pawn.IsColonist)
        {
            return null;
        }
        Thing enemyTarget = pawn.mindState.enemyTarget;
        if (ReachabilityImmediate.CanReachImmediate(pawn, enemyTarget, PathEndMode.Touch))
        {
            return null;
        }
        if ((pawn.Position - enemyTarget.Position).LengthHorizontalSquared < RSW_ArmourySettings.ScaleSquaredDistance(16f))
        {
            return null;
        }
        Verb jumpVerb = JobGiver_AIMeleeJumppack.TryGetJumpVerb(pawn, enemyTarget);
        if (jumpVerb == null)
        {
            return null;
        }
        Job job = JobMaker.MakeJob(JumpJobDefOf.CastJumpOnce, enemyTarget);
        job.verbToUse = jumpVerb;
        return job;
    }

    public static Job GetJunpPackRanged(Pawn pawn)
    {
        if (!RSW_ArmourySettings.jumppackEnabled || !RSW_ArmourySettings.jumppackFlankRanged)
        {
            return null;
        }
        if (!pawn.RaceProps.Humanlike || pawn.IsColonist)
        {
            return null;
        }
        Thing enemyTarget = pawn.mindState.enemyTarget;
        List<CoverInfo> covers = CoverUtility.CalculateCoverGiverSet(enemyTarget, pawn.Position, pawn.Map);
        if (covers.NullOrEmpty() || covers.All((CoverInfo t) => t.BlockChance < 0.3f))
        {
            return null;
        }
        IntVec3 behindTarget = enemyTarget.Position + pawn.Rotation.FacingCell * 3;
        Verb jumpVerb = JobGiver_AIMeleeJumppack.TryGetJumpVerb(pawn, behindTarget);
        if (jumpVerb != null)
        {
            Job job = JobMaker.MakeJob(JumpJobDefOf.CastJumpOnce, behindTarget);
            job.verbToUse = jumpVerb;
            return job;
        }
        IntVec3 inFrontOfTarget = enemyTarget.Position - pawn.Rotation.FacingCell;
        Verb jumpVerb2 = JobGiver_AIMeleeJumppack.TryGetJumpVerb(pawn, inFrontOfTarget);
        if (jumpVerb2 == null)
        {
            return null;
        }
        Job job2 = JobMaker.MakeJob(JumpJobDefOf.CastJumpOnce, inFrontOfTarget);
        job2.verbToUse = jumpVerb2;
        return job2;
    }
}
