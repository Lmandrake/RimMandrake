using System.Collections.Generic;
using System.Globalization;
using System.Text;
using RimWorld;
using Verse;

namespace RimMandrake.FlowWorks.MapControls
{
	/// <summary>FLOW_CONTROLS_BUILD_EIGHT_QUIET_PEBBLES (owner card 2026-10-16, design §2 #1): the LEVEL HOLDER, a flow source and
	/// flow sink in one with a setpoint. Each pulse it brings what it stands on or beside to a set fill fraction, at most
	/// its rate a pulse:
	/// - a DUG CHANNEL (the dug squares in reach): levels poured in through the engine's driver write (TryPourLevel, as
	///   the flow source) or taken out (TryTakeLevel, as the flow sink) until the reach holds the set fraction of what is
	///   dug there; the rest of the channel levels from it. Recorded as map-control flow (NoteMapControlFlow), so the
	///   conservation ledger reads it as external input/exit, never a leak;
	/// - with no dug square in reach, a LIMITED natural BODY (RM_LiquidStock): its stock credited or debited (TryCredit /
	///   TryDebit, the stock's own paths) towards the set fraction of its capacity, a level being the body's own level
	///   unit; recession and refill then redraw the shore. A limitless body needs no holding and is left alone.
	/// Takes only its own liquid; never pours into another (no mixing).</summary>
	public class Building_RM_LevelHolder : Building_RM_MapControl
	{
		public FluidDef fluid;
		public float setpoint = 0.5f;
		public float ratePerPulse = 1f;
		private float carry;
		private int pouredTotal;
		private int takenTotal;
		private float bodyCreditedUnits;
		private float bodyDebitedUnits;

		// Last pulse, derived.
		private string lastMode = "none";
		private int lastHeld;
		private int lastCapacity;
		private int lastNeed;

		private readonly List<IntVec3> candCells = new List<IntVec3>();
		private readonly List<int> candVals = new List<int>();

		public override bool WorksOnDugChannel => false;

		public override void SpawnSetup(Map map, bool respawningAfterLoad)
		{
			base.SpawnSetup(map, respawningAfterLoad);
			if (fluid == null)
			{
				fluid = map.GetComponent<RM_MapComponent_Excavation>()?.ActiveFluid;
			}
		}

		private bool Mine(RM_MapComponent_Excavation ex, IntVec3 c)
		{
			return (ex.FluidAt(c) ?? ex.ActiveFluid) == fluid;
		}

		public override void FlowPulse(RM_MapComponent_Excavation ex)
		{
			if (fluid == null)
			{
				return;
			}
			int due = RM_MapControlMath.Due(ref carry, ratePerPulse);
			if (AnyDugInReach(ex))
			{
				lastMode = "channel";
				HoldChannel(ex, due);
				return;
			}
			RM_LiquidBody body = null;
			IntVec3 at = IntVec3.Invalid;
			foreach (IntVec3 c in Reach())
			{
				if (ex.Stock == null)
				{
					break;
				}
				// A receded (dried) square still belongs to its body: the index first, then a fresh body on wet ground.
				body = ex.Stock.IndexedBodyAt(Map, c) ?? (ex.IsSourceCell(c) ? ex.Stock.BodyAt(Map, c, ex) : null);
				if (body != null)
				{
					at = c;
					break;
				}
			}
			if (body == null || body.limitless)
			{
				lastMode = body == null ? "none" : "limitless";
				lastNeed = 0;
				return;
			}
			lastMode = "body";
			HoldBody(ex, body, at, due);
		}

		private void Measure(RM_MapComponent_Excavation ex, out int held, out int capacity)
		{
			held = 0;
			capacity = 0;
			foreach (IntVec3 c in Reach())
			{
				if (!ex.IsExcavated(c))
				{
					continue;
				}
				capacity += ex.DepthAt(c);
				held += ex.FillAt(c);
			}
		}

		private void HoldChannel(RM_MapComponent_Excavation ex, int due)
		{
			Measure(ex, out lastHeld, out lastCapacity);
			lastNeed = RM_MapControlMath.LevelHolderNeed(lastHeld, lastCapacity, setpoint);
			int poured = 0, taken = 0;
			while (poured + taken < due)
			{
				int need = RM_MapControlMath.LevelHolderNeed(lastHeld + poured - taken, lastCapacity, setpoint);
				if (need == 0)
				{
					break;
				}
				candCells.Clear();
				candVals.Clear();
				foreach (IntVec3 c in Reach())
				{
					if (!Open(ex, c))
					{
						continue;
					}
					if (need > 0 && ex.CanPourLevel(c, fluid))
					{
						candCells.Add(c);
						candVals.Add(ex.FillAt(c) - ex.DepthAt(c));
					}
					else if (need < 0 && ex.FillAt(c) > 0 && Mine(ex, c))
					{
						candCells.Add(c);
						candVals.Add(ex.FillAt(c));
					}
				}
				int pick = need > 0 ? RM_MapControlMath.PickPourTarget(candVals) : RM_MapControlMath.PickDrainTarget(candVals);
				if (pick < 0)
				{
					break;
				}
				if (need > 0)
				{
					if (!ex.TryPourLevel(candCells[pick], fluid))
					{
						break;
					}
					poured++;
				}
				else
				{
					if (!ex.TryTakeLevel(candCells[pick], out _))
					{
						break;
					}
					taken++;
				}
			}
			if (poured > 0 || taken > 0)
			{
				pouredTotal += poured;
				takenTotal += taken;
				ex.NoteMapControlFlow(poured, taken);
			}
		}

