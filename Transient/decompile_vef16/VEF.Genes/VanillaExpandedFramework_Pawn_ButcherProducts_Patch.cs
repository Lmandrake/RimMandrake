using System.Collections.Generic;
using HarmonyLib;
using RimWorld;
using Verse;

namespace VEF.Genes;

[HarmonyPatch(typeof(Pawn), "ButcherProducts")]
public static class VanillaExpandedFramework_Pawn_ButcherProducts_Patch
{
	public static IEnumerable<Thing> Postfix(IEnumerable<Thing> __result, Pawn __instance)
	{
		foreach (Thing item in __result)
		{
			if (StaticCollectionsClass.meat_gene_pawns.ContainsKey((Thing)(object)__instance) && item.def == ThingDefOf.Meat_Human)
			{
				Thing val = ThingMaker.MakeThing(StaticCollectionsClass.meat_gene_pawns[(Thing)(object)__instance], (ThingDef)null);
				val.stackCount = item.stackCount;
				yield return val;
			}
			else if (StaticCollectionsClass.leather_gene_pawns.ContainsKey((Thing)(object)__instance) && item.def == VEFDefOf.Leather_Human)
			{
				Thing val2 = ThingMaker.MakeThing(StaticCollectionsClass.leather_gene_pawns[(Thing)(object)__instance], (ThingDef)null);
				val2.stackCount = item.stackCount;
				yield return val2;
			}
			else
			{
				yield return item;
			}
		}
	}
}
