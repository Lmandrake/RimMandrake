using System;
using System.Linq;
using System.Reflection;
using HarmonyLib;
using RimWorld.Planet;
using Verse;

namespace VEF.Factions;

[HarmonyPatch]
public static class VanillaExpandedFramework_GenerateRoadEndpoints_Patch
{
	[HarmonyTargetMethod]
	public static MethodBase TargetMethod()
	{
		return typeof(WorldGenStep_Roads).GetNestedTypes(AccessTools.all).SelectMany((Type x) => x.GetMethods(AccessTools.all)).FirstOrDefault((MethodInfo x) => x.Name.Contains("<GenerateRoadEndpoints>") && x.ReturnType == typeof(bool));
	}

	public static void Postfix(ref bool __result, WorldObject wo)
	{
		Settlement val = (Settlement)(object)((wo is Settlement) ? wo : null);
		if (val != null && ((WorldObject)val).Faction != null)
		{
			FactionDefExtension modExtension = ((Def)((WorldObject)val).Faction.def).GetModExtension<FactionDefExtension>();
			if (modExtension != null && modExtension.neverConnectToRoads)
			{
				__result = false;
			}
		}
	}
}
