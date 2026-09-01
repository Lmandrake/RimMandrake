using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using System.Reflection.Emit;
using HarmonyLib;
using RimWorld;
using UnityEngine;
using Verse;

namespace VEF.Genes;

[HarmonyPatch(typeof(HealthCardUtility), "DrawHediffRow")]
public static class VanillaExpandedFramework_HealthCardUtility_DrawHediffRow_Patch
{
	public static Pawn curPawn;

	public static string bloodIcon;

	public static void Prefix(Pawn pawn)
	{
		curPawn = pawn;
	}

	public static IEnumerable<CodeInstruction> Transpiler(IEnumerable<CodeInstruction> codeInstructions, ILGenerator ilg)
	{
		List<CodeInstruction> codes = codeInstructions.ToList();
		FieldInfo bleedingIconStaticField = AccessTools.Field(typeof(HealthCardUtility), "BleedingIcon");
		Label label = ilg.DefineLabel();
		for (int i = 0; i < codes.Count; i++)
		{
			yield return codes[i];
			if (codes[i].opcode == OpCodes.Stfld && CodeInstructionExtensions.LoadsField(codes[i - 1], bleedingIconStaticField, false))
			{
				codes[i + 1].labels.Add(label);
				yield return new CodeInstruction(OpCodes.Ldarg_1, (object)null);
				yield return new CodeInstruction(OpCodes.Call, (object)AccessTools.Method(typeof(VanillaExpandedFramework_HealthCardUtility_DrawHediffRow_Patch), "HasBloodIconChangingGene", new Type[1] { typeof(Pawn) }, (Type[])null));
				yield return new CodeInstruction(OpCodes.Brfalse_S, (object)label);
				yield return new CodeInstruction(OpCodes.Ldloc_S, (object)12);
				yield return new CodeInstruction(OpCodes.Call, (object)AccessTools.Method(typeof(VanillaExpandedFramework_HealthCardUtility_DrawHediffRow_Patch), "ChangeIconForThisPawn", (Type[])null, (Type[])null));
				yield return new CodeInstruction(OpCodes.Stfld, (object)AccessTools.Field(typeof(HealthCardUtility).GetNestedTypes(AccessTools.all).First((Type x) => x.Name.Contains("c__DisplayClass32_1")), "bleedingIcon"));
			}
		}
	}

	public static Texture2D ChangeIconForThisPawn()
	{
		return ContentFinder<Texture2D>.Get(bloodIcon, true);
	}

	public static bool HasBloodIconChangingGene(Pawn pawn)
	{
		if (pawn != null && StaticCollectionsClass.bloodIcon_gene_pawns.ContainsKey((Thing)(object)pawn))
		{
			bloodIcon = StaticCollectionsClass.bloodIcon_gene_pawns[(Thing)(object)pawn];
			return true;
		}
		return false;
	}

	public static void Postfix()
	{
		curPawn = null;
	}
}
