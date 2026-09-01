using System;
using System.Collections.Generic;
using System.Linq;
using RimWorld;
using Verse;

namespace BigAndSmall;

public class BigAndSmallCache : GameComponent
{
	public static BigAndSmallCache instance = null;

	public static Dictionary<Gene, bool?> frequentUpdateGenes = new Dictionary<Gene, bool?>();

	private HashSet<BSCache> scribedCache = new HashSet<BSCache>();

	public static bool regenerationAttempted = false;

	public Game game;

	/// <summary>
	/// Increments by one every time a new game is started.
	///
	/// Starts at 1 so thread caches will be invalid from the start.
	/// </summary>
	public static int gameInt = 1;

	public static Queue<Pawn> refreshQueue = new Queue<Pawn>();

	public static Queue<Action> queuedJobs = new Queue<Action>();

	public static Dictionary<int, HashSet<BSCache>> schedulePostUpdate = new Dictionary<int, HashSet<BSCache>>();

	public static Dictionary<int, HashSet<BSCache>> scheduleFullUpdate = new Dictionary<int, HashSet<BSCache>>();

	public static HashSet<BSCache> currentlyQueued = new HashSet<BSCache>();

	public static float globalRandNum = 1f;

	public static HashSet<BSCache> ScribedCache
	{
		get
		{
			return instance.scribedCache;
		}
		set
		{
			instance.scribedCache = value;
		}
	}

	public BigAndSmallCache(Game game)
	{
		this.game = game;
		instance = this;
	}

	public override void FinalizeInit()
	{
		((GameComponent)this).FinalizeInit();
		List<Pawn> all_AliveOrDead = PawnsFinder.All_AliveOrDead;
		RaceFuser.PostSaveLoadedSetup();
		foreach (Pawn item in all_AliveOrDead.Where((Pawn x) => x != null && !((Thing)x).Discarded && !((Thing)x).Destroyed))
		{
			HumanoidPawnScaler.GetCache(item, forceRefresh: false, canRegenerate: true, 1);
		}
	}

	public void QueueJobOrRunNowIfPaused(Action job)
	{
		TickManager tickManager = Find.TickManager;
		if (tickManager != null && tickManager.Paused)
		{
			job();
		}
		else
		{
			queuedJobs.Enqueue(job);
		}
	}

	public override void ExposeData()
	{
		//IL_0012: Unknown result type (might be due to invalid IL or missing references)
		//IL_0018: Invalid comparison between Unknown and I4
		Scribe_Collections.Look<BSCache>(ref scribedCache, false, "BS_scribedCache", (LookMode)2);
		if ((int)Scribe.mode == 2)
		{
			gameInt++;
			queuedJobs.Clear();
			schedulePostUpdate.Clear();
			scheduleFullUpdate.Clear();
			currentlyQueued.Clear();
			DictCache<Pawn, BSCache>.Cache.Clear();
		}
	}

	public override void GameComponentTick()
	{
		BS.IncrementTick();
		int tick = BS.Tick;
		if (queuedJobs.Count > 0)
		{
			queuedJobs.Dequeue()();
		}
		if (schedulePostUpdate.Count > 0 && schedulePostUpdate.TryGetValue(tick, out var value))
		{
			foreach (BSCache item in value)
			{
				item?.DelayedUpdate();
			}
			schedulePostUpdate.Remove(tick);
		}
		if (scheduleFullUpdate.Count > 0 && scheduleFullUpdate.TryGetValue(tick, out var value2))
		{
			foreach (BSCache item2 in value2)
			{
				Pawn val = item2?.pawn;
				try
				{
					if (val != null && !((Thing)val).Discarded)
					{
						HumanoidPawnScaler.GetCache(val, forceRefresh: true);
					}
				}
				finally
				{
					currentlyQueued.Remove(item2);
				}
			}
			scheduleFullUpdate.Remove(tick);
		}
		if (tick % 100 == 0)
		{
			SlowUpdate(tick / 100);
		}
	}

	private static void SlowUpdate(int currentTick)
	{
		Rand.PushState(currentTick);
		globalRandNum = Rand.Value;
		Rand.PopState();
		if (refreshQueue.Count == 0)
		{
			foreach (BSCache value in DictCache<Pawn, BSCache>.Cache.Values)
			{
				if (value.pawn != null)
				{
					refreshQueue.Enqueue(value.pawn);
				}
			}
		}
		else if (currentTick % 5 == 0)
		{
			Pawn val = refreshQueue.Dequeue();
			if (val != null)
			{
				if (!((Thing)val).Spawned)
				{
					Corpse corpse = val.Corpse;
					if (corpse == null || !((Thing)corpse).Spawned)
					{
						goto IL_00a5;
					}
				}
				HumanoidPawnScaler.GetCache(val, forceRefresh: true);
			}
		}
		goto IL_00a5;
		IL_00a5:
		if (BigSmallMod.settings.jesusMode && currentTick % 10 == 0)
		{
			foreach (Pawn item in PawnsFinder.AllMapsAndWorld_Alive.Where((Pawn x) => x != null && !((Thing)x).Discarded && !((Thing)x).Destroyed))
			{
				Pawn_NeedsTracker needs = item.needs;
				if (needs != null)
				{
					needs.AllNeeds?.ForEach(delegate(Need x)
					{
						x.CurLevel = x.MaxLevel;
					});
				}
			}
		}
		bool flag = currentTick % 4 == 0;
		List<Gene> list = new List<Gene>();
		Gene[] array = frequentUpdateGenes.Keys.ToArray();
		foreach (Gene val2 in array)
		{
			Pawn val3 = val2?.pawn;
			if (val3 == null || ((Thing)val3).Discarded)
			{
				list.Add(val2);
			}
			else
			{
				if (!((Thing)val3).Spawned && !val3.IsColonist)
				{
					continue;
				}
				bool? flag2 = frequentUpdateGenes[val2].Value;
				LockedNeed.UpdateLockedNeeds(val2);
				bool flag3 = val2.Active != flag2;
				if (flag)
				{
					if (flag3 && flag2.HasValue)
					{
						HumanoidPawnScaler.GetInvalidateLater(val2.pawn);
					}
					val2.OverrideBy(val2.overriddenByGene);
					if (!flag3)
					{
						flag3 = val2.Active != flag3;
					}
				}
				if (flag3)
				{
					frequentUpdateGenes[val2] = val2.Active;
					val2.pawn.genes.Notify_GenesChanged(val2.def);
				}
			}
		}
		for (int j = 0; j < list.Count; j++)
		{
			frequentUpdateGenes.Remove(list[j]);
		}
	}
}
