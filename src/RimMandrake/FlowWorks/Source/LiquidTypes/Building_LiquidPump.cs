using System.Collections.Generic;
using System.Linq;
using RimWorld;
using UnityEngine;
using Verse;
using RimMandrake.FlowWorks.Machinery;

namespace RimMandrake.FlowWorks.LiquidTypes
{
	/// <summary>Per-def pump tuning (the pumping station: several levels a cycle, reaching water a few cells
	/// off). Absent = the first-slice pump: one level, touching cells only.</summary>
	public class RM_PumpExtension : DefModExtension
	{
		public int levelsPerCycle = 1;
		public float reach = 1.5f;
	}

	/// <summary>
	/// FLOWWORKS_BUILD_PROGRAM_1 Phase 8, first hardware slice — the universal pump (design: liquids framework
	/// §4 "universal pump", mod definition ruling 11: pumps and tanks are FlowWorks' own). Hoses and per-net
	/// adapters are a later slice, so this pump works on what TOUCHES it:
	///
	///   • DRAW: lift one level from a wet cell beside it (a dug channel, or a natural pond/lake — debited from
	///     that body's stock through §8 TryDebit, so a limited pond runs down) into a liquid tank beside it.
	///   • POUR: run one level from a tank marked Dump into a dug channel beside it (fluids never mix; a full or foreign
	///     cell refuses; only tanks marked Dump are drained). This is how a moat is kept topped up — with tar hauled in barrels, say — and how a
	///     channel is filled without a natural source.
	///
	/// One level per cycle (250 ticks) for the first-slice pump, levelsPerCycle for a station (RM_PumpExtension), while powered and switched on;
	/// on Pour at least one level more than a Dump tank's gravity rate (RM_PumpMath.PourLevels). Unit bridge between the two ledgers: one
	/// channel level = <see cref="RM_PumpMath.TankUnitsPerLevel"/> tank units (1,000 L, a cubic metre; LIQUID_LITRES_MIGRATE_DRUMS_ARE_DRUMS).
	/// The pump never writes terrain or stock itself — the excavation engine and the body stock do.
	/// Mod Setting: liquidPumpEnabled (off: a built pump sits idle and draws no power).
	/// </summary>
	public class Building_LiquidPump : Building
	{
		public bool pourMode;
		public int Moved;
		private string lastStatus = "";

		private CompPowerTrader power;
		private CompFlickable flick;

		public override void SpawnSetup(Map map, bool respawningAfterLoad)
		{
			base.SpawnSetup(map, respawningAfterLoad);
			power = GetComp<CompPowerTrader>();
			flick = GetComp<CompFlickable>();
		}

		public override void ExposeData()
		{
			base.ExposeData();
			Scribe_Values.Look(ref pourMode, "RM_pumpPourMode", false);
			Scribe_Values.Look(ref Moved, "RM_pumpMoved", 0);
		}

		private bool Running => RimMandrakeFlowWorksSettings.liquidPumpEnabled
			&& Machinery.RM_MachinerySettings.MachineOn(def)
			&& (power == null || power.PowerOn) && (flick == null || flick.SwitchIsOn);

		private RM_PumpExtension Ext => def.GetModExtension<RM_PumpExtension>();

		/// <summary>The full pump predicate (settings, machine switch, power, flick; G7): an Intake end needs a working pump.</summary>
		public bool Working => Running;

		/// <summary>Cells the pump draws from / pours into: touching cells, or a radius for a station.</summary>
		private IEnumerable<IntVec3> ReachCells()
		{
			float reach = Ext?.reach ?? 1.5f;
			if (reach <= 1.5f)
			{
				foreach (IntVec3 c in GenAdj.CellsAdjacent8Way(this))
				{
					yield return c;
				}
				yield break;
			}
			// P11: reach is measured from the footprint's nearest cell, not a circle about Position; nearest first.
			CellRect rect = this.OccupiedRect();
			var cells = new List<IntVec3>();
			foreach (IntVec3 c in rect.ExpandedBy(UnityEngine.Mathf.CeilToInt(reach)))
			{
				if (RM_PumpMath.InFootprintReach(rect.minX, rect.minZ, rect.maxX, rect.maxZ, c.x, c.z, reach))
				{
					cells.Add(c);
				}
			}
			foreach (IntVec3 c in cells.OrderBy(q => RM_PumpMath.FootprintDistSq(rect.minX, rect.minZ, rect.maxX, rect.maxZ, q.x, q.z)))
			{
				yield return c;
			}
		}

