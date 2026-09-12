using System.Collections.Generic;
using Verse;

namespace RimMandrake.Greentide
{
	/// <summary>
	/// GREENTIDE_STANDALONE_MOD_1 (M8, swallow half). Any loose haulable
	/// Thing left on a terrain carrying RM_MireExtension for that terrain's
	/// swallowTicks gets despawned into a per-cell buried record and a
	/// RM_DesignationDigOutBuried designation appears. RM_JobDriver_DigOutBuried
	/// restores it — nothing is ever destroyed.
	///
	/// 🔴 NO EXEMPTION for items in a player stockpile/haul-to zone — owner
	/// ruling 2026-09-11 on the churnmud card: mud under a stockpile swallows
	/// stored items too. This component deliberately never consults
	/// map.haulDestinationManager or SlotGroup at all.
	/// </summary>
	public class RM_MapComponent_MudSwallow : MapComponent
	{
		private const int CheckIntervalTicks = 250;

		// Not saved — a reload just restarts the dwell clock for anything
		// still sitting there; only actual burials (below) are persistent.
		private readonly Dictionary<Thing, int> firstSeenTick = new Dictionary<Thing, int>();

		private List<RM_BuriedCache> buried = new List<RM_BuriedCache>();

		public RM_MapComponent_MudSwallow(Map map)
			: base(map)
		{
		}

		public override void ExposeData()
		{
			base.ExposeData();
			Scribe_Collections.Look(ref buried, "buriedCaches", LookMode.Deep);
			if (Scribe.mode == LoadSaveMode.PostLoadInit && buried == null)
			{
				buried = new List<RM_BuriedCache>();
			}
		}

		public override void MapComponentTick()
		{
			base.MapComponentTick();
			if (!RM_GreentideSettings.buriedCacheEnabled)
			{
				return; // MOD_OPTIONS_RETROFIT_1: master toggle, all-off degrades to a no-op
			}
			if (Find.TickManager.TicksGame % CheckIntervalTicks != 0)
			{
				return;
			}
			Scan();
		}

		private void Scan()
		{
			// ThingsInGroup returns the engine's LIVE internal list. Bury()
			// below calls Thing.Destroy(), which synchronously removes the
			// thing from that same list — mutating it mid-iteration would
			// shift the next element into the slot we just consumed, so it
			// gets skipped this pass and its firstSeenTick entry is wrongly
			// purged below as "moved off hazardous ground" (full dwell-timer
			// reset, no exception, no log). Snapshot to a copy before Bury()
			// can touch the live list.
			List<Thing> haulables = new List<Thing>(map.listerThings.ThingsInGroup(ThingRequestGroup.HaulableEver));
			var stillPresent = new HashSet<Thing>();
			var toBury = new List<Thing>();
			for (int i = 0; i < haulables.Count; i++)
			{
				Thing thing = haulables[i];
				if (thing == null || !thing.Spawned || thing.ParentHolder != null)
				{
					continue;
				}
				TerrainDef terrain = thing.Position.GetTerrain(map);
				RM_MireExtension ext = terrain?.GetModExtension<RM_MireExtension>();
				if (ext == null)
				{
					continue;
				}
				stillPresent.Add(thing);
				if (!firstSeenTick.TryGetValue(thing, out int firstTick))
				{
					firstSeenTick[thing] = Find.TickManager.TicksGame;
					continue;
				}
				if (Find.TickManager.TicksGame - firstTick >= ext.swallowTicks)
				{
					toBury.Add(thing);
					firstSeenTick.Remove(thing);
				}
			}
			for (int i = 0; i < toBury.Count; i++)
			{
				Bury(toBury[i]);
			}
			// Drop tracking for anything that moved off hazardous ground or despawned.
			if (firstSeenTick.Count > 0)
			{
				var stale = new List<Thing>();
				foreach (KeyValuePair<Thing, int> kv in firstSeenTick)
				{
					if (!stillPresent.Contains(kv.Key))
					{
						stale.Add(kv.Key);
					}
				}
				for (int i = 0; i < stale.Count; i++)
				{
					firstSeenTick.Remove(stale[i]);
				}
			}
		}

		private void Bury(Thing thing)
		{
			IntVec3 cell = thing.Position;
			int stackCount = thing.stackCount;
			ThingDef stuff = thing.Stuff;
			ThingDef def = thing.def;
			thing.Destroy(DestroyMode.Vanish);

			RM_BuriedCache existing = buried.Find(c => c.cell == cell && c.thingDef == def && c.stuffDef == stuff);
			if (existing != null)
			{
				existing.stackCount += stackCount;
				existing.buriedTick = Find.TickManager.TicksGame;
			}
			else
			{
				buried.Add(new RM_BuriedCache(cell, def, stuff, stackCount, Find.TickManager.TicksGame));
			}

			if (map.designationManager.DesignationAt(cell, RM_DefOf.RM_DesignationDigOutBuried) == null)
			{
				map.designationManager.AddDesignation(new Designation(cell, RM_DefOf.RM_DesignationDigOutBuried));
			}
		}

		public bool HasBuriedAt(IntVec3 cell)
		{
			return buried.Exists(c => c.cell == cell);
		}

		/// <summary>Total ticks the oldest cache at this cell has been buried — RM_JobDriver_DigOutBuried scales work by this.</summary>
		public int BuriedDurationAt(IntVec3 cell)
		{
			int longest = 0;
			for (int i = 0; i < buried.Count; i++)
			{
				if (buried[i].cell == cell)
				{
					int age = Find.TickManager.TicksGame - buried[i].buriedTick;
					if (age > longest)
					{
						longest = age;
					}
				}
			}
			return longest;
		}

		/// <summary>Spawns every cache buried at this cell back onto the map and clears the designation. Nothing is lost.</summary>
		public void DigOut(IntVec3 cell)
		{
			for (int i = buried.Count - 1; i >= 0; i--)
			{
				RM_BuriedCache cache = buried[i];
				if (cache.cell != cell)
				{
					continue;
				}
				Thing thing = ThingMaker.MakeThing(cache.thingDef, cache.stuffDef);
				thing.stackCount = cache.stackCount;
				// GenPlace.TryPlaceThing's bool return must be checked: on a fully
				// blocked map it silently drops the Thing (see JawaBenchIncidentTools.cs
				// for the same trap). Only clear the buried record once it actually lands.
				if (GenPlace.TryPlaceThing(thing, cell, map, ThingPlaceMode.Near))
				{
					buried.RemoveAt(i);
				}
			}
			Designation designation = map.designationManager.DesignationAt(cell, RM_DefOf.RM_DesignationDigOutBuried);
			if (designation != null)
			{
				map.designationManager.RemoveDesignation(designation);
			}
		}
	}
}
