using HarmonyLib;
using RimWorld;
using Verse;

namespace BigAndSmall;

[HarmonyPatch(typeof(PawnsArrivalModeWorker), "CanUseWith")]
public static class PawnsArrivalModeWorker_CanUseWith
{
	public static void Postfix(ref bool __result, PawnsArrivalModeWorker __instance, IncidentParms parms)
	{
		//IL_0041: Unknown result type (might be due to invalid IL or missing references)
		//IL_0047: Invalid comparison between Unknown and I4
		if (__result && parms.faction != null && ((Def)parms.faction.def).HasModExtension<Factions>() && !((Def)parms.faction.def).GetModExtension<Factions>().canUseDropPods)
		{
			__result = (int)parms.faction.def.techLevel <= 3;
		}
	}
}
