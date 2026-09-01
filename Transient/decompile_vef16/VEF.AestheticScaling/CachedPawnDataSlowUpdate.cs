using System;
using System.Collections.Generic;
using Verse;

namespace VEF.AestheticScaling;

public class CachedPawnDataSlowUpdate : GameComponent
{
	public Queue<Pawn> pawnsToRefresh = new Queue<Pawn>();

	public static uint Tick;

	public static uint Tick10;

	public CachedPawnDataSlowUpdate(Game game)
	{
		DictCache<Pawn, CachedPawnData>.Cache.Clear();
	}

	public override void GameComponentTick()
	{
		((GameComponent)this).GameComponentTick();
		if (Tick == uint.MaxValue)
		{
			Tick = 0u;
		}
		Tick++;
		Tick10 = Tick / 10;
		if (pawnsToRefresh.Count == 0)
		{
			foreach (CachedPawnData value2 in DictCache<Pawn, CachedPawnData>.Cache.Values)
			{
				if (value2?.pawn != null && !((Thing)value2.pawn).Discarded)
				{
					pawnsToRefresh.Enqueue(value2.pawn);
				}
			}
			return;
		}
		if (Find.TickManager.TicksGame % 25 != 0)
		{
			return;
		}
		Pawn val = pawnsToRefresh.Dequeue();
		try
		{
			if (val == null || ((Thing)val).Discarded)
			{
				return;
			}
			if (!((Thing)val).Spawned)
			{
				Corpse corpse = val.Corpse;
				if (corpse == null || !((Thing)corpse).Spawned)
				{
					return;
				}
			}
			PawnDataCache.GetPawnDataCache(val, forceRefresh: true);
		}
		catch (Exception ex)
		{
			DictCache<Pawn, CachedPawnData>.Cache.TryRemove(val, out var _);
			throw ex;
		}
	}
}