		protected override void Tick()
		{
			base.Tick();
			if (power != null)
			{
				power.PowerOutput = RimMandrakeFlowWorksSettings.liquidPumpEnabled ? -power.Props.PowerConsumption : 0f;
			}
			if (!this.IsHashIntervalTick(RM_PumpMath.CycleTicks))
			{
				return;
			}
			if (!Running)
			{
				lastStatus = "";
				warning = null;
				return;
			}
			// rev 2 §3.3: the budget is levelsPerCycle in total across every source and destination (more Intake ends do not
			// make a pump faster); each Outflow end takes at most one level per cycle
			int levels = System.Math.Max(1, Ext?.levelsPerCycle ?? 1);
			usedOutflows.Clear();
			if (pourMode)
			{
				// Q3: pour is the FAST drain, always more than a Dump tank's gravity rate (RM_PumpMath.PourLevels, selftested)
				levels = RM_PumpMath.PourLevels(levels, Hose.RM_HoseSettings.DumpUnitsPerCycle);
			}
			deadSources.Clear();
			filledPastOutflow = circle = false;
			cycle = Find.TickManager.TicksGame / RM_PumpMath.CycleTicks;
			for (int i = 0; i < levels; i++)
			{
				int before = Moved;
				string status = pourMode ? TryPour() : TryDraw();
				if (Moved == before)
				{
					// a later level that found nothing to move keeps the earlier level's status (it did move)
					if (i == 0)
					{
						lastStatus = status;
					}
					break;
				}
				lastStatus = status;
			}
			NoteNeighbours();
		}

		// ---------------------------------------------------------------- rev 2 §3.3: the pump as world mover (build step L6)
		private readonly HashSet<int> usedOutflows = new HashSet<int>();
		private readonly HashSet<int> deadSources = new HashSet<int>();
		private int cycle;
		private string warning;

		/// <summary>A drawable source cell: a channel cell with fill, or a natural body's source cell (never a dry nozzle cell,
		/// A13); <see cref="port"/> is the Intake end it was found through (null: the pump's own reach).</summary>
		private struct Source
		{
			public IntVec3 cell;
			public bool channel;
			public FluidDef fluid;
			public RM_NetPort port;
		}

		private bool Drawable(RM_MapComponent_Excavation ex, IntVec3 c, out Source s)
		{
			s = new Source { cell = c };
			if (!c.InBounds(Map))
			{
				return false;
			}
			if (ex.IsExcavated(c) && ex.WaterDlAt(c) > 0)   // a thin sheet (no whole notch) is drawable too
			{
				s.channel = true;
				s.fluid = ex.FluidAt(c) ?? ex.ActiveFluid;
				return s.fluid != null;
			}
			if (ex.IsSourceCell(c) && SourceTake(ex, c) > 0)   // POND_PUMP_FIX_LAST_DROP_COUNTS: any decilitre (exact-level on), a whole notch (off)
			{
				s.fluid = ex.Stock.BodyAt(Map, c, ex)?.fluid ?? ex.ActiveFluid;
				return s.fluid != null;
			}
			return false;
		}

		/// <summary>POND_PUMP_FIX_LAST_DROP_COUNTS: the decilitres this cycle's draw takes from the natural body behind <paramref name="c"/>
		/// (RM_PumpMath.SourceTakeUnits, selftested). volumePerTile is pinned to 1 (FluidDef.ConfigErrors), so a fill-unit is
		/// a notch and the body's decilitres are the tank's.</summary>
		private int SourceTake(RM_MapComponent_Excavation ex, IntVec3 c)
		{
			int units = RM_PumpMath.TankUnitsPerLevel;
			return RM_PumpMath.SourceTakeUnits(units, ex.Stock.SupplyDl(Map, c, units, ex), RM_MapComponent_Excavation.LevelExact);
		}

