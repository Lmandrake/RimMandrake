using System;
using System.Collections.Generic;
using System.Text;
using RimWorld;
using Verse;

namespace RimMandrake.FlowWorks.MapControls
{
	/// <summary>FLOW_SOURCE_SINK_BUILD_TAPS_FOR_MAPMAKERS: the flow SOURCE. Each pulse it pours its liquid into the dug squares
	/// in reach (its own, then N/E/S/W), one level at a time into the lowest surface, through the engine's own driver
	/// write (RM_MapComponent_Excavation.TryPourLevel: brim, no-mix, liquids switched off in Mod Settings and the fluid
	/// palette all respected; the square becomes a flow-order input so a flat channel spreads away from it). Liquid
	/// enters the world here, so it is recorded as an external input (NoteMapControlFlow), never a ledger imbalance.</summary>
	public class Building_RM_FlowSource : Building_RM_MapControl
	{
		public FluidDef fluid;
		public float ratePerPulse = 1f;
		private float carry;
		private int pouredTotal;
		private bool backedUp;

		private readonly List<IntVec3> candCells = new List<IntVec3>();
		private readonly List<int> candSurface = new List<int>();

		public override void SpawnSetup(Map map, bool respawningAfterLoad)
		{
			base.SpawnSetup(map, respawningAfterLoad);
			if (fluid == null)
			{
				fluid = map.GetComponent<RM_MapComponent_Excavation>()?.ActiveFluid;
			}
		}

		public override void FlowPulse(RM_MapComponent_Excavation ex)
		{
			if (fluid == null)
			{
				return;
			}
			int due = RM_MapControlMath.Due(ref carry, ratePerPulse);
			int done = 0;
			backedUp = false;
			while (done < due)
			{
				candCells.Clear();
				candSurface.Clear();
				foreach (IntVec3 c in Reach())
				{
					if (Open(ex, c) && ex.CanPourLevel(c, fluid))
					{
						candCells.Add(c);
						candSurface.Add(ex.FillAt(c) - ex.DepthAt(c));
					}
				}
				int pick = RM_MapControlMath.PickPourTarget(candSurface);
				if (pick < 0 || !ex.TryPourLevel(candCells[pick], fluid))
				{
					backedUp = true;
					break;
				}
				done++;
			}
			if (backedUp)
			{
				// P4: a driver held back by a brimming square still feeds the channel; keep it a flow-order input.
				foreach (IntVec3 c in Reach())
				{
					if (Open(ex, c))
					{
						ex.NoteDriverBackedUp(c);
					}
				}
			}
			if (done > 0)
			{
				pouredTotal += done;
				ex.NoteMapControlFlow(done, 0);
			}
		}

		protected override void AppendInspect(StringBuilder sb, RM_MapComponent_Excavation ex)
		{
			sb.AppendLine("Pours " + FluidLabel(fluid) + ": " + RM_MapControlMath.RateLabel(ratePerPulse, RimMandrakeFlowWorksSettings.PulseIntervalTicks));
			if (fluid != null && !RimMandrakeFlowWorksSettings.FluidAllowed(fluid))
			{
				sb.AppendLine("That liquid is switched off in Mod Settings: nothing pours.");
			}
			else if (backedUp)
			{
				sb.AppendLine("Backed up: the channel is full here (or holds another liquid).");
			}
			sb.Append("Poured so far: " + pouredTotal + " level(s)");
		}

		protected override IEnumerable<Gizmo> ControlGizmos()
		{
			yield return new Command_Action
			{
				defaultLabel = "Liquid: " + FluidLabel(fluid),
				defaultDesc = "Choose which liquid this source pours.",
				icon = def.uiIcon,
				action = () =>
				{
					List<FloatMenuOption> opts = new List<FloatMenuOption>();
					foreach (FluidDef f in CanalFluids())
					{
						FluidDef pick = f;
						string label = FluidLabel(f) + (RimMandrakeFlowWorksSettings.FluidAllowed(f) ? "" : " (switched off in Mod Settings)");
						opts.Add(new FloatMenuOption(label, () => fluid = pick));
					}
					Find.WindowStack.Add(new FloatMenu(opts));
				},
			};
			yield return RateGizmo("Pouring", () => ratePerPulse, v => ratePerPulse = RM_MapControlMath.ClampRate(v), false, null, null);
		}

		public override string StateLine()
		{
			return "source " + ThingID + " at " + Position.x + "," + Position.z + " fluid=" + (fluid?.defName ?? "none")
				+ " rate=" + ratePerPulse.ToString("0.###") + " active=" + active + " poured=" + pouredTotal + " backedUp=" + backedUp;
		}

		public override void ExposeData()
		{
			base.ExposeData();
			Scribe_Defs.Look(ref fluid, "RM_flowSourceFluid");
			Scribe_Values.Look(ref ratePerPulse, "RM_flowSourceRate", 1f);
			Scribe_Values.Look(ref carry, "RM_flowSourceCarry", 0f);
			Scribe_Values.Look(ref pouredTotal, "RM_flowSourcePoured", 0);
		}
	}

