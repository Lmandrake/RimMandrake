using System;
using System.Collections.Generic;
using System.Reflection;
using System.Reflection.Emit;
using HarmonyLib;
using Verse;
using Verse.AI;

namespace VEF.Weapons;

[HotSwappable]
[HarmonyPatch]
public static class VanillaExpandedFramework_Toils_Combat_FollowAndMeleeAttack_Patch
{
	public static FieldInfo targetInd;

	public static Pawn curPawn;

	public static void Prefix(Toil ___followAndAttack)
	{
		curPawn = ___followAndAttack.actor;
	}

	public static void Finalizer()
	{
		curPawn = null;
	}

	public static MethodBase TargetMethod()
	{
		Type[] nestedTypes = typeof(Toils_Combat).GetNestedTypes(AccessTools.all);
		foreach (Type type in nestedTypes)
		{
			MethodInfo[] methods = type.GetMethods(AccessTools.all);
			foreach (MethodInfo methodInfo in methods)
			{
				if (methodInfo.Name.Contains("<FollowAndMeleeAttack>"))
				{
					targetInd = type.GetField("targetInd");
					if (targetInd != null)
					{
						return methodInfo;
					}
				}
			}
		}
		return null;
	}

	public static IEnumerable<CodeInstruction> Transpiler(IEnumerable<CodeInstruction> codeInstructions)
	{
		foreach (CodeInstruction instruction in codeInstructions)
		{
			yield return instruction;
			if (instruction.opcode == OpCodes.Stloc_S && instruction.operand is LocalBuilder { LocalIndex: 8 })
			{
				yield return new CodeInstruction(OpCodes.Ldarg_0, (object)null);
				yield return new CodeInstruction(OpCodes.Ldfld, (object)targetInd);
				yield return new CodeInstruction(OpCodes.Ldloc_0, (object)null);
				yield return new CodeInstruction(OpCodes.Ldloca_S, (object)7);
				yield return new CodeInstruction(OpCodes.Ldloca_S, (object)8);
				yield return new CodeInstruction(OpCodes.Call, (object)AccessTools.Method(typeof(VanillaExpandedFramework_Toils_Combat_FollowAndMeleeAttack_Patch), "TryOverrideDestinationAndPathMode", (Type[])null, (Type[])null));
			}
		}
	}

	public static void TryOverrideDestinationAndPathMode(TargetIndex targetInd, Pawn actor, ref LocalTargetInfo destination, ref PathEndMode mode)
	{
		//IL_0011: Unknown result type (might be due to invalid IL or missing references)
		//IL_0012: Unknown result type (might be due to invalid IL or missing references)
		//IL_0017: Unknown result type (might be due to invalid IL or missing references)
		//IL_003c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0083: Unknown result type (might be due to invalid IL or missing references)
		//IL_009f: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a1: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a6: Unknown result type (might be due to invalid IL or missing references)
		curPawn = actor;
		LocalTargetInfo target = actor.jobs.curJob.GetTarget(targetInd);
		Thing thing = ((LocalTargetInfo)(ref target)).Thing;
		Verb meleeVerb = actor.GetMeleeVerb();
		float meleeReachRange = actor.GetMeleeReachRange(meleeVerb);
		if (meleeReachRange > 1.42f)
		{
			CastPositionRequest val = default(CastPositionRequest);
			val.caster = actor;
			val.target = thing;
			val.verb = meleeVerb;
			val.maxRangeFromTarget = meleeReachRange;
			val.wantCoverFromTarget = false;
			float range = meleeVerb.verbProps.range;
			meleeVerb.verbProps.range = meleeReachRange;
			IntVec3 val2 = default(IntVec3);
			if (!CastPositionFinder.TryFindCastPosition(val, ref val2))
			{
				actor.jobs.EndCurrentJob((JobCondition)4, true, true);
			}
			else
			{
				destination = LocalTargetInfo.op_Implicit(val2);
				mode = (PathEndMode)1;
			}
			meleeVerb.verbProps.range = range;
		}
	}
}
