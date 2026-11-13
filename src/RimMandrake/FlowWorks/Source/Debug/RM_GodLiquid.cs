using System.Collections.Generic;
using System.Linq;
using RimMandrake.FlowWorks.MapControls;
using RimMandrake.FlowWorks.Sheet;
using Verse;

namespace RimMandrake.FlowWorks
{
	/// <summary>RIMMANDRAKE_GIVE_GODMODE_LIQUID_POUR_DRAIN: the dev tools that drop large amounts of any liquid on the terrain or in a
	/// pit and take it away again: pour, drain and set-level on the current map. The dev actions (FlowWorksDebugActions "Pour
	/// liquid...", "Drain liquid...", "Set pit liquid level...") and the bridge (jawa/static_call, type
	/// RimMandrake.FlowWorks.RM_GodLiquid) both call these; each returns "OK ..." or "REFUSED: why".
	/// <list type="bullet">
	/// <item>A dug square: the liquid moves through the engine (TryPourDl / TryTakeDl), square by square over the body it joins
	/// (RM_GodLiquidMath plans it, nearest first); the pulse levels it afterwards. What moved is disclosed on the map's flow
	/// ledger (NoteMapControlFlowDl: "inputs: flowSources" / "exits: flowSinks" in the L0 water ledger report).</item>
	/// <item>What a pit has no room for, and a pour on undug ground, spills onto the sheet (canal overflow,
	/// RM_MapComponent_Sheet.Offer, as a flood): first over the pit's own lips, then ring by ring outward from the click. The dev
	/// action pours with the overflow flag (<see cref="PourOverflow"/>, owner 2026-11-12: <i>"It shouldn't do that. It should go
	/// ahead and overflow. I wanted to watch the water bulge and move."</i>), which goes past the overflow switches; the bridge's
	/// <see cref="Pour"/> keeps to them. A drain on undug ground purges the sheet ("dried by hand" on the sheet's own ledger),
	/// from the nearest spilled square when the clicked one is dry. A natural pond or lake is neither poured into nor drained
	/// here.</item>
	/// </list></summary>
	public static class RM_GodLiquid
	{
		/// <summary>Pour <paramref name="litres"/> of the liquid named <paramref name="fluid"/> (a FluidDef defName) at
		/// <paramref name="cell"/>, keeping to the overflow switches: into the pit it is in, or onto undug ground as spilled sheet
		/// liquid while canal overflow is on.</summary>
		public static string Pour(IntVec3 cell, string fluid, float litres)
		{
			return PourCore(cell, fluid, litres, false);
		}

		/// <summary>The dev action's pour: all of <paramref name="litres"/>, never refused for room. The pit takes what it has
		/// room for and the rest overflows onto the ground around it, whatever the overflow switches say. Refused only for a cell
		/// off the map, an amount that is not a positive number of litres, or a liquid with no FluidDef.</summary>
		public static string PourOverflow(IntVec3 cell, string fluid, float litres)
		{
			return PourCore(cell, fluid, litres, true);
		}

		private static string PourCore(IntVec3 cell, string fluid, float litres, bool overflow)
		{
			string why = Prepare(cell, out Map map, out RM_MapComponent_Excavation ex);
			if (why != null || (why = RM_GodLiquidMath.CheckLitres(litres, out long dl)) != null)
			{
				return why;
			}
			List<FluidDef> fluids = Building_RM_MapControl.CanalFluids().ToList();
			if ((why = RM_GodLiquidMath.ResolveLiquid(fluid, fluids.Select(d => d.defName).ToList(), out int k)) != null)
			{
				return why;
			}
			FluidDef f = fluids[k];
			if (!overflow && !RM_MapComponent_Excavation.InputAllowed(f))
			{
				return "REFUSED: " + f.defName + " is switched off in FlowWorks Mod Settings";
			}
			bool dug = ex.IsExcavated(cell);
			if (!overflow && dug && ex.WaterDlAt(cell) > 0 && ex.FluidAt(cell) != f)
			{
				return "REFUSED: " + At(cell) + " holds " + Name(ex.FluidAt(cell)) + "; liquids never mix (drain it first)";
			}
			long poured = 0;
			string pit = "";
			if (dug && (ex.WaterDlAt(cell) == 0 || ex.FluidAt(cell) == f))
			{
				List<int> body = Body(map, ex, cell, f);
				var plan = new List<KeyValuePair<int, long>>();
				RM_GodLiquidMath.PlanPour(body, i => Room(map, ex, i), dl, !RM_MapComponent_Excavation.LevelExact, plan);
				poured = Move(map, ex, f, plan, out _);
				ex.NoteMapControlFlowDl(poured, 0);
				pit = " into a pit of " + body.Count + " squares";
			}
			else if (dug)
			{
				pit = " (the pit holds " + Name(ex.FluidAt(cell)) + "; liquids never mix, so it all goes over the side)";
			}
			string done = "poured " + L(poured) + " of " + L(dl) + " " + f.defName + " at " + At(cell) + pit;
			if (poured >= dl)
			{
				return "OK " + done;
			}
			if (!overflow && dug)
			{
				done += "; " + L(dl - poured) + " had no room (the dev action overflows it)";
				return poured > 0 ? "OK " + done : "REFUSED: nothing " + done;
			}
			return Spill(map, ex, cell, f, dl - poured, overflow, out string spilled) ?? "OK " + done + "; " + spilled;
		}

