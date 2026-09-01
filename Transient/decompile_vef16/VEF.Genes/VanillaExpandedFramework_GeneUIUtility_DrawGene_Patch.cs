using System;
using System.Collections.Generic;
using System.Reflection.Emit;
using HarmonyLib;
using RimWorld;
using Verse;

namespace VEF.Genes;

[HarmonyPatch(typeof(GeneUIUtility), "DrawGene")]
public static class VanillaExpandedFramework_GeneUIUtility_DrawGene_Patch
{
	public static IEnumerable<CodeInstruction> Transpiler(IEnumerable<CodeInstruction> codeInstructions)
	{
		bool patched = false;
		foreach (CodeInstruction code in codeInstructions)
		{
			yield return code;
			if (code.opcode == OpCodes.Stloc_0 && !patched)
			{
				yield return new CodeInstruction(OpCodes.Ldloc_0, (object)null);
				yield return new CodeInstruction(OpCodes.Ldarg_0, (object)null);
				yield return new CodeInstruction(OpCodes.Call, (object)AccessTools.Method(typeof(VanillaExpandedFramework_GeneUIUtility_DrawGene_Patch), "ModifyTooltip", (Type[])null, (Type[])null));
				yield return new CodeInstruction(OpCodes.Stloc_0, (object)null);
				patched = true;
			}
		}
	}

	public static string ModifyTooltip(string tooltip, Gene gene)
	{
		//IL_0010: Unknown result type (might be due to invalid IL or missing references)
		//IL_001b: Unknown result type (might be due to invalid IL or missing references)
		//IL_003b: Unknown result type (might be due to invalid IL or missing references)
		//IL_004b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0050: Unknown result type (might be due to invalid IL or missing references)
		//IL_0055: Unknown result type (might be due to invalid IL or missing references)
		if (gene is GeneGendered geneGendered && ((Gene)geneGendered).pawn.gender != geneGendered.Extension.forGenderOnly)
		{
			tooltip += "\n\n";
			tooltip += ColoredText.Colorize(TranslatorFormattedStringExtensions.Translate("VGE_ForGenderOnly", NamedArgument.op_Implicit(GenText.CapitalizeFirst(GenderUtility.GetLabel(geneGendered.Extension.forGenderOnly, false)))), ColorLibrary.RedReadable);
		}
		return tooltip;
	}
}
