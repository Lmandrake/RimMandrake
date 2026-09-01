using HarmonyLib;
using Verse;

namespace VEF.Maps;

[HarmonyPatch(typeof(TerrainGrid), "RemoveTopLayer")]
internal static class VanillaExpandedFramework_TerrainGrid_RemoveTopLayer
{
	private static void Prefix(IntVec3 c, TerrainGrid __instance, Map ___map)
	{
		//IL_0001: Unknown result type (might be due to invalid IL or missing references)
		//IL_0014: Unknown result type (might be due to invalid IL or missing references)
		if (__instance.TerrainAt(c) is ActiveTerrainDef)
		{
			___map.GetComponent<SpecialTerrainList>().Notify_RemovedTerrainAt(c);
		}
	}
}
