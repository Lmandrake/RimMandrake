using HarmonyLib;
using RimWorld;
using Verse;

namespace FactionLoadout.Patches;

[HarmonyPatch(typeof(PawnWeaponGenerator), "GetCommonality")]
public static class WeaponGetCommonalityBlacklistPatch
{
	private static void Postfix(Pawn pawn, ThingStuffPair pair, ref float __result)
	{
		//IL_0048: Unknown result type (might be due to invalid IL or missing references)
		//IL_002d: Unknown result type (might be due to invalid IL or missing references)
		if (!(__result <= 0f) && pawn?.kindDef != null)
		{
			if (DefCache.WeaponBlacklistCache.TryGetValue(pawn.kindDef, out var value) && value.Contains(pair.thing))
			{
				__result = 0f;
			}
			else if (!DefCache.WeaponMaterialAllows(pawn.kindDef, pair.stuff))
			{
				__result = 0f;
			}
		}
	}
}
