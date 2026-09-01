using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using System.Reflection.Emit;
using HarmonyLib;
using RimWorld;
using Verse;

namespace VEF.Genes;

[HarmonyPatch]
public static class VanillaExpandedFramework_JobDriver_Vomit_MoveNext_Patch
{
	private static MethodBase TargetMethod()
	{
		return typeof(JobDriver_Vomit).GetNestedType("<MakeNewToils>d__4", BindingFlags.Instance | BindingFlags.NonPublic).GetMethod("MoveNext", BindingFlags.Instance | BindingFlags.NonPublic);
	}

	public static IEnumerable<CodeInstruction> Transpiler(IEnumerable<CodeInstruction> codeInstructions)
	{
		List<CodeInstruction> list = codeInstructions.ToList();
		FieldInfo field = AccessTools.Field(typeof(EffecterDefOf), "Vomit");
		foreach (CodeInstruction item in list)
		{
			if (item.opcode == OpCodes.Ldsfld && CodeInstructionExtensions.LoadsField(item, field, false))
			{
				yield return new CodeInstruction(OpCodes.Call, (object)AccessTools.Method(typeof(VanillaExpandedFramework_JobDriver_Vomit_MoveNext_Patch), "GetVomitEffecter", (Type[])null, (Type[])null));
			}
			else
			{
				yield return item;
			}
		}
	}

	public static EffecterDef GetVomitEffecter()
	{
		if (VanillaExpandedFramework_JobDriver_Vomit_MakeNewToils_Patch.curPawn != null && StaticCollectionsClass.vomitEffect_gene_pawns.ContainsKey((Thing)(object)VanillaExpandedFramework_JobDriver_Vomit_MakeNewToils_Patch.curPawn))
		{
			return StaticCollectionsClass.vomitEffect_gene_pawns[(Thing)(object)VanillaExpandedFramework_JobDriver_Vomit_MakeNewToils_Patch.curPawn];
		}
		return EffecterDefOf.Vomit;
	}
}
