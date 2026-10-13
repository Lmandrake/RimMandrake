using System.Collections.Generic;
using System.Linq;
using RimMandrake.FlowWorks.LiquidTypes;
using RimWorld;
using Verse;

namespace RimMandrake.FlowWorks.Machinery
{
	/// <summary>Where liquid leaving the network at an Outflow hose end goes (rev 2 §3.5).</summary>
	/// <remarks>Body (POND_RETURN_LEG_BUILD_WATER_GOES_HOME): a natural pond square or its dry bed takes the level back
	/// into the pond's stock, whole levels only. Appended last so the older values keep their numbers.</remarks>
	public enum RM_OutletKind { Blocked, Channel, Ground, Body }

	/// <summary>
	/// Liquid networks L7 (rev 2 §3.5, §3.7): the world side of an Outflow end, and the spill. A level of a liquid with a channel
	/// form goes into an excavated cell at the end or the best one within 1.5 cells (RM_PumpMath.PickPour, A14); dry open ground
	/// takes any liquid as a spill: its filth (LiquidDef.spillFilth, else RM_Filth_LiquidSpill), one per unitsPerFilth units,
	/// cleanable by colonists in the home area. A full or foreign channel, or a wall, is BLOCKED and moves nothing. Filth is a
	/// world record of the spill, never converted back into liquid units.
	/// </summary>
	public static class RM_LiquidSpill
	{
		/// <summary>State read (probe, selftests): units spilled as filth this session, and spills no cell would take (logged).</summary>
		public static int SpilledUnits, Unplaced;

		/// <summary>What an Outflow end at <paramref name="end"/> does with <paramref name="liquid"/> (<paramref name="fluid"/> is
		/// its channel form, if any): pour into <paramref name="cell"/>, spill there, or nothing.</summary>
		public static RM_OutletKind Outlet(Map map, RM_MapComponent_Excavation ex, IntVec3 end, LiquidDef liquid, FluidDef fluid, out IntVec3 cell)
		{
			cell = IntVec3.Invalid;
			if (map == null || !end.InBounds(map) || (liquid == null && fluid == null))
			{
				return RM_OutletKind.Blocked;
			}
			fluid = fluid ?? liquid?.canalFluid;
			if (ex != null && fluid != null)
			{
				var cells = new List<IntVec3>();
				var cd = new List<(int room, bool wet, FluidDef fill)>();
				foreach (IntVec3 c in new[] { end }.Concat(GenAdj.CellsAdjacent8Way(new TargetInfo(end, map))))
				{
					if (c.InBounds(map) && ex.CanPourLevel(c, fluid))
					{
						cells.Add(c);
						cd.Add((ex.DepthAt(c) - ex.FillAt(c), ex.FillAt(c) > 0, ex.FluidAt(c)));
					}
				}
				var tk = new List<(bool canProvide, FluidDef fluid)> { (true, fluid) };
				if (RM_PumpMath.PickPour(tk, cd, out _, out int ci))
				{
					cell = cells[ci];
					return RM_OutletKind.Channel;
				}
				// POND_RETURN_LEG_BUILD_WATER_GOES_HOME (G1): no dug cell takes it, but the pond (or its dried bed) it came
				// from may: the end square first, then its neighbours in the fixed adjacency order.
				foreach (IntVec3 c in new[] { end }.Concat(GenAdj.CellsAdjacent8Way(new TargetInfo(end, map))))
				{
					if (c.InBounds(map) && ex.CanReturnLevels(c, fluid, 1))
					{
						cell = c;
						return RM_OutletKind.Body;
					}
				}
			}
			// a full or foreign channel, or a wall: blocked; dry open ground takes a spill
			if ((ex != null && ex.IsExcavated(end)) || !end.Standable(map) || end.GetTerrain(map).IsWater)
			{
				return RM_OutletKind.Blocked;
			}
			cell = end;
			return RM_OutletKind.Ground;
		}

		/// <summary>The world leg for an outlet <paramref name="kind"/> at <paramref name="cell"/>: a channel cell takes a level, a
		/// pond takes a whole level back into its stock (all or nothing), dry ground takes the units as a spill. One place, so
		/// the pump's world-to-world move, its pour and the Dump drain all route the same way.</summary>
		public static RM_TransferLeg OutletLeg(Map map, RM_MapComponent_Excavation ex, RM_OutletKind kind, IntVec3 cell, LiquidDef liquid, FluidDef fluid)
		{
			switch (kind)
			{
				case RM_OutletKind.Channel:
					return RM_TransferLeg.World(k => ex.CanPourLevel(cell, fluid), k => ex.TryPourLevel(cell, fluid));
				case RM_OutletKind.Body:
					return RM_TransferLeg.World(k => ex.CanReturnLevels(cell, fluid, 1), k => ex.TryReturnLevels(cell, fluid, 1));
				default:
					return RM_TransferLeg.Sink(k => Spill(map, cell, liquid, k));
			}
		}

