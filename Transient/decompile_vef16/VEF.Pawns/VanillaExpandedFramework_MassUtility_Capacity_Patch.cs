using System;
using System.Collections.Generic;
using System.Reflection;
using System.Reflection.Emit;
using HarmonyLib;
using RimWorld;
using Verse;

namespace VEF.Pawns;

[HarmonyPatch(typeof(MassUtility), "Capacity")]
public static class VanillaExpandedFramework_MassUtility_Capacity_Patch
{
	public static bool includeStatWorkerResult = true;

	public static MethodInfo SetCarryCapacityInfo = AccessTools.Method(typeof(VanillaExpandedFramework_MassUtility_Capacity_Patch), "SetCarryCapacity", (Type[])null, (Type[])null);

	public static IEnumerable<CodeInstruction> Transpiler(IEnumerable<CodeInstruction> codeInstructions)
	{
		foreach (CodeInstruction code in codeInstructions)
		{
			yield return code;
			if (code.opcode == OpCodes.Stloc_0)
			{
				yield return new CodeInstruction(OpCodes.Ldarg_0, (object)null);
				yield return new CodeInstruction(OpCodes.Ldloca_S, (object)0);
				yield return new CodeInstruction(OpCodes.Call, (object)SetCarryCapacityInfo);
			}
		}
	}

	public static void SetCarryCapacity(Pawn p, ref float __result)
	{
		if (includeStatWorkerResult)
		{
			__result = StatExtension.GetStatValue((Thing)(object)p, VEFDefOf.VEF_MassCarryCapacity, true, -1);
		}
	}
}
