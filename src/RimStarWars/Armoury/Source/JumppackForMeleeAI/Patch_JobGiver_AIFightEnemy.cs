using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using System.Reflection.Emit;
using HarmonyLib;
using RimWorld;
using Verse;
using Verse.AI;

namespace JumppackForMeleeAI;

[HarmonyPatch(typeof(JobGiver_AIFightEnemy), "TryGiveJob")]
public static class Patch_JobGiver_AIFightEnemy
{
    [HarmonyTranspiler]
    private static IEnumerable<CodeInstruction> Transpiler(IEnumerable<CodeInstruction> instructions, ILGenerator generator)
    {
        // LOCAL, not a static field: Harmony re-runs every transpiler on a
        // target method whenever any mod adds a further patch to it later
        // (ordinary for JobGiver_AIFightEnemy.TryGiveJob, which combat/AI
        // mods routinely touch). A static counter left at 2 from the first
        // run would skip the melee injection entirely on the second run AND
        // disable the "< 2" failure warning below that exists to catch
        // exactly this.
        int patchCount = 0;
        List<CodeInstruction> list = instructions.ToList();
        MethodInfo isMeleeAttackGetter = AccessTools.Method(typeof(VerbProperties), "get_IsMeleeAttack");
        MethodInfo localTargetInfoImplicit = AccessTools.Method(typeof(LocalTargetInfo), "op_Implicit", new[] { typeof(Thing) });
        for (int i = 0; i < list.Count; i++)
        {
            if (patchCount == 0)
            {
                if (list[i].opcode == OpCodes.Callvirt && (MethodInfo)list[i].operand == isMeleeAttackGetter)
                {
                    patchCount++;
                    Label label = generator.DefineLabel();
                    CodeInstruction popInstruction = new CodeInstruction(OpCodes.Pop);
                    popInstruction.labels.Add(label);
                    list.InsertRange(i + 2, new[]
                    {
                        new CodeInstruction(OpCodes.Ldarg_1),
                        new CodeInstruction(OpCodes.Call, AccessTools.Method(typeof(Patch_JobGiver_AIFightEnemy), nameof(GetJunpPackMelee))),
                        new CodeInstruction(OpCodes.Dup),
                        new CodeInstruction(OpCodes.Brfalse_S, label),
                        new CodeInstruction(OpCodes.Ret),
                        popInstruction
                    });
                }
            }
            else if (list[i].opcode == OpCodes.Call && (MethodInfo)list[i].operand == localTargetInfoImplicit)
            {
                patchCount++;
                Label label2 = generator.DefineLabel();
                CodeInstruction popInstruction2 = new CodeInstruction(OpCodes.Pop);
                popInstruction2.labels.Add(label2);
                list.InsertRange(i, new[]
                {
                    new CodeInstruction(OpCodes.Call, AccessTools.Method(typeof(Patch_JobGiver_AIFightEnemy), nameof(GetJunpPackRanged))),
                    new CodeInstruction(OpCodes.Dup),
                    new CodeInstruction(OpCodes.Brfalse_S, label2),
                    new CodeInstruction(OpCodes.Ret),
                    popInstruction2,
                    new CodeInstruction(OpCodes.Ldarg_1)
                });
                break;
            }
        }
        if (patchCount < 2)
        {
            Log.Warning("[JumppackForMeleeAI]Patch_JobGiver_AIFightEnemy failed!");
        }
        return list;
    }

    public static Job GetJunpPackMelee(Pawn pawn)
    {
        if (!pawn.RaceProps.Humanlike || pawn.IsColonist)
        {
            return null;
        }
        Thing enemyTarget = pawn.mindState.enemyTarget;
        if (ReachabilityImmediate.CanReachImmediate(pawn, enemyTarget, PathEndMode.Touch))
        {
            return null;
        }
        if ((pawn.Position - enemyTarget.Position).LengthHorizontalSquared < 16f)
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
