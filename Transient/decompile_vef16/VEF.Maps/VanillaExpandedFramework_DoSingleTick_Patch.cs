using System.Diagnostics;
using HarmonyLib;
using Verse;

namespace VEF.Maps;

[HarmonyPatch(typeof(TickManager), "DoSingleTick")]
public static class VanillaExpandedFramework_DoSingleTick_Patch
{
	private static SpecialTerrainList[] terrainListers = new SpecialTerrainList[128];

	private static Map[] maps = (Map[])(object)new Map[128];

	private static void Prefix(out Stopwatch __state)
	{
		__state = new Stopwatch();
		__state.Start();
	}

	private static void Postfix(Stopwatch __state)
	{
		__state.Stop();
		foreach (Map map in Find.Maps)
		{
			int index = map.Index;
			SpecialTerrainList specialTerrainList;
			if (maps[index] != map)
			{
				maps[index] = map;
				specialTerrainList = (terrainListers[index] = map.GetComponent<SpecialTerrainList>());
			}
			else
			{
				specialTerrainList = terrainListers[index];
			}
			specialTerrainList.TerrainUpdate((long)((float)__state.ElapsedTicks * 0.25f));
		}
	}
}