		/// <summary>Drain <paramref name="litres"/> from the pit at <paramref name="cell"/> (or the spilled sheet there).</summary>
		public static string Drain(IntVec3 cell, float litres)
		{
			string why = Prepare(cell, out _, out _);
			if (why != null || (why = RM_GodLiquidMath.CheckLitres(litres, out long dl)) != null)
			{
				return why;
			}
			return DrainDl(cell, dl);
		}

		/// <summary>Drain every drop from the pit at <paramref name="cell"/> and the dug squares of that liquid joined to it (or
		/// the spilled sheet there).</summary>
		public static string DrainAll(IntVec3 cell)
		{
			return Prepare(cell, out _, out _) ?? DrainDl(cell, RM_GodLiquidMath.All);
		}

		/// <summary>Set the pit at <paramref name="cell"/> to <paramref name="metres"/> of liquid at that square, the same surface
		/// across the dug squares joined to it (a deeper square holds more, a shallower one less or none), never over a brim. The
		/// liquid is what the pit holds; a dry pit takes <paramref name="fluid"/> (empty = the map's default liquid).</summary>
		public static string SetLevel(IntVec3 cell, string fluid, float metres)
		{
			string why = Prepare(cell, out Map map, out RM_MapComponent_Excavation ex);
			if (why != null || (why = RM_GodLiquidMath.CheckLevelMetres(metres, out long target)) != null)
			{
				return why;
			}
			if (!ex.IsExcavated(cell))
			{
				return "REFUSED: " + At(cell) + " is not dug; a level is set on a pit";
			}
			FluidDef held = ex.WaterDlAt(cell) > 0 ? ex.FluidAt(cell) : null;
			FluidDef f = held ?? ex.ActiveFluid;
			if (!fluid.NullOrEmpty())
			{
				List<FluidDef> fluids = Building_RM_MapControl.CanalFluids().ToList();
				if ((why = RM_GodLiquidMath.ResolveLiquid(fluid, fluids.Select(d => d.defName).ToList(), out int k)) != null)
				{
					return why;
				}
				if (held != null && held != fluids[k])
				{
					return "REFUSED: " + At(cell) + " holds " + Name(held) + ", not " + fluids[k].defName + "; liquids never mix (drain it first)";
				}
				f = fluids[k];
			}
			if (f == null)
			{
				return "REFUSED: " + At(cell) + " holds a liquid this tool cannot name";
			}
			if (!RM_MapComponent_Excavation.InputAllowed(f))
			{
				return "REFUSED: " + f.defName + " is switched off in FlowWorks Mod Settings";
			}
			List<int> body = Body(map, ex, cell, f);
			var plan = new List<KeyValuePair<int, long>>();
			RM_GodLiquidMath.PlanLevel(body, i => ex.DepthAt(map.cellIndices.IndexToCell(i)), i => ex.WaterDlAt(map.cellIndices.IndexToCell(i)),
				ex.DepthAt(cell), target, !RM_MapComponent_Excavation.LevelExact, plan);
			long poured = Move(map, ex, f, plan, out long taken);
			ex.NoteMapControlFlowDl(poured, taken);
			return "OK set " + At(cell) + " to " + metres.ToString("0.##") + " m of " + f.defName + " over " + body.Count + " squares: poured "
				+ L(poured) + ", drained " + L(taken) + "; it now reads " + (ex.PitLabelAt(cell) ?? "?");
		}