		/// <summary>True when the outlet takes whole levels only (a channel or a pond), false for a spill.</summary>
		public static bool WholeLevels(RM_OutletKind kind) => kind == RM_OutletKind.Channel || kind == RM_OutletKind.Body;

		/// <summary>State read: units hoses emptied when they stopped carrying (L8).</summary>
		public static int DrainedUnits;

		/// <summary>Where a stopped hose empties (rev 2 §3.7): out of its free end when it has one, else at the reel.</summary>
		public static IntVec3 DrainCell(Hose.CompHoseReel r, Map map)
		{
			if (r?.parent == null)
			{
				return IntVec3.Invalid;
			}
			IntVec3 end = r.EndCell;
			bool free = end.IsValid && map != null && map.GetComponent<Hose.RM_MapComponent_Hoses>()?.RelayOf(r) == null && Hose.HosePorts.FindAt(map, end, r.parent, out _, out _) == null;
			return free ? end : r.parent.Position;
		}

		/// <summary>L8 (rev 2 §3.7): a hose that stops carrying empties what it holds at <paramref name="cell"/> (its free end, else
		/// the reel): whole levels into a channel that takes them, the rest as a spill; never back into a tank. Conserved: the units
		/// leave the hose's ledger through the transfer service.</summary>
		public static void DrainHeld(Hose.CompHoseReel r, Map map, IntVec3 cell)
		{
			if (r == null || r.heldUnits <= 0)
			{
				return;
			}
			LiquidDef liquid = r.heldLiquid;
			if (map == null || !cell.IsValid)
			{
				// off any map (a reel taken off it): nowhere to put it; said once, never silent
				Log.WarningOnce("[FlowWorks] a hose holding " + r.heldUnits + " " + liquid?.defName + " left the map; the liquid went with it", 0x5B1118);
				object hl0 = liquid;
				RM_HoseHold.Drain(ref hl0, ref r.heldUnits, null);
				r.heldLiquid = null;
				return;
			}
			RM_MapComponent_Excavation ex = RM_SuperdeepTrap.EngineOf(map);
			int units = r.heldUnits;
			int held = r.heldUnits;
			// the hose's ledger as the source leg; the world (channel levels, then a spill) as the sink
			RM_TransferLeg hose = RM_TransferLeg.Store(k => held >= k, k => { held -= k; return true; }, k => { held += k; return true; });
			RM_TransferLeg world = RM_TransferLeg.Sink(k => PlaceHeld(map, ex, cell, liquid, k));
			if (RM_LiquidTransfer.Move(units, hose, world, out _) == units)
			{
				DrainedUnits += units;
			}
			r.heldUnits = held;
			if (held <= 0)
			{
				r.heldLiquid = null;
			}
		}

		/// <summary>Held liquid reaching the world: whole levels into a channel cell at or near <paramref name="cell"/>, the rest
		/// (and any liquid with no channel form) spilled as filth there.</summary>
		private static void PlaceHeld(Map map, RM_MapComponent_Excavation ex, IntVec3 cell, LiquidDef liquid, int units)
		{
			int level = RM_PumpMath.TankUnitsPerLevel;
			while (units >= level && Outlet(map, ex, cell, liquid, liquid?.canalFluid, out IntVec3 c) == RM_OutletKind.Channel && ex.TryPourLevel(c, liquid.canalFluid))
			{
				units -= level;
			}
			if (units > 0)
			{
				Spill(map, cell, liquid, units);
			}
		}

		/// <summary>Spill <paramref name="units"/> of <paramref name="liquid"/> at <paramref name="cell"/> as filth (rev 2 §3.7):
		/// RM_LiquidNetKernel.FilthCount pieces of the liquid's spill filth, propagating to a neighbour where the cell refuses; the
		/// generic spill where its own filth will not lie; one warning if nothing would. Always "accepts" (a sink).</summary>
		public static void Spill(Map map, IntVec3 cell, LiquidDef liquid, int units)
		{
			if (map == null || units <= 0)
			{
				return;
			}
			SpilledUnits += units;
			int n = RM_LiquidNetKernel.FilthCount(units, RM_MachinerySettings.unitsPerFilth);
			ThingDef own = liquid?.spillFilth ?? RimMandrakeFlowWorks_DefOf.RM_Filth_LiquidSpill;
			for (int i = 0; i < n; i++)
			{
				if (FilthMaker.TryMakeFilth(cell, map, own) || (own != RimMandrakeFlowWorks_DefOf.RM_Filth_LiquidSpill
				    && RimMandrakeFlowWorks_DefOf.RM_Filth_LiquidSpill != null && FilthMaker.TryMakeFilth(cell, map, RimMandrakeFlowWorks_DefOf.RM_Filth_LiquidSpill)))
				{
					continue;
				}
				Unplaced++;
				Log.WarningOnce("[FlowWorks] a spill of " + liquid?.defName + " at " + cell + " found no cell that takes filth; the liquid left the network anyway", 0x5B1117);
				break;
			}
		}
	}
}
