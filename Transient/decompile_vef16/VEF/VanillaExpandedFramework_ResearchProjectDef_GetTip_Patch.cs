using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using System.Reflection.Emit;
using HarmonyLib;
using Verse;

namespace VEF;

[HarmonyPatch(typeof(ResearchProjectDef), "GetTip")]
public static class VanillaExpandedFramework_ResearchProjectDef_GetTip_Patch
{
	public static IEnumerable<CodeInstruction> Transpiler(IEnumerable<CodeInstruction> codeInstructions)
	{
		List<CodeInstruction> codes = codeInstructions.ToList();
		MethodInfo get_IsCoreModInfo = AccessTools.Method(typeof(ModContentPack), "get_IsCoreMod", (Type[])null, (Type[])null);
		for (int i = 0; i < codes.Count; i++)
		{
			yield return codes[i];
			if (codes[i].opcode == OpCodes.Brtrue_S && CodeInstructionExtensions.Calls(codes[i - 1], get_IsCoreModInfo))
			{
				yield return new CodeInstruction(OpCodes.Call, (object)AccessTools.Method(typeof(VanillaExpandedFramework_ResearchProjectDef_GetTip_Patch), "ShouldShow", (Type[])null, (Type[])null));
				yield return new CodeInstruction(OpCodes.Brfalse_S, codes[i].operand);
			}
		}
	}

	public static bool ShouldShow()
	{
		return !VFEGlobal.settings.disableModSourceReport;
	}
}
