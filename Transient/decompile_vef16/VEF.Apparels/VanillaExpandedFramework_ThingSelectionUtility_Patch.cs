using HarmonyLib;
using RimWorld;
using Verse;

namespace VEF.Apparels;

[HarmonyPatch(typeof(ThingSelectionUtility), "SelectableByMapClick")]
public static class VanillaExpandedFramework_ThingSelectionUtility_Patch
{
	[HarmonyPostfix]
	public static void GhillieException(ref bool __result, Thing t)
	{
		Pawn val;
		if ((val = (Pawn)(object)((t is Pawn) ? t : null)) != null && (((Thing)val).Faction == null || (((Thing)val).Faction != null && FactionUtility.HostileTo(((Thing)val).Faction, Faction.OfPlayer))) && val.apparel != null && val.apparel.WornApparel != null && StaticCollectionsClass.camouflaged_pawns.Contains((Thing)(object)val))
		{
			__result = false;
		}
	}
}