		// ── shared ──

		private static string Prepare(IntVec3 cell, out Map map, out RM_MapComponent_Excavation ex)
		{
			map = Find.CurrentMap;
			ex = map?.GetComponent<RM_MapComponent_Excavation>();
			if (map == null)
			{
				return "REFUSED: no current map";
			}
			if (ex == null)
			{
				return "REFUSED: this map has no FlowWorks excavation component";
			}
			return RM_GodLiquidMath.CheckCell(cell.x, cell.z, map.Size.x, map.Size.z);
		}

		private static string DrainDl(IntVec3 cell, long dl)
		{
			Map map = Find.CurrentMap;
			RM_MapComponent_Excavation ex = map.GetComponent<RM_MapComponent_Excavation>();
			string want = dl == RM_GodLiquidMath.All ? "all" : L(dl);
			if (!ex.IsExcavated(cell))
			{
				RM_MapComponent_Sheet sheet = RM_MapComponent_Sheet.Of(map);
				// a part drain empties the clicked square first: the rest of the spill is drained from the nearest wet square
				var order = new List<int>();
				int rings = GenRadial.NumCellsInRadius(NearestSpillRadius);
				for (int r = 0; r < rings; r++)
				{
					IntVec3 c = cell + GenRadial.RadialPattern[r];
					if (c.InBounds(map))
					{
						order.Add(map.cellIndices.CellToIndex(c));
					}
				}
				int from = sheet == null ? -1 : RM_GodLiquidMath.NearestWet(order, i => sheet.FluidAt(map.cellIndices.IndexToCell(i)) != null);
				IntVec3 start = from < 0 ? cell : map.cellIndices.IndexToCell(from);
				FluidDef sf = sheet?.FluidAt(start);
				long got = sheet?.PurgeConnectedAt(start, dl) ?? 0;
				return got > 0
					? "OK drained " + L(got) + " of " + want + " spilled " + Name(sf) + " from " + At(start) + " (the sheet ledger counts it dried by hand)"
					: "REFUSED: no spilled liquid within " + NearestSpillRadius + " squares of undug " + At(cell) + " (a natural pond or lake is not drained by this tool)";
			}
			if (ex.WaterDlAt(cell) <= 0)
			{
				return "REFUSED: the pit at " + At(cell) + " is dry";
			}
			FluidDef f = ex.FluidAt(cell);
			if (f == null)
			{
				return "REFUSED: the pit at " + At(cell) + " holds a liquid this tool cannot name";
			}
			List<int> body = Body(map, ex, cell, f);
			var plan = new List<KeyValuePair<int, long>>();
			RM_GodLiquidMath.PlanTake(body, i => ex.WaterDlAt(map.cellIndices.IndexToCell(i)), dl, !RM_MapComponent_Excavation.LevelExact, plan);
			Move(map, ex, f, plan, out long taken);
			ex.NoteMapControlFlowDl(0, taken);
			return "OK drained " + L(taken) + " of " + want + " " + f.defName + " from the pit at " + At(cell) + " (" + body.Count + " squares)";
		}

		/// <summary>The dug squares joined to <paramref name="cell"/> that liquid <paramref name="f"/> may stand in: dug, not sealed
		/// off by a shut flow door, dry or holding <paramref name="f"/> (the engine's pour walk, PlanPour's Joins).</summary>
		private static List<int> Body(Map map, RM_MapComponent_Excavation ex, IntVec3 cell, FluidDef f)
		{
			CellIndices ci = map.cellIndices;
			int Neighbour(int i, int dir)
			{
				IntVec3 n = ci.IndexToCell(i) + GenAdj.CardinalDirections[dir];
				return n.InBounds(map) ? ci.CellToIndex(n) : -1;
			}
			bool Joins(int i)
			{
				IntVec3 c = ci.IndexToCell(i);
				return ex.IsExcavated(c) && !RM_FlowDoorRules.SealsLiquid(map.edificeGrid[i]) && (ex.WaterDlAt(c) == 0 || ex.FluidAt(c) == f);
			}
			return RM_GodLiquidMath.Walk(ci.CellToIndex(cell), Neighbour, Joins, ci.NumGridCells);
		}

		private static long Room(Map map, RM_MapComponent_Excavation ex, int i)
		{
			IntVec3 c = map.cellIndices.IndexToCell(i);
			return ex.DepthAt(c) * (long)RM_LevelSolve.U - ex.WaterDlAt(c);
		}

