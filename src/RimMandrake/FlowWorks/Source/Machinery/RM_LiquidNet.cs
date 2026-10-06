using System.Collections.Generic;
using RimMandrake.FlowWorks.LiquidTypes;
using Verse;

namespace RimMandrake.FlowWorks.Machinery
{
	/// <summary>Marks a ThingDef as a liquid hose (FLOWWORKS_BUILD_PROGRAM_1 Phase 8, "flexible tubing";
	/// design §4 RM_HoseSpool: fast-build, cheap, fragile, NOT terrain and NOT a VE pipe).</summary>
	public class RM_LiquidHoseExtension : DefModExtension
	{
	}

	/// <summary>
	/// The liquid net: which tanks a pump, converter or adapter can reach. A machine reaches every tank that
	/// touches it (8-way, as the first pump slice did), plus every tank touching a hose run that touches it.
	/// Hoses conduct cardinally, like a conduit; tanks and machines do not conduct (a tank is an endpoint, so
	/// two separate runs never merge through a tank by accident). Recomputed on demand — machines cycle every
	/// few hundred ticks and a run is short, so no cached graph to keep in step with build/deconstruct.
	/// Mod Setting: liquidHosesEnabled (off: adjacency only, exactly the first pump slice).
	/// </summary>
	public static class RM_LiquidNet
	{
		/// <summary>Search cap: a hose run longer than this is not followed further (PROVISIONAL).</summary>
		public const int MaxHoseCells = 1500;

		public static bool IsHose(Thing t)
		{
			return t?.def?.GetModExtension<RM_LiquidHoseExtension>() != null;
		}

		public static bool HasHose(IntVec3 c, Map map)
		{
			List<Thing> things = c.GetThingList(map);
			for (int i = 0; i < things.Count; i++)
			{
				if (IsHose(things[i]))
				{
					return true;
				}
			}
			return false;
		}

		/// <summary>Every liquid tank on <paramref name="origin"/>'s net, nearest-first (adjacent tanks lead).
		/// Never includes <paramref name="origin"/> itself.</summary>
		public static List<Building_LiquidTank> TanksFor(Thing origin)
		{
			var result = new List<Building_LiquidTank>();
			Map map = origin?.Map;
			if (map == null)
			{
				return result;
			}
			var seenTanks = new HashSet<Thing>();
			void AddTanksAround(IEnumerable<IntVec3> cells)
			{
				foreach (IntVec3 c in cells)
				{
					if (!c.InBounds(map))
					{
						continue;
					}
					List<Thing> things = c.GetThingList(map);
					for (int i = 0; i < things.Count; i++)
					{
						if (things[i] is Building_LiquidTank tank && tank != origin && seenTanks.Add(tank))
						{
							result.Add(tank);
						}
					}
				}
			}

			AddTanksAround(GenAdj.CellsAdjacent8Way(origin));
			if (!RM_MachinerySettings.liquidHosesEnabled)
			{
				return result;
			}

			var frontier = new Queue<IntVec3>();
			var visited = new HashSet<IntVec3>();
			foreach (IntVec3 c in GenAdj.CellsAdjacent8Way(origin))
			{
				if (c.InBounds(map) && HasHose(c, map) && visited.Add(c))
				{
					frontier.Enqueue(c);
				}
			}
			// A machine standing on a hose (hoses are under-floor-ish) also joins that run.
			foreach (IntVec3 c in origin.OccupiedRect())
			{
				if (c.InBounds(map) && HasHose(c, map) && visited.Add(c))
				{
					frontier.Enqueue(c);
				}
			}
			while (frontier.Count > 0 && visited.Count <= MaxHoseCells)
			{
				IntVec3 c = frontier.Dequeue();
				AddTanksAround(GenAdj.CellsAdjacentCardinal(c, Rot4.North, IntVec2.One));
				AddTanksAround(new[] { c });
				for (int d = 0; d < 4; d++)
				{
					IntVec3 n = c + GenAdj.CardinalDirections[d];
					if (n.InBounds(map) && !visited.Contains(n) && HasHose(n, map))
					{
						visited.Add(n);
						frontier.Enqueue(n);
					}
				}
			}
			return result;
		}

		/// <summary>First tank on the net that can take <paramref name="units"/> of <paramref name="liquid"/>,
		/// preferring one already holding it (so a run fills one tank before opening the next).</summary>
		public static Building_LiquidTank TankToFill(Thing origin, LiquidDef liquid, int units, Building_LiquidTank except = null)
		{
			Building_LiquidTank empty = null;
			foreach (Building_LiquidTank t in TanksFor(origin))
			{
				if (t == except || !t.CanAccept(liquid, units))
				{
					continue;
				}
				if (!t.Empty)
				{
					return t;
				}
				empty = empty ?? t;
			}
			return empty;
		}
	}
}
