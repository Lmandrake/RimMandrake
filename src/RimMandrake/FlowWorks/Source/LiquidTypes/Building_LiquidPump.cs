using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;

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
			CellRect rect = this.OccupiedRect();
			foreach (IntVec3 c in GenRadial.RadialCellsAround(Position, reach + rect.Width / 2f, true))
			{
				if (!rect.Contains(c))
				{
					yield return c;
				}
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
				return "RMFlow_PumpNoTank".Translate();
			}
			int units = RM_PumpMath.TankUnitsPerLevel;
			foreach (IntVec3 c in ReachCells())
			{
				if (!c.InBounds(Map))
				{
					continue;
				}
				if (ex.IsExcavated(c) && ex.FillAt(c) > 0)
				{
					FluidDef f = ex.FluidAt(c) ?? ex.ActiveFluid;
					LiquidDef l = LiquidFor(f);
					Building_LiquidTank tank = l == null ? null : Machinery.RM_LiquidNet.TankToFill(this, l, units);
					if (tank == null)
					{
						continue;
					}
					if (ex.TryTakeLevel(c, out _))
					{
						tank.TryAddLiquid(l, units);
						Moved++;
						return "RMFlow_PumpDrew".Translate(l.label);
					}
				}
				else if (ex.IsSourceCell(c))
				{
					RM_LiquidBody body = ex.Stock.BodyAt(Map, c, ex);
					FluidDef f = body?.fluid ?? ex.ActiveFluid;
					LiquidDef l = LiquidFor(f);
					Building_LiquidTank tank = l == null ? null : Machinery.RM_LiquidNet.TankToFill(this, l, units);
					if (tank == null)
					{
						continue;
					}
					if (ex.Stock.TryDebit(Map, c, f.volumePerTile, ex))
					{
						tank.TryAddLiquid(l, units);
						Moved++;
						return "RMFlow_PumpDrew".Translate(l.label);
					}
				}
			}
			return "RMFlow_PumpNothingToDraw".Translate();
		}

		private string TryPour()
		{
			RM_MapComponent_Excavation ex = RM_SuperdeepTrap.EngineOf(Map);
			int units = RM_PumpMath.TankUnitsPerLevel;
			Building_LiquidTank tank = null;
			foreach (Building_LiquidTank t in NetTanks())
			{
				if (t.CanProvide(units) && t.storedLiquid?.canalFluid != null)
				{
					tank = t;
					break;
				}
				tank = tank ?? (t.CanProvide(units) ? t : null);
			}
			if (ex == null || tank == null)
			{
				return "RMFlow_PumpTankEmpty".Translate();
			}
			FluidDef fluid = tank.storedLiquid?.canalFluid;
			if (fluid == null)
			{
				return "RMFlow_PumpNoChannelForm".Translate(tank.storedLiquid?.label ?? "?");
			}
			// Deepest-emptiest first, so a pump at the head of a channel fills it the way flow would.
			IntVec3 best = IntVec3.Invalid;
			int bestRoom = 0;
			foreach (IntVec3 c in ReachCells())
			{
				if (!c.InBounds(Map) || !ex.IsExcavated(c))
				{
					continue;
				}
				// Skip a cell holding another liquid before ranking by room, so a roomier foreign cell never hides a
				// compatible one beside it (GPT FlowWorks review #20). Same predicate TryPourLevel applies.
				if (!RM_StockMath.FluidsCompatible(ex.FillAt(c) > 0, ex.FluidAt(c), fluid))
				{
					continue;
				}
				int room = ex.DepthAt(c) - ex.FillAt(c);
				if (room > bestRoom)
				{
					best = c;
					bestRoom = room;
				}
			}
			if (!best.IsValid)
			{
				return "RMFlow_PumpNoRoom".Translate();
			}
			if (!ex.TryPourLevel(best, fluid))
			{
				return "RMFlow_PumpForeign".Translate();
			}
			tank.TryRemoveLiquid(units);
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