		/// <summary>Sources in order (rev 2 §3.3): the pump's own reach, then the source cell under or beside every Intake end on its
		/// networks, in reel-id order.</summary>
		private List<Source> Sources(RM_MapComponent_Excavation ex)
		{
			var list = new List<Source>();
			foreach (IntVec3 c in ReachCells())
			{
				if (Drawable(ex, c, out Source s))
				{
					list.Add(s);
				}
			}
			foreach (RM_NetPort p in RM_LiquidNet.PortsOf(this, RM_FreeEndRole.Intake))
			{
				if (!(p.Cell is IntVec3 end))
				{
					continue;
				}
				foreach (IntVec3 c in new[] { end }.Concat(GenAdj.CellsAdjacent8Way(new TargetInfo(end, Map))))
				{
					if (Drawable(ex, c, out Source s))
					{
						s.port = p;
						list.Add(s);
						break;
					}
				}
			}
			return list;
		}

		/// <summary>What an Outflow end does with a level of <paramref name="fluid"/> (RM_LiquidSpill.Outlet, rev 2 §3.5): pour
		/// into a channel cell, spill on dry ground, or nothing (blocked).</summary>
		private RM_OutletKind Outlet(RM_MapComponent_Excavation ex, RM_NetPort p, LiquidDef liquid, FluidDef fluid, out IntVec3 cell)
		{
			cell = IntVec3.Invalid;
			return p?.Cell is IntVec3 end ? RM_LiquidSpill.Outlet(Map, ex, end, liquid ?? LiquidFor(fluid), fluid, out cell) : RM_OutletKind.Blocked;
		}

		/// <summary>The inspect warnings of rev 2 §3.3/§3.6/A20, set once per cycle.</summary>
		private void NoteNeighbours()
		{
			warning = circle ? "RMFlow_PumpCircle".Translate().ToString()
				: filledPastOutflow ? "RMFlow_PumpOutflowBlocked".Translate().ToString() : null;
			if (warning != null || Map == null)
			{
				return;
			}
			foreach (RM_NetComponent c in RM_LiquidNet.Components(Map).ComponentsOf(this))
			{
				foreach (object m in c.Machines)
				{
					if (m != this && m is Building_LiquidPump other && other.pourMode && !pourMode)
					{
						warning = "RMFlow_PumpOtherPouring".Translate();
						return;
					}
				}
			}
		}

		/// <summary>This cycle: a level went into tanks while Outflow ends were on the network (all blocked, A20); a world-to-world
		/// level left and re-entered the same body of water (A19).</summary>
		private bool filledPastOutflow, circle;

		private string lastLiquidLabel;
		// weak keys: a static HashSet<Map> kept every finished game's maps alive for the session
		private static readonly System.Runtime.CompilerServices.ConditionalWeakTable<Map, object> toldPourNeedsDump = new System.Runtime.CompilerServices.ConditionalWeakTable<Map, object>();

		/// <summary>Phase 8 slice 2: every tank on this pump's liquid net (touching it, or on a hose run that
		/// touches it) — RM_LiquidNet. With hoses off in Mod Settings this is the touching tanks only.</summary>
		private List<Building_LiquidTank> NetTanks() => Machinery.RM_LiquidNet.TanksFor(this);

		private static LiquidDef LiquidFor(FluidDef fluid)
		{
			if (fluid == null)
			{
				return null;
			}
			foreach (LiquidDef l in DefDatabase<LiquidDef>.AllDefsListForReading)
			{
				if (l.canalFluid == fluid)
				{
					return l;
				}
			}
			return null;
		}

