using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using System.Reflection.Emit;
using HarmonyLib;
using RimWorld;
using UnityEngine;
using Verse;

namespace VEF.Buildings;

[HarmonyPatch(typeof(CompBreakdownable), "CheckForBreakdown")]
public static class VanillaExpandedFramework_CompBreakdownable_CheckForBreakdown_Patch
{
	public static IEnumerable<CodeInstruction> Transpiler(IEnumerable<CodeInstruction> codeInstructions)
	{
		List<CodeInstruction> codes = codeInstructions.ToList();
		MethodInfo check = AccessTools.Method(typeof(VanillaExpandedFramework_CompBreakdownable_CheckForBreakdown_Patch), "AdjustMTB", (Type[])null, (Type[])null);
		for (int i = 0; i < codes.Count; i++)
		{
			if (codes[i].opcode == OpCodes.Ldc_R4 && codes[i].operand is float num && Mathf.Abs(num - 13680000f) < 0.01f)
			{
				yield return codes[i];
				yield return new CodeInstruction(OpCodes.Ldarg_0, (object)null);
				yield return new CodeInstruction(OpCodes.Call, (object)check);
			}
			else
			{
				yield return codes[i];
			}
		}
	}

	public static float AdjustMTB(float baseline, CompBreakdownable comp)
	{
		return baseline / StatExtension.GetStatValue((Thing)(object)((ThingComp)comp).parent, InternalDefOf.VEF_BuildingBreakdownFactor, true, -1);
	}
}
