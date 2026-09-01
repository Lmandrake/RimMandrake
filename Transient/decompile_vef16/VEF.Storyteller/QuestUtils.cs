using System.Collections.Generic;
using System.Linq;
using RimWorld;
using RimWorld.Planet;
using UnityEngine;
using Verse;

namespace VEF.Storyteller;

public static class QuestUtils
{
	public static void CreateQuest(this QuestScriptDef questDef)
	{
		Quest val = QuestUtility.GenerateQuestAndMakeAvailable(questDef, StorytellerUtility.DefaultThreatPointsNow((IIncidentTarget)(object)Find.World));
		if (questDef.sendAvailableLetter)
		{
			QuestUtility.SendLetterQuestAvailable(val, (string)null);
		}
	}

	public static List<PawnKindDef> GeneratePawnKindList(Faction faction, float points, Site site)
	{
		//IL_0000: Unknown result type (might be due to invalid IL or missing references)
		//IL_0005: Unknown result type (might be due to invalid IL or missing references)
		//IL_0010: Unknown result type (might be due to invalid IL or missing references)
		//IL_0012: Unknown result type (might be due to invalid IL or missing references)
		//IL_0017: Unknown result type (might be due to invalid IL or missing references)
		//IL_001c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0023: Unknown result type (might be due to invalid IL or missing references)
		//IL_002a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0036: Expected O, but got Unknown
		PawnGroupMakerParms val = new PawnGroupMakerParms
		{
			groupKind = PawnGroupKindDefOf.Combat,
			tile = ((WorldObject)site).Tile,
			faction = faction,
			points = points,
			raidStrategy = RaidStrategyDefOf.ImmediateAttack
		};
		float num = faction.def.MinPointsToGeneratePawnGroup(val.groupKind, val);
		points = ((num < float.MaxValue) ? Mathf.Max(points, num) : points);
		val.points = points;
		List<PawnKindDef> list = new List<PawnKindDef>();
		while (!GenCollection.Any<PawnKindDef>(list) && points < 99999f)
		{
			points += 50f;
			val.points = points;
			list = GeneratePawnKinds(val, warnOnZeroResults: false).ToList();
		}
		return list;
	}

	public static IEnumerable<PawnKindDef> GeneratePawnKinds(PawnGroupMakerParms parms, bool warnOnZeroResults = true)
	{
		PawnGroupMaker val = default(PawnGroupMaker);
		if (parms.groupKind == null || parms.faction == null || GenList.NullOrEmpty<PawnGroupMaker>((IList<PawnGroupMaker>)parms.faction.def.pawnGroupMakers) || !PawnGroupMakerUtility.TryGetRandomPawnGroupMaker(parms, ref val, false))
		{
			yield break;
		}
		foreach (PawnKindDef item in val.GeneratePawnKindsExample(parms))
		{
			yield return item;
		}
	}

	public static string FormatPawnListToString(List<PawnKindDef> pawns)
	{
		if (pawns == null || !GenCollection.Any<PawnKindDef>(pawns))
		{
			return "";
		}
		return GenText.ToCommaList(from p in pawns
			group p by p into @group
			select $"{@group.Count()} {((Def)@group.Key).label}", false, false);
	}

	public static T GetAssociatedPart<T>(this MapParent parent) where T : QuestPart_Site
	{
		foreach (Quest item in Find.QuestManager.QuestsListForReading.Where((Quest x) => (int)x.State == 1))
		{
			foreach (T item2 in item.PartsListForReading.OfType<T>())
			{
				if (item2.mapParent != parent)
				{
					PocketMapParent val = (PocketMapParent)(object)((parent is PocketMapParent) ? parent : null);
					if (val == null || val.sourceMap.Parent != item2.mapParent)
					{
						continue;
					}
				}
				return item2;
			}
		}
		return null;
	}
}
