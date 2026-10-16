using System.Collections.Generic;
using System.Globalization;
using System.Text;
using LudeonTK;
using RimWorld;
using Verse;

namespace RimMandrake.FlowWorks.MapControls
{
	/// <summary>FLOW_SOURCE_SINK_BUILD_TAPS_FOR_MAPMAKERS: the map controls' pulse driver, their bridge surface
	/// (jawa/static_call; review_map.py and proofs place and set them with it) and their debug actions.</summary>
	public static class RM_MapControls
	{
		private static List<ThingDef> controlDefs;
		private static readonly List<Thing> scratch = new List<Thing>();

		/// <summary>Every ThingDef whose class is a map control (found once; a new control needs no registration here).</summary>
		public static List<ThingDef> ControlDefs
		{
			get
			{
				if (controlDefs == null)
				{
					controlDefs = new List<ThingDef>();
					foreach (ThingDef d in DefDatabase<ThingDef>.AllDefsListForReading)
					{
						if (d.thingClass != null && typeof(Building_RM_MapControl).IsAssignableFrom(d.thingClass))
						{
							controlDefs.Add(d);
						}
					}
				}
				return controlDefs;
			}
		}

		/// <summary>Called by RM_MapComponent_Excavation.DoPulse after rain, before the kernel measures the pulse.</summary>
		public static void PulseAll(Map map, RM_MapComponent_Excavation ex)
		{
			if (!RM_MapControlSettings.mapControlsEnabled || map == null || ex == null)
			{
				return;
			}
			List<ThingDef> defs = ControlDefs;
			for (int d = 0; d < defs.Count; d++)
			{
				List<Thing> things = map.listerThings.ThingsOfDef(defs[d]);
				if (things.Count == 0)
				{
					continue;
				}
				scratch.Clear();
				scratch.AddRange(things);
				for (int i = 0; i < scratch.Count; i++)
				{
					if (scratch[i] is Building_RM_MapControl mc && mc.Spawned && mc.active)
					{
						mc.FlowPulse(ex);
					}
				}
			}
			scratch.Clear();
		}

		private static IEnumerable<Building_RM_MapControl> All(Map map)
		{
			foreach (ThingDef d in ControlDefs)
			{
				foreach (Thing t in map.listerThings.ThingsOfDef(d))
				{
					if (t is Building_RM_MapControl mc)
					{
						yield return mc;
					}
				}
			}
		}

		// ── bridge surface (jawa/static_call, args '|'-separated) ─────────────

		/// <summary>Place a flow source on the current map. fluid = a FluidDef defName (empty = the map's default liquid);
		/// rate in levels per pulse. "OK &lt;ThingID&gt; ..." or "REFUSED: why".</summary>
		public static string PlaceSource(IntVec3 cell, string fluid, float ratePerPulse)
		{
			FluidDef f = null;
			if (!fluid.NullOrEmpty() && (f = DefDatabase<FluidDef>.GetNamedSilentFail(fluid)) == null)
			{
				return "REFUSED: no FluidDef named '" + fluid + "'";
			}
			if (!Spawn(DefDatabase<ThingDef>.GetNamedSilentFail("RM_FlowSource"), cell, out Thing t, out string why))
			{
				return why;
			}
			Building_RM_FlowSource s = (Building_RM_FlowSource)t;
			if (f != null)
			{
				s.fluid = f;
			}
			s.ratePerPulse = RM_MapControlMath.ClampRate(ratePerPulse);
			return "OK " + s.StateLine();
		}

		/// <summary>Place a flow sink on the current map. filter = a FluidDef defName, or empty/"any" for any liquid;
		/// ratePerPulse &lt; 0 = unlimited.</summary>
		public static string PlaceSink(IntVec3 cell, string filter, float ratePerPulse)
		{
			FluidDef f = null;
			if (!filter.NullOrEmpty() && filter != "any" && (f = DefDatabase<FluidDef>.GetNamedSilentFail(filter)) == null)
			{
				return "REFUSED: no FluidDef named '" + filter + "'";
			}
			if (!Spawn(DefDatabase<ThingDef>.GetNamedSilentFail("RM_FlowSink"), cell, out Thing t, out string why))
			{
				return why;
			}
			Building_RM_FlowSink s = (Building_RM_FlowSink)t;
			s.filter = f;
			s.unlimited = ratePerPulse < 0f;
			s.ratePerPulse = s.unlimited ? 1f : RM_MapControlMath.ClampRate(ratePerPulse);
			return "OK " + s.StateLine();
		}

