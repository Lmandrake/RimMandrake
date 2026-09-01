using HarmonyLib;
using RimWorld.Planet;

namespace VEF.Planet;

[HarmonyPatch(typeof(Caravan_PathFollower), "StartPath")]
public static class Caravan_PathFollower_StartPath_Patch
{
	public static void Postfix(Caravan_PathFollower __instance, PlanetTile destTile)
	{
		//IL_000f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0016: Unknown result type (might be due to invalid IL or missing references)
		if (VanillaExpandedFramework_Caravan_PathFollower_ExposeData_Patch.caravansToFollow.TryGetValue(__instance, out var value) && destTile != ((WorldObject)value.destination).Tile)
		{
			VanillaExpandedFramework_Caravan_PathFollower_ExposeData_Patch.caravansToFollow.Remove(__instance);
		}
	}
}
