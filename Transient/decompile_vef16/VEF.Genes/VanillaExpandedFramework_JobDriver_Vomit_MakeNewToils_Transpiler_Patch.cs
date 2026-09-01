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
public static class VanillaExpandedFramework_JobDriver_Vomit_MakeNewToils_Transpiler_Patch
{
	private static MethodBase TargetMethod()
	{
		return typeof(JobDriver_Vomit).GetMethod("<MakeNewToils>b__4_1", BindingFlags.Instance | BindingFlags.NonPublic);
	}

	public static IEnumerable<CodeInstruction> Transpiler(IEnumerable<CodeInstruction> codeInstructions)
	{
		List<CodeInstruction> list = codeInstructions.ToList();
		FieldInfo field = AccessTools.Field(typeof(ThingDefOf), "Filth_Vomit");
		foreach (CodeInstruction item in list)
		{
			if (item.opcode == OpCodes.Ldsfld && CodeInstructionExtensions.LoadsField(item, field, false))
			{
				yield return new CodeInstruction(OpCodes.Call, (object)AccessTools.Method(typeof(VanillaExpandedFramework_JobDriver_Vomit_MakeNewToils_Transpiler_Patch), "GetVomitFilth", (Type[])null, (Type[])null));
			}
			else
			{
				yield return item;
			}
		}
	}

	public static ThingDef GetVomitFilth()
	{
		if (VanillaExpandedFramework_JobDriver_Vomit_MakeNewToils_Patch.curPawn != null && StaticCollectionsClass.vomitType_gene_pawns.ContainsKey((Thing)(object)VanillaExpandedFramework_JobDriver_Vomit_MakeNewToils_Patch.curPawn))
		{
			return StaticCollectionsClass.vomitType_gene_pawns[(Thing)(object)VanillaExpandedFramework_JobDriver_Vomit_MakeNewToils_Patch.curPawn];
		}
		return ThingDefOf.Filth_Vomit;
	}
}