		/// <summary>Carry out a plan through the engine; returns dL poured and (out) dL taken, as the engine really moved them. A
		/// pour is exactly its square's room or less, so the engine places it in that square.</summary>
		private static long Move(Map map, RM_MapComponent_Excavation ex, FluidDef f, List<KeyValuePair<int, long>> plan, out long taken)
		{
			long poured = 0;
			taken = 0;
			foreach (KeyValuePair<int, long> p in plan)
			{
				IntVec3 c = map.cellIndices.IndexToCell(p.Key);
				if (p.Value < 0)
				{
					taken += ex.TryTakeDl(c, -p.Value, out _);
				}
				else if (ex.TryPourDl(c, f, p.Value))
				{
					poured += p.Value;
				}
			}
			return poured;
		}

		/// <summary>Spill <paramref name="rest"/> dL onto the sheet: over the lips of the pit at <paramref name="cell"/> (or the
		/// undug square itself), then ring by ring outward from it until it is all placed or GiveUpAfter offers in a row place
		/// nothing (the map's wet-square cap, walls, other liquids). Null and <paramref name="said"/> = what happened; else the
		/// refusal (only without <paramref name="overflow"/>: the switches).</summary>
		private static string Spill(Map map, RM_MapComponent_Excavation ex, IntVec3 cell, FluidDef f, long rest, bool overflow, out string said)
		{
			said = null;
			if (!overflow && !RM_SheetSettings.SpillsFrom(RM_SheetMath.Source.Flood))
			{
				return "REFUSED: undug ground holds liquid only as spilled sheet liquid, and canal overflow (or its spills from floods) is OFF;"
					+ " switch it on with the dev action 'Canal overflow: switch on/off (test)' or in Mod Settings, or pour with the dev action";
			}
			if (!overflow && f != RimMandrakeFlowWorks_DefOf.RM_Fluid_Water && !RM_SheetSettings.otherLiquidsSpillEnabled)
			{
				return "REFUSED: only water spills on the ground while 'other liquids spill' is off in Mod Settings";
			}
			RM_MapComponent_Sheet sheet = RM_MapComponent_Sheet.Of(map);
			long got = 0;
			if (sheet != null && RimMandrakeFlowWorksSettings.DepthEngineActive)
			{
				// one offer fills only the few lips nearest it (up to the sheet's depth cap), so a big pour is offered again ring
				// by ring outward from the click
				got = sheet.Offer(cell, rest, f, RM_SheetMath.Source.Flood, overflow);
				int dry = 0;
				int rings = GenRadial.NumCellsInRadius(GenRadial.MaxRadialPatternRadius);
				for (int r = 1; r < rings && got < rest && dry < GiveUpAfter; r++)
				{
					IntVec3 c = cell + GenRadial.RadialPattern[r];
					if (!c.InBounds(map) || ex.IsExcavated(c))
					{
						continue;
					}
					long more = sheet.Offer(c, rest - got, f, RM_SheetMath.Source.Flood, overflow);
					got += more;
					dry = more > 0 ? 0 : dry + 1;
				}
			}
			string whyNot = sheet == null ? " (this map has no sheet component)" : !RimMandrakeFlowWorksSettings.DepthEngineActive
				? " (the FlowWorks depth engine is off in this game)" : " (walls, other liquids or the map's cap on wet squares)";
			said = "spilled " + L(got) + " of " + L(rest) + " on the ground around it" + (rest > got ? "; " + L(rest - got) + " had nowhere to go" + whyNot : "")
				+ " (the sheet ledger counts it as flood input)";
			if (!overflow && got <= 0)
			{
				return "REFUSED: nothing spilled; " + said;
			}
			return null;
		}

		/// <summary>A ground pour stops after this many offers in a row that placed nothing.</summary>
		private const int GiveUpAfter = 64;

		/// <summary>How far from a dry click on undug ground a drain looks for the spill (squares).</summary>
		private const float NearestSpillRadius = 12.9f;

		private static string L(long dl) => RM_Volume.FormatLitres(dl / (double)RM_Volume.UnitsPerLitre);

		private static string At(IntVec3 c) => "(" + c.x + ", " + c.z + ")";

		private static string Name(FluidDef f) => f?.defName ?? "an unknown liquid";
	}
}
