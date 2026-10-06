using System.Collections.Generic;
using RimWorld;
using RimWorld.Planet;
using Verse;

namespace RimMandrake.FlowWorks.Rivers
{
	/// <summary>
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

		public int PendingCount => records.Count;

		public static void WashAway(Pawn p)
		{
			Map map = p.Map;
			if (map == null || !p.Spawned)
			{
				return;
			}
			bool ours = (p.Faction != null && p.Faction.IsPlayer) || (p.HostFaction != null && p.HostFaction.IsPlayer);
			if (!ours)
			{
				Messages.Message(p.LabelShortCap + " was swept off the map by the river.",
					new LookTargets(p.PositionHeld, map), MessageTypeDefOf.NeutralEvent);
				p.DeSpawn();
				Find.WorldPawns.PassToWorld(p, PawnDiscardDecideMode.Decide);
				return;
			}
			RM_WorldComponent_SweptAway comp = Find.World.GetComponent<RM_WorldComponent_SweptAway>();
			if (comp == null)
			{
				return; // cannot hold them: leave the pawn at the edge rather than lose them
			}
			float min = RM_RiversSettings.washedAwayMinDays;
			float max = UnityEngine.Mathf.Max(min, RM_RiversSettings.washedAwayMaxDays);
			float days = Rand.Range(min, max);
			int mapId = map.uniqueID;
			p.DeSpawn();
			Find.WorldPawns.PassToWorld(p, PawnDiscardDecideMode.KeepForever);
			comp.records.Add(new SweptRecord
			{
				pawn = p,
				returnTick = Find.TickManager.TicksGame + (int)(days * GenDate.TicksPerDay),
				mapId = mapId
			});
			Find.LetterStack.ReceiveLetter("Swept away: " + p.LabelShortCap,
				p.LabelShortCap + " was carried off the map by the river's current. "
			  + p.Possessive().CapitalizeFirst() + " will make " + p.Possessive() + " way back on foot in about "
			  + days.ToString("F1") + " days, bruised but alive. Wait for them.",
				LetterDefOf.NegativeEvent);
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
				map = Find.AnyPlayerHomeMap;
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
	}
}