		/// <summary>Set a placed control: fluid (source: a defName; sink: a defName or "any"; empty = unchanged), rate
		/// (levels per pulse; a sink below 0 = unlimited), on/off.</summary>
		public static string Set(Thing control, string fluid, float ratePerPulse, bool on)
		{
			if (!(control is Building_RM_MapControl mc))
			{
				return "REFUSED: " + (control?.ThingID ?? "null") + " is not a FlowWorks map control";
			}
			FluidDef f = null;
			if (!fluid.NullOrEmpty() && fluid != "any" && (f = DefDatabase<FluidDef>.GetNamedSilentFail(fluid)) == null)
			{
				return "REFUSED: no FluidDef named '" + fluid + "'";
			}
			mc.active = on;
			if (mc is Building_RM_FlowSource src)
			{
				if (f != null)
				{
					src.fluid = f;
				}
				src.ratePerPulse = RM_MapControlMath.ClampRate(ratePerPulse);
			}
			else if (mc is Building_RM_FlowSink sink)
			{
				if (fluid == "any")
				{
					sink.filter = null;
				}
				else if (f != null)
				{
					sink.filter = f;
				}
				sink.unlimited = ratePerPulse < 0f;
				if (!sink.unlimited)
				{
					sink.ratePerPulse = RM_MapControlMath.ClampRate(ratePerPulse);
				}
			}
			return "OK " + mc.StateLine();
		}

		/// <summary>Remove a placed control.</summary>
		public static string Remove(Thing control)
		{
			if (!(control is Building_RM_MapControl mc))
			{
				return "REFUSED: not a FlowWorks map control";
			}
			string line = mc.StateLine();
			mc.Destroy(DestroyMode.Vanish);
			return "OK removed " + line;
		}

		/// <summary>Every map control on the current map, one line each, then the ledger's map-control totals.</summary>
		public static string Report()
		{
			Map map = Find.CurrentMap;
			if (map == null)
			{
				return "REFUSED: no current map";
			}
			StringBuilder sb = new StringBuilder();
			int n = 0;
			foreach (Building_RM_MapControl mc in All(map))
			{
				sb.Append(mc.StateLine()).Append('\n');
				n++;
			}
			RM_MapComponent_Excavation ex = map.GetComponent<RM_MapComponent_Excavation>();
			sb.Append("controls=" + n + " enabled=" + RM_MapControlSettings.mapControlsEnabled
				+ " pouredTotal=" + (ex?.MapControlPouredTotal ?? 0f).ToString("F0", CultureInfo.InvariantCulture)
				+ " drainedTotal=" + (ex?.MapControlDrainedTotal ?? 0f).ToString("F0", CultureInfo.InvariantCulture));
			return sb.ToString();
		}

		private static bool Spawn(ThingDef def, IntVec3 cell, out Thing t, out string why)
		{
			t = null;
			why = null;
			Map map = Find.CurrentMap;
			if (map == null)
			{
				why = "REFUSED: no current map";
				return false;
			}
			if (def == null)
			{
				why = "REFUSED: map control def not loaded";
				return false;
			}
			if (!cell.InBounds(map))
			{
				why = "REFUSED: " + cell + " is off the map";
				return false;
			}
			foreach (Thing other in cell.GetThingList(map))
			{
				if (other is Building_RM_MapControl)
				{
					why = "REFUSED: a map control already stands at " + cell + " (" + other.ThingID + ")";
					return false;
				}
			}
			t = GenSpawn.Spawn(ThingMaker.MakeThing(def), cell, map);
			return true;
		}

		// ── debug actions (dev mode) ──────────────────────────────────────

		private const string CAT = "RMFlowWorks";

		[DebugAction(CAT, "Place flow source...", allowedGameStates = AllowedGameStates.PlayingOnMap)]
		private static void DebugPlaceSource()
		{
			List<DebugMenuOption> list = new List<DebugMenuOption>();
			foreach (FluidDef fluid in Building_RM_MapControl.CanalFluids())
			{
				FluidDef f = fluid;
				list.Add(new DebugMenuOption(f.defName, DebugMenuOptionMode.Tool, delegate
				{
					Log.Message("[RMFlowWorksDebug] " + PlaceSource(UI.MouseCell(), f.defName, 1f));
				}));
			}
			Find.WindowStack.Add(new Dialog_DebugOptionListLister(list));
		}

		[DebugAction(CAT, "Place flow sink", allowedGameStates = AllowedGameStates.PlayingOnMap,
			actionType = DebugActionType.ToolMap)]
		private static void DebugPlaceSink()
		{
			Log.Message("[RMFlowWorksDebug] " + PlaceSink(UI.MouseCell(), "any", -1f));
		}

		[DebugAction(CAT, "Report flow sources and sinks", allowedGameStates = AllowedGameStates.PlayingOnMap)]
		private static void DebugReport()
		{
			Log.Message("[RMFlowWorksDebug] " + Report());
		}
	}
}
