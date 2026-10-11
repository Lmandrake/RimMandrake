using System.Collections.Generic;
using System.Linq;
using RimWorld;
using UnityEngine;
using Verse;
using RimMandrake.FlowWorks.Machinery;

namespace RimMandrake.FlowWorks.LiquidTypes
{
	/// <summary>
	/// FLOWWORKS_BUILD_PROGRAM_1 Phase 8, first hardware slice — the universal pump (design: liquids framework
	/// §4 "universal pump", mod definition ruling 11: pumps and tanks are FlowWorks' own). Hoses and per-net
	/// adapters are a later slice, so this pump works on what TOUCHES it:
	///
	///   • DRAW: lift one level from a wet cell beside it (a dug channel, or a natural pond/lake — debited from
	///     that body's stock through §8 TryDebit, so a limited pond runs down) into a liquid tank beside it.
	///   • POUR: run one level from that tank into a dug channel beside it (fluids never mix; a full or foreign
	///     cell refuses). This is how a moat is kept topped up — with tar hauled in barrels, say — and how a
	///     channel is filled without a natural source.
	///
	/// One level per cycle (250 ticks) while powered and switched on. Unit bridge between the two ledgers: one
	/// channel level = <see cref="RM_PumpMath.TankUnitsPerLevel"/> tank units (PROVISIONAL: a level is a bucket).
	/// The pump never writes terrain or stock itself — the excavation engine and the body stock do.
	/// Mod Setting: liquidPumpEnabled (off: a built pump sits idle and draws no power).
	/// </summary>
	/// <summary>Per-def pump tuning (the pumping station: several levels a cycle, reaching water a few cells
	/// off). Absent = the first-slice pump: one level, touching cells only.</summary>
	public class RM_PumpExtension : DefModExtension
	{
		public int levelsPerCycle = 1;
		public float reach = 1.5f;
	}

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
			if (!this.IsHashIntervalTick(RM_PumpMath.CycleTicks) || !Running)
			{
				return;
			}
			// rev 2 §3.3: the budget is levelsPerCycle in total across every source and destination (more Intake ends do not
			// make a pump faster); each Outflow end takes at most one level per cycle
			int levels = System.Math.Max(1, Ext?.levelsPerCycle ?? 1);
			usedOutflows.Clear();
			deadSources.Clear();
			filledPastOutflow = circle = false;
			cycle = Find.TickManager.TicksGame / RM_PumpMath.CycleTicks;
			for (int i = 0; i < levels; i++)
			{
				int before = Moved;
				lastStatus = pourMode ? TryPour() : TryDraw();
				if (Moved == before)
				{
					break;
				}
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
			if (ex.IsExcavated(c) && ex.FillAt(c) > 0)
			{
				s.channel = true;
				s.fluid = ex.FluidAt(c) ?? ex.ActiveFluid;
				return s.fluid != null;
			}
			if (ex.IsSourceCell(c) && ex.Stock.CanSupply(Map, c, ex))
			{
				s.fluid = ex.Stock.BodyAt(Map, c, ex)?.fluid ?? ex.ActiveFluid;
				return s.fluid != null;
			}
			return false;
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

		/// <summary>The cell an Outflow end pours a level of <paramref name="fluid"/> into: the end's cell or the best (deepest,
		/// emptiest, compatible) excavated cell within 1.5 cells of it (RM_PumpMath.PickPour, A14); invalid when blocked.</summary>
		internal static IntVec3 OutflowCell(Map map, RM_MapComponent_Excavation ex, RM_NetPort p, FluidDef fluid)
		{
			if (!(p?.Cell is IntVec3 end) || fluid == null || ex == null)
			{
				return IntVec3.Invalid;
			}
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
			return RM_PumpMath.PickPour(tk, cd, out _, out int ci) ? cells[ci] : IntVec3.Invalid;
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
		private static readonly HashSet<Map> toldPourNeedsDump = new HashSet<Map>();

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
				if (!RM_LiquidNetKernel.PumpNext(sources.Count, i => !deadSources.Contains(i), outflows.Count,
					(o, i) => OutflowCell(Map, ex, outflows[o], sources[i].fluid).IsValid, usedOutflows,
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
					IntVec3 dest = OutflowCell(Map, ex, port, f);
					RM_TransferLeg into = RM_TransferLeg.World(k => ex.CanPourLevel(dest, f), k => ex.TryPourLevel(dest, f));
					RM_TransferLeg from = s.channel
						? RM_TransferLeg.World(k => ex.IsExcavated(cell) && ex.FillAt(cell) > 0, k => ex.TryTakeLevel(cell, out _), k => ex.TryPourLevel(cell, f))
						: RM_TransferLeg.World(k => ex.Stock.CanSupply(Map, cell, ex), k => ex.Stock.TryDebit(Map, cell, f.volumePerTile, ex), k => ex.Stock.TryCredit(Map, cell, f.volumePerTile, ex) >= f.volumePerTile - 1e-4f);
					if (RM_LiquidTransfer.Move(1, from, into, out _) == 1)
					{
						Machinery.RM_LiquidNet.CreditTo(this, port, l, units, RM_PumpMath.CycleTicks);   // credit site: pump to outflow
						Machinery.RM_LiquidNet.CreditTo(this, s.port, l, units, RM_PumpMath.CycleTicks);   // credit site: pump intake (to outflow)
						usedOutflows.Add(oi);
						circle |= ex.Stock.BodyAt(Map, dest, ex) is RM_LiquidBody bd && bd == ex.Stock.BodyAt(Map, cell, ex);   // A19, by body
						Stamp(units);
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
					deadSources.Add(si);
					continue;
				}
				if (s.channel)
				{
					// L1 (§4): the tank leg is reserved first, the channel level (TryTakeLevel, never undone) taken last
					RM_TransferLeg world = RM_TransferLeg.World(k => ex.IsExcavated(cell) && ex.FillAt(cell) > 0, k => ex.TryTakeLevel(cell, out _));
					if (RM_LiquidTransfer.Move(units, world, RM_TransferLeg.Split(plan.Count, i => plan[i].units, (i, k) => plan[i].tank.CanAccept(l, k), (i, k) => plan[i].tank.TryAddLiquid(l, k), (i, k) => plan[i].tank.TryRemoveLiquid(k)), out _) == units)
					{
						foreach ((Building_LiquidTank tank, int units) p in plan) Machinery.RM_LiquidNet.Credit(this, p.tank, l, p.units, RM_PumpMath.CycleTicks);   // credit site: pump draw (channel)
						Machinery.RM_LiquidNet.CreditTo(this, s.port, l, units, RM_PumpMath.CycleTicks);   // credit site: pump intake (channel)
						filledPastOutflow |= outflows.Count > 0;
						Stamp(units);
						Moved++;
						return "RMFlow_PumpDrew".Translate(l.label);
					}
				}
				else
				{
					// L1 (§4): the tank leg is reserved first; the body's debit (TryDebit, never undone) is checked by CanSupply first
					RM_TransferLeg world = RM_TransferLeg.World(k => ex.Stock.CanSupply(Map, cell, ex), k => ex.Stock.TryDebit(Map, cell, f.volumePerTile, ex));
					if (RM_LiquidTransfer.Move(units, world, RM_TransferLeg.Split(plan.Count, i => plan[i].units, (i, k) => plan[i].tank.CanAccept(l, k), (i, k) => plan[i].tank.TryAddLiquid(l, k), (i, k) => plan[i].tank.TryRemoveLiquid(k)), out _) == units)
					{
						foreach ((Building_LiquidTank tank, int units) p in plan) Machinery.RM_LiquidNet.Credit(this, p.tank, l, p.units, RM_PumpMath.CycleTicks);   // credit site: pump draw (source)
						Machinery.RM_LiquidNet.CreditTo(this, s.port, l, units, RM_PumpMath.CycleTicks);   // credit site: pump intake (source)
						filledPastOutflow |= outflows.Count > 0;
						Stamp(units);
						Moved++;
						return "RMFlow_PumpDrew".Translate(l.label);
					}
				}
				deadSources.Add(si);
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
					if (toldPourNeedsDump.Add(Map))
					{
						Messages.Message("RMFlow_PumpPourNeedsDumpMessage".Translate(LabelCap), this, MessageTypeDefOf.NeutralEvent, historical: false);
					}
					return "RMFlow_PumpNoDumpTank".Translate();
				}
				return "RMFlow_PumpTankEmpty".Translate();
			}
			if (!tk.Any(x => x.canProvide && x.fluid != null))
			{
				return "RMFlow_PumpNoChannelForm".Translate(firstProvider.storedLiquid?.label ?? "?");
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
				// rev 2 §3.3: the pour also leaves through Outflow ends on the pump's networks
				string viaOutflow = PourToOutflow(ex, tanks, units);
				if (viaOutflow != null)
				{
					return viaOutflow;
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
					if (!tank.CanProvide(units) || fluid == null)
					{
						continue;
					}
					IntVec3 dest = OutflowCell(Map, ex, port, fluid);
					if (!dest.IsValid)
					{
						continue;
					}
					LiquidDef poured = tank.storedLiquid;
					if (RM_LiquidTransfer.Move(units, RM_TransferLeg.Store(k2 => tank.CanProvide(k2), k2 => tank.TryRemoveLiquid(k2), k2 => tank.TryAddLiquid(poured, k2)),
						RM_TransferLeg.World(k2 => ex.CanPourLevel(dest, fluid), k2 => ex.TryPourLevel(dest, fluid)), out _) == units)
					{
						Machinery.RM_LiquidNet.CreditTo(this, tank, poured, units, RM_PumpMath.CycleTicks);   // credit site: outflow pour (tank)
						Machinery.RM_LiquidNet.CreditTo(this, port, poured, units, RM_PumpMath.CycleTicks);   // credit site: outflow pour (end)
						usedOutflows.Add(oi);
						Stamp(units);
						Moved++;
						return "RMFlow_PumpPouredOutflow".Translate(fluid.label);
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
