using System;
using System.Collections.Generic;
using RimWorld;
using Verse;

namespace VEF.Storyteller;

public class QuestGiverManager : IExposable
{
	public QuestGiverDef def;

	private List<QuestInfo> availableQuests = new List<QuestInfo>();

	private int lastResetTick;

	public Faction FixedQuestGiverFaction
	{
		get
		{
			if (def.fixedQuestGiverFaction == null)
			{
				return Find.FactionManager.RandomAlliedFaction(false, false, true, (TechLevel)0);
			}
			return Find.FactionManager.FirstFactionOfDef(def.fixedQuestGiverFaction);
		}
	}

	public List<QuestInfo> AvailableQuests
	{
		get
		{
			if (availableQuests == null)
			{
				availableQuests = new List<QuestInfo>();
			}
			availableQuests.RemoveAll((QuestInfo x) => x == null || x.askerFaction == null || x.quest_Part_choice == null || x.choice == null);
			return availableQuests;
		}
	}

	public QuestGiverManager()
	{
	}

	public QuestGiverManager(QuestGiverDef def)
	{
		this.def = def;
		availableQuests = new List<QuestInfo>();
	}

	public void Tick()
	{
		if (def.resetEveryTick != -1 && Find.TickManager.TicksAbs > lastResetTick + def.resetEveryTick)
		{
			Reset();
		}
	}

	public void Init()
	{
		GenerateQuests();
	}

	public void Reset()
	{
		availableQuests.Clear();
		GenerateQuests();
		lastResetTick = Find.TickManager.TicksAbs;
	}

	public void GenerateQuests()
	{
		availableQuests.AddRange(def.Worker.GenerateQuests(this));
	}

	public void ActivateQuest(Pawn accepter, QuestInfo questInfo)
	{
		Find.QuestManager.Add(questInfo.Quest);
		questInfo.Quest.Accept(accepter);
		QuestUtility.SendLetterQuestAvailable(questInfo.Quest, (string)null);
		questInfo.currencyInfo?.Buy(questInfo);
		availableQuests.Remove(questInfo);
	}

	public void CallWindow()
	{
		//IL_001a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0020: Expected O, but got Unknown
		Window val = (Window)Activator.CreateInstance(def.windowClass, this);
		Find.WindowStack.Add(val);
	}

	public void ExposeData()
	{
		Scribe_Collections.Look<QuestInfo>(ref availableQuests, "availableQuests", (LookMode)2, Array.Empty<object>());
		Scribe_Defs.Look<QuestGiverDef>(ref def, "def");
		Scribe_Values.Look<int>(ref lastResetTick, "lastResetTick", 0, false);
	}
}
