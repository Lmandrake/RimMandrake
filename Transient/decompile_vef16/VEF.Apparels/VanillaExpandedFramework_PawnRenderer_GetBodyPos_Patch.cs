using System;
using HarmonyLib;
using RimWorld;
using UnityEngine;
using Verse;

namespace VEF.Apparels;

[HarmonyPatch(typeof(PawnRenderer), "GetBodyPos")]
public static class VanillaExpandedFramework_PawnRenderer_GetBodyPos_Patch
{
	public static void Postfix(Pawn ___pawn, Vector3 drawLoc, ref bool showBody)
	{
		if (!showBody)
		{
			if (___pawn.apparel != null && RestUtility.CurrentBed(___pawn) != null && GenCollection.Any<Apparel>(___pawn.apparel.WornApparel, (Predicate<Apparel>)((Apparel x) => ((Def)((Thing)x).def).GetModExtension<ApparelExtension>()?.showBodyInBedAlways ?? false)))
			{
				showBody = true;
			}
		}
	}
}
