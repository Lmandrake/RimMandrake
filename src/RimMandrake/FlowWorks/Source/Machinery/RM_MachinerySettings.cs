using System.Collections.Generic;
using System.Linq;
using UnityEngine;
using RimWorld;
using Verse;

namespace RimMandrake.FlowWorks.Machinery
{
	/// <summary>One Mod Settings switch per machine family. Put on every machine ThingDef (pump, converter,
	/// adapter); tiers of one family share a key, so "Desal plant" is one switch over its wrecked, kludged
	/// and repaired defs. The settings screen lists every key found in the DefDatabase — a new machine def
	/// gets its switch by carrying this extension, with no settings code.</summary>
	public class RM_MachineToggleExtension : DefModExtension
	{
		public string key;
		public string label;
	}

	/// <summary>
	/// Settings for the liquid machinery pass (owner, 2026-10-05: "Build the distillation and other associated
	/// machinery for liquids part of this mod."). Kept in its own class and file, called from
	/// RimMandrakeFlowWorksSettings.ExposeData and the settings window, the same shape as the rivers section.
	/// Defaults = shipped behaviour: everything runs, found works are restored only over their ruin.
	/// </summary>
	public static class RM_MachinerySettings
	{
		/// <summary>Universal pipes join tanks into one net. Off: machines reach only the tanks touching them. (Saved as
		/// `liquidHosesEnabled` until the hose port renamed the pipe, 2026-10-11; the old key is read once.)</summary>
		public static bool universalPipesEnabled = true;

		/// <summary>Scales every converter's throughput (stills, filters, found works, ship distiller).</summary>
		public static float converterRateMultiplier = 1f;

		/// <summary>Map generation scatters ruined industrial liquid works beside matching liquids.</summary>
		public static bool liquidWorksRuinsEnabled = true;

		/// <summary>A ruin is found with a damaged pump and a part-filled tank beside it.</summary>
		public static bool liquidWorksRuinStockEnabled = true;

		/// <summary>Campaign law: industrial works are FOUND, never built from the menu. On (public wave
		/// switch): kludged/repaired works may be built anywhere, not only over their ruin.</summary>
		public static bool industrialWorksBuildAnywhere = false;

		/// <summary>VE PipeSystem adapters move liquid between a FlowWorks tank and a pipe net.</summary>
		public static bool pipeAdaptersEnabled = true;

		/// <summary>Liquid networks L7/L8 (rev 2 §3.7): LITRES of spilled liquid per piece of spill filth (PROVISIONAL 400 L = the
		/// old 2 units; LIQUID_LITRES_MIGRATE_DRUMS_ARE_DRUMS).</summary>
		public static int litresPerFilth = 400;

		/// <summary>The filth step in tank units (decilitres), at its read site.</summary>
		public static int UnitsPerFilth => RM_Volume.Units(litresPerFilth);

		/// <summary>Liquid networks L9 (rev 2 §3.4; owner Q4: allowed, as theft, priced like power theft): another faction's tank
		/// joins a hose or pipe network, and liquid taken from or put into it is theft: once one of theirs within
		/// liquidTheftSightRange sees it, every day it goes on costs liquidTheftGoodwillPerDay goodwill. Off: their tanks and
		/// machines never join your networks.</summary>
		public static bool liquidTheftEnabled = true;
		/// <summary>Ruling #7 (2026-10-11, confirmed for power theft and priced the same here): goodwill per day of caught theft.</summary>
		public static int liquidTheftGoodwillPerDay = 2;
		/// <summary>Ruling #7: how far (cells) one of theirs sees it.</summary>
		public static float liquidTheftSightRange = 12f;

		/// <summary>The look a universal pipe built without a picked style draws in (Scrapper / Industrial / Modern / Futuristic),
		/// owner 2026-10-11 ruling #1: the pipe's looks are picked like the wires'. Also what every pipe built before the looks
		/// existed draws in. Art only.</summary>
		public static string pipeDefaultLook = "Scrapper";

		/// <summary>HOSE_JOINTS_REDESIGN_PUMP_TOO_PUNY (owner 2026-10-16: "if you build a pipe alongside a tank but not under it:
		/// the pipe looks like it doesn't even connect, but it should"): a pipe beside a tank or liquid machine runs its arm on to
		/// the shared edge (RM_LiquidJoins). Art only. Off: the pipe ends in a cap short of it, as before.</summary>
		public static bool pipeLinksIntoMachines = true;

