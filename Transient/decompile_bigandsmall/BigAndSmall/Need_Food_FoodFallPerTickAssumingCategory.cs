using HarmonyLib;
using RimWorld;
using UnityEngine;
using Verse;

namespace BigAndSmall;

[HarmonyPatch(typeof(Need_Food), "FoodFallPerTickAssumingCategory")]
public static class Need_Food_FoodFallPerTickAssumingCategory
{
	public static void Prefix(ref Pawn ___pawn, out float __state)
	{
		//IL_0021: Unknown result type (might be due to invalid IL or missing references)
		//IL_0027: Invalid comparison between Unknown and I4
		__state = ((Thing)___pawn).def.race.baseHungerRate;
		BSCache cachePrepatched = ___pawn.GetCachePrepatched();
		if (cachePrepatched != null && (int)___pawn.DevelopmentalStage > 2)
		{
			float num = __state * Mathf.Max(cachePrepatched.scaleMultiplier.linear, cachePrepatched.scaleMultiplier.DoubleMaxLinear);
			float baseHungerRate = Mathf.Lerp(__state, num, BigSmallMod.settings.hungerRate);
			((Thing)___pawn).def.race.baseHungerRate = baseHungerRate;
		}
	}

	public static void Postfix(ref float __result, Pawn ___pawn, float __state)
	{
		((Thing)___pawn).def.race.baseHungerRate = __state;
	}
}
