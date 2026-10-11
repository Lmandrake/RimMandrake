using System.Collections.Generic;
using System.Linq;
using RimMandrake.FlowWorks.LiquidTypes;
using RimWorld;
using Verse;

namespace RimMandrake.FlowWorks.Machinery
{
	/// <summary>Where liquid leaving the network at an Outflow hose end goes (rev 2 §3.5).</summary>
	public enum RM_OutletKind { Blocked, Channel, Ground }

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
			}
			// a full or foreign channel, or a wall: blocked; dry open ground takes a spill
			if ((ex != null && ex.IsExcavated(end)) || !end.Standable(map) || end.GetTerrain(map).IsWater)
			{
				return RM_OutletKind.Blocked;
			}
			cell = end;
			return RM_OutletKind.Ground;
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