		/// <summary>HOSE_JOINTS_REDESIGN_PUMP_TOO_PUNY: draw a flange/coupler/saddle at every liquid join (RM_LiquidJoins). OFF until
		/// the owner rules on the connector art (design/RimMandrake/liquid_connections_visuals_2026-10-16.md); until then the
		/// pieces draw a placeholder. Art only.</summary>
		public static bool joinFittings = false;

		/// <summary>PIPE_ENDS_BUILD_MEET_IN_THE_MIDDLE (owner 2026-10-18: "draw pipes as though they are connected into the centers of
		/// all pipe-receiving items ... so that it appears to continue beneath them through any transparent boundaries they might
		/// have"): a pipe or hose joining a tank or liquid machine is drawn on beneath it to its centre (RM_LiquidJoins
		/// SectionLayer_RM_PipeCentreStubs; RM_MapComponent_Hoses.DrawPortStub). Art only.</summary>
		public static bool pipesUnderToCentre = true;

		/// <summary>PIPE_POLES_BUILD_SAG_WITH_SUBSTANCE P2 (design/RimMandrake/flowworks_pipes_across_pits_design_2026-10-20.md): the
		/// line crossing rules (RM_LineCrossing). On: rigid pipe and conduit are built on solid ground only (never a dug square,
		/// a pit cover or any bridge deck); a flexible line (power cord) may lie on any bridge deck, rope included; a cover
		/// carries nothing; a committed dig breaks the pipe, conduit or cord on its square once (RM_LineDigBreak, phase 2); a collapsing
		/// deck reels in its hoses and drops its cords as a live wire (RM_DeckCollapseLines, phase 3). Off: lines
		/// take the engine's affordance rules alone (a timber deck admits pipe, rope admits none) and a dig leaves them standing.</summary>
		public static bool lineCrossingRulesEnabled = true;

		/// <summary>PIPE_POLES_BUILD_SAG_WITH_SUBSTANCE phase 4 (P3): pipe poles (RM_PipePole, with Gimme Some Slack) carry a pipe
		/// overhead across pits, trenches and canals. Off: the pole leaves the architect menu; poles already built stay strung.</summary>
		public static bool pipePolesEnabled = true;
		/// <summary>Longest pipe span, cells (owner's proposal 12; RM_PipePoleMath bounds 4-20). Read live by GSS.</summary>
		public static float pipePoleMaxSpan = 12f;
		/// <summary>Pipe span sag, fraction of its length (owner's widths card: about 2%, a third of the wire's; bounds 0-6%).</summary>
		public static float pipePoleSag = 0.02f;

		private static List<string> disabledMachines = new List<string>();

		// Shipped value of every public static bool/float/int/string setting above, read from the field initialisers.
		// MUST stay below the LAST public static field (C# runs initialisers in textual order).
		private static readonly Dictionary<string, object> shippedDefaults = SnapshotDefaults();

		private static Dictionary<string, object> SnapshotDefaults()
		{
			var d = new Dictionary<string, object>();
			foreach (System.Reflection.FieldInfo f in typeof(RM_MachinerySettings).GetFields(System.Reflection.BindingFlags.Public | System.Reflection.BindingFlags.Static))
			{
				if (f.FieldType == typeof(bool) || f.FieldType == typeof(float) || f.FieldType == typeof(int) || f.FieldType == typeof(string))
				{
					d[f.Name] = f.GetValue(null);
				}
			}
			return d;
		}

		/// <summary>The Reset button: every machinery setting back to its shipped value, every machine switched on.</summary>
		public static void ResetAll()
		{
			foreach (KeyValuePair<string, object> kv in shippedDefaults)
			{
				typeof(RM_MachinerySettings).GetField(kv.Key, System.Reflection.BindingFlags.Public | System.Reflection.BindingFlags.Static)?.SetValue(null, kv.Value);
			}
			disabledMachines.Clear();
			if (Current.ProgramState == ProgramState.Playing)
			{
				RM_PipePoles.RedrawSpans();   // the span shadows follow the switch and the sag now, as the sliders do
				if (Find.Maps != null)
				{
					foreach (Map m in Find.Maps) m.mapDrawer.WholeMapChanged((ulong)MapMeshFlagDefOf.Buildings);
				}
			}
		}

