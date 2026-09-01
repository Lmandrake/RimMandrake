using System.Linq;
using HarmonyLib;
using RimWorld;
using Verse;

namespace VEF.Storyteller;

[HarmonyPatch(typeof(IncidentWorker))]
[HarmonyPatch("TryExecute")]
public static class VanillaExpandedFramework_IncidentWorker_TryExecute_Patch
{
	public static bool Prefix(IncidentWorker __instance, IncidentParms parms)
	{
		if (__instance.def.category == IncidentCategoryDefOf.ThreatBig)
		{
			StorytellerDefExtension modExtension = ((Def)Find.Storyteller.def).GetModExtension<StorytellerDefExtension>();
			if (modExtension != null && modExtension.storytellerThreat != null && modExtension.storytellerThreat.disableThreatsAtPopulationCount >= Find.ColonistBar.Entries.Where((Entry x) => x.pawn != null && !x.pawn.Dead && ((Thing)x.pawn).Faction == Faction.OfPlayer).Count())
			{
				return false;
			}
		}
		return true;
	}
}