		private string TryDraw()
		{
			RM_MapComponent_Excavation ex = RM_SuperdeepTrap.EngineOf(Map);
			if (ex == null)
			{
				return "RMFlow_PumpNoTank".Translate();
			}
			int units = RM_PumpMath.TankUnitsPerLevel;
			List<Source> sources = Sources(ex);
			List<RM_NetPort> outflows = RM_LiquidNet.PortsOf(this, RM_FreeEndRole.Outflow);
			if (sources.Count == 0)
			{
				return outflows.Count == 0 && NetTanks().Count == 0
					? (RM_LiquidNet.TooLarge(this) ? "RMFlow_NetTooLarge".Translate() : "RMFlow_PumpNoTank".Translate())
					: "RMFlow_PumpNothingToDraw".Translate();
			}
			// rev 2 §3.3 (RM_LiquidNetKernel.PumpNext, selftested): Outflow ends first (rotated, one level each per cycle), then
			// the tanks in fill order; a refused move marks that source dead for this cycle and the next pair is tried
			for (int attempt = 0; attempt < sources.Count + outflows.Count + 1; attempt++)
			{
				if (!RM_LiquidNetKernel.PumpNext(sources.Count, i => !deadSources.Contains(Map.cellIndices.CellToIndex(sources[i].cell)), outflows.Count,
					(o, i) => Outlet(ex, outflows[o], null, sources[i].fluid, out _) != RM_OutletKind.Blocked, usedOutflows,
					i => LiquidFor(sources[i].fluid) is LiquidDef lq && Machinery.RM_LiquidNet.FillPlan(this, lq, units) != null, cycle,
					out int si, out int oi))
				{
					break;
				}
				Source s = sources[si];
				IntVec3 cell = s.cell;
				FluidDef f = s.fluid;
				LiquidDef l = LiquidFor(f);
				lastLiquidLabel = l?.label ?? f.label;
				if (oi >= 0)
				{
					// world -> world (the tankless transfer): the destination cell is checked first, the source level taken, then
					// poured; the take is put back if the pour is refused all the same
					RM_NetPort port = outflows[oi];
					// L7 (§3.5): a channel cell takes the level; dry open ground takes it as a spill (filth, cleanable)
					RM_OutletKind kind = Outlet(ex, port, l, f, out IntVec3 dest);
					// L8 (§3.7): while its hoses are not yet full, the level goes into them (taken from the move itself)
					bool fillHoses = l != null && RM_LiquidNet.HoseNeed(this, new object[] { port, s.port }, l) > 0;
					// PUMP_CANAL_FEED_FIX_ONE_NOTCH_ONLY: the move is in DECILITRES (tank units): up to one level, what the source
					// holds and what the outlet takes. A canal holding a sheet has no whole notch in any one square, so the old
					// whole-level move stopped after the first level (live S3/S5.G, 1,000 L); it now runs until the canal is
					// brim-full or the source is dry. Whole-notch water (exact-level off) still moves whole levels only.
					long avail = s.channel ? ex.WaterDlAt(cell) : ex.Stock.SupplyDl(Map, cell, units, ex);
					long room = fillHoses ? units : RM_LiquidSpill.OutletRoomDl(ex, kind, dest, f, units);
					int amt = (int)System.Math.Min(units, System.Math.Min(avail, room));
					if (amt <= 0 || (!RM_MapComponent_Excavation.LevelExact && amt < units))
					{
						usedOutflows.Add(oi);   // nothing to move through this end this cycle (a dry source, a full canal)
						continue;
					}
					RM_TransferLeg into = fillHoses ? RM_TransferLeg.Sink(k => RM_LiquidNet.FillRoutes(this, new object[] { s.port, port }, l, k))
						: RM_LiquidSpill.OutletLeg(Map, ex, kind, dest, l, f);
					RM_TransferLeg from = s.channel
						? RM_TransferLeg.World(k => ex.IsExcavated(cell) && ex.WaterDlAt(cell) >= k, k => ex.TryTakeDl(cell, k, out _) == k, k => ex.TryPourDl(cell, f, k))
						: RM_TransferLeg.World(k => ex.Stock.SupplyDl(Map, cell, k, ex) >= k, k => ex.Stock.TryDebitDl(Map, cell, k, ex), k => ex.Stock.CreditDl(Map, cell, k, ex) == k);   // GPT #5: put back exactly what was taken
					if (RM_LiquidTransfer.Move(amt, from, into, out _) == amt)
					{
						Machinery.RM_LiquidNet.CreditTo(this, port, l, amt, RM_PumpMath.CycleTicks);   // credit site: pump to outflow
						Machinery.RM_LiquidNet.CreditTo(this, s.port, l, amt, RM_PumpMath.CycleTicks);   // credit site: pump intake (to outflow)
						usedOutflows.Add(oi);
						circle |= !fillHoses && RM_LiquidSpill.WholeLevels(kind) && ex.Stock.BodyAt(Map, dest, ex) is RM_LiquidBody bd && bd == ex.Stock.BodyAt(Map, cell, ex);   // A19, by body
						Stamp(amt);
						Moved++;
						return "RMFlow_PumpToOutflow".Translate(lastLiquidLabel);
					}
					usedOutflows.Add(oi);
					continue;
				}
				// L3 (§3.2): the fill plan may split the level across tanks (3 + 2 units of room take it)
				List<(Building_LiquidTank tank, int units)> plan = l == null ? null : Machinery.RM_LiquidNet.FillPlan(this, l, units);
				if (plan == null)
				{
					deadSources.Add(Map.cellIndices.CellToIndex(s.cell));
					continue;
				}
				if (s.channel)
				{
					// L1 (§4): the tank leg is reserved first, the channel water (TryTakeDl, never undone) taken last.
					// LIQUID_DEPTH_REWIRE_FIVE_IS_DEAD: up to one notch in DECILITRES, so a thin sheet (4.5 cm = 900 dL) is
					// pumped dry rather than left behind for want of a whole notch; the tank plan is for what is taken.
					int take = RM_PumpMath.ChannelTakeUnits(units, ex.WaterDlAt(cell));
					if (take != units)
					{
						plan = take > 0 ? Machinery.RM_LiquidNet.FillPlan(this, l, take) : null;
						if (plan == null)
						{
							deadSources.Add(Map.cellIndices.CellToIndex(s.cell));
							continue;
						}
					}
					RM_TransferLeg world = RM_TransferLeg.World(k => ex.IsExcavated(cell) && ex.WaterDlAt(cell) >= k, k => ex.TryTakeDl(cell, k, out _) == k);
					if (RM_LiquidTransfer.Move(take, world, RM_TransferLeg.Split(plan.Count, i => plan[i].units, (i, k) => plan[i].tank.CanAccept(l, k), (i, k) => plan[i].tank.TryAddLiquid(l, k), (i, k) => plan[i].tank.TryRemoveLiquid(k)), out _) == take)
					{
						foreach ((Building_LiquidTank tank, int units) p in plan) Machinery.RM_LiquidNet.Credit(this, p.tank, l, p.units, RM_PumpMath.CycleTicks);   // credit site: pump draw (channel)
						Machinery.RM_LiquidNet.CreditTo(this, s.port, l, take, RM_PumpMath.CycleTicks, Machinery.RM_LiquidNet.FillFrom(plan[0].tank, l));   // credit site: pump intake (channel)
						filledPastOutflow |= outflows.Count > 0;
						Stamp(take);
						Moved++;
						return "RMFlow_PumpDrew".Translate(l.label);
					}
				}
				else
				{
					// POND_PUMP_FIX_LAST_DROP_COUNTS (owner by card 2026-10-22, GPT review Q6): up to one notch in DECILITRES, the same rule as a
					// dug channel, so a pond's last <1,000 L is pumped too (the old whole-notch CanSupply/TryDebit stranded it).
					int take = SourceTake(ex, cell);
					if (take != units)
					{
						plan = take > 0 ? Machinery.RM_LiquidNet.FillPlan(this, l, take) : null;
						if (plan == null)
						{
							deadSources.Add(Map.cellIndices.CellToIndex(s.cell));
							continue;
						}
					}
					// L1 (§4): the tank leg is reserved first; the body's exact debit (TryDebitDl, never undone) runs last
					RM_TransferLeg world = RM_TransferLeg.World(k => ex.Stock.SupplyDl(Map, cell, k, ex) >= k, k => ex.Stock.TryDebitDl(Map, cell, k, ex));
					if (RM_LiquidTransfer.Move(take, world, RM_TransferLeg.Split(plan.Count, i => plan[i].units, (i, k) => plan[i].tank.CanAccept(l, k), (i, k) => plan[i].tank.TryAddLiquid(l, k), (i, k) => plan[i].tank.TryRemoveLiquid(k)), out _) == take)
					{
						foreach ((Building_LiquidTank tank, int units) p in plan) Machinery.RM_LiquidNet.Credit(this, p.tank, l, p.units, RM_PumpMath.CycleTicks);   // credit site: pump draw (source)
						Machinery.RM_LiquidNet.CreditTo(this, s.port, l, take, RM_PumpMath.CycleTicks, Machinery.RM_LiquidNet.FillFrom(plan[0].tank, l));   // credit site: pump intake (source)
						filledPastOutflow |= outflows.Count > 0;
						Stamp(take);
						Moved++;
						return "RMFlow_PumpDrew".Translate(l.label);
					}
				}
				deadSources.Add(Map.cellIndices.CellToIndex(s.cell));
			}
			return "RMFlow_PumpNothingToDraw".Translate();
		}

