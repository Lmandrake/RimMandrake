using System;
using System.Collections.Generic;
using System.Linq;
using Verse;

namespace BigAndSmall;

public class HumanoidPawnScaler : DictCache<Pawn, BSCache>
{
	public struct PerThreadMiniCache
	{
		public Pawn pawn;

		public BSCache cache;

		public bool properCache;
	}

	[ThreadStatic]
	private static PerThreadMiniCache _tCache;

	[ThreadStatic]
	private static Dictionary<int, BSCache> _tDictCache;

	[ThreadStatic]
	private static int tick10;

	[ThreadStatic]
	private static int threadGameInt;

	public static void ShedueleForceRegenerateSafe(Pawn pawn, int tick)
	{
		ShedueleForceRegenerate(GetCache(pawn, forceRefresh: false, canRegenerate: false), tick);
	}

	public static BSCache GetCacheUltraSpeed(Pawn pawn, bool canRegenerate = false)
	{
		if (threadGameInt != BigAndSmallCache.gameInt)
		{
			ClearSessionData();
		}
		if (_tCache.pawn != pawn || !_tCache.properCache)
		{
			_tCache.pawn = pawn;
			if (_tDictCache.TryGetValue(((Thing)pawn).thingIDNumber, out var value))
			{
				_tCache.cache = value;
				if (BS.Tick10 != tick10)
				{
					tick10 = BS.Tick10;
					_tDictCache.Clear();
				}
				return value;
			}
			_tCache.cache = GetCache(pawn, forceRefresh: false, canRegenerate);
			_tCache.properCache = !_tCache.cache.IsTempCache;
			return _tCache.cache;
		}
		return _tCache.cache;
	}

	private static void ClearSessionData()
	{
		_tDictCache?.Clear();
		threadGameInt = BigAndSmallCache.gameInt;
		_tDictCache = new Dictionary<int, BSCache>();
		GeneCache.ClearCaches();
	}

	/// <summary>
	/// ForceRefresh and get the cache... later, unless paused. If pasued get it now. Mostly to force updates when in character editor, etc.
	/// </summary>
	public static BSCache GetInvalidateLater(Pawn pawn, int scheduleForce = 10)
	{
		TickManager tickManager = Find.TickManager;
		if (tickManager == null || !tickManager.Paused)
		{
			TickManager tickManager2 = Find.TickManager;
			if (tickManager2 == null || !tickManager2.NotPlaying)
			{
				BSCache cache = GetCache(pawn, forceRefresh: false, canRegenerate: false);
				ShedueleForceRegenerate(cache, scheduleForce);
				return cache;
			}
		}
		return GetCache(pawn, forceRefresh: true);
	}

	/// <summary>
	/// Note that if the pawn is "null" then it will use a generic cache with default values. This is mostly to just get rid of the need to
	/// null-check everything that calls this method.
	/// </summary>
	/// <returns></returns>
	public static BSCache GetCache(Pawn pawn, bool forceRefresh = false, bool canRegenerate = true, int scheduleForce = -1, bool reevaluateGraphics = false)
	{
		if (pawn == null)
		{
			return BSCache.defaultCache;
		}
		BSCache bSCache;
		bool newEntry;
		if (canRegenerate && RunNormalCalculations(pawn))
		{
			bSCache = DictCache<Pawn, BSCache>.GetCacheInner(pawn, out newEntry, forceRefresh);
		}
		else
		{
			bSCache = DictCache<Pawn, BSCache>.GetCacheInner(pawn, out newEntry, forceRefresh, canRegenerate: false);
			if (bSCache.IsTempCache)
			{
				BSCache bSCache2 = CheckForScribedEntry(pawn);
				if (bSCache2 != null)
				{
					bSCache = bSCache2;
				}
			}
		}
		if (newEntry || forceRefresh)
		{
			if (newEntry)
			{
				BSCache bSCache3 = CheckForScribedEntry(pawn);
				if (bSCache3 != null)
				{
					bSCache = bSCache3;
				}
				else
				{
					BigAndSmallCache.ScribedCache.Add(bSCache);
					ShedueleForceRegenerate(bSCache, 1);
				}
			}
			if (!bSCache.IsTempCache)
			{
				pawn.GetCachePrepatchedThreaded() = bSCache;
				pawn.GetCachePrepatched() = bSCache;
			}
			SafeGfxDirty(pawn);
		}
		else if (reevaluateGraphics)
		{
			bSCache.ReevaluateGraphics();
		}
		if (scheduleForce > -1)
		{
			ShedueleForceRegenerate(bSCache, scheduleForce);
		}
		return bSCache;
		static void SafeGfxDirty(Pawn pawn)
		{
			if (((Thing)pawn).Spawned)
			{
				pawn.Drawer.renderer.SetAllGraphicsDirty();
			}
			Corpse corpse = pawn.Corpse;
			if (corpse != null && ((Thing)corpse).Spawned)
			{
				pawn.Corpse.RotStageChanged();
			}
		}
	}

	private static void ShedueleForceRegenerate(BSCache cache, int delay)
	{
		if (!BigAndSmallCache.currentlyQueued.Contains(cache))
		{
			int key = BS.Tick + delay;
			if (!BigAndSmallCache.scheduleFullUpdate.ContainsKey(key))
			{
				BigAndSmallCache.scheduleFullUpdate[key] = new HashSet<BSCache>();
			}
			BigAndSmallCache.scheduleFullUpdate[key].Add(cache);
			BigAndSmallCache.currentlyQueued.Add(cache);
		}
	}

	public static BSCache CheckForScribedEntry(Pawn pawn)
	{
		string id = ((Thing)pawn).ThingID;
		using (IEnumerator<BSCache> enumerator = BigAndSmallCache.ScribedCache.Where((BSCache x) => x.id == id).GetEnumerator())
		{
			if (enumerator.MoveNext())
			{
				BSCache current = enumerator.Current;
				DictCache<Pawn, BSCache>.Cache[pawn] = current;
				current.pawn = pawn;
				return current;
			}
		}
		return null;
	}

	public static bool RunNormalCalculations(Pawn pawn)
	{
		if (pawn != null && BigSmall.performScaleCalculations && (BigSmallMod.settings.scaleAnimals || pawn.RaceProps.Humanlike))
		{
			if (pawn.needs == null)
			{
				return pawn.Dead;
			}
			return true;
		}
		return false;
	}
}
