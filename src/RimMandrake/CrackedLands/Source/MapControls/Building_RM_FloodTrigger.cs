using System.Collections.Generic;
using System.Text;
using RimMandrake.FlowWorks;
using RimMandrake.FlowWorks.MapControls;
using RimWorld;
using Verse;

namespace RimMandrake.CrackedLands.MapControls
{
	/// <summary>FLOOD_SOAK_MARKERS_BUILD_AIMED_AT_CANALS (owner 2026-10-16, by card, from
	/// design/RimMandrake/flowworks_map_controls_design_2026-10-16.md item 2 "Flood Seed"): a canyon-flood ENTRY aimed at a
	/// canal. The flood enters at this marker's own cell and runs along the dug channel joined to it (or, set to spill, spreads
	/// as an ordinary canyon flood from here). It fires on the map's flood clock (the chime, then the wall) or from its button,
	/// and lifts the canyon biome gate for its own flood only (RM_MapComponent_CanyonFlood.Active).
	///
	/// A FlowWorks map control (Building_RM_MapControl): the same plain marker look, no faction, dev-only buttons, saved with
	/// the map. Its work is driven by the flood clock, not the flow pulse, so FlowPulse does nothing.</summary>
	public class Building_RM_FloodTrigger : Building_RM_MapControl
	{
		/// <summary>True: the map's flood clock brings its floods in here. False: only the button fires it.</summary>
		public bool onClock = true;

		/// <summary>False (default): the water stays in the dug channel. True: an ordinary canyon flood seeded here.</summary>
		public bool spill;

		/// <summary>Most cells one flood takes; 0 = the map's canyon-flood size (RM_FloodKernel.TargetCells).</summary>
		public int maxCells;

		public static readonly int[] CapPresets = { 0, 20, 50, 100, 200, 400 };

		public override void FlowPulse(RM_MapComponent_Excavation ex)
		{
			// The flood clock (RM_MapComponent_CanyonFlood) drives a trigger; the flow pulse has nothing for it to do.
		}

		private RM_MapComponent_CanyonFlood Flood => Map?.GetComponent<RM_MapComponent_CanyonFlood>();

		public string Fire(bool warn)
		{
			if (!active)
			{
				return "REFUSED: this flood trigger is switched off";
			}
			RM_MapComponent_CanyonFlood f = Flood;
			return f == null ? "REFUSED: no canyon flood component on this map" : f.FireTrigger(Position, warn);
		}

		private string CapLabel(int cap)
		{
			return cap > 0 ? cap + " cells" : "the map's flood size (" + RM_FloodKernel.TargetCells(Map != null ? Map.Area : 62500) + " cells)";
		}

		protected override void AppendInspect(StringBuilder sb, RM_MapComponent_Excavation ex)
		{
			if (!RM_CrackedLandsSettings.floodTriggersEnabled)
			{
				sb.AppendLine("Flood triggers are switched off in Mod Settings (Cracked Lands): starts nothing.");
			}
			else if (!RM_CrackedLandsSettings.floodCycleEnabled)
			{
				sb.AppendLine("The flood cycle is switched off in Mod Settings (Cracked Lands): starts nothing.");
			}
			sb.AppendLine("Canyon flood entry: " + (onClock ? "on the flood clock and its button" : "its button only")
				+ "; " + (spill ? "spills over the ground from here" : "runs along the dug channel only")
				+ ", up to " + CapLabel(maxCells) + ".");
			RM_MapComponent_CanyonFlood f = Flood;
			if (f != null && f.AimedAt == Position && f.Phase != FloodPhase.Dry)
			{
				sb.AppendLine(f.Phase == FloodPhase.Flooding ? "The flood is running in here now." : "A flood is coming in here.");
			}
		}

		protected override IEnumerable<Gizmo> ControlGizmos()
		{
			yield return new Command_Action
			{
				defaultLabel = "Flood now",
				defaultDesc = "Bring the canyon flood in here now: the wall of water enters at this marker and runs along the dug "
					+ "channel beside it, then recedes after the flood's duration.",
				icon = def.uiIcon,
				action = () => Messages.Message("Flood trigger: " + Fire(false), new TargetInfo(Position, Map), MessageTypeDefOf.SilentInput, false),
			};
			yield return new Command_Action
			{
				defaultLabel = "Flood after warning",
				defaultDesc = "Start the whole warning from the next tick (the signs, the staged chimes), then the wall of water here.",
				icon = def.uiIcon,
				action = () => Messages.Message("Flood trigger: " + Fire(true), new TargetInfo(Position, Map), MessageTypeDefOf.SilentInput, false),
			};
			yield return new Command_Toggle
			{
				defaultLabel = "On the flood clock",
				defaultDesc = "On: the map's flood clock brings its floods in here (on any biome). Off: only the buttons fire it.",
				icon = def.uiIcon,
				isActive = () => onClock,
				toggleAction = () => onClock = !onClock,
			};
			yield return new Command_Toggle
			{
				defaultLabel = "Spill",
				defaultDesc = "Off: the water stays in the dug channel (no ground is flooded). On: an ordinary canyon flood spreads "
					+ "over open ground from here, channels included.",
				icon = def.uiIcon,
				isActive = () => spill,
				toggleAction = () => spill = !spill,
			};
			yield return new Command_Action
			{
				defaultLabel = "Size...",
				defaultDesc = "The most cells one flood from here takes. Now: " + CapLabel(maxCells) + ".",
				icon = def.uiIcon,
				action = () =>
				{
					List<FloatMenuOption> opts = new List<FloatMenuOption>();
					foreach (int c in CapPresets)
					{
						int v = c;
						opts.Add(new FloatMenuOption(CapLabel(v), () => maxCells = v));
					}
					Find.WindowStack.Add(new FloatMenu(opts));
				},
			};
		}

		public override string StateLine()
		{
			return def.defName + " " + ThingID + " at " + Position.x + "," + Position.z + " on=" + active + " clock=" + onClock
				+ " spill=" + spill + " cap=" + maxCells
				// the canal-only footprint is deterministic; a spill footprint rolls Rand, so a report never draws one
				+ " reach=" + (spill ? "spill" : (Flood?.AimedCells(Position).Count ?? -1).ToString());
		}

		public override void ExposeData()
		{
			base.ExposeData();
			Scribe_Values.Look(ref onClock, "RM_floodTriggerOnClock", true);
			Scribe_Values.Look(ref spill, "RM_floodTriggerSpill", false);
			Scribe_Values.Look(ref maxCells, "RM_floodTriggerMaxCells", 0);
		}
	}
}