		/// <summary>State read (inspect, probes): the units of the last successful transfer and its tick (hose port step 6).</summary>
		public int lastMovedUnits, lastMovedTick = -1;

		private void Stamp(int units)
		{
			lastMovedUnits = units;
			lastMovedTick = Find.TickManager.TicksGame;
		}

		private string TryPour()
		{
			RM_MapComponent_Excavation ex = RM_SuperdeepTrap.EngineOf(Map);
			int units = RM_PumpMath.TankUnitsPerLevel;
			// rev 2 §3.3 (Q3: "Keep it as faster draining"): pour drains DUMP tanks only, so a pump never pours out a tank the
			// player did not mark; with tank jobs off in Mod Settings there are no jobs to mark, and it drains any tank as before
			List<Building_LiquidTank> tanks = NetTanks().Where(t => !Hose.RM_HoseSettings.tankModesEnabled || t.EffectiveMode == RM_TankMode.Dump).ToList();
			var tk = new List<(bool canProvide, FluidDef fluid)>(tanks.Count);
			foreach (Building_LiquidTank t in tanks)
			{
				tk.Add((t.CanProvide(units), t.storedLiquid?.canalFluid));
			}
			Building_LiquidTank firstProvider = tanks.FirstOrDefault(t => t.CanProvide(units));
			if (ex == null || firstProvider == null)
			{
				if (Hose.RM_HoseSettings.tankModesEnabled && !NetTanks().Any(t => t.EffectiveMode == RM_TankMode.Dump))
				{
					// §3.11 / G13: a pump saved in pour mode stays idle until a tank is marked Dump; one message per map says so
					if (!toldPourNeedsDump.TryGetValue(Map, out _))
					{
						toldPourNeedsDump.Add(Map, null);
						Messages.Message("RMFlow_PumpPourNeedsDumpMessage".Translate(LabelCap), this, MessageTypeDefOf.NeutralEvent, historical: false);
					}
					return "RMFlow_PumpNoDumpTank".Translate();
				}
				return "RMFlow_PumpTankEmpty".Translate();
			}
			if (!tk.Any(x => x.canProvide && x.fluid != null))
			{
				// no channel form: it can still leave as a spill out of an Outflow end on dry ground (§3.5, G10)
				return PourToOutflow(ex, tanks, units) ?? (string)"RMFlow_PumpNoChannelForm".Translate(firstProvider.storedLiquid?.label ?? "?");
			}
			// Deepest-emptiest compatible cell first, so a pump at the head of a channel fills it the way flow would; P1: every
			// providing tank is tried in net order until one has such a cell (RM_PumpMath.PickPour, selftested).
			var cells = new List<IntVec3>();
			var cd = new List<(int room, bool wet, FluidDef fill)>();
			foreach (IntVec3 c in ReachCells())
			{
				if (!c.InBounds(Map) || !ex.IsExcavated(c))
				{
					continue;
				}
				cells.Add(c);
				cd.Add((ex.DepthAt(c) - ex.FillAt(c), ex.FillAt(c) > 0, ex.FluidAt(c)));
			}
			if (!RM_PumpMath.PickPour(tk, cd, out int ti, out int ci))
			{
				// POND_RETURN_LEG_BUILD_WATER_GOES_HOME (G1): no dug cell in reach takes it; a pond (or its dried bed) in reach
				// takes it back, one whole level into its stock.
				string viaPond = PourToPond(ex, tanks, units);
				if (viaPond != null)
				{
					return viaPond;
				}
				// rev 2 §3.3: the pour also leaves through Outflow ends on the pump's networks
				string viaOutflow = PourToOutflow(ex, tanks, units);
				if (viaOutflow != null)
				{
					return viaOutflow;
				}
				// CANAL_OVERFLOW_BUILD_EVERY_PUDDLE_AUDITED stage 1 (D2): backed up against a brimming canal of its own liquid, the
				// level spills over that canal's lip as a sheet (every FlowWorks liquid, owner 2026-10-22: "Build for all flowworks
				// liquids."; switch off, or the sheet full: refused, backed up as before)
				foreach (Building_LiquidTank st in tanks)
				{
					LiquidDef sp = st.storedLiquid;
					FluidDef spf = sp?.canalFluid;
					if (spf == null || !st.CanProvide(units) || !Sheet.RM_MapComponent_Sheet.PumpSpillOutlet(Map, cells, cd, units, spf, out IntVec3 spillAt))
					{
						continue;
					}
					{
						if (RM_LiquidTransfer.Move(units, RM_TransferLeg.Store(k => st.CanProvide(k), k => st.TryRemoveLiquid(k), k => st.TryAddLiquid(sp, k)), Sheet.RM_MapComponent_Sheet.SpillLeg(Map, spillAt, spf, RM_SheetMath.Source.Pump), out _) == units)
						{
							Machinery.RM_LiquidNet.Credit(this, st, sp, units, RM_PumpMath.CycleTicks);   // credit site: pump overflow spill
							Stamp(units);
							Moved++;
							return "RMFlow_PumpPouredOverflow".Translate(sp.label);
						}
					}
				}
				// P4 (PUMP_FED_CHANNEL_STALL_PROVE_AFTER_RELOAD): backed up against brimming cells of a liquid it holds, the
				// pump is still feeding them, so they stay flow-order inputs (after a load nothing else re-marks them).
				for (int c = 0; c < cells.Count; c++)
				{
					if (cd[c].room <= 0 && cd[c].wet && tk.Any(x => x.canProvide && x.fluid != null && x.fluid == cd[c].fill))
					{
						ex.NoteDriverBackedUp(cells[c]);
					}
				}
				return "RMFlow_PumpNoRoom".Translate();
			}
			Building_LiquidTank tank = tanks[ti];
			FluidDef fluid = tk[ti].fluid;
			LiquidDef poured = tank.storedLiquid;   // captured BEFORE the removal: an emptied tank clears storedLiquid
			IntVec3 cell = cells[ci];
			// L1 (§4): the tank leg is removed first and put back if the cell refuses (TryPourLevel, never undone, runs last)
			RM_TransferLeg world = RM_TransferLeg.World(k => ex.IsExcavated(cell) && ex.FillAt(cell) < ex.DepthAt(cell), k => ex.TryPourLevel(cell, fluid));
			if (RM_LiquidTransfer.Move(units, RM_TransferLeg.Store(k => tank.CanProvide(k), k => tank.TryRemoveLiquid(k), k => tank.TryAddLiquid(poured, k)), world, out RM_MoveOutcome mv) != units)
			{
				return mv.DestRefused ? "RMFlow_PumpForeign".Translate() : "RMFlow_PumpTankEmpty".Translate();
			}
			Machinery.RM_LiquidNet.Credit(this, tank, poured, units, RM_PumpMath.CycleTicks);   // credit site: pump pour
			Stamp(units);
			Moved++;
			return "RMFlow_PumpPoured".Translate(fluid.label);
		}

