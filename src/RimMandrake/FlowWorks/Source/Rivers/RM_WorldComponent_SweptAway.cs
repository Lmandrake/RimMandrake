using System.Collections.Generic;
using RimWorld;
using RimWorld.Planet;
using Verse;

namespace RimMandrake.FlowWorks.Rivers
{
	/// <summary>
	/// LEGACY since TAKEN_BY_LAND_SERVICE_1: drains records saved before the shared service (TakenByLand/RM_TakenByLand.cs); new
	/// takes go through the service. Delete once no save holds a record here.
	/// Owner card 1 (2026-10-03, typed): swept to the map edge = washed away, walks home later,
	/// WITH a letter saying what happened so the player knows to wait. And the heat ruling's
	/// "no pawn ever vanishes without a readable sign" — so strangers get a message too.
	///
	/// A washed-away pawn of ours is held as a world pawn (KeepForever) and respawned at an
	/// edge cell of the same map after 1-3 days (PROVISIONAL). If that map is gone it comes
	/// home to any player home map; if there is none it stays lost and a letter says so.
	/// </summary>
	public class RM_WorldComponent_SweptAway : WorldComponent
	{
		private List<SweptRecord> records = new List<SweptRecord>();

		public RM_WorldComponent_SweptAway(World world) : base(world)
		{
		}

		public int PendingCount => records.Count + (Find.World?.GetComponent<TakenByLand.RM_WorldComponent_TakenByLand>()?.PendingCount ?? 0);

		/// <summary>TAKEN_BY_LAND_SERVICE_1: a pawn washed off the map edge is now taken through the shared service (hold, letter,
		/// ground trace, return). This book only drains records saved before it.</summary>
		public static void WashAway(Pawn p)
		{
			TakenByLand.RM_TakenByLand.Take(p, "river");
		}

		public override void WorldComponentTick()
		{
			if (records.Count == 0 || Find.TickManager.TicksGame % GenTicks.TickRareInterval != 0)
			{
				return;
			}
			int now = Find.TickManager.TicksGame;
			for (int i = records.Count - 1; i >= 0; i--)
			{
				SweptRecord r = records[i];
				if (r.pawn == null || r.pawn.Destroyed || r.pawn.Dead)
				{
					records.RemoveAt(i);
					continue;
				}
				if (now < r.returnTick)
				{
					continue;
				}
				if (TryReturn(r))
				{
					records.RemoveAt(i);
				}
			}
		}

		/// <summary>Bring one back now. Public so the first script can skip the wait.</summary>
		public bool TryReturn(SweptRecord r)
		{
			Map map = null;
			List<Map> maps = Find.Maps;
			for (int i = 0; i < maps.Count; i++)
			{
				if (maps[i].uniqueID == r.mapId)
				{
					map = maps[i];
				}
			}
			if (map == null)
			{
				map = SurfaceHomeMap();
			}
			if (map == null)
			{
				return false; // nowhere to walk home to yet; keep waiting
			}
			if (!CellFinder.TryFindRandomEdgeCellWith(c => c.Standable(map) && !c.GetTerrain(map).IsWater, map,
					CellFinder.EdgeRoadChance_Neutral, out IntVec3 cell)
				&& !CellFinder.TryFindRandomEdgeCellWith(c => c.Standable(map), map, 0f, out cell))
			{
				return false;
			}
			if (Find.WorldPawns.Contains(r.pawn))
			{
				Find.WorldPawns.RemovePawn(r.pawn);
			}
			GenSpawn.Spawn(r.pawn, cell, map);
			Find.LetterStack.ReceiveLetter("Back from the river: " + r.pawn.LabelShortCap,
				r.pawn.LabelShortCap + " has walked back after being washed away downstream.",
				LetterDefOf.PositiveEvent, r.pawn);
			return true;
		}

		public void ReturnAllNow()
		{
			Find.World?.GetComponent<TakenByLand.RM_WorldComponent_TakenByLand>()?.ReturnAllNow();
			for (int i = records.Count - 1; i >= 0; i--)
			{
				if (TryReturn(records[i]))
				{
					records.RemoveAt(i);
				}
			}
		}

		public override void ExposeData()
		{
			base.ExposeData();
			Scribe_Collections.Look(ref records, "rmSweptAway", LookMode.Deep);
			if (Scribe.mode == LoadSaveMode.PostLoadInit && records == null)
			{
				records = new List<SweptRecord>();
			}
		}

		public class SweptRecord : IExposable
		{
			public Pawn pawn;

			public int returnTick;

			public int mapId;

			public void ExposeData()
			{
				Scribe_References.Look(ref pawn, "pawn", true);
				Scribe_Values.Look(ref returnTick, "returnTick", 0);
				Scribe_Values.Look(ref mapId, "mapId", -1);
			}
		}

		// SURFACE_HOME_MAP_HELPER_1: never the sea floor (ship is the only way down). Same test as
		// EnvironmentalHazards.RM_SurfaceHome; FlowWorks cannot reference that assembly, so it is repeated here.
		private static Map SurfaceHomeMap()
		{
			List<Map> maps = Find.Maps;
			for (int i = 0; i < maps.Count; i++)
			{
				Map m = maps[i];
				if (m.IsPlayerHome && !(m.Tile.Valid && m.Tile.Layer?.Def?.defName == "RM_SeabedLayer"))
				{
					return m;
				}
			}
			return null;
		}
}
}
