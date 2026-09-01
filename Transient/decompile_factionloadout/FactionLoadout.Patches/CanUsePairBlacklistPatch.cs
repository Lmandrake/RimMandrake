using HarmonyLib;
using RimWorld;
using Verse;

namespace FactionLoadout.Patches;

[HarmonyPatch(typeof(PawnApparelGenerator), "CanUsePair")]
public static class CanUsePairBlacklistPatch
{
	private static void Postfix(ThingStuffPair pair, Pawn pawn, ref bool __result)
	{
		//IL_003f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0028: Unknown result type (might be due to invalid IL or missing references)
		if (__result && pawn?.kindDef != null)
		{
			if (DefCache.ApparelBlacklistCache.TryGetValue(pawn.kindDef, out var value) && value.Contains(pair.thing))
			{
				__result = false;
			}
			else if (!DefCache.ApparelMaterialAllows(pawn.kindDef, pair.stuff))
			{
				__result = false;
			}
		}
	}
}
