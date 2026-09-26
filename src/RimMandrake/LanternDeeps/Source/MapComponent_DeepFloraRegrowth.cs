using UnityEngine;
using Verse;

namespace RimMandrake.LanternDeeps
{
	// CAVERNS_PARITY_BUILD_1 — regrowth of the Deep's own flora during play.
	//
	// Vanilla's WildPlantSpawner tick never reads the biome's wildPlants under a
	// natural roof (DeepFloraPlanter's header has the measured source), so
	// without this a Deep would only ever regrow the planet-wide cavePlant set.
	//
	// A CustomMapComponent, listed by RM_LanternDeepGenerator.customMapComponents,
	// so it exists ONLY on Deep pocket maps (Verse.Map.FillComponents skips
	// CustomMapComponent subclasses in its auto-add loop). Its own class rather
	// than a tick bolted onto MapComponent_LanternDeepDarkness: that component
	// early-returns on darknessMechanicEnabled, its saved state is ambush
	// exposure, and the two features are separately toggled in Mod Settings —
	// keeping them apart means turning off the darkness mechanic cannot also
	// stop the mushrooms.
	//
	// Cost: every RegrowIntervalTicks, a handful of random-cell attempts and
	// one listerThings count. The whole-map desired total is recomputed only
	// every RecountEveryIntervals intervals (about once a day), never per tick.
	//
	// Rate, loosely against wildPlantRegrowDays 5: a few attempts per interval
	// until the map holds vanilla's desired count, then nothing. Vanilla's
	// saturation curve and per-cell MTB are not chased; the cap is the promise.
	public class MapComponent_DeepFloraRegrowth : CustomMapComponent
	{
		private const int RegrowIntervalTicks = 2000;
		private const int RecountEveryIntervals = 30; // 60,000 ticks = one day
		private const int MinAttemptsPerInterval = 4;
		private const int MaxAttemptsPerInterval = 24;
		private const float AttemptsPerCell = 0.002f;

		private float cachedDesiredTotal = -1f;
		private int intervalsSinceRecount;

		public MapComponent_DeepFloraRegrowth(Map map)
			: base(map)
		{
		}

		// Nothing worth saving: the desired total is recomputed on the first
		// interval after load.

		public override void MapComponentTick()
		{
			if (!LanternDeepsSettings.deepFloraEnabled)
			{
				return;
			}
			if (!map.IsHashIntervalTick(RegrowIntervalTicks))
			{
				return;
			}
			if (!DeepFloraPlanter.IsDeep(map))
			{
				return;
			}
			Regrow();
		}

		private void Regrow()
		{
			if (cachedDesiredTotal < 0f || ++intervalsSinceRecount >= RecountEveryIntervals)
			{
				cachedDesiredTotal = DeepFloraPlanter.DesiredWholeMapCount(map);
				intervalsSinceRecount = 0;
			}
			if (cachedDesiredTotal <= 0f)
			{
				return;
			}
			int have = DeepFloraPlanter.CurrentPlantCount(map);
			if (have >= cachedDesiredTotal)
			{
				return;
			}

			int attempts = Mathf.Clamp(Mathf.CeilToInt(map.Area * AttemptsPerCell),
				MinAttemptsPerInterval, MaxAttemptsPerInterval);
			for (int i = 0; i < attempts && have < cachedDesiredTotal; i++)
			{
				IntVec3 c = CellFinder.RandomCell(map);
				if (DeepFloraPlanter.TryPlantAt(map, c, setRandomGrowth: false))
				{
					have++;
				}
			}
		}
	}
}
