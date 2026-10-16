using System.Collections.Generic;
using System.Text;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.FlowWorks.MapControls
{
	/// <summary>FLOW_SOURCE_SINK_BUILD_TAPS_FOR_MAPMAKERS (owner 2026-10-16: "debug-style objects ... not buildable, just dev
	/// mode placed ... a minimal appearance that can be overlooked"): the base of every FlowWorks MAP CONTROL, a plain
	/// marker a map maker places in development mode that keeps doing one job on the flow engine's pulse and saves with
	/// the map. Flow source and flow sink are the first two; the further ones in
	/// design/RimMandrake/flowworks_map_controls_design_2026-10-16.md (level holder, schedule switch ...) derive from this.
	///
	/// What a subclass gets: an on/off switch (gizmo, saved), no faction (raiders and colonists ignore it), the reach (its
	/// own square and the four beside it), and <see cref="FlowPulse"/>, called by RM_MapControls.PulseAll from
	/// RM_MapComponent_Excavation.DoPulse with rain, before the pulse's conservation ledger measures. It is called only
	/// while the depth engine runs, the master switch (RM_MapControlSettings) is on and this control is switched on.</summary>
	public abstract class Building_RM_MapControl : Building
	{
		public bool active = true;

		/// <summary>One flow pulse of this control's job.</summary>
		public abstract void FlowPulse(RM_MapComponent_Excavation ex);

		/// <summary>The control's own line(s) for the inspect pane, after the shared on/off line.</summary>
		protected abstract void AppendInspect(StringBuilder sb, RM_MapComponent_Excavation ex);

		/// <summary>The control's own gizmos, after the shared on/off switch.</summary>
		protected abstract IEnumerable<Gizmo> ControlGizmos();

		/// <summary>The bridge's one-line state (RM_MapControls.Report).</summary>
		public abstract string StateLine();

		public override void SpawnSetup(Map map, bool respawningAfterLoad)
		{
			base.SpawnSetup(map, respawningAfterLoad);
			// A map fixture belongs to nobody: dev "spawn" may hand it the player's faction, which would make it a raid target.
			if (Faction != null)
			{
				SetFaction(null);
			}
		}

		/// <summary>Its own square, then N, E, S, W (in bounds only).</summary>
		public IEnumerable<IntVec3> Reach()
		{
			yield return Position;
			for (int i = 0; i < 4; i++)
			{
				IntVec3 n = Position + GenAdj.CardinalDirections[i];
				if (n.InBounds(Map))
				{
					yield return n;
				}
			}
		}

		/// <summary>A dug square in reach that liquid may enter or leave now (not under a shut sluice).</summary>
		protected bool Open(RM_MapComponent_Excavation ex, IntVec3 c)
		{
			return ex.IsExcavated(c) && !RM_FlowDoorRules.SealsLiquid(Map.edificeGrid[c]);
		}

		protected bool AnyDugInReach(RM_MapComponent_Excavation ex)
		{
			foreach (IntVec3 c in Reach())
			{
				if (ex.IsExcavated(c))
				{
					return true;
				}
			}
			return false;
		}

		public override void ExposeData()
		{
			base.ExposeData();
			Scribe_Values.Look(ref active, "RM_mapControlActive", true);
		}

		public override IEnumerable<Gizmo> GetGizmos()
		{
			foreach (Gizmo g in base.GetGizmos())
			{
				yield return g;
			}
			// Dev-placed, dev-set: in ordinary play a map's sources and sinks cannot be retuned or removed (the inspect
			// pane still says what they do). Review 2026-10-16.
			if (!DebugSettings.ShowDevGizmos)
			{
				yield break;
			}
			yield return new Command_Toggle
			{
				defaultLabel = "On",
				defaultDesc = "Switch this " + def.label + " on or off. Off, it stays where it is and moves nothing.",
				icon = def.uiIcon,
				isActive = () => active,
				toggleAction = () => active = !active,
			};
			foreach (Gizmo g in ControlGizmos())
			{
				yield return g;
			}
			yield return new Command_Action
			{
				defaultLabel = "Remove",
				defaultDesc = "Take this " + def.label + " off the map. Liquid it already moved stays where it is.",
				icon = def.uiIcon,
				action = () => { if (!Destroyed) Destroy(DestroyMode.Vanish); },
			};
		}

		public override string GetInspectString()
		{
			StringBuilder sb = new StringBuilder();
			string b = base.GetInspectString();
			if (!b.NullOrEmpty())
			{
				sb.AppendLine(b);
			}
			RM_MapComponent_Excavation ex = Map?.GetComponent<RM_MapComponent_Excavation>();
			if (!RM_MapControlSettings.mapControlsEnabled)
			{
				sb.AppendLine("Switched off in Mod Settings (map controls): moves nothing.");
			}
			else if (!RimMandrakeFlowWorksSettings.depthEngineEnabled)
			{
				sb.AppendLine("The FlowWorks depth engine is off in Mod Settings: moves nothing.");
			}
			else if (!active)
			{
				sb.AppendLine("Off.");
			}
			if (ex != null)
			{
				if (!AnyDugInReach(ex))
				{
					sb.AppendLine("Nothing dug here or beside it: it needs a dug channel to work on.");
				}
				AppendInspect(sb, ex);
			}
			return sb.ToString().TrimEndNewlines();
		}

		/// <summary>The liquids a canal can hold: every FluidDef with a fill terrain.</summary>
		public static IEnumerable<FluidDef> CanalFluids()
		{
			foreach (FluidDef f in DefDatabase<FluidDef>.AllDefsListForReading)
			{
				if (f.floodTerrain != null)
				{
					yield return f;
				}
			}
		}

		protected static string FluidLabel(FluidDef f)
		{
			return f == null ? "any liquid" : (f.label.NullOrEmpty() ? f.defName : f.label);
		}

		protected Command_Action RateGizmo(string verb, System.Func<float> get, System.Action<float> set, bool offerUnlimited,
			System.Func<bool> unlimited, System.Action<bool> setUnlimited)
		{
			int pulse = RimMandrakeFlowWorksSettings.PulseIntervalTicks;
			string now = unlimited != null && unlimited() ? "unlimited" : RM_MapControlMath.RateLabel(get(), pulse);
			return new Command_Action
			{
				defaultLabel = "Rate...",
				defaultDesc = verb + " rate, in levels per flow pulse (a level is one fill step of a dug square; the flow "
					+ "engine pulses every " + pulse + " ticks). Now: " + now + ".",
				icon = def.uiIcon,
				action = () =>
				{
					List<FloatMenuOption> opts = new List<FloatMenuOption>();
					if (offerUnlimited)
					{
						opts.Add(new FloatMenuOption("Unlimited (everything in reach, every pulse)", () => setUnlimited(true)));
					}
					foreach (float r in RM_MapControlMath.RatePresets)
					{
						float v = r;
						opts.Add(new FloatMenuOption(RM_MapControlMath.RateLabel(v, pulse), () =>
						{
							set(v);
							setUnlimited?.Invoke(false);
						}));
					}
					Find.WindowStack.Add(new FloatMenu(opts));
				},
			};
		}
	}
}
