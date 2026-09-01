using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using System.Reflection.Emit;
using HarmonyLib;
using RimWorld;
using Verse;

namespace VEF.Plants;

[HarmonyPatch(typeof(PlantUtility))]
[HarmonyPatch("CanSowOnGrower")]
public static class VanillaExpandedFramework_PlantUtility_CanSowOnGrower_Patch
{
	[HarmonyTranspiler]
	public static IEnumerable<CodeInstruction> Transpiler(IEnumerable<CodeInstruction> codeInstructions)
	{
		List<CodeInstruction> codes = codeInstructions.ToList();
		MethodInfo detectNewTags = AccessTools.Method(typeof(VanillaExpandedFramework_PlantUtility_CanSowOnGrower_Patch), "DetectTags", (Type[])null, (Type[])null);
		yield return codes[0];
		for (int i = 1; i < codes.Count; i++)
		{
			if (codes[i].opcode == OpCodes.Callvirt && codes[i - 1].opcode != OpCodes.Ldstr)
			{
				yield return new CodeInstruction(OpCodes.Ldloc_1, (object)null);
				yield return new CodeInstruction(OpCodes.Call, (object)detectNewTags);
			}
			else
			{
				yield return codes[i];
			}
		}
	}

	public static bool DetectTags(List<string> sowTags, string sowTag, Thing sower)
	{
		SowerExtension sowerExtension = ((sower != null) ? ((Def)sower.def).GetModExtension<SowerExtension>() : null);
		if (sowerExtension != null)
		{
			if (sowTags.Contains(sowTag))
			{
				return true;
			}
			return sowTags.Intersect(sowerExtension.extraSowTags).Any();
		}
		return sowTags.Contains(sowTag);
	}
}
