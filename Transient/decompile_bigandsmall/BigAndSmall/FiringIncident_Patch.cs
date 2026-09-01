using HarmonyLib;
using RimWorld;
using Verse;

namespace BigAndSmall;

[HarmonyPatch(/*Could not decode attribute arguments.*/)]
public static class FiringIncident_Patch
{
	public static void Postfix(FiringIncident __instance)
	{
		if (__instance.def != BSDefs.StrangerInBlackJoin || !BigSmall.BSGenesActive)
		{
			return;
		}
		float wealthTotal = Find.AnyPlayerHomeMap.wealthWatcher.WealthTotal;
		int num = Rand.Range(20000, 100000);
		Log.Message($"Player wealth is {wealthTotal}. Required (random) wealth to trigger Woman in blue is {num}.");
		if (wealthTotal > (float)num)
		{
			IncidentDef named = DefDatabase<IncidentDef>.GetNamed("BS_WomanInBlueJoin", true);
			if (named != null)
			{
				Find.Storyteller.incidentQueue.Add(named, 4500, __instance.parms, 0);
			}
		}
	}
}
