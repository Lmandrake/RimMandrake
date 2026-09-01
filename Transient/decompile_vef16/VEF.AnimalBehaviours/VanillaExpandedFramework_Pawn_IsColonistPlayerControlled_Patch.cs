using HarmonyLib;
using RimWorld;
using Verse;

namespace VEF.AnimalBehaviours;

[HarmonyPatch(typeof(Pawn))]
[HarmonyPatch(/*Could not decode attribute arguments.*/)]
public static class VanillaExpandedFramework_Pawn_IsColonistPlayerControlled_Patch
{
	[HarmonyPostfix]
	private static void AddAnimalAsColonist(Pawn __instance, ref bool __result)
	{
		if (StaticCollectionsClass.draftable_animals.Contains((Thing)(object)__instance))
		{
			__result = ((Thing)__instance).Spawned && __instance.HostFaction == null && ((Thing)__instance).Faction == Faction.OfPlayer;
		}
	}
}
