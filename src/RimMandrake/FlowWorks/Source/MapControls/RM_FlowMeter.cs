using System.Collections.Generic;
using System.Globalization;
using System.Text;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.FlowWorks.MapControls
{
	/// <summary>FLOW_CONTROLS_BUILD_EIGHT_QUIET_PEBBLES (owner card 2026-10-16, design §2 #8): the FLOW METER, a readout pebble.
	/// It moves nothing. Each flow pulse it reads what it stands on or beside: the dug channel there (every dug square
	/// joined to it, up to <see cref="MaxWalk"/>: squares, levels held of levels dug, which liquids) or, with no dug square,
	/// the natural liquid body there (id, liquid, stock of capacity, limitless or not), and keeps a day of samples so it can
	/// say the net in/out per day. Dev mode shows the reading as a label over it; the bridge reads <see cref="StateLine"/>.
	/// It makes every other control checkable by eye and by bridge.</summary>
	public class Building_RM_FlowMeter : Building_RM_MapControl
	{
		public const int MaxWalk = 4000;

		// Derived each pulse, never saved: the last reading.
		private string kind = "nothing";
		private int cells;
		private int held;
		private int dug;
		private string fluids = "";
		private int bodyId = -1;
		private float bodyStock;
		private float bodyCapacity;
		private bool bodyLimitless;
		private float perDay;
		private bool haveReading;

		// A day of (tick, amount) samples, so the net per day survives a reload.
		private List<int> sampleTicks = new List<int>();
		private List<float> sampleAmounts = new List<float>();

		private readonly HashSet<IntVec3> seen = new HashSet<IntVec3>();
		private readonly List<IntVec3> queue = new List<IntVec3>();
		private readonly HashSet<string> fluidNames = new HashSet<string>();

		public override bool WorksOnDugChannel => false;

		public override void FlowPulse(RM_MapComponent_Excavation ex)
		{
			Read(ex);
			float amount = kind == "channel" ? held : (kind == "body" ? bodyStock : 0f);
			int now = Find.TickManager.TicksGame;
			sampleTicks.Add(now);
			sampleAmounts.Add(amount);
			while (sampleTicks.Count > 1 && now - sampleTicks[0] > GenDate.TicksPerDay)
			{
				sampleTicks.RemoveAt(0);
				sampleAmounts.RemoveAt(0);
			}
			perDay = RM_MapControlMath.PerDay(amount - sampleAmounts[0], now - sampleTicks[0]);
		}

		/// <summary>Take a reading now (also used by the bridge between pulses).</summary>
		public void Read(RM_MapComponent_Excavation ex)
		{
			haveReading = true;
			cells = held = dug = 0;
			bodyId = -1;
			fluidNames.Clear();
			seen.Clear();
			queue.Clear();
			foreach (IntVec3 c in Reach())
			{
				if (ex.IsExcavated(c) && seen.Add(c))
				{
					queue.Add(c);
				}
			}
			if (queue.Count > 0)
			{
				kind = "channel";
				for (int head = 0; head < queue.Count && cells < MaxWalk; head++)
				{
					IntVec3 c = queue[head];
					cells++;
					int f = ex.FillAt(c);
					held += f;
					dug += ex.DepthAt(c);
					if (f > 0)
					{
						FluidDef fl = ex.FluidAt(c) ?? ex.ActiveFluid;
						fluidNames.Add(fl?.defName ?? "?");
					}
					for (int i = 0; i < 4; i++)
					{
						IntVec3 n = c + GenAdj.CardinalDirections[i];
						if (n.InBounds(Map) && ex.IsExcavated(n) && seen.Add(n))
						{
							queue.Add(n);
						}
					}
				}
				fluids = string.Join("+", fluidNames);
				return;
			}
			RM_LiquidBody body = null;
			foreach (IntVec3 c in Reach())
			{
				body = ex.Stock?.IndexedBodyAt(Map, c);
				if (body != null)
				{
					break;
				}
			}
			if (body != null)
			{
				kind = "body";
				bodyId = body.id;
				bodyStock = body.stock;
				bodyCapacity = body.capacity;
				bodyLimitless = body.limitless;
				cells = body.cells?.Count ?? 0;
				fluids = body.fluid?.defName ?? "?";
				return;
			}
			kind = "nothing";
			fluids = "";
		}

		private string Reading()
		{
			if (!haveReading)
			{
				return "No reading yet (it reads on the next flow pulse).";
			}
			string net = (perDay >= 0f ? "+" : "") + perDay.ToString("0.#", CultureInfo.InvariantCulture);
			if (kind == "channel")
			{
				return "Channel: " + cells + " dug square(s), " + held + " of " + dug + " level(s) full"
					+ (fluids.Length > 0 ? " (" + fluids + ")" : " (dry)") + ", net " + net + " level(s)/day"
					+ (cells >= MaxWalk ? " (read the first " + MaxWalk + " squares)" : "");
			}
			if (kind == "body")
			{
				return "Body #" + bodyId + " (" + fluids + ", " + cells + " squares): "
					+ (bodyLimitless ? "limitless" : bodyStock.ToString("0.#", CultureInfo.InvariantCulture) + " of "
						+ bodyCapacity.ToString("0.#", CultureInfo.InvariantCulture) + " units, net " + net + " units/day");
			}
			return "Nothing to read: no dug channel or known liquid body here or beside it.";
		}

		protected override void AppendInspect(StringBuilder sb, RM_MapComponent_Excavation ex)
		{
			sb.Append(Reading());
		}

		protected override IEnumerable<Gizmo> ControlGizmos()
		{
			yield return new Command_Action
			{
				defaultLabel = "Read now",
				defaultDesc = "Take a reading now and write it to the log.",
				icon = def.uiIcon,
				action = () =>
				{
					RM_MapComponent_Excavation ex = Map?.GetComponent<RM_MapComponent_Excavation>();
					if (ex != null)
					{
						Read(ex);
					}
					Log.Message("[RMFlowWorksDebug] " + StateLine());
				},
			};
		}

		public override void DrawGUIOverlay()
		{
			base.DrawGUIOverlay();
			if (!DebugSettings.ShowDevGizmos || !haveReading || Find.CameraDriver.CurrentZoom > CameraZoomRange.Middle)
			{
				return;
			}
			string s = kind == "channel" ? held + "/" + dug + " " + (perDay >= 0f ? "+" : "") + perDay.ToString("0", CultureInfo.InvariantCulture) + "/d"
				: (kind == "body" ? (bodyLimitless ? "#" + bodyId + " inf" : "#" + bodyId + " " + bodyStock.ToString("0", CultureInfo.InvariantCulture)) : "-");
			GenMapUI.DrawThingLabel(this, s, new Color(0.8f, 0.85f, 0.9f, 0.85f));
		}

		public override string StateLine()
		{
			return "meter " + ThingID + " at " + Position.x + "," + Position.z + " active=" + active + " kind=" + kind
				+ " cells=" + cells + " held=" + held + " dug=" + dug + " fluids=" + (fluids.Length > 0 ? fluids : "none")
				+ " body=" + bodyId + " stock=" + bodyStock.ToString("0.##", CultureInfo.InvariantCulture)
				+ " capacity=" + bodyCapacity.ToString("0.##", CultureInfo.InvariantCulture) + " limitless=" + bodyLimitless
				+ " perDay=" + perDay.ToString("0.##", CultureInfo.InvariantCulture);
		}

		public override void ExposeData()
		{
			base.ExposeData();
			Scribe_Collections.Look(ref sampleTicks, "RM_flowMeterTicks", LookMode.Value);
			Scribe_Collections.Look(ref sampleAmounts, "RM_flowMeterAmounts", LookMode.Value);
			if (Scribe.mode == LoadSaveMode.PostLoadInit)
			{
				sampleTicks = sampleTicks ?? new List<int>();
				sampleAmounts = sampleAmounts ?? new List<float>();
				if (sampleTicks.Count != sampleAmounts.Count)
				{
					sampleTicks.Clear();
					sampleAmounts.Clear();
				}
			}
		}
	}
}
