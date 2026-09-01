using System.Collections.Generic;
using HarmonyLib;
using RimWorld;
using Verse;

namespace VEF.Factions;

[HarmonyPatch(typeof(Building_CommsConsole), "GetCommTargets")]
public static class VanillaExpandedFramework_Building_CommsConsole_GetCommTargets_Patch
{
	public static IEnumerable<ICommunicable> Postfix(IEnumerable<ICommunicable> __result)
	{
		foreach (ICommunicable item in __result)
		{
			Faction val = (Faction)(object)((item is Faction) ? item : null);
			if (val != null)
			{
				FactionDefExtension modExtension = ((Def)val.def).GetModExtension<FactionDefExtension>();
				if (modExtension != null && modExtension.excludeFromCommConsole)
				{
					continue;
				}
			}
			yield return item;
		}
	}
}
