using System.Collections.Generic;
using System.Linq;
using HarmonyLib;
using RimWorld.Planet;
using Verse;

namespace VEF.Buildings;

[HarmonyPatch]
public static class DoorTeleporterPatches
{
	[HarmonyPatch(typeof(Settlement), "GetFloatMenuOptions")]
	[HarmonyPostfix]
	public static void VanillaExpandedFramework_Settlement_GetFloatOptions_Postfix(ref IEnumerable<FloatMenuOption> __result, Settlement __instance, Caravan caravan)
	{
		if (!((MapParent)__instance).HasMap)
		{
			return;
		}
		DoorTeleporter origin = null;
		HashSet<Map> hashSet = new HashSet<Map>();
		List<DoorTeleporter> list = new List<DoorTeleporter>();
		foreach (DoorTeleporter doorTeleporter in WorldComponent_DoorTeleporterManager.Instance.DoorTeleporters)
		{
			if (((Thing)doorTeleporter).Map == ((MapParent)__instance).Map)
			{
				origin = doorTeleporter;
			}
			else if (!hashSet.Contains(((Thing)doorTeleporter).Map))
			{
				hashSet.Add(((Thing)doorTeleporter).Map);
				list.Add(doorTeleporter);
			}
		}
		if (origin != null)
		{
			__result = __result.Concat(list.SelectMany((DoorTeleporter skipdoor) => CaravanArrivalAction_UseDoorTeleporter.GetFloatMenuOptions(caravan, origin, skipdoor)));
		}
	}

	[HarmonyPatch(typeof(MapDeiniter), "Deinit")]
	[HarmonyPrefix]
	public static void VanillaExpandedFramework_MapDeiniter_Deinit_Prefix(Map map)
	{
		WorldComponent_DoorTeleporterManager.Instance.DoorTeleporters.RemoveWhere((DoorTeleporter skipdoor) => ((Thing)skipdoor).Map == map);
	}
}
