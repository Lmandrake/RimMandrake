using System;
using System.Linq;
using HarmonyLib;
using RimWorld;
using Verse;

namespace VEF.Storyteller;

[HarmonyPatch(typeof(Pawn))]
[HarmonyPatch("Kill")]
public static class VanillaExpandedFramework_Pawn_Kill_Patch
{
	public static bool ShouldTriggerReinforcements(Pawn victim, DamageInfo? dinfo, out Faction enemyFaction)
	{
		//IL_0016: Unknown result type (might be due to invalid IL or missing references)
		//IL_001b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0034: Unknown result type (might be due to invalid IL or missing references)
		//IL_0039: Unknown result type (might be due to invalid IL or missing references)
		//IL_0050: Unknown result type (might be due to invalid IL or missing references)
		//IL_0055: Unknown result type (might be due to invalid IL or missing references)
		StorytellerWatcher component = Current.Game.GetComponent<StorytellerWatcher>();
		if (dinfo.HasValue)
		{
			DamageInfo value = dinfo.Value;
			Thing instigator = ((DamageInfo)(ref value)).Instigator;
			if (((instigator != null) ? instigator.Faction : null) != null)
			{
				value = dinfo.Value;
				if (component.FactionPresentInCurrentRaidGroups(((DamageInfo)(ref value)).Instigator.Faction))
				{
					value = dinfo.Value;
					enemyFaction = ((DamageInfo)(ref value)).Instigator.Faction;
					return true;
				}
			}
		}
		if (!dinfo.HasValue)
		{
			foreach (Battle battle in Find.BattleLog.Battles)
			{
				foreach (LogEntry entry in battle.Entries)
				{
					if (entry.Timestamp != Find.TickManager.TicksAbs || !entry.GetConcerns().Contains((Thing)(object)victim))
					{
						continue;
					}
					foreach (Thing concern in entry.GetConcerns())
					{
						if (concern != victim && ((concern != null) ? concern.Faction : null) != null && component.FactionPresentInCurrentRaidGroups(concern.Faction))
						{
							enemyFaction = concern.Faction;
							return true;
						}
					}
				}
			}
			foreach (Battle battle2 in Find.BattleLog.Battles)
			{
				foreach (LogEntry entry2 in battle2.Entries)
				{
					if (entry2.Timestamp <= Find.TickManager.TicksAbs - 60000 || !entry2.GetConcerns().Contains((Thing)(object)victim))
					{
						continue;
					}
					foreach (Thing concern2 in entry2.GetConcerns())
					{
						if (concern2 != victim && ((concern2 != null) ? concern2.Faction : null) != null && component.FactionPresentInCurrentRaidGroups(concern2.Faction))
						{
							enemyFaction = concern2.Faction;
							return true;
						}
					}
				}
			}
		}
		enemyFaction = null;
		return false;
	}

	public static void Prefix(Pawn __instance, DamageInfo? dinfo, Hediff exactCulprit = null)
	{
		//IL_004a: Unknown result type (might be due to invalid IL or missing references)
		//IL_004f: Unknown result type (might be due to invalid IL or missing references)
		//IL_005b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0062: Unknown result type (might be due to invalid IL or missing references)
		//IL_0069: Unknown result type (might be due to invalid IL or missing references)
		//IL_0074: Unknown result type (might be due to invalid IL or missing references)
		//IL_008c: Expected O, but got Unknown
		//IL_00b7: Unknown result type (might be due to invalid IL or missing references)
		//IL_00bc: Unknown result type (might be due to invalid IL or missing references)
		try
		{
			StorytellerDefExtension modExtension = ((Def)Find.Storyteller.def).GetModExtension<StorytellerDefExtension>();
			if (modExtension != null && modExtension.storytellerThreat != null && __instance.IsColonist && ((Thing)__instance).Faction == Faction.OfPlayer && ShouldTriggerReinforcements(__instance, dinfo, out var enemyFaction))
			{
				IncidentParms val = new IncidentParms
				{
					target = (IIncidentTarget)(object)((Thing)__instance).Map,
					faction = enemyFaction,
					forced = true,
					raidStrategy = RaidStrategyDefOf.ImmediateAttack,
					points = StorytellerUtility.DefaultThreatPointsNow((IIncidentTarget)(object)((Thing)__instance).Map) / 4f
				};
				IncidentDef named = DefDatabase<IncidentDef>.GetNamed("VSE_Reinforcements", true);
				IncidentQueue incidentQueue = Find.Storyteller.incidentQueue;
				int ticksGame = Find.TickManager.TicksGame;
				IntRange val2 = new IntRange(300, 600);
				incidentQueue.Add(named, ticksGame + ((IntRange)(ref val2)).RandomInRange, val, 0);
			}
		}
		catch (Exception)
		{
		}
	}
}
