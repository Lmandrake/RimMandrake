using System;
using System.Collections.Generic;
using System.Linq;
using RimWorld;
using RimWorld.QuestGen;
using Verse;

namespace VEF.Storyteller;

public class QuestWorker
{
	public QuestGiverDef def;

	public virtual List<QuestInfo> GenerateQuests(QuestGiverManager questGiverManager)
	{
		//IL_00a5: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ac: Expected O, but got Unknown
		List<QuestInfo> list = new List<QuestInfo>();
		int num = ((def.maximumAvailableQuestCount != -1) ? (def.maximumAvailableQuestCount - questGiverManager.AvailableQuests.Count) : 100);
		float num2 = StorytellerUtility.DefaultThreatPointsNow((IIncidentTarget)(object)Find.World);
		List<QuestScriptDef> list2 = ((questGiverManager.def.onlySpecifiedQuests != null) ? questGiverManager.def.onlySpecifiedQuests : DefDatabase<QuestScriptDef>.AllDefs.Where((QuestScriptDef x) => !x.isRootSpecial && x.IsRootAny).ToList());
		while (list.Count < num && GenCollection.Any<QuestScriptDef>(list2) && GenCollection.Any<QuestScriptDef>(list2))
		{
			QuestScriptDef val = GenCollection.RandomElement<QuestScriptDef>((IEnumerable<QuestScriptDef>)list2);
			list2.Remove(val);
			try
			{
				Slate val2 = new Slate();
				val2.Set<float>("points", num2, false);
				if (val == QuestScriptDefOf.LongRangeMineralScannerLump)
				{
					val2.Set<ThingDef>("targetMineable", ThingDefOf.MineableGold, false);
					val2.Set<Pawn>("worker", PawnsFinder.AllMaps_FreeColonists.FirstOrDefault(), false);
				}
				if (val.CanRun(val2, (IIncidentTarget)(object)Find.World))
				{
					Quest val3 = QuestGen.Generate(val, val2);
					QuestInfo questInfo;
					if (def.currency == null)
					{
						QuestInfo item = new QuestInfo(val3, questGiverManager.FixedQuestGiverFaction, null, questGiverManager.def.onlyOneReward, saveQuestDeeply: true);
						list.Add(item);
					}
					else if (def.currency.Allows(questGiverManager, val3, VanillaExpandedFramework_QuestGen_AddSlateQuestTags_Patch.slate, out questInfo))
					{
						list.Add(questInfo);
					}
				}
			}
			catch (Exception)
			{
			}
		}
		return list;
	}
}
