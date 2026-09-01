using System;
using HarmonyLib;
using UnityEngine;
using Verse;

namespace BigAndSmall.Balancing;

[HarmonyPatch(typeof(VerbProperties), "AdjustedArmorPenetration", new Type[]
{
	typeof(Tool),
	typeof(Pawn),
	typeof(Thing),
	typeof(HediffComp_VerbGiver)
})]
public static class VerbProperties_AdjustedArmorPenetration_Patch
{
	public static void Postfix(ref float __result, Pawn attacker, VerbProperties __instance)
	{
		if (__instance.IsMeleeAttack && attacker != null)
		{
			BSCache cache = HumanoidPawnScaler.GetCache(attacker);
			if (cache != null)
			{
				float num = ((!(cache.scaleMultiplier.linear > 1f)) ? (cache.scaleMultiplier.linear * 0.1f - 0.1f) : (cache.scaleMultiplier.linear * 0.2f - 0.2f));
				num = Mathf.Min(1f, num);
				__result += num;
			}
		}
	}
}
