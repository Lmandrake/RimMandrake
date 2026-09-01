using System;
using System.Collections.Generic;
using System.Linq;
using RimWorld;
using Verse;

namespace VEF.Storyteller;

public class GameComponent_QuestChains : GameComponent
{
	public List<QuestInfo> quests = new List<QuestInfo>();

	public List<FutureQuestInfo> futureQuests = new List<FutureQuestInfo>();

	public static GameComponent_QuestChains Instance;

	private List<QuestScriptDef> questsInChains;

	public Dictionary<QuestChainDef, QuestChainState> questChainStates = new Dictionary<QuestChainDef, QuestChainState>();

	public List<QuestScriptDef> QuestsInChains => questsInChains ?? (questsInChains = DefDatabase<QuestScriptDef>.AllDefsListForReading.Where((QuestScriptDef x) => ((Def)x).GetModExtension<QuestChainExtension>() != null).ToList());

	public GameComponent_QuestChains(Game game)
	{
		Instance = this;
	}

	public override void GameComponentTick()
	{
		((GameComponent)this).GameComponentTick();
		if (Find.TickManager.TicksGame % 60 != 0)
		{
			return;
		}
		for (int num = futureQuests.Count - 1; num >= 0; num--)
		{
			if (futureQuests[num].TryFire())
			{
				futureQuests.RemoveAt(num);
			}
		}
	}

	public override void LoadedGame()
	{
		((GameComponent)this).LoadedGame();
		EnsureAllQuestChainUniquePawns();
		TryScheduleQuests();
	}

	public override void StartedNewGame()
	{
		((GameComponent)this).StartedNewGame();
		EnsureAllQuestChainUniquePawns();
		TryScheduleQuests();
	}

	private void EnsureAllQuestChainUniquePawns()
	{
		foreach (QuestChainDef allDef in DefDatabase<QuestChainDef>.AllDefs)
		{
			allDef.Worker.EnsureAllUniquePawnsCreated();
		}
	}

	public void TryScheduleQuests()
	{
		foreach (QuestScriptDef questsInChain in QuestsInChains)
		{
			TryScheduleQuest(questsInChain);
		}
	}

	public override void ExposeData()
	{
		//IL_0044: Unknown result type (might be due to invalid IL or missing references)
		//IL_004a: Invalid comparison between Unknown and I4
		((GameComponent)this).ExposeData();
		Scribe_Collections.Look<QuestInfo>(ref quests, "finishedQuests", (LookMode)2, Array.Empty<object>());
		Scribe_Collections.Look<FutureQuestInfo>(ref futureQuests, "futureQuests", (LookMode)2, Array.Empty<object>());
		Scribe_Collections.Look<QuestChainDef, QuestChainState>(ref questChainStates, "questChainStates", (LookMode)4, (LookMode)2);
		if ((int)Scribe.mode == 4)
		{
			if (quests == null)
			{
				quests = new List<QuestInfo>();
			}
			if (futureQuests == null)
			{
				futureQuests = new List<FutureQuestInfo>();
			}
			if (questChainStates == null)
			{
				questChainStates = new Dictionary<QuestChainDef, QuestChainState>();
			}
		}
		Instance = this;
	}

	public QuestChainState GetStateFor(QuestChainDef def)
	{
		if (!questChainStates.TryGetValue(def, out var value))
		{
			value = new QuestChainState();
			questChainStates[def] = value;
		}
		return value;
	}

	public void QuestCompleted(Quest quest, QuestEndOutcome outcome)
	{
		//IL_003f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0041: Invalid comparison between Unknown and I4
		//IL_0029: Unknown result type (might be due to invalid IL or missing references)
		//IL_002a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0057: Unknown result type (might be due to invalid IL or missing references)
		//IL_0059: Invalid comparison between Unknown and I4
		QuestInfo questInfo = quests.LastOrDefault((QuestInfo x) => x.Quest == quest);
		if (questInfo != null)
		{
			questInfo.outcome = outcome;
			questInfo.tickCompleted = Find.TickManager.TicksGame;
		}
		if ((int)outcome == 2)
		{
			TryGrantAgainOnFailure(quest.root);
		}
		else if ((int)outcome == 1)
		{
			TryGrantAgainOnSuccess(quest.root);
		}
		TryScheduleQuests();
	}

	public void QuestExpired(Quest quest)
	{
		QuestInfo questInfo = GenCollection.FirstOrDefault<QuestInfo>(quests, (Predicate<QuestInfo>)((QuestInfo x) => x.Quest == quest));
		if (questInfo != null)
		{
			questInfo.tickExpired = Find.TickManager.TicksGame;
		}
		TryGrantAgainOnExpiry(quest.root);
		TryScheduleQuests();
	}

	public bool QuestIsCompletedAndSucceeded(QuestScriptDef quest)
	{
		return GenCollection.Any<QuestInfo>(quests, (Predicate<QuestInfo>)((QuestInfo x) => x.questDef == quest && (int)x.outcome == 1));
	}

	public bool QuestIsCompletedAndFailed(QuestScriptDef quest)
	{
		return GenCollection.Any<QuestInfo>(quests, (Predicate<QuestInfo>)((QuestInfo x) => x.questDef == quest && (int)x.outcome == 2));
	}

