using System;
using HarmonyLib;
using Verse;

namespace VEF.AnimalBehaviours;

[HarmonyPatch(typeof(VerbProperties))]
[HarmonyPatch("AdjustedCooldown")]
[HarmonyPatch(new Type[]
{
	typeof(Tool),
	typeof(Pawn),
	typeof(Thing)
})]
public static class VanillaExpandedFramework_VerbProperties_AdjustedCooldown_Patch
{
	[HarmonyPostfix]
	public static void LastStand(Tool tool, Pawn attacker, Thing equipment, ref float __result)
	{
		if (attacker != null && attacker.TryGetLastStandAnimalRate(out var rate))
		{
			float summaryHealthPercent = attacker.health.summaryHealth.SummaryHealthPercent;
			float num = (rate - 1f) * (1f - summaryHealthPercent) + 1f;
			__result /= num;
		}
	}
}