		private void HoldBody(RM_MapComponent_Excavation ex, RM_LiquidBody body, IntVec3 at, int due)
		{
			float unit = RM_LiquidStock.LevelUnitOf(body, ex);
			if (!(unit > 0f) || body.fluid != fluid)
			{
				lastNeed = lastHeld = lastCapacity = 0;
				lastMode = "other liquid";
				return;
			}
			lastCapacity = (int)(body.capacity / unit);
			lastHeld = (int)(body.stock / unit);
			lastNeed = RM_MapControlMath.LevelHolderNeed(lastHeld, lastCapacity, setpoint);
			int n = System.Math.Min(due, System.Math.Abs(lastNeed));
			if (n <= 0)
			{
				return;
			}
			if (lastNeed > 0)
			{
				bodyCreditedUnits += ex.Stock.TryCredit(Map, at, n * unit, ex);
			}
			else
			{
				float before = body.stock;
				ex.Stock.TryDebit(Map, at, n * unit, ex);
				bodyDebitedUnits += before - body.stock;   // 0 when the source budget is off (stock is not kept then)
			}
		}

		protected override void AppendInspect(StringBuilder sb, RM_MapComponent_Excavation ex)
		{
			sb.AppendLine("Holds " + FluidLabel(fluid) + " at " + setpoint.ToStringPercent() + " full, at most "
				+ RM_MapControlMath.RateLabel(ratePerPulse, RimMandrakeFlowWorksSettings.PulseIntervalTicks));
			if (lastMode == "channel" || lastMode == "body")
			{
				sb.AppendLine("Now: " + lastHeld + " of " + lastCapacity + " level(s) (" + lastMode + ")"
					+ (lastNeed > 0 ? ", filling" : (lastNeed < 0 ? ", draining" : ", holding")));
			}
			else if (lastMode == "limitless")
			{
				sb.AppendLine("The body here is limitless: nothing to hold.");
			}
			sb.Append("Poured " + pouredTotal + ", taken " + takenTotal + " level(s) in a channel; body +"
				+ bodyCreditedUnits.ToString("0.#", CultureInfo.InvariantCulture) + " / -"
				+ bodyDebitedUnits.ToString("0.#", CultureInfo.InvariantCulture) + " units");
		}

		protected override IEnumerable<Gizmo> ControlGizmos()
		{
			yield return new Command_Action
			{
				defaultLabel = "Liquid: " + FluidLabel(fluid),
				defaultDesc = "Choose which liquid this level holder holds (it pours and takes only that one).",
				icon = def.uiIcon,
				action = () =>
				{
					List<FloatMenuOption> opts = new List<FloatMenuOption>();
					foreach (FluidDef f in CanalFluids())
					{
						FluidDef pick = f;
						opts.Add(new FloatMenuOption(FluidLabel(f), () => fluid = pick));
					}
					Find.WindowStack.Add(new FloatMenu(opts));
				},
			};
			yield return new Command_Action
			{
				defaultLabel = "Hold at " + setpoint.ToStringPercent(),
				defaultDesc = "The fill this level holder keeps: a fraction of what is dug beside it, or of the body's capacity.",
				icon = def.uiIcon,
				action = () =>
				{
					List<FloatMenuOption> opts = new List<FloatMenuOption>();
					foreach (float v in RM_MapControlMath.SetpointPresets)
					{
						float pick = v;
						opts.Add(new FloatMenuOption(pick.ToStringPercent() + " full", () => setpoint = pick));
					}
					Find.WindowStack.Add(new FloatMenu(opts));
				},
			};
			yield return RateGizmo("Pouring or taking", () => ratePerPulse, v => ratePerPulse = RM_MapControlMath.ClampRate(v), false, null, null);
		}

		public override string StateLine()
		{
			return "levelholder " + ThingID + " at " + Position.x + "," + Position.z + " fluid=" + (fluid?.defName ?? "none")
				+ " setpoint=" + setpoint.ToString("0.###", CultureInfo.InvariantCulture)
				+ " rate=" + ratePerPulse.ToString("0.###", CultureInfo.InvariantCulture) + " active=" + active
				+ " mode=" + lastMode + " held=" + lastHeld + " capacity=" + lastCapacity + " need=" + lastNeed
				+ " poured=" + pouredTotal + " taken=" + takenTotal
				+ " bodyIn=" + bodyCreditedUnits.ToString("0.##", CultureInfo.InvariantCulture)
				+ " bodyOut=" + bodyDebitedUnits.ToString("0.##", CultureInfo.InvariantCulture);
		}

		public override void ExposeData()
		{
			base.ExposeData();
			Scribe_Defs.Look(ref fluid, "RM_levelHolderFluid");
			Scribe_Values.Look(ref setpoint, "RM_levelHolderSetpoint", 0.5f);
			Scribe_Values.Look(ref ratePerPulse, "RM_levelHolderRate", 1f);
			Scribe_Values.Look(ref carry, "RM_levelHolderCarry", 0f);
			Scribe_Values.Look(ref pouredTotal, "RM_levelHolderPoured", 0);
			Scribe_Values.Look(ref takenTotal, "RM_levelHolderTaken", 0);
			Scribe_Values.Look(ref bodyCreditedUnits, "RM_levelHolderBodyIn", 0f);
			Scribe_Values.Look(ref bodyDebitedUnits, "RM_levelHolderBodyOut", 0f);
		}
	}
}
