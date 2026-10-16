using System.Collections.Generic;
using System.Text;
using RimWorld;
using Verse;

namespace RimMandrake.FlowWorks.MapControls
{
	/// <summary>FLOW_CONTROLS_BUILD_EIGHT_QUIET_PEBBLES (owner card 2026-10-16, design §2 #5): the MAP-EDGE SETTER. One pebble
	/// anywhere on the map sets each of the four map edges (north, east, south, west) to:
	/// - AUTOMATIC: today's rules (the edge-sink band drains when "Map-edge sinks drain" is on; a body touching the edge
	///   past the size floor is limitless);
	/// - SEALED: no off-map reservoir there: the edge band never drains, and a body touching only sealed edges is LIMITED
	///   (finite: it can be pumped dry);
	/// - DRAIN: the edge band always drains (even with the automatic edge sinks switched off), and a body touching it is
	///   limitless whatever its size.
	/// Read by RM_MapComponent_Excavation.IsSinkCell (and the kernel's edge-sink gate) and RM_LiquidStock's body
	/// classification through <see cref="RM_MapControls.EdgeModes"/>. Body classification is sticky (ruling 16): the
	/// setter rules bodies first met AFTER it is set, so a map maker places it before the water is touched.
	/// More than one on a map: the first found rules, the rest are reported as idle.</summary>
	public class Building_RM_EdgeSetter : Building_RM_MapControl
	{
		public int[] modes = { RM_MapControlMath.EdgeAuto, RM_MapControlMath.EdgeAuto, RM_MapControlMath.EdgeAuto, RM_MapControlMath.EdgeAuto };

		public static readonly string[] EdgeNames = { "north", "east", "south", "west" };

		public override bool WorksOnDugChannel => false;
		public override bool TimerSwitchable => false;

		public override void SpawnSetup(Map map, bool respawningAfterLoad)
		{
			base.SpawnSetup(map, respawningAfterLoad);
			RM_MapControls.EdgeRuleChanged();
		}

		public override void DeSpawn(DestroyMode mode = DestroyMode.Vanish)
		{
			base.DeSpawn(mode);
			RM_MapControls.EdgeRuleChanged();
		}

		protected override void OnActiveChanged()
		{
			RM_MapControls.EdgeRuleChanged();
		}

		public override void FlowPulse(RM_MapComponent_Excavation ex)
		{
			// Nothing to do on the pulse: the rule is read where the edge matters (RM_MapControls.EdgeModes).
		}

		public string ModesLine()
		{
			StringBuilder sb = new StringBuilder();
			for (int i = 0; i < 4; i++)
			{
				if (i > 0)
				{
					sb.Append(", ");
				}
				sb.Append(EdgeNames[i]).Append(' ').Append(RM_MapControlMath.EdgeModeLabel(modes[i]));
			}
			return sb.ToString();
		}

		protected override void AppendInspect(StringBuilder sb, RM_MapComponent_Excavation ex)
		{
			sb.AppendLine("Map edges: " + ModesLine() + ".");
			Building_RM_EdgeSetter ruling = RM_MapControls.RulingEdgeSetter(Map);
			if (ruling != null && ruling != this)
			{
				sb.AppendLine("Idle: another map-edge setter (" + ruling.ThingID + ") rules this map.");
			}
			sb.Append("Rules the edge sinks now; a liquid body is ruled when it is first met (bodies already met keep their class).");
		}

		protected override IEnumerable<Gizmo> ControlGizmos()
		{
			for (int i = 0; i < 4; i++)
			{
				int edge = i;
				yield return new Command_Action
				{
					defaultLabel = EdgeNames[edge] + ": " + RM_MapControlMath.EdgeModeLabel(modes[edge]),
					defaultDesc = "Set the " + EdgeNames[edge] + " map edge: automatic (today's rules), sealed (no off-map "
						+ "reservoir: nothing drains there and a body touching it is finite) or drain (the edge always drains and a "
						+ "body touching it is limitless).",
					icon = def.uiIcon,
					action = () =>
					{
						List<FloatMenuOption> opts = new List<FloatMenuOption>();
						foreach (int m in new[] { RM_MapControlMath.EdgeAuto, RM_MapControlMath.EdgeSealed, RM_MapControlMath.EdgeDrain })
						{
							int pick = m;
							opts.Add(new FloatMenuOption(RM_MapControlMath.EdgeModeLabel(pick), () => { modes[edge] = pick; RM_MapControls.EdgeRuleChanged(); }));
						}
						Find.WindowStack.Add(new FloatMenu(opts));
					},
				};
			}
		}

		public override string StateLine()
		{
			return "edgesetter " + ThingID + " at " + Position.x + "," + Position.z + " active=" + active
				+ " N=" + RM_MapControlMath.EdgeModeLabel(modes[0]) + " E=" + RM_MapControlMath.EdgeModeLabel(modes[1])
				+ " S=" + RM_MapControlMath.EdgeModeLabel(modes[2]) + " W=" + RM_MapControlMath.EdgeModeLabel(modes[3])
				+ " ruling=" + (RM_MapControls.RulingEdgeSetter(Map) == this);
		}

		public override void ExposeData()
		{
			base.ExposeData();
			List<int> list = new List<int>(modes);
			Scribe_Collections.Look(ref list, "RM_edgeSetterModes", LookMode.Value);
			if (Scribe.mode == LoadSaveMode.LoadingVars || Scribe.mode == LoadSaveMode.PostLoadInit)
			{
				int[] m = { 0, 0, 0, 0 };
				for (int i = 0; list != null && i < 4 && i < list.Count; i++)
				{
					m[i] = list[i] < RM_MapControlMath.EdgeAuto || list[i] > RM_MapControlMath.EdgeDrain ? RM_MapControlMath.EdgeAuto : list[i];
				}
				modes = m;
			}
		}
	}
}