	public bool TryScheduleQuest(QuestScriptDef quest)
	{
		//IL_02d7: Unknown result type (might be due to invalid IL or missing references)
		//IL_02dc: Unknown result type (might be due to invalid IL or missing references)
		QuestChainExtension ext = ((Def)quest).GetModExtension<QuestChainExtension>();
		if (ext.requiredResearch != null && !ext.requiredResearch.IsFinished)
		{
			return false;
		}
		if (GenCollection.Any<FutureQuestInfo>(futureQuests, (Predicate<FutureQuestInfo>)((FutureQuestInfo x) => x.questDef == quest)))
		{
			return false;
		}
		if (GenCollection.Any<Quest>(Find.QuestManager.QuestsListForReading, (Predicate<Quest>)((Quest x) => x.root == quest && ((int)x.State == 1 || (int)x.State == 0))))
		{
			return false;
		}
		if (!ext.isRepeatable && GenCollection.Any<QuestInfo>(quests, (Predicate<QuestInfo>)((QuestInfo x) => x.questDef == quest)))
		{
			return false;
		}
		if (ext.conditionEither != null && GenCollection.Any<QuestInfo>(quests, (Predicate<QuestInfo>)((QuestInfo x) => x.questDef == ext.conditionEither && x.tickAccepted > 0)))
		{
			return false;
		}
		if (ext.conditionSucceedQuestsCount != null && ext.conditionSucceedQuestsCount.Count > 0)
		{
			foreach (ConditionSucceedQuestsCount cond in ext.conditionSucceedQuestsCount)
			{
				if (GenCollection.Count<QuestInfo>(quests, (Predicate<QuestInfo>)((QuestInfo x) => x.questDef == cond.questDef && (int)x.outcome == 1)) < cond.count)
				{
					return false;
				}
			}
		}
		if (ext.conditionSucceedQuests != null && !GenList.NullOrEmpty<QuestScriptDef>((IList<QuestScriptDef>)ext.conditionSucceedQuests))
		{
			if (!ext.conditionSucceedQuests.All(QuestIsCompletedAndSucceeded))
			{
				return false;
			}
			ScheduleQuestInTicks(quest, ((IntRange)(ref ext.ticksSinceSucceed)).RandomInRange);
			return true;
		}
		if (ext.conditionFailQuests != null && !GenList.NullOrEmpty<QuestScriptDef>((IList<QuestScriptDef>)ext.conditionFailQuests))
		{
			if (!ext.conditionFailQuests.All(QuestIsCompletedAndFailed))
			{
				return false;
			}
			ScheduleQuestInTicks(quest, ((IntRange)(ref ext.ticksSinceFail)).RandomInRange);
			return true;
		}
		int num = 0;
		if (ext.conditionMinDaysSinceStart.min > 0f && !GenCollection.Any<QuestInfo>(quests, (Predicate<QuestInfo>)((QuestInfo x) => x.questDef == quest)))
		{
			float num2 = ((FloatRange)(ref ext.conditionMinDaysSinceStart)).RandomInRange - (float)GenDate.DaysPassed;
			if (num2 > 0f)
			{
				num = (int)(num2 * 60000f);
				ScheduleQuestInTicks(quest, num);
				return true;
			}
		}
		if (ext.isRepeatable && ext.mtbDaysRepeat > 0f)
		{
			ScheduleQuestMTB(quest, ext.mtbDaysRepeat);
			return true;
		}
		if (ext.delayTicksAfterTriggering.HasValue)
		{
			QuestScriptDef quest2 = quest;
			IntRange value = ext.delayTicksAfterTriggering.Value;
			ScheduleQuestInTicks(quest2, ((IntRange)(ref value)).RandomInRange);
		}
		else
		{
			quest.CreateQuest();
		}
		return true;
	}

	public bool TryGrantAgainOnFailure(QuestScriptDef quest)
	{
		QuestChainExtension modExtension = ((Def)quest).GetModExtension<QuestChainExtension>();
		if (!modExtension.grantAgainOnFailure)
		{
			return false;
		}
		ScheduleQuestInTicks(quest, (int)(60000f * ((FloatRange)(ref modExtension.daysUntilGrantAgainOnFailure)).RandomInRange));
		return true;
	}

	public bool TryGrantAgainOnSuccess(QuestScriptDef quest)
	{
		QuestChainExtension modExtension = ((Def)quest).GetModExtension<QuestChainExtension>();
		if (!modExtension.grantAgainOnSuccess)
		{
			return false;
		}
		ScheduleQuestInTicks(quest, (int)(60000f * ((FloatRange)(ref modExtension.daysUntilGrantAgainOnSuccess)).RandomInRange));
		return true;
	}

	public bool TryGrantAgainOnExpiry(QuestScriptDef quest)
	{
		QuestChainExtension modExtension = ((Def)quest).GetModExtension<QuestChainExtension>();
		if (!modExtension.grantAgainOnExpiry)
		{
			return false;
		}
		ScheduleQuestMTB(quest, (int)(60000f * ((FloatRange)(ref modExtension.daysUntilGrantAgainOnExpiry)).RandomInRange));
		return true;
	}

	public void ScheduleQuestInTicks(QuestScriptDef quest, int ticksInFuture)
	{
		futureQuests.Add(new FutureQuestInfo
		{
			questDef = quest,
			tickToFire = Find.TickManager.TicksGame + ticksInFuture
		});
	}

	public void ScheduleQuestMTB(QuestScriptDef quest, float mtbDays)
	{
		futureQuests.Add(new FutureQuestInfo
		{
			questDef = quest,
			mtbDays = mtbDays
		});
	}
}
