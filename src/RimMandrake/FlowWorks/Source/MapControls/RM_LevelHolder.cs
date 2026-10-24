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
		private float pouredTotal;
		private float takenTotal;
		private float bodyCreditedUnits;
		private float lastUnit;
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

		/// <summary>LEVEL_HOLDER_FIX_REFILLS_FRACTIONAL_BASIN: held is measured in dL (whole notches AND the part notch), so a
		/// spread sheet with no whole notch reads as the water it is, not as an empty basin.</summary>
		private void Measure(RM_MapComponent_Excavation ex, out long heldDl, out int capacity)
		{
			heldDl = 0;
			capacity = 0;
			foreach (IntVec3 c in Reach())
			{
				if (!ex.IsExcavated(c))
				{
					continue;
				}
				capacity += ex.DepthAt(c);
				heldDl += ex.WaterDlAt(c);
			}
		}

		private void HoldChannel(RM_MapComponent_Excavation ex, int due)
		{
			Measure(ex, out long heldDl, out lastCapacity);
			lastHeld = RM_MapControlMath.HeldLevels(heldDl, RM_LevelSolve.U);
			lastNeed = RM_MapControlMath.LevelHolderNeed(lastHeld, lastCapacity, setpoint);
			long dueDl = due * RM_LevelSolve.U;
			long poured = 0, taken = 0;   // dL
			while (poured + taken < dueDl)
			{
				int need = RM_MapControlMath.LevelHolderNeed(RM_MapControlMath.HeldLevels(heldDl + poured - taken, RM_LevelSolve.U),
					lastCapacity, setpoint);
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
					else if (need < 0 && ex.WaterDlAt(c) > 0 && Mine(ex, c))
					{
						candCells.Add(c);
						candVals.Add((int)System.Math.Min(ex.WaterDlAt(c), int.MaxValue));
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
					poured += RM_LevelSolve.U;
				}
				else
				{
					long took = ex.TryTakeDl(candCells[pick], RM_LevelSolve.U, out _);
					if (took <= 0)
					{
						break;
					}
					taken += took;
				}
			}
			if (poured > 0 || taken > 0)
			{
				pouredTotal += poured / (float)RM_LevelSolve.U;
				takenTotal += taken / (float)RM_LevelSolve.U;
				ex.NoteMapControlFlowDl(poured, taken);
			}
		}

		private void HoldBody(RM_MapComponent_Excavation ex, RM_LiquidBody body, IntVec3 at, int due)
		{
			float unit = RM_LiquidStock.LevelUnitOf(body, ex);
			lastUnit = unit;
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
				// LIQUID_DEPTH_REWIRE_FIVE_IS_DEAD (unified depth spec §4.3): litres, never "level N" as a count
				sb.AppendLine("Now: " + RM_Volume.FormatLitres(lastHeld * (double)RM_Volume.LitresPerLevel)
					+ " of " + RM_Volume.FormatLitres(lastCapacity * (double)RM_Volume.LitresPerLevel) + " (" + lastMode + ")"
					+ (lastNeed > 0 ? ", filling" : (lastNeed < 0 ? ", draining" : ", holding")));
			}
			else if (lastMode == "limitless")
			{
				sb.AppendLine("The body here is limitless: nothing to hold.");
			}
			// body counters are fill-units; a level of this body is lastUnit of them and 1,000 L (LIQUID_LITRES_MIGRATE_DRUMS_ARE_DRUMS)
			float perLevel = lastUnit > 0f ? lastUnit : 1f;
			sb.Append("Poured " + RM_Volume.FormatLitres(pouredTotal * (double)RM_Volume.LitresPerLevel) + ", taken "
				+ RM_Volume.FormatLitres(takenTotal * (double)RM_Volume.LitresPerLevel) + " in a channel; body +"
				+ RM_Volume.FormatLitres(bodyCreditedUnits / perLevel * RM_Volume.LitresPerLevel) + " / -"
				+ RM_Volume.FormatLitres(bodyDebitedUnits / perLevel * RM_Volume.LitresPerLevel));
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
				+ " poured=" + pouredTotal.ToString("0.###", CultureInfo.InvariantCulture) + " taken=" + takenTotal.ToString("0.###", CultureInfo.InvariantCulture)
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
			Scribe_Values.Look(ref pouredTotal, "RM_levelHolderPoured", 0f);
			Scribe_Values.Look(ref takenTotal, "RM_levelHolderTaken", 0f);
			Scribe_Values.Look(ref bodyCreditedUnits, "RM_levelHolderBodyIn", 0f);
			Scribe_Values.Look(ref bodyDebitedUnits, "RM_levelHolderBodyOut", 0f);
		}
	}
}
