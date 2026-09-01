using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using System.Reflection.Emit;
using HarmonyLib;
using RimWorld;
using Verse;

namespace VEF.Pawns;

[HarmonyPatch(typeof(HediffGiver_Heat), "OnIntervalPassed")]
public static class VanillaExpandedFramework_HediffGiver_Heat_OnIntervalPassed_Patch
{
	public static IEnumerable<CodeInstruction> Transpiler(IEnumerable<CodeInstruction> codeInstructions)
	{
		List<CodeInstruction> codes = codeInstructions.ToList();
		MethodInfo ModifyHeatstrokeSeverityAdvance = AccessTools.Method(typeof(VanillaExpandedFramework_HediffGiver_Heat_OnIntervalPassed_Patch), "ModifyHeatstrokeSeverityAdvance", (Type[])null, (Type[])null);
		FieldInfo hediffField = AccessTools.DeclaredField(typeof(HediffGiver), "hediff");
		for (int i = 0; i < codes.Count; i++)
		{
			if (i > 0 && CodeInstructionExtensions.LoadsField(codes[i - 1], hediffField, false) && codes[i].opcode == OpCodes.Ldloc_S && codes[i].operand is LocalBuilder { LocalIndex: 5 })
			{
				yield return new CodeInstruction(OpCodes.Ldarg_1, (object)null);
				yield return codes[i];
				yield return new CodeInstruction(OpCodes.Call, (object)ModifyHeatstrokeSeverityAdvance);
			}
			else
			{
				yield return codes[i];
			}
		}
	}

	public static float ModifyHeatstrokeSeverityAdvance(Pawn p, float rate)
	{
		if (p != null)
		{
			float statValue = StatExtension.GetStatValue((Thing)(object)p, InternalDefOf.VEF_HeatstrokeBuildupMultiplier, true, -1);
			return rate * statValue;
		}
		return rate;
	}
}
