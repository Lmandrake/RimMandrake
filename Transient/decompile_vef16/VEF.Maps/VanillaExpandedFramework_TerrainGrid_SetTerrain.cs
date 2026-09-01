using HarmonyLib;
using Verse;

namespace VEF.Maps;

[HarmonyPatch(typeof(TerrainGrid), "SetTerrain")]
public static class VanillaExpandedFramework_TerrainGrid_SetTerrain
{
	private static void Prefix(IntVec3 c, TerrainDef newTerr, TerrainGrid __instance, Map ___map)
	{
		//IL_0006: Unknown result type (might be due to invalid IL or missing references)
		//IL_0019: Unknown result type (might be due to invalid IL or missing references)
		if (___map.terrainGrid.TerrainAt(c) is ActiveTerrainDef)
		{
			___map.GetComponent<SpecialTerrainList>().Notify_RemovedTerrainAt(c);
		}
	}

	private static void Postfix(IntVec3 c, TerrainDef newTerr, TerrainGrid __instance, Map ___map)
	{
		//IL_0011: Unknown result type (might be due to invalid IL or missing references)
		if (newTerr is ActiveTerrainDef special)
		{
			___map.GetComponent<SpecialTerrainList>().RegisterAt(special, c);
		}
	}
}
