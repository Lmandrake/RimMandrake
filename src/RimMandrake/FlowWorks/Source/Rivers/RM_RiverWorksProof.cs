using System.Collections.Generic;
using RimWorld;
using Verse;

namespace RimMandrake.FlowWorks.Rivers
{
	/// <summary>
	/// State reads and self-contained probes for River Works' first script
	/// (src/RimMandrake/RiverWorks/validation.py), reached through jawa/static_call. Every
	/// method takes one string and returns one line; a line starting "UNMEASURED" means the
	/// question could not be asked (e.g. no river on the current map), never a pass.
	/// </summary>
	public static class RM_RiverWorksProof
	{
		private static RM_MapComponent_RiverCurrent Comp(out Map map)
		{
			map = Find.CurrentMap;
			return map?.GetComponent<RM_MapComponent_RiverCurrent>();
		}

		/// <summary>"GRID current=N fast=F edge=E size=S flood=B" on the current map.</summary>
		public static string ProofGrid(string arg)
		{
			RM_MapComponent_RiverCurrent comp = Comp(out Map map);
			if (comp == null)
			{
				return "UNMEASURED no map or no RM_MapComponent_RiverCurrent";
			}
			int n = 0, fast = 0, edge = 0;
			foreach (IntVec3 c in map.AllCells)
			{
				if (comp.FlowDirAt(c) < 0)
				{
					continue;
				}
				n++;
				int lane = comp.LaneAt(c);
				if (lane == RM_RiverMath.LaneCentre) fast++;
				else if (lane == RM_RiverMath.LaneMargin) edge++;
			}
			return "GRID current=" + n + " fast=" + fast + " edge=" + edge
			  + " size=" + comp.SizeFactor.ToString("F2") + " flood=" + RM_RiverWorks.FloodActive(map);
		}

		/// <summary>arg = "fast" | "edge" | "ford" [ "|steps" ]. Finds a cell of that lane with
		/// river downstream, spawns a throwaway colonist there (on a fresh ford for "ford"), applies
		/// the shove `steps` times (default 3), reports, and cleans up.
		/// "MOVED k from x,z to x,z lane=L" — k is cells actually moved.</summary>
		public static string ProofShove(string arg)
		{
			RM_MapComponent_RiverCurrent comp = Comp(out Map map);
			if (comp == null || !comp.AnyCurrent)
			{
				return "UNMEASURED no river current on the current map";
			}
			string[] parts = (arg ?? "fast").Split('|');
			string mode = parts[0].Trim().ToLowerInvariant();
			int steps = parts.Length > 1 && int.TryParse(parts[1], out int s) ? s : 3;
			int wantLane = mode == "edge" ? RM_RiverMath.LaneMargin : (mode == "ford" ? RM_RiverMath.LaneMargin : RM_RiverMath.LaneCentre);
			IntVec3 cell = FindRun(comp, map, wantLane, steps + 1);
			if (!cell.IsValid)
			{
				return "UNMEASURED no " + mode + "-lane run of " + (steps + 1) + " cells on this map";
			}
			TerrainDef ford = DefDatabase<TerrainDef>.GetNamedSilentFail("RM_FordStones");
			bool laidFord = false;
			if (mode == "ford")
			{
				if (ford == null)
				{
					return "UNMEASURED RM_FordStones def missing";
				}
				map.terrainGrid.SetTerrain(cell, ford);
				laidFord = true;
			}
			Pawn p = PawnGenerator.GeneratePawn(PawnKindDefOf.Colonist, Faction.OfPlayer);
			GenSpawn.Spawn(p, cell, map);
			IntVec3 start = p.Position;
			try
			{
				for (int i = 0; i < steps && p.Spawned; i++)
				{
					if (!comp.IsCarried(p))
					{
						break;
					}
					comp.StepOne(p);
				}
				IntVec3 end = p.Spawned ? p.Position : IntVec3.Invalid;
				int moved = end.IsValid ? (int)System.Math.Round(start.DistanceTo(end)) : -1;
				return "MOVED " + moved + " from " + start.x + "," + start.z + " to "
				  + (end.IsValid ? end.x + "," + end.z : "offmap") + " lane=" + wantLane;
			}
			finally
			{
				if (p.Spawned)
				{
					p.Destroy();
				}
				if (laidFord)
				{
					map.terrainGrid.RemoveTopLayer(cell, false);
				}
			}
		}

		/// <summary>"EXEMPT building=B" — a wall is never carried.</summary>
		public static string ProofExemptions(string arg)
		{
			RM_MapComponent_RiverCurrent comp = Comp(out Map _);
			if (comp == null)
			{
				return "UNMEASURED no map";
			}
			Thing wall = ThingMaker.MakeThing(ThingDefOf.Wall, ThingDefOf.WoodLog);
			return "EXEMPT building=" + !comp.IsCarried(wall);
		}

		/// <summary>"SWEPT pending=N" and, with arg "return", walks them all home now.</summary>
		public static string ProofSwept(string arg)
		{
			RM_WorldComponent_SweptAway w = Find.World?.GetComponent<RM_WorldComponent_SweptAway>();
			if (w == null)
			{
				return "UNMEASURED no world component";
			}
			if (arg == "return")
			{
				w.ReturnAllNow();
			}
			return "SWEPT pending=" + w.PendingCount;
		}

		private static IntVec3 FindRun(RM_MapComponent_RiverCurrent comp, Map map, int lane, int length)
		{
			List<IntVec3> cells = new List<IntVec3>(map.AllCells);
			foreach (IntVec3 c in cells)
			{
				if (comp.LaneAt(c) != lane || c.GetFirstPawn(map) != null || comp.NearFord(c))
				{
					continue;
				}
				IntVec3 cur = c;
				bool ok = true;
				for (int i = 0; i < length; i++)
				{
					int d = comp.FlowDirAt(cur);
					if (d < 0 || comp.LaneAt(cur) == RM_RiverMath.LaneNone)
					{
						ok = false;
						break;
					}
					IntVec3 nx = new IntVec3(cur.x + RM_RiverMath.StepX[d], 0, cur.z + RM_RiverMath.StepZ[d]);
					if (!nx.InBounds(map) || !nx.Standable(map) || comp.NearFord(nx))
					{
						ok = false;
						break;
					}
					cur = nx;
				}
				if (ok)
				{
					return c;
				}
			}
			return IntVec3.Invalid;
		}
	}
}
