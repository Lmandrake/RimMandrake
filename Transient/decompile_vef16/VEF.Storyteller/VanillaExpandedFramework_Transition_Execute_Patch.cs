using System.Collections.Generic;
using System.Linq;
using HarmonyLib;
using RimWorld;
using Verse;
using Verse.AI.Group;

namespace VEF.Storyteller;

[HarmonyPatch(typeof(Transition))]
[HarmonyPatch("Execute")]
public static class VanillaExpandedFramework_Transition_Execute_Patch
{
	public static void Prefix(Transition __instance, Lord lord)
	{
		//IL_0090: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a5: Unknown result type (might be due to invalid IL or missing references)
		//IL_00aa: Unknown result type (might be due to invalid IL or missing references)
		//IL_00e0: Unknown result type (might be due to invalid IL or missing references)
		//IL_00f5: Unknown result type (might be due to invalid IL or missing references)
		//IL_00fa: Unknown result type (might be due to invalid IL or missing references)
		//IL_01f7: Unknown result type (might be due to invalid IL or missing references)
		//IL_01fc: Unknown result type (might be due to invalid IL or missing references)
		//IL_020d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0214: Unknown result type (might be due to invalid IL or missing references)
		//IL_022c: Expected O, but got Unknown
		//IL_0268: Unknown result type (might be due to invalid IL or missing references)
		//IL_026d: Unknown result type (might be due to invalid IL or missing references)
		StorytellerDefExtension modExtension = ((Def)Find.Storyteller.def).GetModExtension<StorytellerDefExtension>();
		if (modExtension == null || modExtension.storytellerThreat == null || (!__instance.canMoveToSameState && __instance.target == lord.CurLordToil))
		{
			return;
		}
		for (int i = 0; i < __instance.preActions.Count; i++)
		{
			TransitionAction obj = __instance.preActions[i];
			TransitionAction_Message val = (TransitionAction_Message)(object)((obj is TransitionAction_Message) ? obj : null);
			if (val == null || (!(val.message == TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate("MessageRaidersGivenUpLeaving", NamedArgument.op_Implicit(GenText.CapitalizeFirst(lord.faction.def.pawnsPlural)), NamedArgument.op_Implicit(lord.faction.Name)))) && !(val.message == TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate("MessageFightersFleeing", NamedArgument.op_Implicit(GenText.CapitalizeFirst(lord.faction.def.pawnsPlural)), NamedArgument.op_Implicit(lord.faction.Name))))))
			{
				continue;
			}
			StorytellerWatcher component = Current.Game.GetComponent<StorytellerWatcher>();
			for (int num = component.raidGroups.Count - 1; num >= 0; num--)
			{
				if (component.raidGroups[num].lords.Contains(lord) && component.raidGroups[num].lords.Count > 1)
				{
					component.raidGroups[num].lords.Remove(lord);
					return;
				}
			}
			RaidGroup raidGroup = component.raidGroups.Where((RaidGroup x) => x.lords.Contains(lord)).FirstOrDefault();
			if (raidGroup != null)
			{
				if (__instance.Map.IsPlayerHome && FactionUtility.HostileTo(lord.faction, Faction.OfPlayer))
				{
					IncidentParms val2 = new IncidentParms
					{
						target = (IIncidentTarget)(object)lord.Map,
						forced = true,
						points = StorytellerUtility.DefaultThreatPointsNow((IIncidentTarget)(object)lord.Map)
					};
					IncidentDef named = DefDatabase<IncidentDef>.GetNamed(GenCollection.RandomElement<string>((IEnumerable<string>)modExtension.storytellerThreat.goodIncidents), true);
					if (named != null)
					{
						IncidentQueue incidentQueue = Find.Storyteller.incidentQueue;
						int ticksGame = Find.TickManager.TicksGame;
						IntRange val3 = new IntRange(6000, 12000);
						incidentQueue.Add(named, ticksGame + ((IntRange)(ref val3)).RandomInRange, val2, 0);
					}
				}
				component.raidGroups.Remove(raidGroup);
			}
			if (component.reinforcementGroups.Where((RaidGroup x) => x.lords.Contains(lord)).FirstOrDefault() != null)
			{
				component.reinforcementGroups.Remove(raidGroup);
			}
		}
	}
}
