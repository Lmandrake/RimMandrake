using System;
using HarmonyLib;
using RimWorld;
using Verse;

namespace VEF.Apparels;

[HarmonyPatch(typeof(PawnRenderNodeWorker_Apparel_Head), "CanDrawNow")]
public static class VanillaExpandedFramework_PawnRenderNodeWorker_Apparel_Head_CanDrawNow_Patch
{
	public static void Prefix(PawnDrawParms parms, out bool __state)
	{
		//IL_0007: Unknown result type (might be due to invalid IL or missing references)
		//IL_0019: Unknown result type (might be due to invalid IL or missing references)
		__state = Prefs.HatsOnlyOnMap;
		if (parms.pawn.apparel.AnyApparel && GenCollection.FirstOrDefault<Apparel>(parms.pawn.apparel.WornApparel, (Predicate<Apparel>)((Apparel x) => ((Def)((Thing)x).def).GetModExtension<ApparelExtension>()?.hideHead ?? false)) != null)
		{
			Prefs.HatsOnlyOnMap = false;
		}
	}

	public static void Finalizer(bool __state)
	{
		Prefs.HatsOnlyOnMap = __state;
	}
}
