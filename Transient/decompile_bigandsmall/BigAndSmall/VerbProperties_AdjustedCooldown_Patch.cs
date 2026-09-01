using System;
using HarmonyLib;
using Verse;

namespace BigAndSmall;

[HarmonyPatch(typeof(VerbProperties), "AdjustedCooldown", new Type[]
{
	typeof(Tool),
	typeof(Pawn),
	typeof(Thing)
})]
public static class VerbProperties_AdjustedCooldown_Patch
{
	public static void Postfix(Tool tool, Pawn attacker, Thing equipment, ref float __result)
	{
		BSCache cache = HumanoidPawnScaler.GetCache(attacker);
		if (cache != null)
		{
			if (equipment == null)
			{
				__result /= cache.attackSpeedUnarmedMultiplier + cache.attackSpeedMultiplier - 1f;
			}
			else
			{
				__result /= cache.attackSpeedMultiplier;
			}
		}
	}
}
