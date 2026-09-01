using System;
using HarmonyLib;
using UnityEngine;
using Verse;

namespace BigAndSmall.Balancing;

[HarmonyPatch(typeof(VerbProperties), "AdjustedMeleeDamageAmount", new Type[]
{
	typeof(Tool),
	typeof(Pawn),
	typeof(Thing),
	typeof(HediffComp_VerbGiver)
})]
public static class AdjustedMeleeDamageAmount_Patch
{
	public static void Postfix(ref float __result, Tool tool, Pawn attacker, Thing equipment, HediffComp_VerbGiver hediffCompSource, VerbProperties __instance)
	{
		__result = GetSizeAdjustedBaseDamage(__result, attacker, tool, __instance);
	}

	public static float GetSizeAdjustedBaseDamage(float __result, Pawn attacker, Tool tool, VerbProperties verbProperties)
	{
		if (attacker != null)
		{
			BSCache cache = HumanoidPawnScaler.GetCache(attacker);
			if (cache != null)
			{
				float linear = cache.scaleMultiplier.linear;
				float num = linear;
				if (linear > 1f)
				{
					float num2 = (linear - 1f) * BigSmallMod.settings.flatDamageIncrease;
					float num3 = __result + num2;
					num = Mathf.Pow(num, BigSmallMod.settings.dmgExponent);
					__result = Mathf.Min(__result * num, num3);
				}
				else
				{
					__result *= linear;
				}
			}
		}
		return __result;
	}
}
