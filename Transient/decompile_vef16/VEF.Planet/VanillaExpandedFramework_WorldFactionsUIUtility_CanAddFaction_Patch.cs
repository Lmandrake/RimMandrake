using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using System.Reflection.Emit;
using HarmonyLib;
using RimWorld.Planet;

namespace VEF.Planet;

[HarmonyPatch]
public static class VanillaExpandedFramework_WorldFactionsUIUtility_CanAddFaction_Patch
{
	[HarmonyTargetMethod]
	public static MethodBase TargetMethod()
	{
		return typeof(WorldFactionsUIUtility).GetNestedTypes(AccessTools.all).SelectMany((Type nestedType) => AccessTools.GetDeclaredMethods(nestedType)).FirstOrDefault((MethodInfo declaredMethod) => declaredMethod.Name.Contains("CanAddFaction"));
	}

	[HarmonyTranspiler]
	public static IEnumerable<CodeInstruction> Transpiler(IEnumerable<CodeInstruction> instructions)
	{
		foreach (CodeInstruction instruction in instructions)
		{
			if (instruction.opcode == OpCodes.Ldc_I4_S && CodeInstructionExtensions.OperandIs(instruction, (object)12))
			{
				yield return new CodeInstruction(OpCodes.Ldc_I4, (object)99);
			}
			else
			{
				yield return instruction;
			}
		}
	}
}
