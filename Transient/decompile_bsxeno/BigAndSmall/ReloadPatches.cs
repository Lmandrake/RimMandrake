using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using System.Reflection.Emit;
using HarmonyLib;
using RimWorld;

namespace BigAndSmall;

[HarmonyPatch]
public static class ReloadPatches
{
	[HarmonyPatch(typeof(DefGenerator), "GenerateImpliedDefs_PreResolve")]
	[HarmonyPrefix]
	public static void GenerateImpliedDefs_Prefix(bool hotReload)
	{
		BSCore.RunBeforeGenerateImpliedDefs(hotReload);
	}

	[HarmonyPatch(typeof(DefGenerator), "GenerateImpliedDefs_PreResolve")]
	[HarmonyTranspiler]
	public static IEnumerable<CodeInstruction> InsertBeforeResolveAllWantedCrossReferences(IEnumerable<CodeInstruction> instructions, ILGenerator generator)
	{
		//IL_0069: Unknown result type (might be due to invalid IL or missing references)
		//IL_0073: Expected O, but got Unknown
		//IL_007d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0087: Expected O, but got Unknown
		List<CodeInstruction> list = new List<CodeInstruction>(instructions);
		MethodInfo methodInfo = AccessTools.Method(typeof(BSCore), "RunDuringGenerateImpliedDefs", (Type[])null, (Type[])null);
		for (int i = 0; i < list.Count; i++)
		{
			if (list[i].opcode == OpCodes.Call && list[i].operand is MethodInfo { Name: "ResolveAllWantedCrossReferences" })
			{
				list.Insert(i, new CodeInstruction(OpCodes.Ldarg_0, (object)null));
				list.Insert(i + 1, new CodeInstruction(OpCodes.Call, (object)methodInfo));
				break;
			}
		}
		return list.AsEnumerable();
	}

	[HarmonyPatch(typeof(DefGenerator), "GenerateImpliedDefs_PreResolve")]
	[HarmonyPostfix]
	public static void GenerateImpliedDefs_Postfix(bool hotReload)
	{
		BSCore.RunAfterGenerateImpliedDefs(hotReload);
	}
}
