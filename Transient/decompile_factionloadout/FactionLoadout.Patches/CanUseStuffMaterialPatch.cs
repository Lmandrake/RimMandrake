using HarmonyLib;
using RimWorld;
using Verse;

namespace FactionLoadout.Patches;

[HarmonyPatch(typeof(PawnApparelGenerator), "CanUseStuff")]
public static class CanUseStuffMaterialPatch
{
	private static void Postfix(Pawn pawn, ThingStuffPair pair, ref bool __result)
	{
		//IL_0018: Unknown result type (might be due to invalid IL or missing references)
		if (__result && pawn?.kindDef != null && !DefCache.ApparelMaterialAllows(pawn.kindDef, pair.stuff))
		{
			__result = false;
		}
	}
}
