using System;
using System.Collections.Generic;
using System.Linq;
using RimWorld;
using Verse;

namespace VEF.Storyteller;

public class QuestInfo : IExposable
{
	public Quest questRef;

	private Quest questDeep;

	public int quest_Part_choiceInd = -1;

	public QuestPart_Choice quest_Part_choice;

	public Choice choice;

	public Faction askerFaction;

	public int tickGenerated;

	public QuestCurrencyInfo currencyInfo;

	public int tickCompleted;

	public int tickExpired;

	public int tickAccepted;

	public QuestEndOutcome outcome;

	public QuestScriptDef questDef;

	public Quest Quest
	{
		get
		{
			if (questRef == null)
			{
				return questDeep;
			}
			return questRef;
		}
	}

	public QuestInfo()
	{
	}

	public QuestInfo(Quest quest, Faction askerFaction, QuestCurrencyInfo currencyInfo, bool onlyOneChoice = false, bool saveQuestDeeply = false)
	{
		if (saveQuestDeeply)
		{
			questDeep = quest;
		}
		else
		{
			questRef = quest;
		}
		this.askerFaction = askerFaction;
		this.currencyInfo = currencyInfo;
		tickGenerated = Find.TickManager.TicksAbs;
		if (onlyOneChoice)
		{
			List<QuestPart_Choice> list = Quest.PartsListForReading.Where((QuestPart x) => x is QuestPart_Choice).Cast<QuestPart_Choice>().ToList();
			if (GenCollection.Any<QuestPart_Choice>(list))
			{
				quest_Part_choice = GenCollection.RandomElement<QuestPart_Choice>((IEnumerable<QuestPart_Choice>)list);
				quest_Part_choiceInd = list.IndexOf(quest_Part_choice);
				choice = GenCollection.RandomElement<Choice>((IEnumerable<Choice>)quest_Part_choice.choices);
			}
		}
	}

	public void ExposeData()
	{
		//IL_00d4: Unknown result type (might be due to invalid IL or missing references)
		//IL_00da: Invalid comparison between Unknown and I4
		Scribe_Values.Look<int>(ref tickGenerated, "tickGenerated", 0, false);
		Scribe_References.Look<Faction>(ref askerFaction, "askerFaction", false);
		Scribe_Deep.Look<Quest>(ref questDeep, "questDeep", Array.Empty<object>());
		Scribe_References.Look<Quest>(ref questRef, "quest", false);
		Scribe_Deep.Look<Choice>(ref choice, "choice", Array.Empty<object>());
		Scribe_Deep.Look<QuestCurrencyInfo>(ref currencyInfo, "currencyInfo", Array.Empty<object>());
		Scribe_Values.Look<int>(ref quest_Part_choiceInd, "quest_Part_choiceInd", 0, false);
		Scribe_Defs.Look<QuestScriptDef>(ref questDef, "questDef");
		Scribe_Values.Look<QuestEndOutcome>(ref outcome, "outcome", (QuestEndOutcome)0, false);
		Scribe_Values.Look<int>(ref tickCompleted, "tickCompleted", 0, false);
		Scribe_Values.Look<int>(ref tickExpired, "tickExpired", 0, false);
		if (quest_Part_choiceInd != -1 && (int)Scribe.mode == 4)
		{
			quest_Part_choice = Quest.PartsListForReading.Where((QuestPart x) => x is QuestPart_Choice).Cast<QuestPart_Choice>().ToList()[quest_Part_choiceInd];
		}
	}
}
