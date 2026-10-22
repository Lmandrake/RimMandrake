using System.Collections.Generic;
using HarmonyLib;
using Verse;

namespace RimMandrake.FlowWorks
{
	/// <summary>SETTINGS_SEARCH_FIX_LABELS_NOT_FOUND: the Flow Works Mod Settings search finds a row by the words it SHOWS.
	/// Live 2026-10-22 (ee9fa61fbc): 'Liquid crosses', 'huge network', 'pieces' read "No setting matches" although the Water
	/// engine section draws the checkbox "Liquid crosses between the pieces of a huge network": a section was matched only by
	/// its title and its field names, never by the labels its rows draw with raw list.CheckboxLabeled.
	///
	/// The rows are plain Listing_Standard calls, so their labels are recorded as they are drawn: while the settings screen
	/// draws a section or block body (<see cref="Recording"/> set), the prefixes below add each row's label to that section's
	/// entry. A search then also hits a section whose recorded labels match. A section never drawn yet this session (collapsed,
	/// or first seen under a search) has no entry: under a search it draws one frame to be recorded, then filters by it.
	/// Only short Label() lines are recorded (a heading or a slider's value line, at most <see cref="MaxLabelLine"/> chars),
	/// not the explanatory paragraphs, so a common word does not hit every section by its prose.</summary>
	public static class RM_SettingsSearchIndex
	{
		public const int MaxLabelLine = 90;

		private static readonly Dictionary<string, List<string>> labels = new Dictionary<string, List<string>>();

		/// <summary>The section or block whose body is drawing now, and the listing drawing it; null outside the screen.</summary>
		internal static string Recording;
		internal static Listing_Standard RecordingList;

		/// <summary>Start recording a body: its entry is rebuilt from what it draws this frame.</summary>
		public static void Begin(Listing_Standard list, string key)
		{
			Recording = key;
			RecordingList = list;
			if (key != null)
			{
				labels[key] = new List<string>();
			}
		}

		public static void End()
		{
			Recording = null;
			RecordingList = null;
		}

		public static bool Known(string key)
		{
			return key != null && labels.ContainsKey(key);
		}

		/// <summary>True when any label recorded for this section matches the query (the kit's rule: case-insensitive substring).</summary>
		public static bool LabelsMatch(string key, string query)
		{
			if (key == null || !labels.TryGetValue(key, out List<string> l))
			{
				return false;
			}
			foreach (string s in l)
			{
				if (RimMandrake.Shared.SettingsKitCore.Matches(s, query))
				{
					return true;
				}
			}
			return false;
		}

		public static void Record(Listing_Standard list, string label, bool line)
		{
			if (Recording == null || label == null || !ReferenceEquals(list, RecordingList))
			{
				return;
			}
			if (line && label.Length > MaxLabelLine)
			{
				return;
			}
			labels[Recording].Add(label);
		}

		/// <summary>Search rule for one section: title or field names hit, or its drawn labels do, or it has never been drawn
		/// (drawn once so it can be recorded).</summary>
		public static bool SectionHits(string key, IEnumerable<string> names, string query)
		{
			if (RimMandrake.Shared.SettingsKitCore.Matches(key, query))
			{
				return true;
			}
			if (names != null)
			{
				foreach (string n in names)
				{
					if (RimMandrake.Shared.SettingsKitCore.Matches(n, query))
					{
						return true;
					}
				}
			}
			return !Known(key) || LabelsMatch(key, query);
		}
	}

	[HarmonyPatch(typeof(Listing_Standard), nameof(Listing_Standard.CheckboxLabeled),
		new[] { typeof(string), typeof(bool), typeof(string), typeof(float), typeof(float) },
		new[] { ArgumentType.Normal, ArgumentType.Ref, ArgumentType.Normal, ArgumentType.Normal, ArgumentType.Normal })]
	public static class RM_Patch_SettingsIndexCheckbox
	{
		public static void Prefix(Listing_Standard __instance, string label)
		{
			if (RM_SettingsSearchIndex.Recording != null)
			{
				RM_SettingsSearchIndex.Record(__instance, label, false);
			}
		}
	}

	[HarmonyPatch(typeof(Listing_Standard), nameof(Listing_Standard.CheckboxLabeled),
		new[] { typeof(string), typeof(bool), typeof(float) },
		new[] { ArgumentType.Normal, ArgumentType.Ref, ArgumentType.Normal })]
	public static class RM_Patch_SettingsIndexCheckboxTab
	{
		public static void Prefix(Listing_Standard __instance, string label)
		{
			if (RM_SettingsSearchIndex.Recording != null)
			{
				RM_SettingsSearchIndex.Record(__instance, label, false);
			}
		}
	}

	[HarmonyPatch(typeof(Listing_Standard), nameof(Listing_Standard.Label),
		new[] { typeof(string), typeof(float), typeof(TipSignal?) })]
	public static class RM_Patch_SettingsIndexLabel
	{
		public static void Prefix(Listing_Standard __instance, string label)
		{
			if (RM_SettingsSearchIndex.Recording != null)
			{
				RM_SettingsSearchIndex.Record(__instance, label, true);
			}
		}
	}

	[HarmonyPatch(typeof(Listing_Standard), nameof(Listing_Standard.SliderLabeled))]
	public static class RM_Patch_SettingsIndexSlider
	{
		public static void Prefix(Listing_Standard __instance, string label)
		{
			if (RM_SettingsSearchIndex.Recording != null)
			{
				RM_SettingsSearchIndex.Record(__instance, label, false);
			}
		}
	}

	[HarmonyPatch(typeof(Listing_Standard), nameof(Listing_Standard.ButtonTextLabeled))]
	public static class RM_Patch_SettingsIndexButton
	{
		public static void Prefix(Listing_Standard __instance, string label)
		{
			if (RM_SettingsSearchIndex.Recording != null)
			{
				RM_SettingsSearchIndex.Record(__instance, label, false);
			}
		}
	}
}
