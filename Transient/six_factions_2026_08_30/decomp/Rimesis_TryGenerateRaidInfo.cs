using System;
using System.Collections.Generic;
using System.Linq;
using HarmonyLib;
using RimWorld;
using Verse;
using Verse.AI;

namespace Rimesis;

[HarmonyPatch(typeof(IncidentWorker_Raid), "TryGenerateRaidInfo")]
public static class Patch_IncidentWorker_Raid_TryGenerateRaidInfo
{
	[HarmonyPriority(800)]
	public static void Prefix(IncidentWorker_Raid __instance, IncidentParms parms)
	{
		RimesisRaidGenerationContext.Begin(parms, __instance);
	}

	[HarmonyPriority(0)]
	public static void Postfix(IncidentParms parms, List<Pawn> pawns, bool __result)
	{
		//IL_0176: Unknown result type (might be due to invalid IL or missing references)
		//IL_017b: Unknown result type (might be due to invalid IL or missing references)
		if (!__result || pawns == null)
		{
			if (__result)
			{
				RimesisRaidPlan.Consume(parms.faction);
			}
			return;
		}
		RimesisWorldComponent manager = RimesisWorldComponent.Current;
		List<Pawn> list = pawns.Where((Pawn p) => manager?.Get(p) != null).Distinct().ToList();
		if (list.Count == 0)
		{
			RimesisRaidPlan rimesisRaidPlan = RimesisRaidPlan.For(parms.faction);
			if (rimesisRaidPlan != null && rimesisRaidPlan.records.Count > 0)
			{
				Faction faction = parms.faction;
				Log.Warning("[Rimesis] A raid plan for " + (((faction != null) ? faction.Name : null) ?? "unknown faction") + " selected Rimesis pawns, but none reached the generated pawn list.");
			}
			RimesisRaidPlan.Consume(parms.faction);
			return;
		}
		foreach (Pawn item in list)
		{
			if (((Thing)item).Spawned && ((Def)(item.jobs?.curJob?.def?)).defName == "IdleWhileDespawned")
			{
				item.jobs.EndCurrentJob((JobCondition)16, false, true);
			}
		}
		RimesisRecord rimesisRecord = manager.Get(list[0]);
		RimesisRaidPlan rimesisRaidPlan2 = RimesisRaidPlan.For(parms.faction);
		RimesisRecord rimesisRecord2 = rimesisRaidPlan2?.records.FirstOrDefault() ?? rimesisRecord;
		RimesisRecord rimesisRecord3 = BrightArchotechFacilityRaidContext.GuardianFor(parms);
		string text = RimesisWorldComponent.IncidentTargetName(parms.target);
		if (text == null)
		{
			TaggedString val = Translator.Translate("Rimesis_TheSettlement");
			text = ((object)(TaggedString)(ref val)/*cast due to .constrained prefix*/).ToString();
		}
		string text2 = text;
		foreach (Pawn item2 in list)
		{
			RimesisRecord rimesisRecord4 = manager.Get(item2);
			manager.MarkReturned(item2, false, rimesisRaidPlan2?.colonyProfile, (rimesisRecord4 == rimesisRecord3) ? RimesisEventType.Ambushed : ((rimesisRecord4 == rimesisRecord2) ? RimesisEventType.LedAssault : RimesisEventType.JoinedAssault), text2);
		}
		RetaliationRecord retaliationRecord = ((rimesisRaidPlan2 != null && rimesisRaidPlan2.retaliationArmed) ? manager.PendingRetaliation(parms.faction) : null);
		if (retaliationRecord != null)
		{
			retaliationRecord.consumed = true;
			rimesisRecord.AddEvent(RimesisEventType.SettlementRetaliation, retaliationRecord.settlementName);
			if (rimesisRaidPlan2 != null && rimesisRaidPlan2.retaliationPointsCaptured)
			{
				object[] array = new object[5];
				Faction faction2 = parms.faction;
				array[0] = ((faction2 != null) ? faction2.Name : null) ?? "unknown faction";
				array[1] = retaliationRecord.settlementName;
				array[2] = rimesisRaidPlan2.retaliationPointsBefore;
				array[3] = rimesisRaidPlan2.retaliationPointsAfter;
				array[4] = rimesisRaidPlan2.retaliationPointMultiplier;
				RimesisLog.DevMessage(string.Format("[Rimesis] Settlement retaliation fired for {0} after the destruction of {1}: raid points {2:0.##} -> {3:0.##} (x{4:0.00}).", array));
			}
		}
		RimesisRaidLetterContext.Remember(parms, from r in list.Select(manager.Get)
			where r != null
			select r, manager.BuildRaidLetterAddition(list.Select(manager.Get), retaliationRecord?.settlementName, text2));
		RimesisRaidPlan.Consume(parms.faction);
	}

	public static Exception Finalizer(Exception __exception)
	{
		RimesisRaidGenerationContext.End();
		return __exception;
	}
}
You are not using the latest version of the tool, please update.
Latest version is '11.0.0.9375' (yours is '9.0.0.7889')
