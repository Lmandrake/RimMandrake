using System.Collections.Generic;
using System.Linq;
using HarmonyLib;
using RimWorld;
using Verse;
using Verse.AI.Group;

namespace VEF.Storyteller;

[HarmonyPatch(typeof(Lord))]
[HarmonyPatch("Cleanup")]
public static class VanillaExpandedFramework_Lord_Cleanup_Patch
{
	public static void Prefix(Lord __instance)
	{
		//IL_00ff: Unknown result type (might be due to invalid IL or missing references)
		//IL_0104: Unknown result type (might be due to invalid IL or missing references)
		//IL_0115: Unknown result type (might be due to invalid IL or missing references)
		//IL_011c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0134: Expected O, but got Unknown
		//IL_0170: Unknown result type (might be due to invalid IL or missing references)
		//IL_0175: Unknown result type (might be due to invalid IL or missing references)
		StorytellerDefExtension modExtension = ((Def)Find.Storyteller.def).GetModExtension<StorytellerDefExtension>();
		if (modExtension == null || modExtension.storytellerThreat == null)
		{
			return;
		}
		StorytellerWatcher component = Current.Game.GetComponent<StorytellerWatcher>();
		for (int num = component.raidGroups.Count - 1; num >= 0; num--)
		{
			if (component.raidGroups[num].lords.Contains(__instance) && component.raidGroups[num].lords.Count > 1)
			{
				component.raidGroups[num].lords.Remove(__instance);
				return;
			}
		}
		RaidGroup raidGroup = component.raidGroups.Where((RaidGroup x) => x.lords.Contains(__instance)).FirstOrDefault();
		if (raidGroup != null)
		{
			if (__instance.Map.IsPlayerHome && FactionUtility.HostileTo(__instance.faction, Faction.OfPlayer))
			{
				IncidentParms val = new IncidentParms
				{
					target = (IIncidentTarget)(object)__instance.Map,
					forced = true,
					points = StorytellerUtility.DefaultThreatPointsNow((IIncidentTarget)(object)__instance.Map)
				};
				IncidentDef named = DefDatabase<IncidentDef>.GetNamed(GenCollection.RandomElement<string>((IEnumerable<string>)modExtension.storytellerThreat.goodIncidents), true);
				if (named != null)
				{
					IncidentQueue incidentQueue = Find.Storyteller.incidentQueue;
					int ticksGame = Find.TickManager.TicksGame;
					IntRange val2 = new IntRange(6000, 12000);
					incidentQueue.Add(named, ticksGame + ((IntRange)(ref val2)).RandomInRange, val, 0);
				}
			}
			component.raidGroups.Remove(raidGroup);
		}
		if (component.reinforcementGroups.Where((RaidGroup x) => x.lords.Contains(__instance)).FirstOrDefault() != null)
		{
			component.reinforcementGroups.Remove(raidGroup);
		}
	}
}
