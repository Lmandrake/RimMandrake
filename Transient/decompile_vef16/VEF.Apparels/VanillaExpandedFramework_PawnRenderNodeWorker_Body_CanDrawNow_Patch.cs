using System;
using HarmonyLib;
using RimWorld;
using Verse;

namespace VEF.Apparels;

[HarmonyPatch(typeof(PawnRenderNodeWorker_Body), "CanDrawNow")]
public static class VanillaExpandedFramework_PawnRenderNodeWorker_Body_CanDrawNow_Patch
{
	public static void Postfix(PawnRenderNode node, PawnDrawParms parms, ref bool __result)
	{
		//IL_0004: Unknown result type (might be due to invalid IL or missing references)
		//IL_000c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0019: Unknown result type (might be due to invalid IL or missing references)
		if (!__result && parms.bed != null && parms.pawn.apparel != null && GenCollection.Any<Apparel>(parms.pawn.apparel.WornApparel, (Predicate<Apparel>)((Apparel x) => ((Def)((Thing)x).def).GetModExtension<ApparelExtension>()?.showBodyInBedAlways ?? false)))
		{
			__result = true;
		}
	}
}