		public static string KeyOf(ThingDef def)
		{
			RM_MachineToggleExtension ext = def?.GetModExtension<RM_MachineToggleExtension>();
			return ext?.key.NullOrEmpty() == false ? ext.key : def?.defName;
		}

		public static bool MachineOn(ThingDef def)
		{
			string key = KeyOf(def);
			return key == null || !disabledMachines.Contains(key);
		}

		public static void ExposeData()
		{
			Scribe_Values.Look(ref universalPipesEnabled, "universalPipesEnabled", true);
			if (Scribe.mode == LoadSaveMode.LoadingVars && Scribe.loader?.curXmlParent?["universalPipesEnabled"] == null)
			{
				// a settings file written before the rename: carry the old key's value over once (it is never written again)
				bool legacy = true;
				Scribe_Values.Look(ref legacy, "liquidHosesEnabled", true);
				universalPipesEnabled = legacy;
			}
			Scribe_Values.Look(ref converterRateMultiplier, "converterRateMultiplier", 1f);
			Scribe_Values.Look(ref liquidWorksRuinsEnabled, "liquidWorksRuinsEnabled", true);
			Scribe_Values.Look(ref liquidWorksRuinStockEnabled, "liquidWorksRuinStockEnabled", true);
			Scribe_Values.Look(ref industrialWorksBuildAnywhere, "industrialWorksBuildAnywhere", false);
			Scribe_Values.Look(ref pipeAdaptersEnabled, "pipeAdaptersEnabled", true);
			Scribe_Values.Look(ref pipeDefaultLook, "pipeDefaultLook", "Scrapper");
			Scribe_Values.Look(ref pipeLinksIntoMachines, "pipeLinksIntoMachines", true);
			Scribe_Values.Look(ref joinFittings, "joinFittings", false);
			Scribe_Values.Look(ref pipesUnderToCentre, "pipesUnderToCentre", true);
			Scribe_Values.Look(ref lineCrossingRulesEnabled, "lineCrossingRulesEnabled", true);
			Scribe_Values.Look(ref pipePolesEnabled, "pipePolesEnabled", true);
			Scribe_Values.Look(ref pipePoleMaxSpan, "pipePoleMaxSpan", 12f);
			Scribe_Values.Look(ref pipePoleSag, "pipePoleSag", 0.02f);
			Scribe_Values.Look(ref litresPerFilth, "litresPerFilth", 400);
			// model 2 saved this in 200 L units under "unitsPerFilth": read once when the new key was never written
			if (Scribe.mode == LoadSaveMode.LoadingVars && Scribe.loader.curXmlParent?["litresPerFilth"] == null
				&& Scribe.loader.curXmlParent?["unitsPerFilth"] is System.Xml.XmlNode oldFilth && int.TryParse(oldFilth.InnerText, out int oldUnits))
			{
				litresPerFilth = oldUnits * RM_Volume.LegacyUnitLitres;
			}
			Scribe_Values.Look(ref liquidTheftEnabled, "liquidTheftEnabled", true);
			Scribe_Values.Look(ref liquidTheftGoodwillPerDay, "liquidTheftGoodwillPerDay", 2);
			Scribe_Values.Look(ref liquidTheftSightRange, "liquidTheftSightRange", 12f);
			Scribe_Collections.Look(ref disabledMachines, "disabledLiquidMachines", LookMode.Value);
			if (disabledMachines == null)
			{
				disabledMachines = new List<string>();
			}
		}

		private static List<(string key, string label)> ToggleRows()
		{
			var rows = new Dictionary<string, string>();
			foreach (ThingDef d in DefDatabase<ThingDef>.AllDefsListForReading)
			{
				RM_MachineToggleExtension ext = d.GetModExtension<RM_MachineToggleExtension>();
				if (ext == null)
				{
					continue;
				}
				string key = KeyOf(d);
				if (!rows.ContainsKey(key))
				{
					rows[key] = ext.label.NullOrEmpty() ? d.LabelCap.ToString() : ext.label;
				}
			}
			return rows.Select(kv => (kv.Key, kv.Value)).OrderBy(r => r.Value).ToList();
		}

