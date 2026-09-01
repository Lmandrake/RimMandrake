using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using System.Reflection.Emit;
using HarmonyLib;
using RimWorld;
using Verse;

namespace VEF;

[HarmonyPatch(typeof(BackstoryDef), "FullDescriptionFor")]
public static class VanillaExpandedFramework_BackstoryDef_FullDescriptionFor_Patch
{
	public static IEnumerable<CodeInstruction> Transpiler(IEnumerable<CodeInstruction> codeInstructions)
	{
		List<CodeInstruction> codes = codeInstructions.ToList();
		MethodInfo get_IsCoreModInfo = AccessTools.Method(typeof(ModContentPack), "get_IsOfficialMod", (Type[])null, (Type[])null);
		for (int i = 0; i < codes.Count; i++)
		{
			yield return codes[i];
			if (codes[i].opcode == OpCodes.Brtrue_S && CodeInstructionExtensions.Calls(codes[i - 1], get_IsCoreModInfo))
			{
				yield return new CodeInstruction(OpCodes.Call, (object)AccessTools.Method(typeof(VanillaExpandedFramework_BackstoryDef_FullDescriptionFor_Patch), "ShouldShow", (Type[])null, (Type[])null));
				yield return new CodeInstruction(OpCodes.Brfalse_S, codes[i].operand);
			}
		}
	}

	public static bool ShouldShow()
	{
		return !VFEGlobal.settings.disableModSourceReport;
	}
}
