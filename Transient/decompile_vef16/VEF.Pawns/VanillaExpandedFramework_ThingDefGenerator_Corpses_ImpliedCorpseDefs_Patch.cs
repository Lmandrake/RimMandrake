using System.Collections.Generic;
using HarmonyLib;
using RimWorld;
using VEF.Things;
using Verse;

namespace VEF.Pawns;

[HarmonyPatch(typeof(ThingDefGenerator_Corpses), "ImpliedCorpseDefs")]
public static class VanillaExpandedFramework_ThingDefGenerator_Corpses_ImpliedCorpseDefs_Patch
{
	public static IEnumerable<ThingDef> Postfix(IEnumerable<ThingDef> __result)
	{
		foreach (ThingDef item in __result)
		{
			if (!SkipDef(item))
			{
				yield return item;
			}
		}
	}

	public static bool SkipDef(ThingDef thingDef)
	{
		if (thingDef.ingestible?.sourceDef != null)
		{
			ThingDefExtension modExtension = ((Def)thingDef.ingestible.sourceDef).GetModExtension<ThingDefExtension>();
			if (modExtension != null && modExtension.destroyCorpse)
			{
				return true;
			}
		}
		return false;
	}
}
