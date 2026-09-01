using HarmonyLib;
using RimWorld;
using Verse;

namespace VEF.AnimalBehaviours;

[HarmonyPatch(/*Could not decode attribute arguments.*/)]
public static class VanillaExpandedFramework_Pawn_CanTakeOrder_Patch
{
	[HarmonyPostfix]
	public static void MakePawnControllable(Pawn __instance, ref bool __result)
	{
		int num;
		if (((Thing)__instance).Faction != null)
		{
			Faction faction = ((Thing)__instance).Faction;
			num = ((faction != null && faction.IsPlayer) ? 1 : 0);
		}
		else
		{
			num = 0;
		}
		bool flag = (byte)num != 0;
		if (StaticCollectionsClass.draftable_animals.Contains((Thing)(object)__instance) && flag)
		{
			__result = true;
		}
	}
}
