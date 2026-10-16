using System.Collections.Generic;
using System.Globalization;
using System.Text;
using HarmonyLib;
using RimWorld;
using Verse;

namespace RimMandrake.FlowWorks.MapControls
{
	/// <summary>FLOW_CONTROLS_BUILD_EIGHT_QUIET_PEBBLES (owner card 2026-10-16, design §2 #3): the TIMER SWITCH. Each flow pulse
	/// it decides ON or OFF (RM_MapControlMath.TimerOn: by hours of the local day, or by a period counted from game start,
	/// optionally inverted) and sets everything it links within its radius:
	/// - every other map control (source, sink, level holder, thermostat ...; never another timer) is switched on/off;
	/// - every flow door (sluice or grate) is held open while ON and let close while OFF (vanilla's hold-open flag, so a
	///   pawn may still open it in passing; a shut sluice then seals its canal as always).
	/// A linked control follows the timer: switching it by hand lasts until the timer's next pulse. A ROUTE-shaped water
	/// day (fountain at dawn, bath drained at night) for Inhabited.</summary>
	public class Building_RM_TimerSwitch : Building_RM_MapControl
	{
		public int mode = RM_MapControlMath.TimerByHours;
		public int startHour = 6;
		public int endHour = 18;
		public float periodHours = 24f;
		public float onHours = 6f;
		public bool invert;
		public float radius = 5f;

		private bool lastOn;
		private bool decided;
		private int lastControls;
		private int lastDoors;

		private static readonly AccessTools.FieldRef<Building_Door, bool> HoldOpenRef =
			AccessTools.FieldRefAccess<Building_Door, bool>("holdOpenInt");

		public override bool WorksOnDugChannel => false;
		public override bool TimerSwitchable => false;
		protected override float SelectionRadius => radius;

		public bool OnNow()
		{
			float hour = Map != null ? GenLocalDate.HourFloat(Map) : 0f;
			return RM_MapControlMath.TimerOn(mode, hour, startHour, endHour, Find.TickManager.TicksGame, periodHours, onHours, invert);
		}

		public override void FlowPulse(RM_MapComponent_Excavation ex)
		{
			Apply(OnNow());
		}

		/// <summary>Set every linked control and flow door to <paramref name="on"/>.</summary>
		public void Apply(bool on)
		{
			lastOn = on;
			decided = true;
			lastControls = lastDoors = 0;
			HashSet<Thing> done = new HashSet<Thing>();
			foreach (IntVec3 c in CellsInRadius(radius))
			{
				List<Thing> things = c.GetThingList(Map);
				for (int i = 0; i < things.Count; i++)
				{
					Thing t = things[i];
					if (t == this || !done.Add(t))
					{
						continue;
					}
					if (t is Building_RM_MapControl mc && mc.TimerSwitchable)
					{
						mc.active = on;
						lastControls++;
					}
					else if (t is Building_Door door && RM_FlowDoorRules.IsFlowDoor(door))
					{
						HoldOpenRef(door) = on;
						if (on && !door.Open)
						{
							door.StartManualOpenBy(null);
						}
						lastDoors++;
					}
				}
			}
		}

		private string Schedule()
		{
			string s = mode == RM_MapControlMath.TimerByPeriod
				? "on for " + onHours.ToString("0.#", CultureInfo.InvariantCulture) + " h of every "
					+ periodHours.ToString("0.#", CultureInfo.InvariantCulture) + " h"
				: (startHour == endHour ? "on all day" : "on from " + startHour + ":00 to " + endHour + ":00");
			return s + (invert ? " (inverted: off then, on otherwise)" : "");
		}

		protected override void AppendInspect(StringBuilder sb, RM_MapComponent_Excavation ex)
		{
			sb.AppendLine("Timer: " + Schedule() + ", radius " + radius.ToString("0.#", CultureInfo.InvariantCulture));
			sb.Append(decided ? "Now " + (lastOn ? "ON" : "OFF") + ": " + lastControls + " control(s), " + lastDoors + " flow door(s) linked"
				: "Not run yet (it switches on the next flow pulse).");
		}

		protected override IEnumerable<Gizmo> ControlGizmos()
		{
			yield return new Command_Action
			{
				defaultLabel = "Schedule...",
				defaultDesc = "Now: " + Schedule() + ".",
				icon = def.uiIcon,
				action = () =>
				{
					List<FloatMenuOption> opts = new List<FloatMenuOption>();
					int[][] hours = { new[] { 6, 18 }, new[] { 18, 6 }, new[] { 5, 8 }, new[] { 20, 23 }, new[] { 0, 0 } };
					foreach (int[] h in hours)
					{
						int a = h[0], b = h[1];
						opts.Add(new FloatMenuOption(a == b ? "By hours: all day" : "By hours: " + a + ":00 to " + b + ":00", () =>
						{
							mode = RM_MapControlMath.TimerByHours;
							startHour = a;
							endHour = b;
						}));
					}
					float[][] periods = { new[] { 1f, 12.4f }, new[] { 2f, 6f }, new[] { 6f, 24f }, new[] { 24f, 72f } };
					foreach (float[] p in periods)
					{
						float on = p[0], per = p[1];
						opts.Add(new FloatMenuOption("By period: " + on + " h on every " + per + " h", () =>
						{
							mode = RM_MapControlMath.TimerByPeriod;
							onHours = on;
							periodHours = per;
						}));
					}
					Find.WindowStack.Add(new FloatMenu(opts));
				},
			};
			yield return new Command_Toggle
			{
				defaultLabel = "Invert",
				defaultDesc = "Swap on and off.",
				icon = def.uiIcon,
				isActive = () => invert,
				toggleAction = () => invert = !invert,
			};
			yield return RadiusGizmo("the controls and flow doors it switches", () => radius, v => radius = v);
		}

		public override string StateLine()
		{
			return "timer " + ThingID + " at " + Position.x + "," + Position.z + " active=" + active + " mode="
				+ (mode == RM_MapControlMath.TimerByPeriod ? "period" : "hours") + " start=" + startHour + " end=" + endHour
				+ " period=" + periodHours.ToString("0.##", CultureInfo.InvariantCulture)
				+ " on=" + onHours.ToString("0.##", CultureInfo.InvariantCulture) + " invert=" + invert
				+ " radius=" + radius.ToString("0.#", CultureInfo.InvariantCulture)
				+ " now=" + (decided ? (lastOn ? "ON" : "OFF") : "unset") + " controls=" + lastControls + " doors=" + lastDoors;
		}

		public override void ExposeData()
		{
			base.ExposeData();
			Scribe_Values.Look(ref mode, "RM_timerMode", RM_MapControlMath.TimerByHours);
			Scribe_Values.Look(ref startHour, "RM_timerStart", 6);
			Scribe_Values.Look(ref endHour, "RM_timerEnd", 18);
			Scribe_Values.Look(ref periodHours, "RM_timerPeriod", 24f);
			Scribe_Values.Look(ref onHours, "RM_timerOnHours", 6f);
			Scribe_Values.Look(ref invert, "RM_timerInvert", false);
			Scribe_Values.Look(ref radius, "RM_timerRadius", 5f);
		}
	}
}