		/// <summary>POND_RETURN_LEG_BUILD_WATER_GOES_HOME: pour one level from the first Dump tank (net order) whose liquid a pond
		/// square or dried bed square in reach takes back (reach order). Tank removed first and put back if the pond refuses.
		/// Null when none can.</summary>
		private string PourToPond(RM_MapComponent_Excavation ex, List<Building_LiquidTank> tanks, int units)
		{
			foreach (Building_LiquidTank tank in tanks)
			{
				FluidDef fluid = tank.storedLiquid?.canalFluid;
				if (fluid == null || !tank.CanProvide(units))
				{
					continue;
				}
				foreach (IntVec3 c in ReachCells())
				{
					if (!c.InBounds(Map) || !ex.CanReturnLevels(c, fluid, 1))
					{
						continue;
					}
					LiquidDef poured = tank.storedLiquid;
					IntVec3 cell = c;
					if (RM_LiquidTransfer.Move(units, RM_TransferLeg.Store(k => tank.CanProvide(k), k => tank.TryRemoveLiquid(k), k => tank.TryAddLiquid(poured, k)),
						RM_LiquidSpill.OutletLeg(Map, ex, RM_OutletKind.Body, cell, poured, fluid), out _) == units)
					{
						Machinery.RM_LiquidNet.Credit(this, tank, poured, units, RM_PumpMath.CycleTicks);   // credit site: pond return (pump)
						Stamp(units);
						Moved++;
						return "RMFlow_PumpPoured".Translate(fluid.label);
					}
					break;
				}
			}
			return null;
		}

