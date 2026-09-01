using System;
using HarmonyLib;
using RimWorld;
using RimWorld.Planet;
using Verse;

namespace VEF.Factions;

[HarmonyPatch(typeof(SiteMakerHelper), "FactionCanOwn", new Type[]
{
	typeof(SitePartDef),
	typeof(Faction),
	typeof(bool),
	typeof(Predicate<Faction>)
})]
public static class VanillaExpandedFramework_SiteMakerHelper_FactionCanOwn_Patch
{
	public static void Postfix(ref bool __result, SitePartDef sitePart, Faction faction, bool disallowNonHostileFactions, Predicate<Faction> extraFactionValidator)
	{
		FactionDefExtension factionDefExtension = ((faction != null) ? ((Def)faction.def).GetModExtension<FactionDefExtension>() : null);
		if (factionDefExtension != null && factionDefExtension.excludeFromQuests)
		{
			__result = false;
		}
	}
}
