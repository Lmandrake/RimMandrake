using HarmonyLib;
using RimWorld;
using Verse;

namespace VEF.Apparels;

[HarmonyPatch(typeof(PawnUIOverlay), "DrawPawnGUIOverlay")]
public static class VanillaExpandedFramework_PawnUIOverlay_Patch
{
	[HarmonyPrefix]
	public static bool GhillieException(PawnUIOverlay __instance, Pawn ___pawn)
	{
		bool flag = FactionUtility.HostileTo(((Thing)___pawn).Faction, Faction.OfPlayer) && ___pawn.apparel != null && ___pawn.apparel.WornApparel != null && StaticCollectionsClass.camouflaged_pawns.Contains((Thing)(object)___pawn);
		return !flag;
	}
}
