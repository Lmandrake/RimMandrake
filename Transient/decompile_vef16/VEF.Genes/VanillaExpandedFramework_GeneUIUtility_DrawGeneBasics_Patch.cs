using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using System.Reflection.Emit;
using HarmonyLib;
using RimWorld;
using Verse;

namespace VEF.Genes;

[HarmonyPatch(typeof(GeneUIUtility))]
[HarmonyPatch("DrawGeneBasics")]
public static class VanillaExpandedFramework_GeneUIUtility_DrawGeneBasics_Patch
{
	private static IEnumerable<CodeInstruction> Transpiler(IEnumerable<CodeInstruction> instructions)
	{
		FieldInfo loadsField = AccessTools.Field(typeof(GeneUIUtility), "GeneBackground_Endogene");
		FieldInfo loadsFieldTwo = AccessTools.Field(typeof(GeneUIUtility), "GeneBackground_Xenogene");
		FieldInfo loadsFieldArchite = AccessTools.Field(typeof(GeneUIUtility), "GeneBackground_Archite");
		List<CodeInstruction> codes = instructions.ToList();
		for (int i = 0; i < codes.Count; i++)
		{
			CodeInstruction val = codes[i];
			if (codes[i].opcode == OpCodes.Ldsfld && CodeInstructionExtensions.LoadsField(codes[i], loadsField, false))
			{
				yield return CodeInstructionExtensions.MoveLabelsFrom(new CodeInstruction(OpCodes.Ldarg_0, (object)null), codes[i]);
				yield return new CodeInstruction(OpCodes.Call, (object)typeof(VanillaExpandedFramework_GeneUIUtility_DrawGeneBasics_Patch).GetMethod("ChooseEndogeneBackground"));
			}
			else if (codes[i].opcode == OpCodes.Ldsfld && CodeInstructionExtensions.LoadsField(codes[i], loadsFieldTwo, false))
			{
				yield return CodeInstructionExtensions.MoveLabelsFrom(new CodeInstruction(OpCodes.Ldarg_0, (object)null), codes[i]);
				yield return new CodeInstruction(OpCodes.Call, (object)typeof(VanillaExpandedFramework_GeneUIUtility_DrawGeneBasics_Patch).GetMethod("ChooseXenogeneBackground"));
			}
			else if (codes[i].opcode == OpCodes.Ldsfld && CodeInstructionExtensions.LoadsField(codes[i], loadsFieldArchite, false))
			{
				yield return CodeInstructionExtensions.MoveLabelsFrom(new CodeInstruction(OpCodes.Ldarg_0, (object)null), codes[i]);
				yield return new CodeInstruction(OpCodes.Call, (object)typeof(VanillaExpandedFramework_GeneUIUtility_DrawGeneBasics_Patch).GetMethod("ChooseArchiteBackground"));
			}
			else
			{
				yield return val;
			}
		}
	}

	public static object ChooseEndogeneBackground(GeneDef gene)
	{
		if (((Def)gene).GetModExtension<GeneExtension>()?.backgroundPathEndogenes != null)
		{
			return Activator.CreateInstance(GraphicsCache.cachedTextureType, ((Def)gene).GetModExtension<GeneExtension>().backgroundPathEndogenes);
		}
		return GraphicsCache.GeneBackground_Endogene;
	}

	public static object ChooseXenogeneBackground(GeneDef gene)
	{
		if (((Def)gene).GetModExtension<GeneExtension>()?.backgroundPathXenogenes != null)
		{
			return Activator.CreateInstance(GraphicsCache.cachedTextureType, ((Def)gene).GetModExtension<GeneExtension>().backgroundPathXenogenes);
		}
		return GraphicsCache.GeneBackground_Xenogene;
	}

	public static object ChooseArchiteBackground(GeneDef gene)
	{
		if (((Def)gene).GetModExtension<GeneExtension>()?.backgroundPathArchite != null)
		{
			return Activator.CreateInstance(GraphicsCache.cachedTextureType, ((Def)gene).GetModExtension<GeneExtension>().backgroundPathArchite);
		}
		return GraphicsCache.GeneBackground_Archite;
	}
}
