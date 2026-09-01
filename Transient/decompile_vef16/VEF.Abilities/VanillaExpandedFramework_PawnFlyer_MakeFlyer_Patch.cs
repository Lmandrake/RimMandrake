using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using System.Reflection.Emit;
using HarmonyLib;
using RimWorld;
using Verse;
using Verse.AI;

namespace VEF.Abilities;

[HarmonyPatch(typeof(PawnFlyer), "MakeFlyer")]
public static class VanillaExpandedFramework_PawnFlyer_MakeFlyer_Patch
{
	private static FieldInfo jobdef = AccessTools.Field(typeof(Job), "def");

	private static FieldInfo castJump = AccessTools.Field(typeof(JobDefOf), "CastJump");

	private static MethodInfo myMethod = AccessTools.Method(typeof(VanillaExpandedFramework_PawnFlyer_MakeFlyer_Patch), "ShouldEndJob", (Type[])null, (Type[])null);

	private static IEnumerable<CodeInstruction> Transpiler(IEnumerable<CodeInstruction> instructions)
	{
		List<CodeInstruction> codes = instructions.ToList();
		for (int i = 0; i < codes.Count; i++)
		{
			if (CodeInstructionExtensions.LoadsField(codes[i], jobdef, false))
			{
				yield return codes[i];
				yield return new CodeInstruction(OpCodes.Ldarg_0, (object)null);
				yield return new CodeInstruction(OpCodes.Call, (object)myMethod);
				yield return new CodeInstruction(OpCodes.Brfalse_S, codes[i + 2].operand);
			}
			else if (!CodeInstructionExtensions.LoadsField(codes[i], castJump, false) && (!(codes[i].opcode == OpCodes.Bne_Un_S) || !CodeInstructionExtensions.LoadsField(codes[i - 1], castJump, false)))
			{
				if (codes[i].opcode == OpCodes.Stloc_0)
				{
					yield return codes[i];
					yield return CodeInstruction.LoadLocal(0, false);
					yield return CodeInstruction.LoadArgument(1, false);
					yield return CodeInstruction.Call(typeof(VanillaExpandedFramework_PawnFlyer_MakeFlyer_Patch), "SetSelectOnSpawn", (Type[])null, (Type[])null);
				}
				else
				{
					yield return codes[i];
				}
			}
		}
	}

	public static bool ShouldEndJob(JobDef jobDef, ThingDef thingDef)
	{
		if (jobDef == JobDefOf.CastJump || typeof(AbilityPawnFlyer).IsAssignableFrom(thingDef.thingClass))
		{
			return true;
		}
		return false;
	}

	public static void SetSelectOnSpawn(PawnFlyer flyer, Pawn pawn)
	{
		if (flyer is AbilityPawnFlyer abilityPawnFlyer && Find.Selector.IsSelected((object)pawn) && abilityPawnFlyer.AutoSelectPawn(pawn))
		{
			abilityPawnFlyer.selectOnSpawn = true;
		}
	}
}
