using System.Collections.Generic;
using System.Linq;
using UnityEngine;
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
		/// <summary>Hoses join tanks into one net. Off: machines reach only the tanks touching them.</summary>
		public static bool liquidHosesEnabled = true;

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

		private static List<string> disabledMachines = new List<string>();

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
			Scribe_Values.Look(ref liquidHosesEnabled, "liquidHosesEnabled", true);
			Scribe_Values.Look(ref converterRateMultiplier, "converterRateMultiplier", 1f);
			Scribe_Values.Look(ref liquidWorksRuinsEnabled, "liquidWorksRuinsEnabled", true);
			Scribe_Values.Look(ref liquidWorksRuinStockEnabled, "liquidWorksRuinStockEnabled", true);
			Scribe_Values.Look(ref industrialWorksBuildAnywhere, "industrialWorksBuildAnywhere", false);
			Scribe_Values.Look(ref pipeAdaptersEnabled, "pipeAdaptersEnabled", true);
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
			list.Label("Liquid machinery (hoses, stills, found works, adapters)");
			list.CheckboxLabeled("Hoses join tanks into a net", ref liquidHosesEnabled,
				"On: a pump, still or adapter reaches every tank on a hose run that touches it. Off: only tanks touching the machine.");
			list.Label("Converter throughput: " + converterRateMultiplier.ToString("0.00") + "x");
			converterRateMultiplier = list.Slider(converterRateMultiplier, 0.1f, 5f);
			list.CheckboxLabeled("Ruined liquid works appear on new maps (map generation)", ref liquidWorksRuinsEnabled,
				"Desal plants by salt water and brine, detox works by toxic or acid water, tar refineries by tar, pumping stations by any liquid. Affects only maps generated after the change.");
			list.CheckboxLabeled("Ruins come with a damaged pump and a part-filled tank", ref liquidWorksRuinStockEnabled);
			list.CheckboxLabeled("Industrial works may be built anywhere (not only over a ruin)", ref industrialWorksBuildAnywhere,
				"Off (campaign default): industrial scale is found, never built — a kludged or repaired works can only be raised over its ruin.");
			list.CheckboxLabeled("Pipe-net adapters run (Vanilla Expanded pipe nets)", ref pipeAdaptersEnabled);
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
		}
	}
}
