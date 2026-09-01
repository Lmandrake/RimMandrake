using System.Collections.Generic;
using HarmonyLib;
using RimWorld;
using Verse;

namespace VEF.Pawns;

[HarmonyPatch(typeof(HediffSet), "CalculatePain")]
public static class VanillaExpandedFramework_HediffSet_CalculatePain_Patch
{
	public static void Postfix(HediffSet __instance, ref float __result)
	{
		foreach (Trait item in __instance.pawn.story?.traits?.allTraits ?? new List<Trait>())
		{
			TraitExtension modExtension = ((Def)item.def).GetModExtension<TraitExtension>();
			if (modExtension != null && modExtension.painFactor != 1f)
			{
				__result *= modExtension.painFactor;
			}
		}
	}
}
