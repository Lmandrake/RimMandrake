using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using HarmonyLib;
using RimWorld;
using Verse;

namespace VEF.Storyteller;

[StaticConstructorOnStartup]
public static class RaidPatches
{
	public static bool includeRaidToTheList;

	static RaidPatches()
	{
		//IL_004e: Unknown result type (might be due to invalid IL or missing references)
		//IL_005a: Expected O, but got Unknown
		includeRaidToTheList = true;
		MethodInfo method = typeof(RaidPatches).GetMethod("RaidGroupChecker");
		foreach (Type item in GenTypes.AllSubclassesNonAbstract(typeof(PawnsArrivalModeWorker)))
		{
			MethodInfo method2 = item.GetMethod("Arrive");
			try
			{
				VEF_Mod.harmonyInstance.Patch((MethodBase)method2, (HarmonyMethod)null, new HarmonyMethod(method), (HarmonyMethod)null, (HarmonyMethod)null);
			}
			catch (Exception)
			{
				Log.Error("Error patching " + item?.ToString() + " - " + method2);
			}
		}
	}

	public static void RaidGroupChecker(List<Pawn> pawns, IncidentParms parms)
	{
		if (pawns == null || parms == null)
		{
			return;
		}
		Game game = Current.Game;
		StorytellerWatcher storytellerWatcher = ((game != null) ? game.GetComponent<StorytellerWatcher>() : null);
		if (storytellerWatcher == null)
		{
			return;
		}
		RaidGroup raidGroup = new RaidGroup();
		if (parms.faction != null)
		{
			raidGroup.faction = parms.faction;
		}
		else
		{
			raidGroup.faction = ((Thing)pawns.First()).Faction;
		}
		raidGroup.pawns = pawns.ToHashSet();
		if (includeRaidToTheList)
		{
			if (storytellerWatcher.raidGroups == null)
			{
				storytellerWatcher.raidGroups = new List<RaidGroup>();
			}
			storytellerWatcher.raidGroups.Add(raidGroup);
		}
		else
		{
			if (storytellerWatcher.reinforcementGroups == null)
			{
				storytellerWatcher.reinforcementGroups = new List<RaidGroup>();
			}
			storytellerWatcher.reinforcementGroups.Add(raidGroup);
		}
	}
}
