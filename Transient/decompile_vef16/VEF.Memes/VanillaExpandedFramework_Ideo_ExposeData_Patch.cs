using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using System.Reflection.Emit;
using HarmonyLib;
using RimWorld;
using UnityEngine;
using Verse;

namespace VEF.Memes;

[HarmonyPatch(typeof(Ideo))]
[HarmonyPatch("ExposeData")]
public static class VanillaExpandedFramework_Ideo_ExposeData_Patch
{
	private static MethodInfo AddPrecept = AccessTools.Method(typeof(Ideo), "AddPrecept", (Type[])null, (Type[])null);

	private static MethodInfo DebugLog = AccessTools.Method(typeof(Log), "Warning", new Type[1] { typeof(string) }, (Type[])null);

	private static IEnumerable<CodeInstruction> Transpiler(IEnumerable<CodeInstruction> instructions)
	{
		List<CodeInstruction> codes = instructions.ToList();
		bool found = false;
		int debugCall = 0;
		for (int i = 0; i < codes.Count; i++)
		{
			yield return codes[i];
			if (!found && CodeInstructionExtensions.Calls(codes[i], AddPrecept) && codes[i - 1].opcode == OpCodes.Ldloc_S && codes[i - 1].operand is LocalBuilder { LocalIndex: 6 })
			{
				found = true;
				codes[i].opcode = OpCodes.Nop;
				yield return new CodeInstruction(OpCodes.Call, (object)AccessTools.Method(typeof(VanillaExpandedFramework_Ideo_ExposeData_Patch), "CheckIfCanAdd", (Type[])null, (Type[])null));
				if (CodeInstructionExtensions.Calls(codes[i + 7], DebugLog))
				{
					debugCall = i + 7;
				}
			}
			if (found && i <= debugCall)
			{
				codes[i].opcode = OpCodes.Nop;
			}
		}
		if (!found)
		{
			Log.Warning("VanillaExpandedFramework: Memes Transpiler on Ideo:ExposeData could not find hook");
		}
	}

	public static void CheckIfCanAdd(Ideo ideo, Precept precept, bool init = false, FactionDef generatingFor = null, RitualPatternDef ritualPatternBase = null)
	{
		//IL_0015: Unknown result type (might be due to invalid IL or missing references)
		//IL_0044: Unknown result type (might be due to invalid IL or missing references)
		//IL_0049: Unknown result type (might be due to invalid IL or missing references)
		if ((ideo.foundation == null || AcceptanceReport.op_Implicit(ideo.foundation.CanAdd(precept.def, true))) && precept.def.canGenerateAsSpecialPrecept)
		{
			ideo.AddPrecept(precept, true, (FactionDef)null, ritualPatternBase);
			Debug.LogWarning((object)("A hidden ritual precept was missing, adding: " + ((Def)precept.def).LabelCap));
		}
	}
}
