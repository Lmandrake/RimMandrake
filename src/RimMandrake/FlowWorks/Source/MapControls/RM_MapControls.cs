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

		// ── FLOW_CONTROLS_BUILD_EIGHT_QUIET_PEBBLES: hooks the engine reads ──────────────

		private static Map edgeCacheMap;
		private static int edgeCacheTick = -1;
		private static int[] edgeCacheModes;
		private static Building_RM_EdgeSetter edgeCacheRuler;

		private static List<Thing> ThingsOf(Map map, string defName)
		{
			ThingDef d = DefDatabase<ThingDef>.GetNamedSilentFail(defName);
			return d == null || map == null ? null : map.listerThings.ThingsOfDef(d);
		}

		/// <summary>The map-edge setter that rules <paramref name="map"/>: the first spawned, switched-on one (null when
		/// none, or the map controls are switched off in Mod Settings).</summary>
		public static Building_RM_EdgeSetter RulingEdgeSetter(Map map)
		{
			RefreshEdgeCache(map);
			return edgeCacheRuler;
		}

		/// <summary>The per-edge modes (N, E, S, W; RM_MapControlMath.EdgeAuto/Sealed/Drain) in force on
		/// <paramref name="map"/>, or null when every edge is automatic. Cached per map per tick: IsSinkCell asks per cell.</summary>
		public static int[] EdgeModes(Map map)
		{
			RefreshEdgeCache(map);
			return edgeCacheModes;
		}

		/// <summary>Does any edge of <paramref name="map"/> drain by the setter (the kernel's edge-sink gate opens for it
		/// even with the automatic edge sinks off)?</summary>
		public static bool AnyDrainEdge(Map map)
		{
			int[] m = EdgeModes(map);
			if (m == null)
			{
				return false;
			}
			for (int i = 0; i < m.Length; i++)
			{
				if (m[i] == RM_MapControlMath.EdgeDrain)
				{
					return true;
				}
			}
			return false;
		}

		private static void RefreshEdgeCache(Map map)
		{
			int now = Find.TickManager?.TicksGame ?? 0;
			if (map == edgeCacheMap && now == edgeCacheTick)
			{
				return;
			}
			edgeCacheMap = map;
			edgeCacheTick = now;
			edgeCacheModes = null;
			edgeCacheRuler = null;
			if (!RM_MapControlSettings.mapControlsEnabled)
			{
				return;
			}
			List<Thing> setters = ThingsOf(map, "RM_MapEdgeSetter");
			if (setters == null)
			{
				return;
			}
			for (int i = 0; i < setters.Count; i++)
			{
				if (setters[i] is Building_RM_EdgeSetter es && es.Spawned && es.active)
				{
					edgeCacheRuler = es;
					for (int k = 0; k < 4; k++)
					{
						if (es.modes[k] != RM_MapControlMath.EdgeAuto)
						{
							edgeCacheModes = (int[])es.modes.Clone();
							break;
						}
					}
					return;
				}
			}
		}

		/// <summary>Forget the cached edge rule (a gizmo or the bridge changed it this tick).</summary>
		public static void EdgeRuleChanged()
		{
			edgeCacheTick = -1;
		}

		/// <summary>Is a dug square at <paramref name="c"/> a map-edge sink, with the setter's rule on top of the automatic
		/// one (<paramref name="autoRule"/>: the automatic edge sinks are on)? Caller has checked the square is dug.</summary>
		public static bool EdgeSinkAt(Map map, IntVec3 c, bool autoRule)
		{
			int w = GenGrid.NoBuildEdgeWidth;
			bool n = c.z >= map.Size.z - w, e = c.x >= map.Size.x - w, s = c.z < w, west = c.x < w;
			return RM_MapControlMath.EdgeSink(EdgeModes(map), n, e, s, west, autoRule);
		}

		/// <summary>A body footprint's edge contact under the setter: <paramref name="touchesOpenEdge"/> replaces the
		/// automatic "touches the edge" and <paramref name="forceLimitless"/> is a drain edge touched. Only called when
		/// <see cref="EdgeModes"/> is not null.</summary>
		public static void BodyEdgeContact(Map map, int[] modes, List<int> footprint, out bool touchesOpenEdge, out bool forceLimitless)
		{
			int sx = map.Size.x, sz = map.Size.z;
			bool tn = false, te = false, ts = false, tw = false;
			for (int i = 0; i < footprint.Count; i++)
			{
				int x = footprint[i] % sx, z = footprint[i] / sx;
				tn |= z == sz - 1;
				ts |= z == 0;
				te |= x == sx - 1;
				tw |= x == 0;
			}
			RM_MapControlMath.BodyEdges(modes, tn, te, ts, tw, out touchesOpenEdge, out forceLimitless);
		}

		/// <summary>Is any current painter placed on <paramref name="map"/>?</summary>
		public static bool AnyPainter(Map map)
		{
			List<Thing> ps = ThingsOf(map, "RM_CurrentPainter");
			return ps != null && ps.Count > 0;
		}

		/// <summary>Paint every switched-on current painter into the overlay (RM_MapComponent_RiverCurrent). Returns the
		/// painted water squares. Nothing when the map controls are switched off in Mod Settings.</summary>
		public static int PaintCurrent(Map map, sbyte[] dir, sbyte[] lane)
		{
			if (!RM_MapControlSettings.mapControlsEnabled)
			{
				return 0;
			}
			List<Thing> ps = ThingsOf(map, "RM_CurrentPainter");
			if (ps == null)
			{
				return 0;
			}
			for (int i = 0; i < ps.Count; i++)
			{
				if (ps[i] is Building_RM_CurrentPainter p && p.Spawned && p.active)
				{
					p.PaintInto(dir, lane);
				}
			}
			int n = 0;
			for (int i = 0; i < dir.Length; i++)
			{
				if (dir[i] >= 0)
				{
					n++;
				}
			}
			return n;
		}

		/// <summary>Called by RM_LiquidHeat.Tick after its own push, each 250-tick interval while liquid heat is on.</summary>
		public static void HeatAll(Map map, RM_MapComponent_Excavation ex, float strength)
		{
			if (!RM_MapControlSettings.mapControlsEnabled || map == null || ex == null)
			{
				return;
			}
			List<Thing> ts = ThingsOf(map, "RM_LiquidThermostat");
			if (ts == null || ts.Count == 0)
			{
				return;
			}
			scratch.Clear();
			scratch.AddRange(ts);
			for (int i = 0; i < scratch.Count; i++)
			{
				if (scratch[i] is Building_RM_LiquidThermostat t && t.Spawned && t.active)
				{
					t.HeatInterval(ex, strength);
				}
			}
			scratch.Clear();
		}

		// ── FLOW_CONTROLS_BUILD_EIGHT_QUIET_PEBBLES: bridge surface ──────────────────────────────

		private static FluidDef FluidOrNull(string name, out string why)
		{
			why = null;
			if (name.NullOrEmpty())
			{
				return null;
			}
			FluidDef f = DefDatabase<FluidDef>.GetNamedSilentFail(name);
			if (f == null)
			{
				why = "REFUSED: no FluidDef named '" + name + "'";
			}
			return f;
		}

		/// <summary>Place a flow meter. "OK meter ..." with its first reading.</summary>
		public static string PlaceMeter(IntVec3 cell)
		{
			if (!Spawn(DefDatabase<ThingDef>.GetNamedSilentFail("RM_FlowMeter"), cell, out Thing t, out string why))
			{
				return why;
			}
			return ReadMeter(t);
		}

		/// <summary>A flow meter's reading, taken now.</summary>
		public static string ReadMeter(Thing meter)
		{
			if (!(meter is Building_RM_FlowMeter m))
			{
				return "REFUSED: " + (meter?.ThingID ?? "null") + " is not a flow meter";
			}
			RM_MapComponent_Excavation ex = m.Map?.GetComponent<RM_MapComponent_Excavation>();
			if (ex != null)
			{
				m.Read(ex);
			}
			return "OK " + m.StateLine();
		}

		/// <summary>Place a level holder: fluid defName (empty = the map's default liquid), setpoint 0..1, rate levels/pulse.</summary>
		public static string PlaceLevelHolder(IntVec3 cell, string fluid, float setpoint, float ratePerPulse)
		{
			FluidDef f = FluidOrNull(fluid, out string bad);
			if (bad != null)
			{
				return bad;
			}
			if (!Spawn(DefDatabase<ThingDef>.GetNamedSilentFail("RM_LevelHolder"), cell, out Thing t, out string why))
			{
				return why;
			}
			return SetLevelHolder(t, f?.defName ?? "", setpoint, ratePerPulse, true);
		}

		/// <summary>Set a level holder (fluid empty = unchanged).</summary>
		public static string SetLevelHolder(Thing holder, string fluid, float setpoint, float ratePerPulse, bool on)
		{
			if (!(holder is Building_RM_LevelHolder h))
			{
				return "REFUSED: " + (holder?.ThingID ?? "null") + " is not a level holder";
			}
			FluidDef f = FluidOrNull(fluid, out string bad);
			if (bad != null)
			{
				return bad;
			}
			if (f != null)
			{
				h.fluid = f;
			}
			h.setpoint = float.IsNaN(setpoint) ? 0.5f : UnityEngine.Mathf.Clamp01(setpoint);
			h.ratePerPulse = RM_MapControlMath.ClampRate(ratePerPulse);
			h.active = on;
			return "OK " + h.StateLine();
		}

		/// <summary>Place a timer switch. mode "hours" (a = start hour, b = end hour) or "period" (a = hours on, b = period
		/// hours); radius in squares.</summary>
		public static string PlaceTimer(IntVec3 cell, string mode, float a, float b, bool invert, float radius)
		{
			if (!Spawn(DefDatabase<ThingDef>.GetNamedSilentFail("RM_TimerSwitch"), cell, out Thing t, out string why))
			{
				return why;
			}
			return SetTimer(t, mode, a, b, invert, radius, true);
		}

		public static string SetTimer(Thing timer, string mode, float a, float b, bool invert, float radius, bool on)
		{
			if (!(timer is Building_RM_TimerSwitch ts))
			{
				return "REFUSED: " + (timer?.ThingID ?? "null") + " is not a timer switch";
			}
			if (mode == "period")
			{
				ts.mode = RM_MapControlMath.TimerByPeriod;
				ts.onHours = UnityEngine.Mathf.Max(0f, a);
				ts.periodHours = UnityEngine.Mathf.Max(0.1f, b);
			}
			else if (mode == "hours")
			{
				ts.mode = RM_MapControlMath.TimerByHours;
				ts.startHour = ((int)a % 24 + 24) % 24;
				ts.endHour = ((int)b % 24 + 24) % 24;
			}
			else
			{
				return "REFUSED: mode must be 'hours' or 'period'";
			}
			ts.invert = invert;
			ts.radius = UnityEngine.Mathf.Clamp(radius, 1f, GenRadial.MaxRadialPatternRadius - 1f);
			ts.active = on;
			return "OK " + ts.StateLine();
		}

		/// <summary>Run a timer's decision now (as its next pulse would) and apply it.</summary>
		public static string PulseTimer(Thing timer)
		{
			if (!(timer is Building_RM_TimerSwitch ts))
			{
				return "REFUSED: not a timer switch";
			}
			ts.Apply(ts.OnNow());
			return "OK " + ts.StateLine();
		}

		/// <summary>Place a map-edge setter. modes = four letters N E S W, each a (automatic), s (sealed) or d (drain),
		/// e.g. "ssda".</summary>
		public static string PlaceEdgeSetter(IntVec3 cell, string modes)
		{
			if (!Spawn(DefDatabase<ThingDef>.GetNamedSilentFail("RM_MapEdgeSetter"), cell, out Thing t, out string why))
			{
				return why;
			}
			return SetEdges(t, modes, true);
		}

		public static string SetEdges(Thing setter, string modes, bool on)
		{
			if (!(setter is Building_RM_EdgeSetter es))
			{
				return "REFUSED: " + (setter?.ThingID ?? "null") + " is not a map-edge setter";
			}
			if (modes == null || modes.Length != 4)
			{
				return "REFUSED: modes must be four letters (N E S W), each a, s or d";
			}
			int[] m = new int[4];
			for (int i = 0; i < 4; i++)
			{
				char ch = char.ToLowerInvariant(modes[i]);
				m[i] = ch == 's' ? RM_MapControlMath.EdgeSealed : (ch == 'd' ? RM_MapControlMath.EdgeDrain : (ch == 'a' ? RM_MapControlMath.EdgeAuto : -1));
				if (m[i] < 0)
				{
					return "REFUSED: '" + modes[i] + "' is not a, s or d";
				}
			}
			es.modes = m;
			es.active = on;
			EdgeRuleChanged();
			return "OK " + es.StateLine();
		}

		/// <summary>Is the dug square at <paramref name="cell"/> a map-edge sink now (the rule the kernel drains by)?</summary>
		public static string EdgeSinkReport(IntVec3 cell)
		{
			Map map = Find.CurrentMap;
			RM_MapComponent_Excavation ex = map?.GetComponent<RM_MapComponent_Excavation>();
			if (ex == null)
			{
				return "REFUSED: no current map";
			}
			int[] m = EdgeModes(map);
			return "OK cell=" + cell.x + "," + cell.z + " dug=" + ex.IsExcavated(cell) + " sink=" + ex.IsSinkCell(cell)
				+ " modes=" + (m == null ? "auto" : string.Join(",", m)) + " autoEdgeSinks=" + RimMandrakeFlowWorksSettings.edgeSinksEnabled;
		}

		/// <summary>Place a current painter: direction 0..7 (0 east, counter-clockwise: 2 north, 4 west, 6 south), fast lane
		/// or slow, radius in squares.</summary>
		public static string PlacePainter(IntVec3 cell, int direction, bool fast, float radius)
		{
			if (!Spawn(DefDatabase<ThingDef>.GetNamedSilentFail("RM_CurrentPainter"), cell, out Thing t, out string why))
			{
				return why;
			}
			return SetPainter(t, direction, fast, radius, true);
		}

		public static string SetPainter(Thing painter, int direction, bool fast, float radius, bool on)
		{
			if (!(painter is Building_RM_CurrentPainter p))
			{
				return "REFUSED: " + (painter?.ThingID ?? "null") + " is not a current painter";
			}
			p.direction = ((direction % 8) + 8) % 8;
			p.fast = fast;
			p.radius = UnityEngine.Mathf.Clamp(radius, 1f, GenRadial.MaxRadialPatternRadius - 1f);
			p.active = on;
			p.Changed();
			return "OK " + p.StateLine();
		}

		/// <summary>The surface current at a cell: direction, lane, painted or river. "OK cell=x,z dir=.. lane=.."</summary>
		public static string CurrentAt(IntVec3 cell)
		{
			Map map = Find.CurrentMap;
			Rivers.RM_MapComponent_RiverCurrent cur = map?.GetComponent<Rivers.RM_MapComponent_RiverCurrent>();
			if (cur == null)
			{
				return "REFUSED: no current component on the current map";
			}
			return "OK cell=" + cell.x + "," + cell.z + " dir=" + cur.FlowDirAt(cell) + " lane=" + cur.LaneAt(cell)
				+ " painted=" + cur.PaintedCellCount + " currentOn=" + Rivers.RM_RiversSettings.CurrentActive;
		}

		/// <summary>Place a liquid thermostat: target in C, radius in squares.</summary>
		public static string PlaceThermostat(IntVec3 cell, float targetC, float radius)
		{
			if (!Spawn(DefDatabase<ThingDef>.GetNamedSilentFail("RM_LiquidThermostat"), cell, out Thing t, out string why))
			{
				return why;
			}
			return SetThermostat(t, targetC, radius, true);
		}

		public static string SetThermostat(Thing thermostat, float targetC, float radius, bool on)
		{
			if (!(thermostat is Building_RM_LiquidThermostat th))
			{
				return "REFUSED: " + (thermostat?.ThingID ?? "null") + " is not a liquid thermostat";
			}
			th.targetC = float.IsNaN(targetC) ? 21f : UnityEngine.Mathf.Clamp(targetC, -100f, 200f);
			th.radius = UnityEngine.Mathf.Clamp(radius, 1f, GenRadial.MaxRadialPatternRadius - 1f);
			th.active = on;
			return "OK " + th.StateLine();
		}

		/// <summary>Run one heat interval of a thermostat now (as RM_LiquidHeat's next interval would).</summary>
		public static string HeatNow(Thing thermostat)
		{
			if (!(thermostat is Building_RM_LiquidThermostat th))
			{
				return "REFUSED: not a liquid thermostat";
			}
			RM_MapComponent_Excavation ex = th.Map?.GetComponent<RM_MapComponent_Excavation>();
			if (ex == null)
			{
				return "REFUSED: no excavation component";
			}
			th.HeatInterval(ex, RimMandrakeFlowWorksSettings.liquidHeatStrength);
			return "OK " + th.StateLine();
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

		[DebugAction(CAT, "Place flow meter", allowedGameStates = AllowedGameStates.PlayingOnMap,
			actionType = DebugActionType.ToolMap)]
		private static void DebugPlaceMeter()
		{
			Log.Message("[RMFlowWorksDebug] " + PlaceMeter(UI.MouseCell()));
		}

		[DebugAction(CAT, "Place level holder (50%)", allowedGameStates = AllowedGameStates.PlayingOnMap,
			actionType = DebugActionType.ToolMap)]
		private static void DebugPlaceLevelHolder()
		{
			Log.Message("[RMFlowWorksDebug] " + PlaceLevelHolder(UI.MouseCell(), "", 0.5f, 1f));
		}

		[DebugAction(CAT, "Place timer switch (6:00-18:00)", allowedGameStates = AllowedGameStates.PlayingOnMap,
			actionType = DebugActionType.ToolMap)]
		private static void DebugPlaceTimer()
		{
			Log.Message("[RMFlowWorksDebug] " + PlaceTimer(UI.MouseCell(), "hours", 6f, 18f, false, 5f));
		}

		[DebugAction(CAT, "Place map-edge setter", allowedGameStates = AllowedGameStates.PlayingOnMap,
			actionType = DebugActionType.ToolMap)]
		private static void DebugPlaceEdgeSetter()
		{
			Log.Message("[RMFlowWorksDebug] " + PlaceEdgeSetter(UI.MouseCell(), "aaaa"));
		}

		[DebugAction(CAT, "Place current painter...", allowedGameStates = AllowedGameStates.PlayingOnMap)]
		private static void DebugPlacePainter()
		{
			List<DebugMenuOption> list = new List<DebugMenuOption>();
			for (int d = 0; d < 8; d++)
			{
				int dir = d;
				list.Add(new DebugMenuOption("flows " + Building_RM_CurrentPainter.CompassNames[dir], DebugMenuOptionMode.Tool, delegate
				{
					Log.Message("[RMFlowWorksDebug] " + PlacePainter(UI.MouseCell(), dir, false, 3f));
				}));
			}
			Find.WindowStack.Add(new Dialog_DebugOptionListLister(list));
		}

		[DebugAction(CAT, "Place liquid thermostat...", allowedGameStates = AllowedGameStates.PlayingOnMap)]
		private static void DebugPlaceThermostat()
		{
			List<DebugMenuOption> list = new List<DebugMenuOption>();
			foreach (float t in RM_MapControlMath.ThermostatPresets)
			{
				float target = t;
				list.Add(new DebugMenuOption(target.ToString("0") + " C", DebugMenuOptionMode.Tool, delegate
				{
					Log.Message("[RMFlowWorksDebug] " + PlaceThermostat(UI.MouseCell(), target, 3f));
				}));
			}
			Find.WindowStack.Add(new Dialog_DebugOptionListLister(list));
		}

		[DebugAction(CAT, "Report map controls", allowedGameStates = AllowedGameStates.PlayingOnMap)]
		private static void DebugReport()
		{
			Log.Message("[RMFlowWorksDebug] " + Report());
		}
	}
}
