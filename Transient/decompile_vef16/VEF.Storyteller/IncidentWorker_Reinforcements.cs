using System;
using System.Collections.Generic;
using System.Linq;
using RimWorld;
using Verse;

namespace VEF.Storyteller;

public class IncidentWorker_Reinforcements : IncidentWorker_RaidEnemy
{
	protected override string GetLetterLabel(IncidentParms parms)
	{
		//IL_0005: Unknown result type (might be due to invalid IL or missing references)
		//IL_000f: Unknown result type (might be due to invalid IL or missing references)
		//IL_001f: Unknown result type (might be due to invalid IL or missing references)
		return TaggedString.op_Implicit(Translator.Translate("VSE.Reinforcements") + ": " + parms.faction.Name);
	}

	protected override string GetLetterText(IncidentParms parms, List<Pawn> pawns)
	{
		//IL_0010: Unknown result type (might be due to invalid IL or missing references)
		//IL_0015: Unknown result type (might be due to invalid IL or missing references)
		//IL_0089: Unknown result type (might be due to invalid IL or missing references)
		//IL_0094: Unknown result type (might be due to invalid IL or missing references)
		//IL_009f: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a4: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a9: Unknown result type (might be due to invalid IL or missing references)
		string text = TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate("VSE.ReinforcementsDesc", NamedArgumentUtility.Named((object)parms.faction, "FACTION")));
		text += "\n\n";
		text += parms.raidStrategy.arrivalTextEnemy;
		Pawn val = pawns.Find((Pawn x) => ((Thing)x).Faction.leader == x);
		if (val != null)
		{
			text += "\n\n";
			text = TaggedString.op_Implicit(text + TranslatorFormattedStringExtensions.Translate("EnemyRaidLeaderPresent", NamedArgument.op_Implicit(((Thing)val).Faction.def.pawnsPlural), NamedArgument.op_Implicit(((Entity)val).LabelShort), NamedArgumentUtility.Named((object)val, "LEADER")));
		}
		return text;
	}

	protected override bool TryExecuteWorker(IncidentParms parms)
	{
		//IL_00fc: Unknown result type (might be due to invalid IL or missing references)
		//IL_0101: Unknown result type (might be due to invalid IL or missing references)
		//IL_010a: Unknown result type (might be due to invalid IL or missing references)
		//IL_010f: Unknown result type (might be due to invalid IL or missing references)
		//IL_021c: Unknown result type (might be due to invalid IL or missing references)
		//IL_021d: Unknown result type (might be due to invalid IL or missing references)
		//IL_017f: Unknown result type (might be due to invalid IL or missing references)
		//IL_01f8: Unknown result type (might be due to invalid IL or missing references)
		//IL_01bc: Unknown result type (might be due to invalid IL or missing references)
		((IncidentWorker_Raid)this).ResolveRaidPoints(parms);
		if (!((IncidentWorker_Raid)this).TryResolveRaidFaction(parms))
		{
			return false;
		}
		PawnGroupKindDef combat = PawnGroupKindDefOf.Combat;
		((IncidentWorker_Raid)this).ResolveRaidStrategy(parms, combat);
		((IncidentWorker_Raid)this).ResolveRaidArriveMode(parms);
		parms.raidStrategy.Worker.TryGenerateThreats(parms);
		if (!parms.raidArrivalMode.Worker.TryResolveRaidSpawnCenter(parms))
		{
			return false;
		}
		float points = parms.points;
		parms.points = IncidentWorker_Raid.AdjustedRaidPoints(parms.points, parms.raidArrivalMode, parms.raidStrategy, parms.faction, combat, parms.target, (RaidAgeRestrictionDef)null);
		RaidPatches.includeRaidToTheList = false;
		List<Pawn> list = parms.raidStrategy.Worker.SpawnThreats(parms);
		if (list == null)
		{
			list = PawnGroupMakerUtility.GeneratePawns(IncidentParmsUtility.GetDefaultPawnGroupMakerParms(combat, parms, false), true).ToList();
			if (list.Count == 0)
			{
				Log.Error("Got no pawns spawning raid from parms " + (object)parms);
				return false;
			}
			parms.raidArrivalMode.Worker.Arrive(list, parms);
		}
		RaidPatches.includeRaidToTheList = true;
		((IncidentWorker_Raid)this).GenerateRaidLoot(parms, points, list);
		TaggedString val = TaggedString.op_Implicit(((IncidentWorker_Raid)this).GetLetterLabel(parms));
		TaggedString val2 = TaggedString.op_Implicit(((IncidentWorker_Raid)this).GetLetterText(parms, list));
		PawnRelationUtility.Notify_PawnsSeenByPlayer_Letter((IEnumerable<Pawn>)list, ref val, ref val2, ((IncidentWorker_Raid)this).GetRelatedPawnsInfoLetterText(parms), true, true);
		List<TargetInfo> list2 = new List<TargetInfo>();
		if (parms.pawnGroups != null)
		{
			List<List<Pawn>> list3 = IncidentParmsUtility.SplitIntoGroups(list, parms.pawnGroups);
			List<Pawn> list4 = GenCollection.MaxBy<List<Pawn>, int>((IEnumerable<List<Pawn>>)list3, (Func<List<Pawn>, int>)((List<Pawn> x) => x.Count));
			if (GenCollection.Any<Pawn>(list4))
			{
				list2.Add(TargetInfo.op_Implicit((Thing)(object)list4[0]));
			}
			for (int i = 0; i < list3.Count; i++)
			{
				if (list3[i] != list4 && GenCollection.Any<Pawn>(list3[i]))
				{
					list2.Add(TargetInfo.op_Implicit((Thing)(object)list3[i][0]));
				}
			}
		}
		else if (GenCollection.Any<Pawn>(list))
		{
			foreach (Pawn item in list)
			{
				list2.Add(TargetInfo.op_Implicit((Thing)(object)item));
			}
		}
		((IncidentWorker)this).SendStandardLetter(val, val2, ((IncidentWorker_Raid)this).GetLetterDef(), parms, LookTargets.op_Implicit(list2), Array.Empty<NamedArgument>());
		parms.raidStrategy.Worker.MakeLords(parms, list);
		LessonAutoActivator.TeachOpportunity(ConceptDefOf.EquippingWeapons, (OpportunityType)2);
		if (!PlayerKnowledgeDatabase.IsComplete(ConceptDefOf.ShieldBelts))
		{
			for (int j = 0; j < list.Count; j++)
			{
				Pawn_ApparelTracker apparel = list[j].apparel;
				if (apparel != null && GenCollection.Any<Apparel>(apparel.WornApparel, (Predicate<Apparel>)((Apparel ap) => ((ThingWithComps)ap).GetComp<CompShield>() != null)))
				{
					LessonAutoActivator.TeachOpportunity(ConceptDefOf.ShieldBelts, (OpportunityType)2);
					break;
				}
			}
		}
		Find.TickManager.slower.SignalForceNormalSpeedShort();
		StatsRecord statsRecord = Find.StoryWatcher.statsRecord;
		statsRecord.numRaidsEnemy++;
		return true;
	}
}
