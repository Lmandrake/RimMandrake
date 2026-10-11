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
			int levels = System.Math.Max(1, Ext?.levelsPerCycle ?? 1);
			for (int i = 0; i < levels; i++)
			{
				int before = Moved;
				lastStatus = pourMode ? TryPour() : TryDraw();
				if (Moved == before)
				{
					break;
				}
			}
		}

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
			List<Building_LiquidTank> tanks = NetTanks();
			if (ex == null || tanks.Count == 0)
			{
				return Machinery.RM_LiquidNet.TooLarge(this) ? "RMFlow_NetTooLarge".Translate() : "RMFlow_PumpNoTank".Translate();
			}
			int units = RM_PumpMath.TankUnitsPerLevel;
			foreach (IntVec3 c in ReachCells())
			{
				if (!c.InBounds(Map))
				{
					continue;
				}
				IntVec3 cell = c;
				if (ex.IsExcavated(c) && ex.FillAt(c) > 0)
				{
					FluidDef f = ex.FluidAt(c) ?? ex.ActiveFluid;
					LiquidDef l = LiquidFor(f);
					// L3 (§3.2): the fill plan may split the level across tanks (3 + 2 units of room take it)
					List<(Building_LiquidTank tank, int units)> plan = l == null ? null : Machinery.RM_LiquidNet.FillPlan(this, l, units);
					if (plan == null)
					{
						continue;
					}
					// L1 (§4): the tank leg is reserved first, the channel level (TryTakeLevel, never undone) taken last
					RM_TransferLeg world = RM_TransferLeg.World(k => ex.IsExcavated(cell) && ex.FillAt(cell) > 0, k => ex.TryTakeLevel(cell, out _));
					if (RM_LiquidTransfer.Move(units, world, RM_TransferLeg.Split(plan.Count, i => plan[i].units, (i, k) => plan[i].tank.CanAccept(l, k), (i, k) => plan[i].tank.TryAddLiquid(l, k), (i, k) => plan[i].tank.TryRemoveLiquid(k)), out _) == units)
					{
						foreach ((Building_LiquidTank tank, int units) p in plan) Machinery.RM_LiquidNet.Credit(this, p.tank, l, p.units, RM_PumpMath.CycleTicks);   // credit site: pump draw (channel)
						Stamp(units);
						Moved++;
						return "RMFlow_PumpDrew".Translate(l.label);
					}
				}
				else if (ex.IsSourceCell(c))
				{
					RM_LiquidBody body = ex.Stock.BodyAt(Map, c, ex);
					FluidDef f = body?.fluid ?? ex.ActiveFluid;
					LiquidDef l = LiquidFor(f);
					// L3 (§3.2): the fill plan may split the level across tanks (3 + 2 units of room take it)
					List<(Building_LiquidTank tank, int units)> plan = l == null ? null : Machinery.RM_LiquidNet.FillPlan(this, l, units);
					if (plan == null)
					{
						continue;
					}
					// L1 (§4): the tank leg is reserved first; the body's debit (TryDebit, never undone) is checked by CanSupply first
					RM_TransferLeg world = RM_TransferLeg.World(k => ex.Stock.CanSupply(Map, cell, ex), k => ex.Stock.TryDebit(Map, cell, f.volumePerTile, ex));
					if (RM_LiquidTransfer.Move(units, world, RM_TransferLeg.Split(plan.Count, i => plan[i].units, (i, k) => plan[i].tank.CanAccept(l, k), (i, k) => plan[i].tank.TryAddLiquid(l, k), (i, k) => plan[i].tank.TryRemoveLiquid(k)), out _) == units)
					{
						foreach ((Building_LiquidTank tank, int units) p in plan) Machinery.RM_LiquidNet.Credit(this, p.tank, l, p.units, RM_PumpMath.CycleTicks);   // credit site: pump draw (source)
						Stamp(units);
						Moved++;
						return "RMFlow_PumpDrew".Translate(l.label);
					}
				}
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
			List<Building_LiquidTank> tanks = NetTanks();
			var tk = new List<(bool canProvide, FluidDef fluid)>(tanks.Count);
			foreach (Building_LiquidTank t in tanks)
			{
				tk.Add((t.CanProvide(units), t.storedLiquid?.canalFluid));
			}
			Building_LiquidTank firstProvider = tanks.FirstOrDefault(t => t.CanProvide(units));
			if (ex == null || firstProvider == null)
			{
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
				+ (lastStatus.NullOrEmpty() ? "" : ": " + lastStatus);
			return s.NullOrEmpty() ? mine : s + "\n" + mine;
		}
	}
}