	/// <summary>FLOW_SOURCE_SINK_BUILD_TAPS_FOR_MAPMAKERS: the flow SINK, a source in reverse. Each pulse it takes levels out
	/// of the dug squares in reach, up to a level at a time from the fullest, part notches too (RM_MapComponent_Excavation.TryTakeDl), at its
	/// rate or, unlimited, everything in reach. Optional liquid filter (default: any). The liquid leaves the map like a
	/// map-edge sink's and is recorded as an exit (NoteMapControlFlow), never a ledger imbalance.</summary>
	public class Building_RM_FlowSink : Building_RM_MapControl
	{
		/// <summary>Null = any liquid.</summary>
		public FluidDef filter;
		public float ratePerPulse = 1f;
		public bool unlimited = true;
		private float carry;
		private float drainedTotal;

		private readonly List<IntVec3> candCells = new List<IntVec3>();
		private readonly List<int> candFill = new List<int>();

		/// <summary>Cap for an unlimited sink: no reach can hold more than this many levels.</summary>
		private const int UnlimitedCap = 5 * 255;

		public override void FlowPulse(RM_MapComponent_Excavation ex)
		{
			int due = unlimited ? UnlimitedCap : RM_MapControlMath.Due(ref carry, ratePerPulse);
			// UNLIMITED_SINK_FIX_FRACTIONAL_WATER: measured and taken in dL, so a part-notch sheet (exact-level water; no whole
			// notch, FillAt 0) is a candidate and is drained, the part notch first. Fullest (in dL) first, a notch at most per take.
			long dueDl = due * RM_LevelSolve.U;
			long doneDl = 0;
			while (doneDl < dueDl)
			{
				candCells.Clear();
				candFill.Clear();
				foreach (IntVec3 c in Reach())
				{
					if (!Open(ex, c))
					{
						continue;
					}
					long w = ex.WaterDlAt(c);
					if (w > 0 && (filter == null || (ex.FluidAt(c) ?? ex.ActiveFluid) == filter))
					{
						candCells.Add(c);
						candFill.Add((int)Math.Min(w, int.MaxValue));
					}
				}
				int pick = RM_MapControlMath.PickDrainTarget(candFill);
				if (pick < 0)
				{
					break;
				}
				long took = ex.TryTakeDl(candCells[pick], Math.Min(RM_LevelSolve.U, dueDl - doneDl), out _);
				if (took <= 0)
				{
					break;
				}
				doneDl += took;
			}
			if (doneDl > 0)
			{
				drainedTotal += doneDl / (float)RM_LevelSolve.U;
				ex.NoteMapControlFlowDl(0, doneDl);
			}
		}

		protected override void AppendInspect(StringBuilder sb, RM_MapComponent_Excavation ex)
		{
			sb.AppendLine("Takes " + FluidLabel(filter) + ": "
				+ (unlimited ? "unlimited" : RM_MapControlMath.RateLabel(ratePerPulse, RimMandrakeFlowWorksSettings.PulseIntervalTicks)));
			sb.Append("Taken so far: " + drainedTotal.ToString("0.##") + " level(s)");
		}

		protected override IEnumerable<Gizmo> ControlGizmos()
		{
			yield return new Command_Action
			{
				defaultLabel = "Takes: " + FluidLabel(filter),
				defaultDesc = "Choose which liquid this sink takes (any liquid, or only one).",
				icon = def.uiIcon,
				action = () =>
				{
					List<FloatMenuOption> opts = new List<FloatMenuOption> { new FloatMenuOption("Any liquid", () => filter = null) };
					foreach (FluidDef f in CanalFluids())
					{
						FluidDef pick = f;
						opts.Add(new FloatMenuOption(FluidLabel(f), () => filter = pick));
					}
					Find.WindowStack.Add(new FloatMenu(opts));
				},
			};
			yield return RateGizmo("Draining", () => ratePerPulse, v => ratePerPulse = RM_MapControlMath.ClampRate(v), true,
				() => unlimited, u => unlimited = u);
		}

		public override string StateLine()
		{
			return "sink " + ThingID + " at " + Position.x + "," + Position.z + " filter=" + (filter?.defName ?? "any")
				+ " rate=" + (unlimited ? "unlimited" : ratePerPulse.ToString("0.###")) + " active=" + active + " drained=" + drainedTotal.ToString("0.###");
		}

		public override void ExposeData()
		{
			base.ExposeData();
			Scribe_Defs.Look(ref filter, "RM_flowSinkFilter");
			Scribe_Values.Look(ref ratePerPulse, "RM_flowSinkRate", 1f);
			Scribe_Values.Look(ref unlimited, "RM_flowSinkUnlimited", true);
			Scribe_Values.Look(ref carry, "RM_flowSinkCarry", 0f);
			Scribe_Values.Look(ref drainedTotal, "RM_flowSinkDrained", 0f);
		}
	}
}