		public static void DoSettingsSection(Listing_Standard list)
		{
			list.GapLine();
			list.Label("Pipes, stills and found works (universal pipes, adapters, ruined works)");
			list.CheckboxLabeled("Universal pipes join tanks into a net", ref universalPipesEnabled,
				"On: a pump, still or adapter reaches every tank on a universal-pipe run that touches it. Off: only tanks touching the machine.");
			list.Label("Converter throughput: " + converterRateMultiplier.ToString("0.00") + "x");
			converterRateMultiplier = list.Slider(converterRateMultiplier, 0.1f, 5f);
			list.CheckboxLabeled("Ruined liquid works appear on new maps (map generation)", ref liquidWorksRuinsEnabled,
				"Desal plants by salt water and brine, detox works by toxic or acid water, tar refineries by tar, pumping stations by any liquid. Affects only maps generated after the change.");
			list.CheckboxLabeled("Ruins come with a damaged pump and a part-filled tank", ref liquidWorksRuinStockEnabled,
				"On, a ruined works comes with a damaged pump and a tank part full of liquid, so there is something to salvage. Off: empty ruins. Applies to maps made from now on (map generation).");
			list.CheckboxLabeled("Industrial works may be built anywhere (not only over a ruin)", ref industrialWorksBuildAnywhere,
				"Off (campaign default): industrial scale is found, never built — a kludged or repaired works can only be raised over its ruin.");
			list.CheckboxLabeled("Pipe-net adapters run (Vanilla Expanded pipe nets)", ref pipeAdaptersEnabled,
				"On, our pipes can join Vanilla Expanded pipe nets through adapters. Off: the two kinds of pipe never connect.");
			list.Label("Spills: one patch of mess per " + RM_Volume.FormatLitres(litresPerFilth) + " of liquid run out onto the ground", -1f,
				(TipSignal?)"Liquid leaving a hose's outflow end onto dry ground, or a stopped hose emptying, leaves a cleanable spill. Fewer litres per patch = more mess.");
			litresPerFilth = UnityEngine.Mathf.RoundToInt(list.Slider(litresPerFilth, 50f, 2000f) / 50f) * 50;
			list.CheckboxLabeled("Hoses and pipes may tap other factions' tanks (theft)", ref liquidTheftEnabled,
				"On: another faction's tank or machine joins your hose or pipe network like your own. Taking liquid from it (or putting it in) is " +
				"theft: once one of theirs sees it, every day it goes on costs goodwill, like a power-tap clamp. Off: their tanks never join your networks.");
			list.Label("Caught liquid theft costs " + liquidTheftGoodwillPerDay + " goodwill a day, seen within " + liquidTheftSightRange.ToString("0") + " squares");
			liquidTheftGoodwillPerDay = UnityEngine.Mathf.RoundToInt(list.Slider(liquidTheftGoodwillPerDay, 0f, 10f));
			liquidTheftSightRange = UnityEngine.Mathf.Round(list.Slider(liquidTheftSightRange, 4f, 30f));
			list.Label("Default look of universal pipes (art only; a pipe built without a picked look, and every older pipe):");
			if (list.ButtonText(PipeStyles.DefaultLook(pipeDefaultLook)))
			{
				var opts = new List<FloatMenuOption>();
				foreach (string look in PipeStyles.Looks)
				{
					string l = look;
					opts.Add(new FloatMenuOption(l, () => pipeDefaultLook = l));
				}
				Find.WindowStack.Add(new FloatMenu(opts));
			}
			list.CheckboxLabeled("Rigid pipe and conduit need solid ground; cords lie on any bridge deck", ref lineCrossingRulesEnabled,
				"On: pipe and power conduit cannot be built on a dug square (pit, trench, canal, moat), a concealed pit or any bridge deck: "
			  + "they are rigid. A flexible power cord may lie on any bridge deck, rope included. A concealed pit carries no lines. "
			  + "A hose goes into a dug square only down a ramp or a ladder (a raised ladder still holds it), never over a sheer wall, "
			  + "and its end couples only to a pump, tank or water on its own level; a hose already laid across a newly dug square "
			  + "re-routes or reels in. A frame that ends up on such a square is cancelled and refunded. Digging a square breaks the pipe, conduit or cord "
			  + "on it when the cut is made (not when it is ordered); the materials drop as salvage. A bridge deck that collapses reels in "
			  + "the hoses across it, and a powered cord it drops lies in the hole as a live wire (it shocks through Gimme Some Slack's "
			  + "fallen-wire setting, when that mod is loaded). Off: lines (and hoses) follow the game's ground rules alone, digging leaves them "
			  + "standing, and a collapsing deck only destroys what stands on it.");
			bool polesWere = pipePolesEnabled;
			list.CheckboxLabeled("Pipe poles carry pipe overhead across pits, trenches and canals (needs Gimme Some Slack loaded)", ref pipePolesEnabled,
				"On: a pipe pole (Pipe networks menu) hangs a stiff overhead pipe to another pipe pole, using Gimme Some Slack's overhead "
			  + "lines. Poles stand on solid ground only, never on a bridge deck, a concealed pit or a dug square; a span is not walkable. "
			  + "Digging out a pole's square knocks it down and its spans fall. This is the pipe poles' own switch: Gimme Some Slack's "
			  + "power-lines switch does not touch them. Off: the pole leaves the build menu, new poles do not link, built spans are not "
			  + "drawn and carry no liquid; they stay strung and come back when switched on. The art is a stand-in until the pipe widths "
			  + "are judged in game.");
			if (pipePolesEnabled != polesWere)
			{
				RM_PipePoles.RedrawSpans();   // the span shadows on the ground follow the switch now
			}
			if (pipePolesEnabled)
			{
				list.Label(RM_PipePoleMath.SpanLabel(pipePoleMaxSpan), -1f, (TipSignal?)"How far one pipe span may reach between two poles. Applies now to new links; spans already strung stay.");
				pipePoleMaxSpan = RM_PipePoleMath.ClampSpan(list.Slider(pipePoleMaxSpan, RM_PipePoleMath.MaxSpanMin, RM_PipePoleMath.MaxSpanMax));
				list.Label(RM_PipePoleMath.SagLabel(pipePoleSag), -1f, (TipSignal?)"How far a pipe span hangs at its middle. Power wires hang about 6%; a pipe is stiffer. Art only; applies now.");
				float sagWas = pipePoleSag;
				pipePoleSag = RM_PipePoleMath.ClampSag(UnityEngine.Mathf.Round(list.Slider(pipePoleSag, RM_PipePoleMath.SagMin, RM_PipePoleMath.SagMax) * 1000f) / 1000f);
				if (pipePoleSag != sagWas)
				{
					RM_PipePoles.RedrawSpans();   // the span shadows on the ground re-print now, not at the next unrelated dirty
				}
			}
			bool linksWas = pipeLinksIntoMachines, fitWas = joinFittings, underWas = pipesUnderToCentre;
			list.CheckboxLabeled("Pipes run right up to the tanks and machines they join (art only)", ref pipeLinksIntoMachines,
				"On: a pipe beside a tank, pump or still draws its run on to the shared edge, so you can see it joins. Off: it ends in a cap short of it. Needs a restart to take effect if it was off at startup.");
			list.CheckboxLabeled("Connector fittings at liquid joins (preview: placeholder art)", ref joinFittings,
				"Draws a flange where a pipe meets a tank or machine, a coupler where a pump touches a tank, and a saddle where a hose couples onto a pipe. " +
				"The fitting art is still being designed; until it lands every fitting draws a stand-in. Art only.");
			list.CheckboxLabeled("Pipes and hoses run on beneath tanks and machines to their centre (art only)", ref pipesUnderToCentre,
				"On: a pipe or hose joining a tank, pump, bleed well, sprinkler or other liquid machine is drawn on underneath it to the middle of the building, so it shows through any see-through edges as if it plugs into the centre. Off: it stops at the building's edge.");
			if ((linksWas != pipeLinksIntoMachines || fitWas != joinFittings || underWas != pipesUnderToCentre) && Current.ProgramState == ProgramState.Playing && Find.Maps != null)
			{
				foreach (Map m in Find.Maps) m.mapDrawer.WholeMapChanged((ulong)MapMeshFlagDefOf.Buildings);
			}
			foreach ((string key, string label) row in ToggleRows())
			{
				bool on = !disabledMachines.Contains(row.key);
				bool was = on;
				list.CheckboxLabeled(row.label + " runs", ref on);
				if (on != was)
				{
					if (on)
					{
						disabledMachines.Remove(row.key);
					}
					else
					{
						disabledMachines.Add(row.key);
					}
				}
			}
			list.GapLine();
			RimMandrake.Shared.SettingsKitDrawer.ResetButton(list, ResetAll);
		}
	}
}
