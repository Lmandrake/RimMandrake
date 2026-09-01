using System;
using System.Collections.Generic;
using RimWorld;
using Verse;

namespace VEF.Storyteller;

public class StorytellerWatcher : GameComponent
{
	public int lastRaidExpansionTicks;

	public StorytellerDef currentStoryteller;

	public List<RaidGroup> raidGroups;

	public List<RaidGroup> reinforcementGroups;

	public List<RaidQueue> raidQueues;

	public Dictionary<int, QuestGiverManager> questGiverManagers;

	private List<int> intKeys = new List<int>();

	private List<QuestGiverManager> questGiverValues = new List<QuestGiverManager>();

	public StorytellerWatcher()
	{
	}

	public StorytellerWatcher(Game game)
	{
	}

	public QuestGiverManager AddQuestGiverManager(int questManagerID, QuestGiverDef def)
	{
		QuestGiverManager questGiverManager = new QuestGiverManager(def);
		questGiverManagers[questManagerID] = questGiverManager;
		if (def.generateOnce)
		{
			questGiverManager.GenerateQuests();
		}
		return questGiverManager;
	}

	public override void GameComponentTick()
	{
		((GameComponent)this).GameComponentTick();
		if (Find.TickManager.TicksGame % 60 == 0)
		{
			CheckStorytellerChanges();
			foreach (QuestGiverManager value in questGiverManagers.Values)
			{
				value.Tick();
			}
		}
		List<RaidQueue> list = raidQueues;
		if (list == null || !GenCollection.Any<RaidQueue>(list))
		{
			return;
		}
		for (int num = raidQueues.Count - 1; num >= 0; num--)
		{
			RaidQueue raidQueue = raidQueues[num];
			if (Find.TickManager.TicksAbs >= raidQueue.tickToFire)
			{
				try
				{
					raidQueue.incidentDef.Worker.TryExecute(raidQueue.parms);
				}
				catch
				{
					try
					{
						if (raidQueue.parms.target == null)
						{
							raidQueue.parms.target = (IIncidentTarget)(object)Find.RandomPlayerHomeMap;
						}
						IncidentParms val = StorytellerUtility.DefaultParmsNow(raidQueue.incidentDef.category, raidQueue.parms.target);
						val.faction = raidQueue.parms.faction;
						raidQueue.incidentDef.Worker.TryExecute(val);
					}
					catch
					{
					}
				}
				raidQueues.RemoveAt(num);
			}
		}
	}

	public void PreInit()
	{
		if (raidGroups == null)
		{
			raidGroups = new List<RaidGroup>();
		}
		if (reinforcementGroups == null)
		{
			reinforcementGroups = new List<RaidGroup>();
		}
		if (raidQueues == null)
		{
			raidQueues = new List<RaidQueue>();
		}
		if (questGiverManagers == null)
		{
			questGiverManagers = new Dictionary<int, QuestGiverManager>();
		}
	}

	public override void LoadedGame()
	{
		((GameComponent)this).LoadedGame();
		PreInit();
	}

	public override void StartedNewGame()
	{
		((GameComponent)this).StartedNewGame();
		PreInit();
	}

	public void CheckStorytellerChanges()
	{
		if (currentStoryteller != Find.Storyteller.def)
		{
			currentStoryteller = Find.Storyteller.def;
		}
	}

	public bool GroupHasLivingPawns(HashSet<Pawn> group)
	{
		foreach (Pawn item in group)
		{
			if (item != null && ((Thing)item).Map != null && !item.Dead && !item.Downed && !((Thing)item).Destroyed)
			{
				return true;
			}
		}
		return false;
	}

	public bool FactionPresentInCurrentRaidGroups(Faction faction)
	{
		for (int num = raidGroups.Count - 1; num >= 0; num--)
		{
			if (raidGroups[num].faction == faction)
			{
				if (GroupHasLivingPawns(raidGroups[num].pawns))
				{
					return true;
				}
				raidGroups.RemoveAt(num);
			}
		}
		for (int num2 = reinforcementGroups.Count - 1; num2 >= 0; num2--)
		{
			if (reinforcementGroups[num2].faction == faction)
			{
				if (GroupHasLivingPawns(reinforcementGroups[num2].pawns))
				{
					return true;
				}
				reinforcementGroups.RemoveAt(num2);
			}
		}
		return false;
	}

	public override void ExposeData()
	{
		((GameComponent)this).ExposeData();
		Scribe_Values.Look<int>(ref lastRaidExpansionTicks, "lastRaidExpansionTicks", 0, false);
		Scribe_Defs.Look<StorytellerDef>(ref currentStoryteller, "currentStoryteller");
		Scribe_Collections.Look<RaidGroup>(ref raidGroups, "raidGroups", (LookMode)2, Array.Empty<object>());
		Scribe_Collections.Look<RaidGroup>(ref reinforcementGroups, "reinforcementGroups", (LookMode)2, Array.Empty<object>());
		Scribe_Collections.Look<int, QuestGiverManager>(ref questGiverManagers, "questGiverManagers", (LookMode)1, (LookMode)2, ref intKeys, ref questGiverValues, true, false, false);
		Scribe_Collections.Look<RaidQueue>(ref raidQueues, "raidQueues", (LookMode)2, Array.Empty<object>());
	}
}