		/// <summary>Pour through an Outflow end (rev 2 §3.3): a Dump tank's level out of the first unused end, rotated by cycle,
		/// that can take it. Null when none can.</summary>
		private string PourToOutflow(RM_MapComponent_Excavation ex, List<Building_LiquidTank> tanks, int units)
		{
			List<RM_NetPort> outflows = RM_LiquidNet.PortsOf(this, RM_FreeEndRole.Outflow);
			for (int k = 0; k < outflows.Count; k++)
			{
				int oi = (cycle + k) % outflows.Count;
				if (usedOutflows.Contains(oi))
				{
					continue;
				}
				RM_NetPort port = outflows[oi];
				foreach (Building_LiquidTank tank in tanks)
				{
					FluidDef fluid = tank.storedLiquid?.canalFluid;
					if (!tank.CanProvide(units))
					{
						continue;
					}
					// a liquid with no channel form still spills on dry ground (never discarded, G10)
					RM_OutletKind kind = Outlet(ex, port, tank.storedLiquid, fluid, out IntVec3 dest);
					if (kind == RM_OutletKind.Blocked)
					{
						continue;
					}
					LiquidDef poured = tank.storedLiquid;
					RM_TransferLeg outlet = RM_LiquidSpill.OutletLeg(Map, ex, kind, dest, poured, fluid);
					if (RM_LiquidTransfer.Move(units, RM_TransferLeg.Store(k2 => tank.CanProvide(k2), k2 => tank.TryRemoveLiquid(k2), k2 => tank.TryAddLiquid(poured, k2)), outlet, out _) == units)
					{
						Machinery.RM_LiquidNet.CreditTo(this, tank, poured, units, RM_PumpMath.CycleTicks, Machinery.RM_LiquidNet.FillFrom(tank, poured));   // credit site: outflow pour (tank)
						Machinery.RM_LiquidNet.CreditTo(this, port, poured, units, RM_PumpMath.CycleTicks, Machinery.RM_LiquidNet.FillFrom(tank, poured));   // credit site: outflow pour (end)
						usedOutflows.Add(oi);
						Stamp(units);
						Moved++;
						return "RMFlow_PumpPouredOutflow".Translate(poured.label);
					}
				}
			}
			return null;
		}

		public override IEnumerable<Gizmo> GetGizmos()
		{
			foreach (Gizmo g in base.GetGizmos())
			{
				yield return g;
			}
			yield return new Command_Toggle
			{
				defaultLabel = pourMode ? "RMFlow_PumpModePour".Translate() : "RMFlow_PumpModeDraw".Translate(),
				defaultDesc = "RMFlow_PumpModeDesc".Translate(),
				icon = TexCommand.ForbidOff,
				isActive = () => pourMode,
				toggleAction = () => pourMode = !pourMode
			};
		}

		public override string GetInspectString()
		{
			string s = base.GetInspectString();
			string mine = (pourMode ? "RMFlow_PumpModePour".Translate() : "RMFlow_PumpModeDraw".Translate())
				+ (lastStatus.NullOrEmpty() ? "" : ": " + lastStatus) + (warning.NullOrEmpty() ? "" : "\n" + warning);
			return s.NullOrEmpty() ? mine : s + "\n" + mine;
		}
	}
}
