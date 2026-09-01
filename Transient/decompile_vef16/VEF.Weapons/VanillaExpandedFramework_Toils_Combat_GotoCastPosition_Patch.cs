using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using System.Reflection.Emit;
using HarmonyLib;
using Verse.AI;

namespace VEF.Weapons;

[HarmonyPatch]
public static class VanillaExpandedFramework_Toils_Combat_GotoCastPosition_Patch
{
	public static MethodBase TargetMethod()
	{
		return typeof(Toils_Combat).GetNestedTypes(AccessTools.all).SelectMany((Type innerType) => AccessTools.GetDeclaredMethods(innerType)).FirstOrDefault((MethodInfo method) => method.Name.Contains("<GotoCastPosition>") && method.ReturnType == typeof(void) && method.GetParameters().Length == 0);
	}

	public static IEnumerable<CodeInstruction> Transpiler(IEnumerable<CodeInstruction> instructions)
	{
		List<CodeInstruction> codes = instructions.ToList();
		for (int i = 0; i < codes.Count; i++)
		{
			if (codes[i].opcode == OpCodes.Ldc_R4 && CodeInstructionExtensions.OperandIs(codes[i], (object)1.42f))
			{
				yield return new CodeInstruction(OpCodes.Ldloc_0, (object)null);
				yield return new CodeInstruction(OpCodes.Ldloc_1, (object)null);
				yield return new CodeInstruction(OpCodes.Ldfld, (object)AccessTools.Field(typeof(Job), "verbToUse"));
				yield return new CodeInstruction(OpCodes.Call, (object)AccessTools.Method(typeof(MeleeReachCombatUtility), "GetMeleeReachRange", (Type[])null, (Type[])null));
			}
			else
			{
				yield return codes[i];
			}
		}
	}
}
