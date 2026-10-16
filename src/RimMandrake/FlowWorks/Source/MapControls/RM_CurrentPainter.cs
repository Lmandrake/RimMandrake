using System.Collections.Generic;
using System.Globalization;
using System.Text;
using RimMandrake.FlowWorks.Rivers;
using RimWorld;
using Verse;

namespace RimMandrake.FlowWorks.MapControls
{
	/// <summary>FLOW_CONTROLS_BUILD_EIGHT_QUIET_PEBBLES (owner card 2026-10-16, design §2 #4): the CURRENT PAINTER. Surface current
	/// (Rivers/RM_MapComponent_RiverCurrent) is read from vanilla's riverFlowMap, which only a generated river writes, so a
	/// hand-made channel had none. This pebble paints a current over the WATER squares within its radius: a compass
	/// direction (8 ways) and a strength (the river's two lanes: "fast" = mid-river, "slow" = river margin). Painted
	/// squares are carried exactly like a river's (the same shove, cadence, hazards, fords, weir pools and ferry ropes);
	/// a painted square overrides the river's own direction there. Only water terrain is painted: dry ground in the
	/// radius is never carried. The painted grid is derived from the placed painters (rebuilt every 250 ticks and on any
	/// change), never saved on the current component; the painter itself saves its settings.
	/// Not painted: the current's look (vanilla draws river flow only on generated rivers). Silt drift was not checked
	/// against painted squares.</summary>
	public class Building_RM_CurrentPainter : Building_RM_MapControl
	{
		public int direction;
		public bool fast;
		public float radius = 3f;

		public static readonly string[] CompassNames = { "east", "north-east", "north", "north-west", "west", "south-west", "south", "south-east" };

		public override bool WorksOnDugChannel => false;
		public override bool NeedsDepthEngine => false;
		protected override float SelectionRadius => radius;

		public int Lane => fast ? RM_RiverMath.LaneCentre : RM_RiverMath.LaneMargin;

		public override void FlowPulse(RM_MapComponent_Excavation ex)
		{
			// Nothing on the flow pulse: the current component reads painters itself.
		}

		public override void SpawnSetup(Map map, bool respawningAfterLoad)
		{
			base.SpawnSetup(map, respawningAfterLoad);
			Changed();
		}

		public override void DeSpawn(DestroyMode mode = DestroyMode.Vanish)
		{
			Map m = Map;
			base.DeSpawn(mode);
			m?.GetComponent<RM_MapComponent_RiverCurrent>()?.MarkPaintDirty();
		}

		public void Changed()
		{
			Map?.GetComponent<RM_MapComponent_RiverCurrent>()?.MarkPaintDirty();
		}

		/// <summary>Paint this painter's cells into the overlay (called by RM_MapComponent_RiverCurrent's rebuild).</summary>
		public int PaintInto(sbyte[] dir, sbyte[] lane)
		{
			int n = 0;
			foreach (IntVec3 c in CellsInRadius(radius))
			{
				TerrainDef t = c.GetTerrain(Map);
				if (t == null || !t.IsWater)
				{
					continue;
				}
				int i = Map.cellIndices.CellToIndex(c);
				dir[i] = (sbyte)direction;
				lane[i] = (sbyte)Lane;
				n++;
			}
			return n;
		}

		protected override void AppendInspect(StringBuilder sb, RM_MapComponent_Excavation ex)
		{
			sb.AppendLine("Paints a " + (fast ? "fast" : "slow") + " current flowing " + CompassNames[direction & 7]
				+ " over the water within " + radius.ToString("0.#", CultureInfo.InvariantCulture) + " squares.");
			if (!RM_RiversSettings.CurrentActive)
			{
				sb.AppendLine("River current is switched off in Mod Settings: nothing is carried.");
			}
			RM_MapComponent_RiverCurrent cur = Map.GetComponent<RM_MapComponent_RiverCurrent>();
			sb.Append("Painted water squares on this map: " + (cur?.PaintedCellCount ?? 0));
		}

		protected override IEnumerable<Gizmo> ControlGizmos()
		{
			yield return new Command_Action
			{
				defaultLabel = "Flows " + CompassNames[direction & 7],
				defaultDesc = "The direction the painted current carries things.",
				icon = def.uiIcon,
				action = () =>
				{
					List<FloatMenuOption> opts = new List<FloatMenuOption>();
					for (int d = 0; d < 8; d++)
					{
						int pick = d;
						opts.Add(new FloatMenuOption(CompassNames[pick], () => { direction = pick; Changed(); }));
					}
					Find.WindowStack.Add(new FloatMenu(opts));
				},
			};
			yield return new Command_Toggle
			{
				defaultLabel = "Fast",
				defaultDesc = "Fast = a river's mid-stream lane (quick, hazardous); off = its margin lane (slow).",
				icon = def.uiIcon,
				isActive = () => fast,
				toggleAction = () => { fast = !fast; Changed(); },
			};
			yield return RadiusGizmo("the water it paints", () => radius, v => { radius = v; Changed(); });
		}

		public override string StateLine()
		{
			return "currentpainter " + ThingID + " at " + Position.x + "," + Position.z + " active=" + active + " dir=" + direction
				+ " (" + CompassNames[direction & 7] + ") fast=" + fast + " radius=" + radius.ToString("0.#", CultureInfo.InvariantCulture)
				+ " painted=" + (Map?.GetComponent<RM_MapComponent_RiverCurrent>()?.PaintedCellCount ?? 0);
		}

		public override void ExposeData()
		{
			base.ExposeData();
			Scribe_Values.Look(ref direction, "RM_painterDir", 0);
			Scribe_Values.Look(ref fast, "RM_painterFast", false);
			Scribe_Values.Look(ref radius, "RM_painterRadius", 3f);
			if (Scribe.mode == LoadSaveMode.PostLoadInit)
			{
				direction &= 7;
			}
		}
	}
}
