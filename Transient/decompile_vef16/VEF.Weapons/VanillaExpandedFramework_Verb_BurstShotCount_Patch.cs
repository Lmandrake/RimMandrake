using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using System.Reflection.Emit;
using HarmonyLib;
using RimWorld;
using Verse;

namespace VEF.Weapons;

public static class VanillaExpandedFramework_Verb_BurstShotCount_Patch
{
	public static IEnumerable<CodeInstruction> RandomizeBurstCount(IEnumerable<CodeInstruction> codeInstructions)
	{
		List<CodeInstruction> codes = codeInstructions.ToList();
		MethodInfo changeBurst = AccessTools.Method(typeof(VanillaExpandedFramework_Verb_BurstShotCount_Patch), "ChangeBurstCount", (Type[])null, (Type[])null);
		for (int i = 0; i < codes.Count; i++)
		{
			if (i > 0 && codes[i].opcode == OpCodes.Stloc_0 && codes[i - 1].opcode == OpCodes.Mul)
			{
				yield return codes[i];
				yield return new CodeInstruction(OpCodes.Ldloc_0, (object)null);
				yield return new CodeInstruction(OpCodes.Ldloc_3, (object)null);
				yield return new CodeInstruction(OpCodes.Call, (object)changeBurst);
				yield return new CodeInstruction(OpCodes.Mul, (object)null);
				yield return new CodeInstruction(OpCodes.Stloc_0, (object)null);
			}
			else
			{
				yield return codes[i];
			}
		}
	}

	public static float ChangeBurstCount(WeaponTraitDef trait)
	{
		WeaponTraitDefExtension modExtension = ((Def)trait).GetModExtension<WeaponTraitDefExtension>();
		if (modExtension != null && modExtension.burstShotCountRange != null)
		{
			return GenCollection.RandomElement<float>((IEnumerable<float>)modExtension.burstShotCountRange);
		}
		return 1f;
	}
}
