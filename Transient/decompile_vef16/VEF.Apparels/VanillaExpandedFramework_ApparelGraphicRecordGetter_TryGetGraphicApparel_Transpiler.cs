using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using System.Reflection.Emit;
using HarmonyLib;
using RimWorld;
using Verse;

namespace VEF.Apparels;

[HarmonyPatch(typeof(ApparelGraphicRecordGetter), "TryGetGraphicApparel")]
public static class VanillaExpandedFramework_ApparelGraphicRecordGetter_TryGetGraphicApparel_Transpiler
{
	public static IEnumerable<CodeInstruction> Transpiler(IEnumerable<CodeInstruction> codeInstructions)
	{
		MethodInfo renderAsPackMethod = AccessTools.Method(typeof(PawnRenderUtility), "RenderAsPack", (Type[])null, (Type[])null);
		List<CodeInstruction> codes = codeInstructions.ToList();
		bool found = false;
		for (int i = 0; i < codes.Count; i++)
		{
			yield return codes[i];
			if (codes[i].opcode == OpCodes.Brtrue_S && CodeInstructionExtensions.Calls(codes[i - 1], renderAsPackMethod))
			{
				found = true;
				yield return new CodeInstruction(OpCodes.Ldarg_0, (object)null);
				yield return new CodeInstruction(OpCodes.Call, (object)AccessTools.Method(typeof(VanillaExpandedFramework_ApparelGraphicRecordGetter_TryGetGraphicApparel_Transpiler), "IsUnifiedApparel", (Type[])null, (Type[])null));
				yield return new CodeInstruction(OpCodes.Brtrue_S, codes[i].operand);
			}
		}
		if (!found)
		{
			Log.Error("[Vanilla Framework Expanded] Transpiler on ApparelGraphicRecordGetter:TryGetGraphicApparel failed.");
		}
	}

	public static bool IsUnifiedApparel(Apparel apparel)
	{
		return ((Def)((Thing)apparel).def).GetModExtension<ApparelExtension>()?.isUnifiedApparel ?? false;
	}
}
