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
		// Not saved — a reload just restarts the dwell clock for anything
		// still sitting there; only actual burials (below) are persistent.
		private readonly RM_SwallowKernel.Dwell dwell = new RM_SwallowKernel.Dwell();

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
			if (Find.TickManager.TicksGame % RM_SwallowKernel.CheckIntervalTicks != 0)
			{
				return;
			}
			Scan();
		}

		private void Scan()
		{
			// ThingsInGroup returns the engine's LIVE internal list. Bury()
			// below calls Thing.Destroy(), which synchronously removes the
			// thing from that same list - snapshot to a copy before Bury()
			// can touch the live list.
			List<Thing> haulables = new List<Thing>(map.listerThings.ThingsInGroup(ThingRequestGroup.HaulableEver));
			var byId = new Dictionary<int, Thing>();
			var ids = new List<int>();
			var onMire = new List<bool>();
			var ticks = new List<int>();
			for (int i = 0; i < haulables.Count; i++)
			{
				Thing thing = haulables[i];
				// Not ParentHolder != null: a spawned thing's holder is the map's own spawnedThings ThingOwner.
				if (thing == null || !thing.Spawned)
				{
					continue;
				}
				RM_MireExtension ext = thing.Position.GetTerrain(map)?.GetModExtension<RM_MireExtension>();
				byId[thing.thingIDNumber] = thing;
				ids.Add(thing.thingIDNumber);
				onMire.Add(ext != null);
				ticks.Add(ext != null ? ext.swallowTicks : 0);
			}
			List<int> toBury = dwell.Scan(Find.TickManager.TicksGame, ids.Count, ids.ToArray(), onMire.ToArray(), ticks.ToArray());
			for (int i = 0; i < toBury.Count; i++)
			{
				Bury(byId[toBury[i]]);
			}
		}

		private void Bury(Thing thing)
		{
			IntVec3 cell = thing.Position;
			int stackCount = thing.stackCount;
			ThingDef stuff = thing.Stuff;
			ThingDef def = thing.def;
			thing.Destroy(DestroyMode.Vanish);

			RM_SwallowKernel.Bury(buried, cell.x, cell.z, def, stuff, stackCount, Find.TickManager.TicksGame, () => new RM_BuriedCache());

			if (map.designationManager.DesignationAt(cell, RM_DefOf.RM_DesignationDigOutBuried) == null)
			{
				map.designationManager.AddDesignation(new Designation(cell, RM_DefOf.RM_DesignationDigOutBuried));
			}
		}

		public bool HasBuriedAt(IntVec3 cell)
		{
			return RM_SwallowKernel.HasBuriedAt(buried, cell.x, cell.z);
		}

		/// <summary>Total ticks the oldest cache at this cell has been buried - RM_JobDriver_DigOutBuried scales work by this.</summary>
		public int BuriedDurationAt(IntVec3 cell)
		{
			return RM_SwallowKernel.BuriedDurationAt(buried, cell.x, cell.z, Find.TickManager.TicksGame);
		}

		/// <summary>Spawns every cache buried at this cell back onto the map, in stacks within the def's limit. Whatever cannot be
		/// placed stays buried and keeps the dig designation, so nothing is lost and nothing is orphaned.</summary>
		public void DigOut(IntVec3 cell)
		{
			int left = RM_SwallowKernel.DigOut(buried, cell.x, cell.z, d => ((ThingDef)d).stackLimit, (cache, n) =>
			{
				Thing thing = ThingMaker.MakeThing(cache.thingDef, cache.stuffDef);
				thing.stackCount = n;
				// GenPlace.TryPlaceThing's bool return must be checked: on a fully blocked map it silently drops the Thing.
				return GenPlace.TryPlaceThing(thing, cell, map, ThingPlaceMode.Near);
			});
			if (left == 0)
			{
				Designation designation = map.designationManager.DesignationAt(cell, RM_DefOf.RM_DesignationDigOutBuried);
				if (designation != null)
				{
					map.designationManager.RemoveDesignation(designation);
				}
			}
		}
	}
}
